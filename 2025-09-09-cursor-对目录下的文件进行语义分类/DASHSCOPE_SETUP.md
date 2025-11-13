### DashScope（阿里云百炼）Embedding 配置指南

以下配置将让 `--group-by semantic-vec` 使用阿里 DashScope 的 OpenAI 兼容 Embedding 接口。

- 代码默认读取以下环境变量：
  - `DASHSCOPE_API_KEY`（必填）
  - `EMBEDDING_API_URL`（可选，默认：`https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings`）
  - `EMBEDDING_MODEL`（可选，默认：`text-embedding-v1`）

#### 1) 获取 API Key
- 登录阿里云百炼（DashScope）控制台，创建并复制 API Key。
- 控制台入口（仅供参考）：`https://dashscope.console.aliyun.com`

#### 2) 在终端导出环境变量
```bash
export DASHSCOPE_API_KEY='你的_DashScope_API_Key'
# 可选：如需覆盖默认值
# export EMBEDDING_API_URL='https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings'
# export EMBEDDING_MODEL='text-embedding-v1'
```

#### 3) 运行索引生成（语义向量模式）
```bash
python3 /home/chester/gitlab.chesterwang.com/cursor_projects/text_indexer.py \
  /home/chester/gitlab.chesterwang.com/cursor_projects \
  --group-by semantic-vec
```

#### 4) 常见问题
- 401 或 403：检查 `DASHSCOPE_API_KEY` 是否正确、是否有调用权限。
- 404 或 400：检查 `EMBEDDING_API_URL` 与 `EMBEDDING_MODEL` 是否存在/拼写正确。
- 网络错误：重试或检查网络；未配置 Key 时脚本会自动回退到哈希向量方案。


