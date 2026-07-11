import json
import re

import gradio as gr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

plt.rcParams.update({
    "font.sans-serif": ["Noto Sans CJK SC", "Noto Sans CJK TC", "DejaVu Sans"],
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.unicode_minus": False,
})

from hy3_showcase import Hy3Client

EXTRACT_TPL = """提取关于「{topic}」的核心概念和关系，以 JSON 格式输出，JSON 结构如下：
{{
  "entities": [{{"id": "1", "name": "概念名", "type": "concept/mechanism/component/application"}}],
  "relations": [{{"source": "1", "target": "2", "label": "关系描述"}}]
}}
要求：至少 6 个实体，至少 6 条关系。只输出 JSON，不要包含其他内容。"""

EXPLAIN_TPL = """用通俗的语言解释 {topic} 的核心概念，要求：
1. 用 3 句话以内的类比帮助理解
2. 列举 2-3 个实际应用场景
3. 控制在 200 字以内"""

TYPE_COLORS = {
    "concept": "#ff6b6b",
    "mechanism": "#4ecdc4",
    "component": "#45b7d1",
    "application": "#96ceb4",
}

client = Hy3Client()


def extract_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return m.group() if m else None


def render(data, title):
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")

    if not data or "entities" not in data or len(data["entities"]) < 2:
        ax.text(0.5, 0.5, "输入主题生成知识图谱", ha="center", va="center",
                fontsize=16, color="#64748b", fontstyle="italic")
        ax.axis("off")
        return fig, ax

    G = nx.DiGraph()
    for e in data["entities"]:
        G.add_node(e["name"], type=e.get("type", ""))
    for r in data.get("relations", []):
        names = {e["id"]: e["name"] for e in data["entities"]}
        src = names.get(r["source"], r["source"])
        tgt = names.get(r["target"], r["target"])
        if src in G and tgt in G:
            G.add_edge(src, tgt, label=r.get("label", ""))

    pos = nx.spring_layout(G, k=2.5, iterations=50, seed=42)

    for node in G.nodes:
        t = G.nodes[node].get("type", "")
        G.nodes[node]["color"] = TYPE_COLORS.get(t, "#a8e6cf")

    colors = [G.nodes[n]["color"] for n in G.nodes]
    nx.draw_networkx_nodes(
        G, pos, node_color=colors, node_size=2800, alpha=0.9,
        edgecolors="#1e293b", linewidths=2,
    )
    nx.draw_networkx_labels(
        G, pos, font_size=9, font_weight="bold",
        font_color="white", font_family="sans-serif",
    )
    nx.draw_networkx_edges(
        G, pos, arrows=True, arrowsize=18, arrowstyle="->",
        edge_color="#475569", width=1.5, alpha=0.6,
        connectionstyle="arc3,rad=0.1",
    )
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True) if d.get("label")}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=7,
        font_color="#94a3b8", font_family="sans-serif",
        bbox=dict(boxstyle="round,pad=0.1", fc="#1e293b", ec="none", alpha=0.7),
    )

    ax.set_title(f"「{title}」知识图谱", fontsize=18, fontweight="bold",
                  color="#f1f5f9", pad=24)
    ax.axis("off")
    fig.tight_layout()
    return fig, ax


def build_graph(topic, progress=gr.Progress()):
    if not topic.strip():
        return None, "等待输入...", "", ""

    progress(0.05, desc="🤔 分析主题结构...")
    content = ""
    for chunk in client.chat(
        [
            {"role": "system", "content": EXTRACT_TPL.format(topic=topic)},
            {"role": "user", "content": f"分析 {topic}"},
        ],
        stream=True,
        reasoning_effort="high",
    ):
        content += chunk["content"]

    progress(0.5, desc="🎨 渲染知识图谱...")
    raw = extract_json(content)
    data = {}
    if raw:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            pass

    fig, _ = render(data, topic)

    progress(0.7, desc="💡 生成解释...")
    explain = ""
    for chunk in client.chat(
        [
            {"role": "system", "content": EXPLAIN_TPL.format(topic=topic)},
            {"role": "user", "content": f"解释 {topic}"},
        ],
        stream=True,
        reasoning_effort="low",
    ):
        explain += chunk["content"]

    progress(1.0, desc="✅ 完成")
    return (
        fig,
        content if not data else json.dumps(data, ensure_ascii=False, indent=2),
        explain,
        f"⚡ {topic}",
    )


CSS = """
#title { text-align: center; margin-bottom: 0.5em; }
#subtitle { text-align: center; color: #94a3b8; margin-bottom: 1.5em; }
"""

with gr.Blocks(
    title="Hy3 知识图谱",
    css=CSS,
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown("# 🧠 Hy3 知识图谱", elem_id="title")
    gr.Markdown(
        "输入任意主题，Hy3 自动提取核心概念与关系，生成可视化知识图谱",
        elem_id="subtitle",
    )

    with gr.Row():
        with gr.Column(scale=1):
            topic = gr.Textbox(
                label="主题",
                placeholder="输入一个概念，如 Transformer、注意力机制、量子计算...",
                scale=3,
            )
            btn = gr.Button("✨ 生成图谱", variant="primary", scale=1)

        with gr.Column(scale=1, min_width=200):
            pass

    with gr.Row():
        with gr.Column(scale=3):
            plot = gr.Plot(label="知识图谱")

        with gr.Column(scale=2):
            explain = gr.Markdown(label="通俗解释")
            status = gr.Markdown(visible=False)

    with gr.Accordion("📋 原始提取数据", open=False):
            raw_json = gr.Markdown()

    btn.click(
        fn=build_graph,
        inputs=[topic],
        outputs=[plot, raw_json, explain, status],
    )
    topic.submit(
        fn=build_graph,
        inputs=[topic],
        outputs=[plot, raw_json, explain, status],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
