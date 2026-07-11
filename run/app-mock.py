#!/usr/bin/env python3
"""Web + Mock 模式截图。先启动 app.py，再运行本脚本。"""
import os, sys

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
    page.screenshot(path=os.path.join(OUT, "app-mock-initial.png"), full_page=True)
    print("✓ app-mock-initial.png")

    page.locator("textarea").fill("介绍一下 MoE 架构")
    page.keyboard.press("Enter")
    page.wait_for_timeout(8000)
    page.screenshot(path=os.path.join(OUT, "app-mock-chat.png"), full_page=True)
    print("✓ app-mock-chat.png")

    page.locator('button[role="tab"]', has_text="工具调用").click()
    page.wait_for_timeout(1000)
    page.locator("button", has_text="运行").click()
    page.wait_for_timeout(5000)
    page.screenshot(path=os.path.join(OUT, "app-mock-tool.png"), full_page=True)
    print("✓ app-mock-tool.png")

    page.locator('button[role="tab"]', has_text="关于").click()
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(OUT, "app-mock-about.png"), full_page=True)
    print("✓ app-mock-about.png")

    browser.close()
    print("\n=== 完成 ===")
