# AI Agent Lab 配置管理

## 配置目录结构

```
~/.openclaw/config/
├── skills.json          # 技能包全局配置
├── credentials.json     # API密钥和凭证 (gitignore)
└── README.md           # 本文档
```

## 配置说明

### skills.json
技能包的全局配置，包含启用状态和功能开关。

### credentials.json
敏感凭证存储，**不应提交到Git仓库**。

示例格式：
```json
{
  "tushare_token": "your_token_here",
  "openai_api_key": "your_key_here",
  "tavily_api_key": "your_key_here"
}
```

## 使用方法

```python
from pathlib import Path
import json

config_dir = Path.home() / ".openclaw/config"
skills_config = json.loads((config_dir / "skills.json").read_text())
```

## 安全提醒

- credentials.json 已添加到 .gitignore
- 永远不要将真实API密钥提交到代码仓库
- 定期轮换API密钥
