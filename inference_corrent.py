import json
import httpx
from openai import OpenAI
import threading
import time

def read_and_parse_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def generate_prompt(code, analysis):
    api_descriptions = ". ".join([f"API '{api[0]}' with arguments {api[1]}" for api in analysis])
    return f"You are a senior programmer, you need to combine code and tree-sitter analysis to explain the overall code usage and functionality, and the usage and functionality of each API and its arguments. Your explanation should be detailed, clear, and comprehensive, and should not skip any details. Here is the code: '{code}'. Analysis: {api_descriptions}."

def process_data(api_key, base_url, data_chunk, output_path):
    with httpx.Client(base_url=base_url, follow_redirects=True) as http_client:
        client = OpenAI(api_key=api_key, http_client=http_client)    
        for record in data_chunk:
            prompt = generate_prompt(record['prompt'], record['prompt_analysis'])
            attempt = 0
            while attempt < 5:  # Retry up to 3 times
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",
                        messages=[
                            {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    record['prompt'] = response.choices[0].message.content  # Modify the record with the response
                    break  # Break the loop if success
                except (httpx.HTTPError, json.JSONDecodeError) as e:
                    print(f"Attempt {attempt+1}: HTTP or JSON error, retrying...")
                    attempt += 1
                    time.sleep(2**attempt)  # Exponential backoff
                except Exception as e:
                    print(f"Attempt {attempt+1}: An unexpected error occurred - {str(e)}")
                    attempt += 1
                    time.sleep(2**attempt)  # Exponential backoff
                    
            for i, chunk in enumerate(record['crossfile_context']['list']):
                attempt0 = 0 
                while attempt0 < 10:
                    try:
                        chunk_prompt = generate_prompt(chunk['retrieved_chunk'], record['crossfile_context']['list_analysis'][i])
                        chunk_response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
                                {"role": "user", "content": chunk_prompt}
                            ]
                        )
                        record['crossfile_context']['list'][i]['retrieved_chunk'] = f"'''{chunk_response.choices[0].message.content}'''\n{chunk['retrieved_chunk']}"
                        print(chunk_response.choices[0].message.content)
                        break
                    except json.JSONDecodeError:
                        print(f"Attempt {attempt+1}: JSON format error, retrying...")
                        attempt0 += 1
                        time.sleep(2**attempt)  # Exponential backoff
                    except Exception as e:
                        print(f"Attempt {attempt+1}: An error occurred - {str(e)}")
                        time.sleep(2**attempt)  # Exponential backoff
                        attempt0 += 1
            with open(output_path, 'a') as file:
                file.write(json.dumps(record) + '\n')

def main(file_path, output_path, api_keys, base_urls, start_index=2283):
    data = read_and_parse_jsonl(file_path)
    
    threads = []
    for i, (api_key, base_url) in enumerate(zip(api_keys, base_urls)):
        chunk = data[start_index + i::len(api_keys)]
        thread = threading.Thread(target=process_data, args=(api_key, base_url, chunk, output_path))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Usage
api_keys = ["sk-gp2npDc6HA5CPi2bC37510B812D84053A9F153AbF7Bb6483", "sk-QFCqUFqUcwMNzhimriFJert3v7qd4tSbJk4WGFX23NhQmjNJ"]
base_urls = ["https://svip.xty.app/v1", "https://api.chatanywhere.tech/v1"]
main('/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/line_completion_oracle_openai_cosine_sim_analysis.jsonl', '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/line_completion_oracle_openai_cosine_sim_final.jsonl', api_keys, base_urls)
