# Hy3 Showcase 🚀

基于腾讯混元 **Hy3** 模型构建的交互式演示项目，展示 Hy3 的核心能力：智能对话、多级推理（思维链）和工具调用。

Hy3 是腾讯混元团队研发的快慢思考融合混合专家模型（MoE），总参数量 295B，激活参数 21B，支持 256K 上下文长度。

## 项目结构

```
hy3-showcase/
├── app.py              # Gradio Web 应用
├── cli.py              # 命令行聊天客户端
├── requirements.txt    # Python 依赖
├── README.md           # 本文件
└── demo/               # Demo 记录
    └── real-session.txt  # 真实 API 调用记录
```

## 快速开始

### 前提条件

- Hy3 API 端点可用（自部署 或 [腾讯混元 API](https://hunyuan.cloud.tencent.com/)）
- Python 3.10+

### 安装

```bash
git clone https://github.com/lazypool/hy3-showcase
cd hy3-showcase
pip install -r requirements.txt
```

### 环境变量

```bash
export HY3_API_BASE="https://api.hunyuan.cloud.tencent.com/v1"
export HY3_API_KEY="your-api-key-here"
export HY3_MODEL="hunyuan-pro"
```

### 启动 Web 应用

```bash
python app.py
```

打开浏览器访问 `http://localhost:7860`

### 使用 CLI

```bash
# 普通对话
python cli.py "你好！请介绍一下你自己"

# 启用深度推理
python cli.py --reasoning high "设计一个分布式缓存系统"

# 流式输出
python cli.py --stream --reasoning low "用 Python 写一个快速排序"

# 交互模式
python cli.py -i
```

## 核心功能

### 1. 智能对话

支持多轮对话，Hy3 能准确理解上下文语境和指代关系，在多轮交互中保持意图一致性。

### 2. 三级推理模式

| 模式 | 值 | 适用场景 |
|------|-----|---------|
| **直接回复** | `no_think` | 日常问答、简单知识查询 |
| **轻度推理** | `low` | 中等复杂度任务、代码解释 |
| **深度推理** | `high` | 数学证明、复杂编程、逻辑推理 |

通过 `extra_body` 参数控制：

```python
extra_body={
    "chat_template_kwargs": {
        "reasoning_effort": "high"
    }
}
```

### 3. 工具调用（Agent 能力）

Hy3 支持函数调用（Function Calling），可配合计算器、搜索等工具完成任务。启动 vLLM 时需添加：

```bash
--enable-auto-tool-choice --tool-call-parser hy_v3
```

## 技术栈

- **Hy3** — 腾讯混元 MoE 大模型
- **OpenAI Python SDK** — 兼容 API 调用
- **Gradio** — Web 交互界面
- **Rich** — CLI 终端美化

## 在主流工具中使用 Hy3

Hy3 的集成指南请参考 [Hy3 官方仓库 → docs/integrations/](https://github.com/Tencent-Hunyuan/Hy3/tree/rhinobird2026/docs/integrations)

## 演示视频

[演示视频链接]（≤ 1 min，待录制）

## Hy3 在本项目中的角色

本项目全程通过 **Hy3 的 `/chat/completions` HTTP API** 调用模型（OpenAI 兼容协议），不进行训练、微调或本地部署。Hy3 负责：

1. **意图理解与对话** — 理解用户自然语言并生成回复
2. **多级推理** — 三级思考模式满足不同复杂度需求
3. **工具调用** — Function Calling 实现精确计算等 Agent 能力

## 许可证

Apache 2.0
