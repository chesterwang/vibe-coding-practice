from modelscope.hub.snapshot_download import snapshot_download
from llama_cpp import Llama
import os
import sys
import time

model_dir = "/home/chester/gitlab.chesterwang.com/chester_ai_projects/models"

# llm = Llama.from_pretrained(
#     repo_id="Qwen/Qwen3-0.6B-GGUF",
#     filename="*q8_0.gguf",
#     local_dir=model_dir,
#     verbose=False
# )

MODELSCOPE_REPO_ID = "Qwen/Qwen3-0.6B-GGUF"
GGUF_FILENAME = "Qwen3-0.6B-Q8_0.gguf"

# 1. 使用 ModelScope API 下载模型
print(f"开始从 ModelScope 下载模型: {MODELSCOPE_REPO_ID}")

try:
    # snapshot_download 会将模型下载到 ModelScope 的默认缓存目录
    cache_dir = snapshot_download(MODELSCOPE_REPO_ID,cache_dir=model_dir)
    # 构造完整的模型路径
    model_path = os.path.join(cache_dir, GGUF_FILENAME)
except Exception as e:
    print(f"\n[错误] ModelScope 下载失败: {e}")
    sys.exit(1)

# 2. 将本地路径传递给 Llama 构造函数
print(f"\n成功下载。开始加载模型: {model_path}")
llm = Llama(
    model_path=model_path,
    n_gpu_layers=0,  # 如果有GPU并支持CUDA/Metal，可以设置为 > 0 的值
    n_ctx=4096,  # 上下文窗口大小,
    verbose=False
)

print("-" * 40)
print("模型加载成功，开始推理...")

# 3. 进行推理
prompt = "用户：请用中文写一个关于开源和AI模型的短句子。"
output = llm(
    prompt,
    max_tokens=64,
    stop=["用户", "\n"],
    echo=True,
    temperature=5,
    top_p=0.9,
    seed = time.time_ns()
)

# 打印结果
generated_text = output["choices"][0]["text"]
print(f"输入: {prompt}")
print(f"输出: {generated_text.strip()}")
print("-" * 40)


prompt = generated_text + "  机器人助手："
output = llm(
    prompt,
    max_tokens=1024,
    stop=["用户", "\n", "助手"],
    echo=True,
    temperature=5,
    top_p=0.9,
    seed = time.time_ns()
)

# 打印结果
generated_text = output["choices"][0]["text"]
print(f"输入: {prompt}")
print(f"输出: {generated_text.strip()}")
print("-" * 40)


prompt = generated_text + "  用户：关于AI对人类智力的影响。"
output = llm(
    prompt,
    max_tokens=1024,
    stop=["用户", "\n", "助手"],
    echo=True,
    temperature=5,
    top_p=0.9,
    seed = time.time_ns()
)

# 打印结果
generated_text = output["choices"][0]["text"]
print(f"输入: {prompt}")
print(f"输出: {generated_text.strip()}")
print("-" * 40)

del llm