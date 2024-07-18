from vllm import LLM, SamplingParams
from functools import partial

def load_llm(modelPath):
    """
    vllm is not a stable library. Watch its updates.
    """
    llm = LLM(model=modelPath,
              gpu_memory_utilization=0.9,
              swap_space=4, # https://github.com/vllm-project/vllm/issues/787#issuecomment-1876636749
              enforce_eager=True,
              tensor_parallel_size=4)
    
    sampling_params = SamplingParams(n=1,
                                     temperature=0.8,
                                     top_p=0.95,
                                     max_tokens=2048,
                                     stop=[])#["\nmodule", "\n`include","\n```", "endmodule"])
    
    return partial(llm.generate, sampling_params=sampling_params, use_tqdm=False)

modelPath = ""
complete = load_llm(modelPath)
while True:
    x = input("# Your question:")
    if x == "0":
        break
    with open("prompt.txt","r") as f:
        prompts = f.read()
        prompts = "[INST]" + prompts + "[/INST]"
    output = complete([prompts])
    print("# Response:", output[0].outputs[0].text)
