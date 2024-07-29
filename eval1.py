import json
from difflib import SequenceMatcher
import re

def load_data(file_path):
    """加载数据文件。"""
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            yield json.loads(line)

def calculate_exact_match(pred, groundtruth):
    """计算精确匹配得分。"""
    return 1 if pred.startswith(groundtruth) else 0

def extract_first_two_code_lines(code):
    """提取前两行有效代码行（排除空行和注释）。"""
    lines = code.split('\n')
    valid_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    return '\n'.join(valid_lines[:2])

def calculate_edit_similarity(pred, groundtruth):
    """计算编辑相似度得分。"""
    pred_code_lines = extract_first_two_code_lines(pred)
    groundtruth_code_lines = extract_first_two_code_lines(groundtruth)
    return SequenceMatcher(None, pred_code_lines, groundtruth_code_lines).ratio()

def extract_identifiers(code):
    """提取代码中的标识符。"""
    return set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code))

def calculate_identifier_match(pred, groundtruth):
    """计算标识符匹配得分，只考虑前两行有效代码。"""
    pred_code_lines = extract_first_two_code_lines(pred)
    groundtruth_code_lines = extract_first_two_code_lines(groundtruth)
    
    pred_identifiers = extract_identifiers(pred_code_lines)
    groundtruth_identifiers = extract_identifiers(groundtruth_code_lines)
    if not pred_identifiers or not groundtruth_identifiers:
        return 0  # 避免除以零
    common_identifiers = pred_identifiers.intersection(groundtruth_identifiers)
    return len(common_identifiers) / len(groundtruth_identifiers)

def join_groundtruth_and_context(groundtruth, right_context):
    """确保groundtruth和right context被正确连接为字符串。"""
    # 如果groundtruth或right context不是字符串，则尝试将其内容转换为字符串
    if not isinstance(groundtruth, str):
        groundtruth = ' '.join(groundtruth) if isinstance(groundtruth, list) else str(groundtruth)
    if not isinstance(right_context, str):
        right_context = ' '.join(right_context) if isinstance(right_context, list) else str(right_context)
    return groundtruth + right_context

def add_scores_to_data(file_path):
    """计算得分并添加到数据中。"""
    updated_data = []

    for item in load_data(file_path):
        pred = item.get('pred', '')
        groundtruth0 = item.get('groundtruth', '')
        groundtruth = item.get('groundtruth', '')
        right_context = item.get('right_context', '')
        full_groundtruth = join_groundtruth_and_context(groundtruth, right_context)
        
        exact_match = calculate_exact_match(pred, groundtruth0)
        edit_similarity = calculate_edit_similarity(pred, full_groundtruth)
        identifier_match = calculate_identifier_match(pred, full_groundtruth)
        
        item['scores'] = {
            'exact_match': exact_match,
            'edit_similarity': edit_similarity,
            'identifier_match': identifier_match,
            'groundtruth_valid': extract_first_two_code_lines(full_groundtruth)
        }
        
        updated_data.append(item)

    return updated_data

def save_updated_data_to_jsonl(updated_data, output_file_path):
    """将更新后的数据保存到JSONL文件中。"""
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for item in updated_data:
            file.write(json.dumps(item) + '\n')

# 输入文件路径
input_file_path = '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/New_prediction.jsonl'  # 请替换为实际路径
# 输出文件路径
output_file_path = '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/New_evaluation_base.jsonl'  # 请替换为实际路径

# 执行评估并保存结果
updated_data = add_scores_to_data(input_file_path)
save_updated_data_to_jsonl(updated_data, output_file_path)

print(f"处理完成，评估结果已保存到 {output_file_path}")
