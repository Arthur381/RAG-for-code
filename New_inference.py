import json
import httpx
from openai import OpenAI
import time
from analyze_prompt import General_Analyze_Prompt
import textwrap

def read_and_parse_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def generate_prompt(retrieved_code,prompt, identifiers):
    identifier_list = ", ".join([f"'{identifier}'" for identifier in identifiers])
    return General_Analyze_Prompt.format(
        retrieved_code=textwrap.dedent(retrieved_code).strip(),
        prompt=textwrap.dedent(prompt).strip(),
        identifiers=identifier_list
    )

def main(file_path, output_path,state_path):
    # Read and parse the JSONL file
    data = read_and_parse_jsonl(file_path)
    # Initialize the OpenAI client
    client = OpenAI(
        base_url="https://api.chatanywhere.tech/v1", 
        api_key="sk-QFCqUFqUcwMNzhimriFJert3v7qd4tSbJk4WGFX23NhQmjNJ",
        http_client=httpx.Client(
            base_url="https://api.chatanywhere.tech/v1",
            follow_redirects=True,
        )
    )
    start_index = 0
    
    try:
        with open(state_path, 'r') as file:
            state = json.load(file)
            start_index = state['last_index'] + 1
    except (FileNotFoundError, json.JSONDecodeError):
        print("No state file found, starting from the beginning.")

    # Process each record
    for index,record in enumerate(data[start_index:], start=start_index):       
        # Handle 'retrieved_chunk' and corresponding 'list_analysis'
        for i, chunk in enumerate(record['crossfile_context']['list']):
            attempt0 = 0
            while attempt0 < 30:
                try:
                    chunk_prompt = generate_prompt(chunk['retrieved_chunk'], record['prompt'], record['crossfile_context']['list_identifiers'][i])
                    chunk_response = client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",
                        messages=[
                            {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
                            {"role": "user", "content": chunk_prompt}
                        ]
                    )
                    # 尝试解析JSON，以验证格式
                    chunk_response = chunk_response.choices[0].message.content
                    response = json.loads(chunk_response.replace('```', '').replace('json', '').strip())
                    print(response)
                    #***分割输出，analyze做标识作为新元素，help做标识作为新元素，生成代码做标识作为新元素
                    record['analyze'] = json.dumps(response['analyze'], indent=2)   
                    record['guideline'] = response['guideline']
                    record['completion'] = response['completion']
                    with open(output_path, 'a') as file:
                        file.write(json.dumps(record) + '\n')
                
                    with open(state_path, 'w') as file:
                        json.dump({'last_index': index}, file)
                    break
                
                except json.JSONDecodeError:
                    print(f"Attempt {attempt0+1}: JSON format error, retrying...")
                    attempt0 += 1
                    time.sleep(2*attempt0)  # Exponential backoff
                except Exception as e:
                    print(f"Attempt {attempt0+1}: An error occurred - {str(e)}")
                    time.sleep(2*attempt0)  # Exponential backoff
                    attempt0 += 1

# Usage
main('/home/zhangxuanming/cceval/data/python/New_line_completion_oracle_openai_cosine_sim.jsonl', '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/New_line_completion_oracle_openai_cosine_sim.jsonl','/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/state.json')
