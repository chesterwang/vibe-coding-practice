# 生成式AI推荐系统论文获取器

这个脚本可以自动获取网络上关于生成式AI推荐系统的近期论文，并将结果发送到指定邮箱。

## 功能特性

- 🔍 从多个学术数据库搜索论文（arXiv、Semantic Scholar）
- 📅 获取指定时间范围内的最新论文（默认30天）
- 📧 自动发送格式化的论文列表到指定邮箱
- 💾 支持保存为HTML文件
- 🔧 可配置的搜索关键词和参数
- 🚫 自动去重功能

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制并编辑配置文件：
```bash
cp config.json my_config.json
```

2. 在 `my_config.json` 中配置以下信息：
   - **邮箱设置**：发件人邮箱、密码（建议使用应用专用密码）、收件人邮箱
   - **搜索参数**：关键词、时间范围、最大结果数

### Gmail 配置说明

如果使用 Gmail 发送邮件，需要：
1. 开启两步验证
2. 生成应用专用密码：[Google账户安全设置](https://myaccount.google.com/security)
3. 在配置文件中使用应用专用密码，而不是账户密码

## 使用方法

### 基本用法

```bash
# 使用默认配置搜索并发送邮件
python paper_fetcher.py

# 使用自定义配置文件
python paper_fetcher.py --config my_config.json

# 发送到指定邮箱
python paper_fetcher.py --email recipient@example.com
```

### 仅保存到文件

```bash
# 只保存到文件，不发送邮件
python paper_fetcher.py --save-only

# 指定输出文件名
python paper_fetcher.py --save-only --output my_papers.html
```

### 命令行参数

- `--config, -c`: 指定配置文件路径
- `--email, -e`: 指定收件人邮箱地址
- `--save-only, -s`: 仅保存到文件，不发送邮件
- `--output, -o`: 指定输出文件名

## 配置文件说明

```json
{
  "search_terms": [
    "generative AI recommendation",
    "generative recommendation system",
    "LLM recommendation"
  ],
  "days_back": 30,
  "max_results": 50,
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",
    "recipient_email": "recipient@example.com"
  }
}
```

### 参数说明

- `search_terms`: 搜索关键词列表
- `days_back`: 搜索多少天内的论文（默认30天）
- `max_results`: 每个关键词的最大搜索结果数
- `email`: 邮件发送配置

## 输出格式

脚本会生成包含以下信息的论文列表：
- 论文标题
- 作者列表
- 发表日期
- 论文摘要
- 论文链接
- 数据源（arXiv 或 Semantic Scholar）

## 定时运行

可以使用 cron 定时运行脚本：

```bash
# 每天上午9点运行
0 9 * * * /usr/bin/python3 /path/to/paper_fetcher.py --config /path/to/config.json
```

## 注意事项

1. **API限制**：请遵守各学术数据库的API使用限制
2. **邮箱安全**：建议使用应用专用密码，不要使用主密码
3. **网络连接**：确保网络连接稳定，脚本会自动重试失败的请求
4. **去重机制**：脚本会自动去除重复论文，基于标题相似度判断

## 故障排除

### 常见问题

1. **邮件发送失败**
   - 检查邮箱配置是否正确
   - 确认使用了应用专用密码（Gmail）
   - 检查网络连接

2. **搜索结果为空**
   - 尝试调整搜索关键词
   - 增加时间范围（days_back）
   - 检查网络连接

3. **编码问题**
   - 确保系统支持UTF-8编码
   - 检查配置文件编码格式

## 扩展功能

脚本支持以下扩展：
- 添加更多学术数据库API
- 自定义论文过滤条件
- 支持更多邮件服务提供商
- 添加论文质量评估功能

## 许可证

MIT License
