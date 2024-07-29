import json

# 读取文件并解析JSON
evaluation_data = []
with open('/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/New_evaluation.jsonl', 'r') as file:
    for line in file:
        evaluation_data.append(json.loads(line))

# 按task_id分组，并筛选base_prompt和chunk_{i}的数据
grouped_data = {}
for data in evaluation_data:
    task_id = data['task_id']
    context_type = data['context_type']
    if context_type == 'base_prompt' or context_type.startswith('chunk_'):
        if task_id not in grouped_data:
            grouped_data[task_id] = {'base_prompt': None, 'chunks': []}
        if context_type == 'base_prompt':
            grouped_data[task_id]['base_prompt'] = data
        else:
            grouped_data[task_id]['chunks'].append(data)

# 对比base_prompt和chunk_{i}下的edit_similarity，确定增强、拖累、不变的数据量
enhanced = 0
degraded = 0
unchanged = 0

for task_id, data in grouped_data.items():
    base_prompt_es = data['base_prompt']['scores']['edit_similarity'] if data['base_prompt'] else None
    for chunk_data in data['chunks']:
        if base_prompt_es is not None:
            chunk_es = chunk_data['scores']['edit_similarity']
            if chunk_es > base_prompt_es:
                enhanced += 1
            elif chunk_es < base_prompt_es:
                degraded += 1
            else:
                unchanged += 1

total = enhanced + degraded + unchanged

print(enhanced, degraded, unchanged, total)
