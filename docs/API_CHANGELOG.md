# API 变更日志 (API Changelog)

本文档记录 ClawHub API 的所有变更，包括新功能、修改和弃用。

## 版本规范

- **主版本号 (X.y.z)**: 不兼容的 API 变更
- **次版本号 (x.Y.z)**: 向后兼容的功能添加
- **修订号 (x.y.Z)**: 向后兼容的问题修复

---

## [2.0.0] - 2026-02-28

### 新增 (Added)

#### 技能包管理 API
- `GET /api/skills` - 获取技能包列表
  - 支持查询参数: `tag`, `search`, `sort`
  - 排序选项: `downloads`, `rating`, `updated`
- `GET /api/skills/:name` - 获取单个技能包详情
- `GET /api/categories` - 获取技能分类列表
- `GET /api/stats` - 获取注册表统计信息

#### ClawHub CLI
- `claw list` - 列出可用技能包
- `claw info <name>` - 查看技能包详情
- `claw install <name>` - 从 GitHub 安装技能包
  - 支持 `--force` 参数覆盖安装
  - 自动安装依赖 (requirements.txt)
  - 创建安装标记文件
- `claw categories` - 查看技能分类
- `claw stats` - 查看注册表统计
- `claw status` - 检查注册表连接状态

#### 注册表数据源
- 支持 GitHub Pages 作为静态注册表托管
- 默认注册表URL: `https://claw-bft.github.io/ai-agent-lab/registry/api`

### 变更 (Changed)

- **注册表URL更新**: 从 Vercel (`https://clawhub-registry.vercel.app`) 迁移到 GitHub Pages
  - 影响: 所有 CLI 客户端需要更新到最新版本
  - 向后兼容: 旧版本仍可通过环境变量 `CLAWHUB_REGISTRY` 指定新地址

### 技能包列表

| 技能包 | 版本 | 描述 |
|--------|------|------|
| skill-cli | 2.0.0 | 自然语言执行层 |
| finance-pro | 1.2.0 | 多数据源金融数据获取 |
| coding-pro | 1.1.0 | AI代码生成器 |
| research-pro | 1.0.0 | 智能研究助手 |
| product-pro | 1.0.0 | PRD生成与产品管理 |
| memory-enhanced | 1.0.0 | 向量记忆系统 |
| agent-collaboration | 1.0.0 | ACP协议多智能体协作 |

---

## [1.1.0] - 2026-02-27

### 新增 (Added)

- `finance-pro` 模块支持东方财富数据源
- `coding-pro` 测试覆盖率提升至 97%

### 修复 (Fixed)

- 修复了技能包评分系统的计算错误

---

## [1.0.0] - 2026-02-20

### 初始版本 (Initial Release)

- ClawHub Registry API 首次发布
- 支持基础技能包查询功能
- 7个核心技能包上线

---

## 未来计划 (Upcoming)

### 2.1.0 (计划中)
- [ ] `POST /api/skills/:name/rate` - 技能包评分 API
- [ ] `GET /api/search` - 高级搜索 API (全文检索)
- [ ] 技能包自动更新检查

### 3.0.0 (规划中)
- [ ] 用户认证与授权
- [ ] 私有技能包支持
- [ ] 技能包版本管理

---

## 迁移指南

### 从 1.x 迁移到 2.0

1. 更新 CLI 工具:
   ```bash
   pip install --upgrade clawhub-cli
   ```

2. 验证注册表连接:
   ```bash
   claw status
   ```

3. 如遇连接问题，手动指定注册表:
   ```bash
   export CLAWHUB_REGISTRY=https://claw-bft.github.io/ai-agent-lab/registry/api
   ```

---

## 参考链接

- [API 文档](https://claw-bft.github.io/ai-agent-lab/docs/api)
- [CLI 使用指南](https://claw-bft.github.io/ai-agent-lab/docs/cli)
- [GitHub 仓库](https://github.com/claw-bft/ai-agent-lab)
