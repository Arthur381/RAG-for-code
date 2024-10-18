import json
import difflib
from nltk.translate.bleu_score import sentence_bleu
from nltk.util import ngrams
from collections import Counter
import tokenize
from io import BytesIO
import keyword
import re

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = [json.loads(line) for line in file]
    return data

def extract_identifiers_advanced(code):
    identifiers = set()
    try:
        tokens = tokenize.tokenize(BytesIO(code.encode('utf-8')).readline)
        for toknum, tokval, _, _, _ in tokens:
            if toknum == tokenize.NAME and not keyword.iskeyword(tokval):
                identifiers.add(tokval)
    except tokenize.TokenError as e:
        print(f"Token error processing code: {e}")  # Optionally log the error
    except IndentationError as e:
        print(f"Indentation error processing code: {e}")  # Optionally log the error
    return list(identifiers)

def code_tokenize(code):
    """Tokenizes the code and returns a list of tokens, excluding comments and whitespace."""
    code = re.sub(r'([^A-Za-z0-9_])', r' \1 ', code)
    code = re.sub(r'([a-z])([A-Z])', r'\1 \2', code)
    code = re.sub(r'\s+', ' ', code)
    code = code.replace('"', '`')
    code = code.replace('\'', '`')
    tokens = [t for t in code.split(' ') if t]

    return tokens

def lcs(X, Y):
    """Computes the Longest Common Subsequence (LCS) of X and Y."""
    m, n = len(X), len(Y)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i - 1] == Y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
                
    # Reconstruct LCS
    index = L[m][n]
    lcs_seq = [''] * (index + 1)
    lcs_seq = []
    
    i, j = m, n
    while i > 0 and j > 0:
        if X[i - 1] == Y[j - 1]:
            lcs_seq.insert(0, X[i - 1])
            i -= 1
            j -= 1
        elif L[i - 1][j] > L[i][j - 1]:
            i -= 1
        else:
            j -= 1
            
    return ''.join(lcs_seq)

def compute_similarity_metrics(retrieved_chunk, groundtruth_context):
    retrieved_tokens = code_tokenize(retrieved_chunk)
    groundtruth_tokens = code_tokenize(groundtruth_context)

    ngram_size=4
    ngrams_retrieved = set(zip(*[retrieved_tokens[i:] for i in range(ngram_size)]))
    ngrams_groundtruth = set(zip(*[groundtruth_tokens[i:] for i in range(ngram_size)]))
    ngrams_overlap = ngrams_retrieved & ngrams_groundtruth
    ngram_overlap_content = [' '.join(ngram) for ngram in ngrams_overlap]
    
    ngram_size1=3
    ngrams_retrieved1 = set(zip(*[retrieved_tokens[i:] for i in range(ngram_size1)]))
    ngrams_groundtruth1 = set(zip(*[groundtruth_tokens[i:] for i in range(ngram_size1)]))
    ngrams_overlap1 = ngrams_retrieved1 & ngrams_groundtruth1
    ngram_overlap_content1 = [' '.join(ngram) for ngram in ngrams_overlap1]
    
    ngram_size2=2
    ngrams_retrieved2 = set(zip(*[retrieved_tokens[i:] for i in range(ngram_size2)]))
    ngrams_groundtruth2 = set(zip(*[groundtruth_tokens[i:] for i in range(ngram_size2)]))
    ngrams_overlap2 = ngrams_retrieved2 & ngrams_groundtruth2
    ngram_overlap_content2 = [' '.join(ngram) for ngram in ngrams_overlap2]
    
    ngram_size3=1
    ngrams_retrieved3 = set(zip(*[retrieved_tokens[i:] for i in range(ngram_size3)]))
    ngrams_groundtruth3 = set(zip(*[groundtruth_tokens[i:] for i in range(ngram_size3)]))
    ngrams_overlap3 = ngrams_retrieved3 & ngrams_groundtruth3
    ngram_overlap_content3 = [' '.join(ngram) for ngram in ngrams_overlap3]
    
    lcs_result = lcs(retrieved_tokens, groundtruth_tokens)                
    bleu_score = sentence_bleu([groundtruth_tokens], retrieved_tokens, weights=(0.25, 0.25, 0.25, 0.25))

    edit_similarity = difflib.SequenceMatcher(None, retrieved_tokens, groundtruth_tokens).ratio()

    retrieved_identifiers = set([token for token in retrieved_tokens if token.isidentifier()])
    groundtruth_identifiers = set([token for token in groundtruth_tokens if token.isidentifier()])
    identifier_match = len(retrieved_identifiers.intersection(groundtruth_identifiers)) / max(1, len(groundtruth_identifiers))

    return {
        '4gram_score': len(ngrams_overlap),
        '4gram_result': ngram_overlap_content,
        '3gram_score': len(ngrams_overlap1),
        '3gram_result': ngram_overlap_content1,
        '2gram_score': len(ngrams_overlap2),
        '2gram_result': ngram_overlap_content2,
        '1gram_score': len(ngrams_overlap3),
        '1gram_result': ngram_overlap_content3,
        'bleu': bleu_score,
        'edit_similarity': edit_similarity,
        'identifier_match': identifier_match,
        'lcs_score': len(lcs_result) / max(1, len(groundtruth_context)),
        'lcs_result': lcs_result
    }

def find_retrieved_chunk(item):
    chunk_index = None
    if item['context_type'] != 'base_prompt':
        _, chunk_index_str = item['context_type'].split('_')
        chunk_index = int(chunk_index_str) - 1
    if chunk_index is not None and chunk_index < len(item['crossfile_context']['list']):
        return item['crossfile_context']['list'][chunk_index]['retrieved_chunk'], item['crossfile_context']['list'][chunk_index]['score']
    else:
        return None, None

def process_data(data):
    grouped_data = {}
    for item in data:
        task_id = item['task_id']
        if task_id not in grouped_data:
            grouped_data[task_id] = []
        grouped_data[task_id].append(item)
    
    for task_id, items in grouped_data.items():
        base_prompt_item = next((item for item in items if item['context_type'] == 'base_prompt'), None)
        chunk_items = [item for item in items if 'chunk' in item['context_type']]
        
        for item in chunk_items:
            retrieved_chunk, score = find_retrieved_chunk(item)
            if retrieved_chunk:
                item['similarity_metrics'] = compute_similarity_metrics(
                    retrieved_chunk,
                    item['groundtruth'] + item['right_context']
                )
                item['similarity_score'] = score
                item['edit_similarity_difference'] = item['scores']['edit_similarity'] - base_prompt_item['scores']['edit_similarity']
                
            # Extract common identifiers between pred and ground_truth + right_context
                pred_identifiers = set(extract_identifiers_advanced(item['pred']))
                groundtruth_context_identifiers = set(extract_identifiers_advanced(item['groundtruth'] + item['right_context']))
                common_identifiers = list(pred_identifiers.intersection(groundtruth_context_identifiers))
                item['common_identifiers'] = common_identifiers
        
        chunk_items.sort(key=lambda x: x['edit_similarity_difference'], reverse=True)
        
        grouped_data[task_id] = [base_prompt_item] + chunk_items if base_prompt_item else chunk_items
    
    return grouped_data

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        for task_id, items in data.items():
            for item in items:
                file.write(json.dumps(item) + '\n')

# Main flow
input_file_path = 'cceval/tmp/crosscodeeval_testrun/evaluation_final.jsonl'
output_file_path = 'cceval/tmp/crosscodeeval_testrun/conclude_identifiers_final.jsonl'

data = load_data(input_file_path)
processed_data = process_data(data)
save_data(output_file_path, processed_data)
