import json

def process_and_format_jsonl_final(input_path, output_path):
    with open(input_path, 'r') as file, open(output_path, 'w') as output:
        for line_number, line in enumerate(file, 1):
            try:
                data = json.loads(line)
                context_type = data.get('context_type', '')
                prompt = data.get("prompt", '')
                similarity_score = data.get("similarity_score", 0)
                edit_similarity_difference = data.get("edit_similarity_difference", 0)
                scores = data.get("scores", {})
                # 检查 context_type 是否符合格式 'chunk_{i}'
                if context_type.startswith('chunk_'):
                    index = int(context_type.split('_')[1])  # 从context_type获取索引i
                    # 从 crossfile_context 的 list 中获取第 i 个元素的 retrieved_chunk
                    retrieved_chunk = data['crossfile_context']['list'][index]['retrieved_chunk']
                    # 直接从顶层提取 common_identifiers 和 similarity_metrics
                    #common_identifiers = data.get('common_identifiers', [])
                    #similarity_metrics = data.get('similarity_metrics', {})
                    # 从 scores 中提取 groundtruth_valid
                    #groundtruth_valid = data['scores'].get('groundtruth_valid', 'N/A')

                    # 检查 common_identifiers 和 similarity_metrics 是否为空，如果为空则记录错误
                    #if not common_identifiers or not similarity_metrics:
                        #print(f"Warning: Empty common_identifiers or similarity_metrics on line {line_number}.")

                    # 将信息格式化并写入文件
                    output.write("【Prompt】\n")
                    output.write(f"{prompt}\n")
                    # 写入retrieved_chunk
                    output.write("【Retrieved Chunk】\n")
                    output.write(f"{retrieved_chunk}\n")
                    # 写入groundtruth_valid
                    #output.write("【Groundtruth Valid】\n")                        
                    #output.write(f"{groundtruth_valid}\n")
                        
                    output.write("【Retrieved Similarity】\n")
                    output.write(f"{similarity_score}\n")
                    output.write("【Edit Similarity Differnce】\n")
                    output.write(f"{edit_similarity_difference}\n")
                        
                    # 写入common_identifiers
                    #out_file.write("【Common Identifiers】\n")
                    #out_file.write(f"{', '.join(common_identifiers)}\n\n")
                    # 写入similarity_metric
                    output.write("【Scores】\n")
                    for key, value in scores.items():
                        output.write(f"【{key.capitalize()}】\n")
                        output.write(f"{key}: {value}\n")
                    
                    # 写入所有 similarity metrics 的子元素
                    '''for metric, value in similarity_metrics.items():
                        output.write(f"【{metric.capitalize()}】\n")
                        output.write(f"{value}\n")'''
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_number}: {e}")

# 调用函数以处理文件并生成输出
input_path = '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/conclude_identifiers_final.jsonl'
output_path = '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/conclude_identifiers_final.txt'
process_and_format_jsonl_final(input_path, output_path)
                                         
#process_jsonl('/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/conclude_identifiers.jsonl', '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun')
