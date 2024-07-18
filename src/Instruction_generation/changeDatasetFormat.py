import json
import random
random.seed(6)
jsonl_file = r''
output_file = r""
def read_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                json_data = json.loads(line)
                data.append(json_data)
            except:
                pass
    return data

import re
def find_module_end(text):
    pattern = r'module[\s\S]+?\s*\);'
    match = re.search(pattern, text)
    if match:
        module_end_pos = match.end()
        return module_end_pos
    else:
        return 0
    
json_data_list = read_jsonl(jsonl_file)
# random.shuffle(json_data_list)
with open(output_file, "w") as f:
    for json_data in json_data_list:
        instruction = json_data['describe']+"\n"+json_data['code'][:find_module_end(json_data['code'])]
        response = f"{json_data['code']}"
        zy08_0to10k_data = {"instruction": instruction,  "response":response}
        f.write(json.dumps(zy08_0to10k_data)+"\n")