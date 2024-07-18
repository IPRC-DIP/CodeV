import requests
import json
import os
import time
import random
import shutil
import threading
import time
import copy

import openai

semaphore = threading.Semaphore(100)# 
write_lock = threading.Lock()

def getTheFormatData(code):
    with open(r"", "r") as f:
        template = f.read()
    
    data = template.replace("{our_code}",code)
    #print(data)
    return data



def getAnswerGPT(code, progress_bar_func, content_func,task_id):
    global api_key
    client = openai.OpenAI(api_key = api_key)
    with semaphore:
        while True:#not signal:#
            try:
                # print("generate")
                dic = {}
                with open(output_path, "a", encoding="utf-8") as nl_file:
                    messages = [
                                    {
                                    "role": "user",
                                    "content":getTheFormatData(code)
                                    }
                                ]
                    response = client.chat.completions.create(
                        model="",#"deepseek-chat", #
                        messages = messages,
                        temperature = 0.7
                    )

                    response_exe =  response.choices[0].message.content
                    dic['task_id'] = task_id
                    dic["describe"] = response_exe
                    dic["prompt"] = getTheFormatData(code)
                    dic['code'] = code
                    #dic['table'] = table
                    json_data = json.dumps(dic)  
                    write_lock.acquire()
                    nl_file.write(json_data + '\n')
                    write_lock.release()
                    print("generate success!")
                    break
            except Exception as e:
                print("error:",e)
                time.sleep(60)

        return 1



def get_describe_from_gpt(descri_path ,
                          output_path, 
                          id_begin=0, ):

    progress_bar = 0#
    id = 0
    content = ""
    threads = []

    verilog_list = []
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as nl_file:
            for line in nl_file:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        verilog_list.append(data['code'].replace("\n",' ').replace("\t",' '))
                    except:
                        continue
                    
    
    # print("step")
    with open(descri_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                except:
                    continue
                data_func = copy.deepcopy(data)
                code = data.get("verilog")
                task_id = data.get('task_id')
                #table = data.get("instruction")
                if code:
                    if id < id_begin:
                        id += 1
                        progress_bar+=1
                        continue
                    else:
                        id = id + 1
                        progress_bar+=1
                        print(progress_bar)
                if code.replace("\n",' ').replace("\t",' ') in verilog_list:
                    verilog_list.remove(code.replace("\n",' ').replace("\t",' '))
                    print("skip")
                    continue
                getAnswerGPT(code, progress_bar, data_func, task_id)

if __name__ == "__main__":
    descri_path=""
    output_path=""
    get_describe_from_gpt(descri_path,output_path)