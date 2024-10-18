import json
from tree_sitter import Language, Parser

# Build and load the language grammar for Python
Language.build_library(
  '/home/zhangxuanming/build/my-languages.so',
  ['/home/zhangxuanming/tree-sitter-python-master']
)

PY_LANGUAGE = Language('/home/zhangxuanming/build/my-languages.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)

def extract_functions_and_args(source_code):
    tree = parser.parse(bytes(source_code, "utf8"))
    root_node = tree.root_node
    functions = []

    def visit(node):
        if node.type == 'call':
            function_name = source_code[node.child_by_field_name('function').start_byte:node.child_by_field_name('function').end_byte]
            arg_list = []
            args = node.child_by_field_name('arguments')
            if args:
                for arg in args.children:
                    if arg.type == 'named_expression' or arg.type == 'identifier':
                        arg_list.append(source_code[arg.start_byte:arg.end_byte])
            functions.append((function_name, arg_list))
        for child in node.children:
            visit(child)

    visit(root_node)
    return functions

def analyze_code_from_jsonl(input_file_path, output_file_path):
    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        for line in infile:
            json_data = json.loads(line)
            prompt_code = json_data['prompt']
            prompt_analysis = extract_functions_and_args(prompt_code)
            json_data['prompt_analysis'] = prompt_analysis

            list_analysis = []
            for item in json_data['crossfile_context']['list']:
                    
                chunk_code = item['retrieved_chunk']
                chunk_analysis = extract_functions_and_args(chunk_code)
                list_analysis.append(chunk_analysis)
            json_data['crossfile_context']['list_analysis'] = list_analysis
            json.dump(json_data, outfile)
            outfile.write('\n')

# Set the path to your JSONL file
input_file_path = '/home/zhangxuanming/cceval/data/python/line_completion_oracle_openai_cosine_sim.jsonl'
output_file_path = '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/line_completion_oracle_openai_cosine_sim_analysis.jsonl'
analyzed_data = analyze_code_from_jsonl(input_file_path, output_file_path)
