import json

# 读取 prediction.jsonl 文件，并为每条记录按照 task_id 添加对应的 right_context
updated_lines = []
with open("/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/prediction_final.jsonl", "r", encoding="utf-8") as file:
    predictions = [json.loads(line) for line in file]

# 读取 line_completion_rg1_unixcoder_cosine_sim.jsonl 文件，并将数据存储在字典中，键为 task_id，值为 right_context
right_context_map = {}
with open("/home/zhangxuanming/cceval/data/python/line_completion_oracle_openai_cosine_sim_final.jsonl", "r", encoding="utf-8") as file:
    right_contexts = [json.loads(line) for line in file]

# 创建一个字典来快速查找right_contexts
right_contexts_dict = {item['task_id']: item['right_context'] for item in right_contexts}

# 更新predictions列表中的元素
for prediction in predictions:
    task = prediction.get('task_id')
    if task in right_contexts_dict:
        # 如果在right_contexts_dict中找到了相应的任务，就添加right_context字段
        prediction['right_context'] = right_contexts_dict[task]

# 将更新后的数据写回 prediction.jsonl 文件
with open("/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/prediction_updated_final.jsonl", "w", encoding="utf-8") as file:
    for item in predictions:
        json.dump(item, file)
        file.write('\n')  # 保持jsonl的格式，每个json对象后面跟一个换行符
