# GitHub 技能安装方案

## 发现
找到了 OpenClaw 官方技能仓库的 GitHub 镜像！

**主仓库**: https://github.com/VoltAgent/awesome-openclaw-skills
**中文仓库**: https://github.com/clawdbot-ai/awesome-openclaw-skills-zh

## 需要安装的技能 (GitHub 版本)

### 金融投资领域
| 技能 | GitHub 仓库 | 状态 |
|------|------------|------|
| tushare-finance | 搜索中... | ☐ |
| stock-monitor-skill | 搜索中... | ☐ |
| technical-analyst | 搜索中... | ☐ |
| fear-greed | 搜索中... | ☐ |

### 程序员领域
| 技能 | GitHub 仓库 | 状态 |
|------|------------|------|
| debug-pro | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/debug-pro | ☐ |
| code | 搜索中... | ☐ |
| git | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/git-essentials | ☐ |
| code-review | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/code-review | ☐ |
| devops | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/devops | ☐ |
| ci-cd | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/ci-cd | ☐ |
| database-operations | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/database-operations | ☐ |

### 产品经理领域
| 技能 | GitHub 仓库 | 状态 |
|------|------------|------|
| deepresearch-conversation | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/deepresearch-conversation | ☐ |
| competitor-analysis | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/competitor-analysis | ☐ |
| marketing-mode | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/marketing-mode | ☐ |
| ppt-generator | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/ppt-generator | ☐ |

### 通用技能
| 技能 | GitHub 仓库 | 状态 |
|------|------------|------|
| data-analysis | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/data-analysis | ☐ |
| tavily-search | https://github.com/VoltAgent/awesome-openclaw-skills/tree/main/skills/tavily | ☐ |

## 安装方法

### 方法 1: 直接克隆
```bash
# 进入技能目录
cd /root/.openclaw/workspace/.claude/skills

# 克隆单个技能
git clone https://github.com/VoltAgent/awesome-openclaw-skills.git temp-repo
cp -r temp-repo/skills/debug-pro ./
rm -rf temp-repo
```

### 方法 2: 使用 sparse-checkout (推荐)
```bash
# 克隆仓库并只检出需要的技能
git clone --filter=blob:none --no-checkout https://github.com/VoltAgent/awesome-openclaw-skills.git
cd awesome-openclaw-skills
git sparse-checkout init --cone
git sparse-checkout set skills/debug-pro skills/git-essentials skills/code-review
git checkout
```

### 方法 3: 下载 ZIP
```bash
# 下载特定技能的 ZIP
curl -L https://github.com/VoltAgent/awesome-openclaw-skills/archive/refs/heads/main.zip -o skills.zip
unzip skills.zip
mv awesome-openclaw-skills-main/skills/* /root/.openclaw/workspace/.claude/skills/
```

## 批量安装脚本

```bash
#!/bin/bash
SKILLS_DIR="/root/.openclaw/workspace/.claude/skills"
REPO_URL="https://github.com/VoltAgent/awesome-openclaw-skills"

# 要安装的技能列表
SKILLS=(
  "debug-pro"
  "git-essentials"
  "code-review"
  "devops"
  "ci-cd"
  "database-operations"
  "deepresearch-conversation"
  "competitor-analysis"
  "marketing-mode"
  "ppt-generator"
  "data-analysis"
  "tavily"
)

# 创建临时目录
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

# 克隆仓库
git clone --depth 1 $REPO_URL

# 复制技能
for skill in "${SKILLS[@]}"; do
  if [ -d "awesome-openclaw-skills/skills/$skill" ]; then
    cp -r "awesome-openclaw-skills/skills/$skill" "$SKILLS_DIR/"
    echo "✓ Installed: $skill"
  else
    echo "✗ Not found: $skill"
  fi
done

# 清理
rm -rf $TEMP_DIR
echo "Installation complete!"
```

## 下一步
1. 执行批量安装脚本
2. 验证每个技能是否正确安装
3. 更新 SKILL_INSTALL.md 记录安装状态
