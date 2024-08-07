import os
import ast
import json
'''对于每个.py 文件，使用 JSON文件储存，我想要储存一个all_class[[f1,f2],[],[]...] 即 all_class[i] 代表第 i 个类对应的成员函数'''
'''再储存一个 list [f1,f2],  fi:function_block'''
class function_block():
    def __init__(self,name=None,b_class=None,s_line=None,e_line=None,calls=None,import_list=None):
        self.name=name
        self.belong_class=b_class
        self.start_line=s_line
        self.end_line=e_line
        self.call_func=calls
        self.import_repo=import_list
        '''还有 args 和 returns method'''
    
    def __repr__(self):
        return (f"FunctionBlock(name={self.name}, class_name={self.belong_class}, "
                f"lineno={self.start_line}, end_lineno={self.end_line}, calls={self.call_func}),import={self.import_repo}")
    
    def to_dict(self):
        return {
            'name': self.name,
            'class': self.belong_class,
            'lineno': self.start_line,
            'end_lineno': self.end_line,
            'calls': self.call_func,
            'import':self.import_repo
        }

def get_python_files(directory):
    """遍历目录，获取所有 Python 文件的路径"""
    python_files = []
    cnt=0
    print(directory)
    for root, dirs, files in os.walk(directory):
        for file in files:
            cnt+=1
            if file.endswith(".py"):  # 确定类型
                python_files.append(os.path.join(root, file))
    return python_files



class FunctionVisitor(ast.NodeVisitor):
    
    def __init__(self):
        self.functions = []

    def get_function_calls(self, node):
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Name):
                    calls.append(func.id)
                elif isinstance(func, ast.Attribute):
                    value = func.value
                    if isinstance(value, ast.Name):
                        calls.append(f"{value.id}.{func.attr}")
                    elif isinstance(value, ast.Attribute):
                        # For nested attributes like module.class.method
                        attr_chain = []
                        while isinstance(value, ast.Attribute):
                            attr_chain.append(value.attr)
                            value = value.value
                        if isinstance(value, ast.Name):
                            attr_chain.append(value.id)
                            calls.append(".".join(reversed(attr_chain)))
        return calls

    def visit_FunctionDef(self, node):
        # 检查父节点是否为ClassDef
        class_name = None
        current = node
        while current:
            # 向上回溯父节点
            if isinstance(current, ast.ClassDef):
                class_name = current.name
                break
            current = getattr(current, 'parent', None)

        new_func = function_block(
            node.name,
            class_name,  # 添加类名信息
            node.lineno,
            node.end_lineno,
            self.get_function_calls(node),
        )
        self.functions.append(new_func)
        self.generic_visit(node)


def add_parent_references(node):#递归
    for child in ast.iter_child_nodes(node):
        child.parent = node
        add_parent_references(child)

def parse_functions(file_content):
    '''对某个确定的 py 文件切割里面的函数 '''
    # 解析传递的 Python 文件内容
    tree = ast.parse(file_content)
    add_parent_references(tree)  # 为 tree 中的节点添加父节点
    visitor = FunctionVisitor()
    visitor.visit(tree)

    def parse_imports():
        '''得到文件 import 的类，也需要加在该类切割的函数的 block 里面'''
        tree = ast.parse(file_content)

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):  # 导入模块，如 torch
                for alias in node.names:
                    # 加入名称而不加入 asname
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):  # 导入模块中的部分
                module = node.module  # 找到这一部分对应的模块
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports
    
    this_file_import = parse_imports()  # 为 block 中添加 import 信息
    for func in visitor.functions:
        func.import_repo = this_file_import
    
    return visitor.functions

def parse_class_methods(file_content):
    """解析 Python 文件，提取类和函数信息"""
    # 解析传递的 Python 文件内容
    tree = ast.parse(file_content)
    parsed_class = list()
    for node in ast.walk(tree):
        '''考虑 class and its methods '''
        if isinstance(node, ast.ClassDef):
            # 向列表中加入类
            class_info = {
                "class_name": node.name,
                "methods": []
            }
            for sub_node in node.body:
                # TODO: 这里没有解决函数的嵌套定义
                if isinstance(sub_node, ast.FunctionDef):
                    # 这里仅仅使用 method 的名字进行索引
                    class_info["methods"].append(sub_node.name)
                    
            parsed_class.append(class_info)
    return parsed_class

def save_to_json(data, output_file="json_temp.json"):
    """将数据保存为 JSON 文件"""
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def BC_main(python_file_context):
    all_parsed_data = {}

    for key, value in python_file_context.items():
        parsed_data = {"Functions": [], "Classes": []}
        parsed_data_ori = {"Functions": []}
        # Step 1: 解析函数
        parsed_data_ori["Functions"] = parse_functions(value)
        parsed_data["Functions"] = [func.to_dict() for func in parsed_data_ori["Functions"]]
        # Step 2: 解析类和方法
        parsed_data["Classes"] = parse_class_methods(value)
        all_parsed_data[key] = parsed_data
    save_to_json(all_parsed_data)

'''Finally what will be in the json file is a big dictionary, key: file_path(only python file), value: {functions ; class}(both are lists)'''

