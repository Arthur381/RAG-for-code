import json

# Load the provided JSONL file
file_path = '/home/zhangxuanming/cceval/data/python/line_completion_oracle_openai_cosine_sim copy.jsonl'
processed_data = []

with open(file_path, 'r') as file:
    for line in file:
        # Convert each line from JSONL to dictionary
        data = json.loads(line.strip())
        
        # Check if 'crossfile_context' and 'list' are in the dictionary and proceed if present
        if 'crossfile_context' in data and 'list' in data['crossfile_context']:
            # Sort the list of dictionaries by 'score' in descending order
            sorted_list = sorted(data['crossfile_context']['list'], key=lambda x: x['score'], reverse=True)
            
            # Keep only the highest and lowest score tuples
            if len(sorted_list) > 1:
                data['crossfile_context']['list'] = [sorted_list[0], sorted_list[-1]]
            else:
                # If there's only one element, we keep it as both the highest and lowest
                data['crossfile_context']['list'] = sorted_list
            
        # Append the modified data to the list for later use
        processed_data.append(data)

# Define the path for the new JSONL file
new_file_path = '/home/zhangxuanming/cceval/data/python/line_completion_oracle_openai_cosine_sim.jsonl'

# Write the processed data back to a new JSONL file
with open(new_file_path, 'w') as file:
    for entry in processed_data:
        file.write(json.dumps(entry) + '\n')
