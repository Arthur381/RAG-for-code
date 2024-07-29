import json

def process_data(file_path):
    # Initialize dictionaries to store total scores and counts for averaging
    scores = {
        'base_prompt': {'edit_similarity': 0.0, 'identifier_match': 0.0, 'count': 0},
        'full_context': {'edit_similarity': 0.0, 'identifier_match': 0.0, 'count': 0},
        'chunk': {'edit_similarity': 0.0, 'identifier_match': 0.0, 'count': 0}
    }

    # Read the file and process each line
    with open(file_path, 'r') as file:
        for line in file:
            data = json.loads(line)

            scores['chunk']['edit_similarity'] += data['scores']['edit_similarity']
            scores['chunk']['identifier_match'] += data['scores']['identifier_match']
            scores['chunk']['count'] += 1

    # Calculate averages
    averages = {}
    for key in scores:
        if scores[key]['count'] > 0:
            averages[key] = {
                'edit_similarity_avg': scores[key]['edit_similarity'] / scores[key]['count'],
                'identifier_match_avg': scores[key]['identifier_match'] / scores[key]['count']
            }
        else:
            averages[key] = {'edit_similarity_avg': None, 'identifier_match_avg': None}

    return averages

# Specify the path to your JSONL file
file_path = '/home/zhangxuanming/cceval/tmp/crosscodeeval_testrun/New_evaluation_go.jsonl'

# Process the file and get the averages
averages = process_data(file_path)
print(averages)
