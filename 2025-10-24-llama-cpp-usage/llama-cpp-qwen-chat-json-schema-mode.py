from modelscope.hub.snapshot_download import snapshot_download
from llama_cpp import Llama
import os
import sys
import time

model_dir = "/home/chester/gitlab.chesterwang.com/chester_ai_projects/models"

MODELSCOPE_REPO_ID = "Qwen/Qwen3-0.6B-GGUF"
GGUF_FILENAME = "Qwen3-0.6B-Q8_0.gguf"

# 1. 使用 ModelScope API 下载模型
print(f"开始从 ModelScope 下载模型: {MODELSCOPE_REPO_ID}")

try:
    # snapshot_download 会将模型下载到 ModelScope 的默认缓存目录
    cache_dir = snapshot_download(MODELSCOPE_REPO_ID, cache_dir=model_dir)
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

for k,v in llm.metadata.items():
    print(f"{k}: {v}")

print("-" * 40)
print("模型加载成功，开始推理...")

# 3. 进行推理
output = llm.create_chat_completion(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that outputs in JSON.",
        },
        {"role": "user", "content": "Who won the world series in 2020"},
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {"team_name": {"type": "string"}},
            "required": ["team_name"],
        },
    },
    temperature=0.7,
)

# 打印结果
generated_text = output["choices"][0]["message"]["content"]
print(f"输出: {generated_text.strip()}")
print("-" * 40)

del llm
