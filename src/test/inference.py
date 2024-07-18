from functools import partial
import json
import logging
from pathlib import Path
from vllm import LLM, SamplingParams

def read_config(cfg_path):
    with open(cfg_path, "r") as f:
        return json.load(f)

def load_tasks(cfg):
    """
    format: {"task_id:"..., "prompt":...}
    """
    with open(cfg["testset_path"], "r", encoding='utf-8') as f:
        tasks = [json.loads(l) for l in f.readlines()]
    return tasks[cfg["testset_start"]:]

def load_llm(cfg):
    """
    vllm is not a stable library. Watch its updates.
    """
    llm = LLM(model=cfg["llm_path"],
              gpu_memory_utilization=0.9,
              swap_space=4, # https://github.com/vllm-project/vllm/issues/787#issuecomment-1876636749
              enforce_eager=True,
              tensor_parallel_size=cfg["num_gpus"])
    
    sampling_params = SamplingParams(n=1,
                                     temperature=0.2,
                                     top_p=0.95,
                                     max_tokens=2048,
                                     stop=cfg["stop"])
    
    return partial(llm.generate, sampling_params=sampling_params, use_tqdm=False)

def get_results(outputs):
    return [o.outputs[0].text for o in outputs]

def save_jsonl(completion_dir, tid, outputs):
    tid_path = tid.replace("/", "-")
    path = Path(completion_dir) / f"{tid_path}.jsonl"
    lines = [
        json.dumps({"task_id": tid, "completion": o.text+"\nendmodule"}) + '\n'
        for request_output in outputs
        for o in request_output.outputs
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def main(cfg_path):
    """
    save the results after each task is generated.
    The process may be terminated at any time.
    """
    cfg = read_config(cfg_path)
    tasks = load_tasks(cfg)
    complete = load_llm(cfg)
    
    total_num = len(tasks)
    for i, task in enumerate(tasks):
        tid, prompt = task["task_id"], task["prompt"]
        logging.info(f"{i:03}/{total_num:03}: {tid}")
        inputs = [prompt] * cfg["k"]
        outputs = complete(inputs)
        save_jsonl(cfg["completion_dir"], tid, outputs)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('cfgpath', type=Path)
    args = parser.parse_args()

    main(args.cfgpath)
