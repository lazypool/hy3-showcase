# Hy3 Showcase 🚀

基于腾讯混元 **Hy3** 模型构建的交互式演示项目，展示 Hy3 的核心能力：智能对话、多级推理（思维链）和工具调用。

Hy3 是腾讯混元团队研发的快慢思考融合混合专家模型（MoE），总参数量 295B，激活参数 21B，支持 256K 上下文长度。

## 项目结构

```
hy3-showcase/
├── hy3_showcase/
│   ├── __init__.py      # 模块入口
│   ├── client.py        # Hy3 API 客户端（含 Mock 离线模式）
│   └── config.py        # 配置加载（环境变量）
├── app.py               # Gradio Web 应用
├── cli.py               # 命令行聊天客户端
├── scripts/
│   └── e2e_test.py      # 端到端验证脚本（提供 API Key 即可运行）
├── tests/
│   └── test_mock.py     # 10 项 Mock 单元测试
├── demo/
│   ├── mock-session.txt # Mock 模式端到端测试记录
│   └── real-session.txt # 真实 Hy3 API 端到端测试记录
├── .env.example         # 环境变量模板
├── .gitignore
├── requirements.txt     # Python 依赖
└── README.md            # 本文件
```

## ✨ 特性

- **Mock 离线模式** — 无需 API Key 即可完整运行，开箱即用
- **三级推理** — no_think（直接回复）/ low（轻度推理）/ high（深度思维链）
- **工具调用** — Function Calling 演示（计算器 Agent）
- **双形态** — Web 界面（Gradio）+ CLI 命令行
- **流式输出** — 实时显示生成内容
- **10 项单元测试** + **6 项端到端验证**

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/lazypool/hy3-showcase
cd hy3-showcase
pip install -r requirements.txt
```

### 运行（Mock 模式——无需 API Key）

```bash
export HY3_MOCK=true

# 方式 A：Web 界面
python app.py
# 访问 http://localhost:7860

# 方式 B：命令行
python cli.py "你好！请介绍一下你自己"
python cli.py --stream --reasoning high "用 Python 写一个快排"
python cli.py --reasoning high "24点问题：3, 3, 8, 8"
python cli.py -i  # 交互模式
```

### 运行（真实 Hy3 / OpenAI 兼容 API）

```bash
export HY3_API_BASE="https://tokenhub.tencentmaas.com/v1"
export HY3_API_KEY="sk-xxxxxxxxxxxxxxxx"
export HY3_MODEL="hy3"

python app.py
```

## 🧪 端到端验证

提供 API Key 即可一键运行 6 项端到端测试：

```bash
# 方式一：环境变量
export HY3_API_KEY="sk-xxxxxxxx"
python scripts/e2e_test.py

# 方式二：命令行参数
python scripts/e2e_test.py --api-key sk-xxxxxxxx

# Mock 模式（无需 Key）
python scripts/e2e_test.py --mock
```

### 测试内容

| # | 测试项 | 说明 |
|---|--------|------|
| 1 | 基础对话 | 非流式请求，验证 API 连通性 |
| 2 | 多轮对话 | 上下文保持能力，验证指代消解 |
| 3 | 流式输出 | 逐 chunk 流式代码生成 |
| 4 | 深度推理 | reasoning_effort=high 思维链 |
| 5 | 工具调用 | Function Calling Agent 能力 |
| 6 | CLI 可用性 | 命令行端到端冒烟测试 |

### 真实 API 测试结果

使用 TokenHub 端点 (`hy3` 模型) 实测：

```
=== Hy3 端到端验证 (🟢 真实 API 模式) ===
  ✅ PASS  非流式请求成功
  ✅ PASS  多轮对话成功
  ✅ PASS  流式输出有内容
  ✅ PASS  high 模式返回结果
  ✅ PASS  工具调用成功
  ✅ PASS  CLI 可执行
结果汇总:  ✅ PASS 6/6
```

详细记录见 [`demo/real-session.txt`](demo/real-session.txt)。

### 单元测试

```bash
# Mock 模式单元测试（无需 API Key）
python -m pytest tests/ -v
```

## 🎬 演示流程

| Demo | 命令 | 说明 |
|------|------|------|
| 1 | `python cli.py "介绍一下 MoE 架构"` | 智能对话（no_think） |
| 2 | `python cli.py --reasoning high "24点问题：3, 3, 8, 8"` | 深度推理（high） |
| 3 | 访问 Web 界面 → 工具调用标签页 | Agent 工具调用 |
| 4 | `python cli.py --stream "用 Python 写一个快速排序"` | 流式代码生成 |
| 5 | `python cli.py -i` | 交互式多轮对话 |

## 🧩 Hy3 在项目中的角色

本项目全程通过 **Hy3 的 `/chat/completions` HTTP API** 调用模型（OpenAI 兼容协议），不进行训练、微调或本地部署。Hy3 负责：

1. **意图理解与对话** — 理解用户自然语言并生成回复
2. **多级推理** — 三级思考模式满足不同复杂度需求
3. **工具调用** — Function Calling 实现 Agent 能力

当无 API Key 时，`hy3_showcase/client.py` 自动降级为 **Mock 模式**，基于关键词驱动返回预置响应，确保离线可演示。

## ⚙️ 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HY3_API_BASE` | `http://localhost:8000/v1` | API 端点地址 |
| `HY3_API_KEY` | `""` | API 密钥（留空则进入 Mock 模式） |
| `HY3_MODEL` | `hy3` | 模型名称 |
| `HY3_MOCK` | `false` | 设为 `true` 强制 Mock 模式 |

## 在主流工具中使用 Hy3

Hy3 的集成指南（OpenRouter / Cursor / Cline / CodeBuddy / Dify）请参考：

👉 [Hy3 官方仓库 → docs/integrations/](https://github.com/Tencent-Hunyuan/Hy3/tree/rhinobird2026/docs/integrations)

## 技术栈

- **Hy3** — 腾讯混元 MoE 大模型
- **OpenAI Python SDK** — 兼容 API 调用
- **Gradio** — Web 交互界面
- **pytest** — 单元测试

## 📄 License

Apache 2.0
