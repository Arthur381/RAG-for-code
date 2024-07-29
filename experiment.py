import json

# 要删除的 context_type 值
types_to_remove = {'base_prompt', 'full_context'}

# 打开原始文件和创建新文件
with open('/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/New_evaluation_base.jsonl', 'r') as original_file, open('/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/New_evaluation_go.jsonl', 'w') as filtered_file:
    for line in original_file:
        data = json.loads(line)  # 将每行转换成字典
        if data.get('context_type') not in types_to_remove:
            filtered_file.write(line)  # 如果不是要删除的类型，写入新文件
