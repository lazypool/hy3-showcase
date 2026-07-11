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
├── tests/
│   └── test_mock.py     # 10 项 Mock 单元测试
├── demo/
│   └── mock-session.txt # Mock 模式端到端测试记录
├── .env.example         # 环境变量模板
├── requirements.txt     # Python 依赖
└── README.md            # 本文件
```

## ✨ 特性

- **Mock 离线模式** — 无需 API Key 即可完整运行，开箱即用
- **三级推理** — no_think（直接回复）/ low（轻度推理）/ high（深度思维链）
- **工具调用** — Function Calling 演示（计算器 Agent）
- **双形态** — Web 界面（Gradio）+ CLI 命令行
- **流式输出** — 实时显示生成内容
- **10 项测试** — 覆盖全部核心功能（`python -m pytest`）

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/lazypool/hy3-showcase
cd hy3-showcase
pip install -r requirements.txt
```

### 运行（Mock 模式——无需 API Key）

```bash
# Mock 模式：不设置 HY3_API_KEY 自动进入
export HY3_MOCK=true

# 方式 A：Web 界面
python app.py
# 访问 http://localhost:7860

# 方式 B：命令行
python cli.py "你好！请介绍一下你自己"
python cli.py --stream --reasoning high "用 Python 写一个快排"
python cli.py -i  # 交互模式
```

### 运行（真实 Hy3 模式）

```bash
export HY3_API_BASE="http://your-server:8000/v1"
export HY3_API_KEY="your-key"
export HY3_MODEL="hy3"

python app.py
```

### 运行测试

```bash
python -m pytest tests/ -v
```

输出示例：
```
tests/test_mock.py::TestHy3MockClient::test_basic_chat PASSED
tests/test_mock.py::TestHy3MockClient::test_quicksort_mock PASSED
...
============================== 10 passed in 2.20s ==============================
```

## 🧩 Hy3 在项目中的角色

本项目全程通过 **Hy3 的 `/chat/completions` HTTP API** 调用模型（OpenAI 兼容协议），不进行训练、微调或本地部署。Hy3 负责：

1. **意图理解与对话** — 理解用户自然语言并生成回复
2. **多级推理** — 三级思考模式满足不同复杂度需求
3. **工具调用** — Function Calling 实现 Agent 能力

当无 API Key 时，`hy3_showcase/client.py` 自动降级为 **Mock 模式**，基于关键词驱动返回预置响应，确保离线可演示。

## 🎬 端到端 Demo 流程

**Demo 1 — 智能对话（no_think）**

```
$ python cli.py "介绍一下你自己"
→ 我是 **Hy3**，由腾讯混元团队研发的快慢思考融合混合专家模型（MoE）。
  我有 295B 总参数量、21B 激活参数，支持 256K 上下文...
```

**Demo 2 — 深度推理（high）**

```
$ python cli.py --reasoning high "24点问题：3, 3, 8, 8"
→ 【推理过程】1. 分析问题...   【最终回答】8 ÷ (3 - 8 ÷ 3) = 24
```

**Demo 3 — 工具调用（Agent）**

```
Web 界面 → 工具调用标签页 → 点击「运行演示」
→ Hy3 调用了计算器工具：(238491 * 78345) / 100
```

完整 Mock 模式测试记录见 [`demo/mock-session.txt`](demo/mock-session.txt)。

## 推理模式说明

| 模式 | 值 | 适用场景 | 示例问题 |
|------|-----|---------|---------|
| 直接回复 | `no_think` | 日常问答 | "介绍一下 MoE 架构" |
| 轻度推理 | `low` | 中等复杂度 | "用 Python 写一个装饰器" |
| 深度推理 | `high` | 复杂推理 | "设计一个分布式缓存系统" |

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
