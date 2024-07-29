import json
import httpx
from openai import OpenAI

# 假设已经从evaluation_prompt.py导入了所需的评分指导
from evaluation_prompt import EVALUATION_GUIDELINE, General_Judge_Prompt

def load_data(file_path):
    """Load and parse JSON file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def create_evaluation_prompt(data_entry, guideline):
    """ Create evaluation prompts based on the provided data entry and guideline """
    if isinstance(data_entry, dict):
        character_profile = data_entry.get('character_profile', 'No character profile provided')
        dialogue = "\n".join([f"{turn['speaker']}: {turn['utterance']}" for turn in data_entry.get('dialogue', [])])
        user_query = data_entry.get('dialogue', [])[-1].get('utterance', 'No query provided') if data_entry.get('dialogue') else 'No dialogue provided'
        character_response = data_entry.get('response_messages', {}).get('response', 'No response provided')
    else:
        return "Invalid data entry format; expected a dictionary."

    return General_Judge_Prompt.format(
        task_guideline=guideline,
        character_profile=character_profile,
        dialogue=dialogue,
        user_query=user_query,
        character_response=character_response
    )

def save_progress(index):
    """ Save the current progress to a file """
    with open('/home/zhangxuanming/CharacterBench/progress.txt', 'w') as file:
        file.write(str(index))
        
def load_progress():
    """ Load the current progress from a file """
    try:
        with open('/home/zhangxuanming/CharacterBench/progress.txt', 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0

def main():
    client = OpenAI(base_url="https://svip.xty.app/v1", api_key="sk-gp2npDc6HA5CPi2bC37510B812D84053A9F153AbF7Bb6483", http_client=httpx.Client(base_url="https://svip.xty.app/v1", follow_redirects=True))

    data = load_data("/home/zhangxuanming/CharacterBench/emotion_self_awareness_benchmark_data_sample.json")
    data1 = load_data("/home/zhangxuanming/CharacterBench/human_likeness_benchmark_data_sample.json")
    data2 = load_data("/home/zhangxuanming/CharacterBench/emotion_reccognization_benchmark_data_sample.json")
    start_index = load_progress()
    with open("/home/zhangxuanming/CharacterBench/evaluation_results.jsonl", 'a', encoding='utf-8') as outfile: 
        for i in range(start_index, len(data)):
            entry = data[i]
            entry1 = data1[i]
            entry2 = data2[i]
            prompt_recall_emotion = create_evaluation_prompt(entry, EVALUATION_GUIDELINE['recall_emotion'])
            prompt_human_likeness = create_evaluation_prompt(entry1, EVALUATION_GUIDELINE['human_likeness'])
            prompt_emotion_recognization = create_evaluation_prompt(entry2, EVALUATION_GUIDELINE['emotion_recognization'])
        # 请求模型进行评分
            response_recall_emotion = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt_recall_emotion}]
            )
            print("Emotion Evaluation:", response_recall_emotion.choices[0].message.content)
            response_human_likeness = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt_human_likeness}]
            )
            print("Human Likeness Evaluation:", response_human_likeness.choices[0].message.content)
            response_emotion_recognization = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt_emotion_recognization}]
            )
            print("Emotion Recognization Evaluation:", response_emotion_recognization.choices[0].message.content)
            # Write to JSONL file
            json.dump({
                "Emotion Evaluation Prompt": prompt_recall_emotion,
                "Emotion Evaluation": response_recall_emotion.choices[0].message.content,
                "Human Likeness Evaluation Prompt": prompt_human_likeness,
                "Human Likeness Evaluation": response_human_likeness.choices[0].message.content,
                "Emotion Recognization Evaluation Prompt": prompt_emotion_recognization,
                "Emotion Recognization Evaluation": response_emotion_recognization.choices[0].message.content
            }, outfile,ensure_ascii=False)
            outfile.write('\n')  # Write a new line for the next JSON object    
            save_progress(i+1)

if __name__ == "__main__":
    main()