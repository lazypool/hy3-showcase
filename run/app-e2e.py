#!/usr/bin/env python3
"""Web + 真实 API 截图。先启动 app.py（设 HY3_API_KEY），再运行本脚本。"""
import os, sys

if not os.environ.get("HY3_API_KEY"):
    print("❌ 需要设置 HY3_API_KEY 环境变量")
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "demo", "screenshots")
os.makedirs(OUT, exist_ok=True)

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    page.goto("http://localhost:7860")
    page.wait_for_timeout(2000)
    page.screenshot(path=os.path.join(OUT, "app-e2e-initial.png"), full_page=True)
    print("✓ app-e2e-initial.png")

    questions = [
        "用Python写一个程序，管理个人通讯录，支持添加和查找联系人",
        "给通讯录添加删除和列出所有联系人的功能",
        "把通讯录数据保存到JSON文件，启动时自动加载",
        "用改造后的通讯录添加三个联系人，然后列出他们",
    ]
    for i, q in enumerate(questions, 1):
        page.locator("textarea").fill(q)
        page.keyboard.press("Enter")
        page.wait_for_timeout(12000)
        page.screenshot(path=os.path.join(OUT, f"app-e2e-turn{i}.png"), full_page=True)
        print(f"✓ app-e2e-turn{i}.png")

    page.locator('button[role="tab"]', has_text="工具调用").click()
    page.wait_for_timeout(1000)
    page.locator("button", has_text="运行").click()
    page.wait_for_timeout(5000)
    page.screenshot(path=os.path.join(OUT, "app-e2e-tool.png"), full_page=True)
    print("✓ app-e2e-tool.png")

    page.locator('button[role="tab"]', has_text="关于").click()
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(OUT, "app-e2e-about.png"), full_page=True)
    print("✓ app-e2e-about.png")

    browser.close()
    print("\n=== 完成 ===")
