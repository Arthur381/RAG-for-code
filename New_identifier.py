import json
from tree_sitter import Language, Parser

# Assume the language grammar is already built and loaded
PY_LANGUAGE = Language('/home/zhangxuanming/build/my-languages.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)

def extract_identifiers(source_code):
    tree = parser.parse(bytes(source_code, "utf8"))
    root_node = tree.root_node
    identifiers = []

    def visit(node):
        if node.type == 'identifier':
            identifier = source_code[node.start_byte:node.end_byte]
            if identifier not in identifiers:
                identifiers.append(identifier)
        for child in node.children:
            visit(child)

    visit(root_node)
    return identifiers

def analyze_code_from_jsonl(input_file_path, output_file_path):
    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        for line in infile:
            json_data = json.loads(line)
            # Analyze prompt for identifiers
            prompt_code = json_data['prompt']
            prompt_identifiers = extract_identifiers(prompt_code)
            json_data['prompt_identifiers'] = prompt_identifiers

            # Analyze retrieved_chunks in crossfile_context for identifiers
            if 'crossfile_context' in json_data:
                list_identifiers = []
                for item in json_data['crossfile_context']['list']:
                    chunk_code = item['retrieved_chunk']
                    chunk_identifiers = extract_identifiers(chunk_code)
                    list_identifiers.append(chunk_identifiers)
                json_data['crossfile_context']['list_identifiers'] = list_identifiers

            # Write the modified line back to a new file
            json.dump(json_data, outfile)
            outfile.write('\n')

# Specify the input and output file paths
input_file_path = '/home/zhangxuanming/cceval/data/python/line_completion_oracle_openai_cosine_sim.jsonl'
output_file_path = '/home/zhangxuanming/cceval/data/python/New_line_completion_oracle_openai_cosine_sim.jsonl'
analyze_code_from_jsonl(input_file_path, output_file_path)
