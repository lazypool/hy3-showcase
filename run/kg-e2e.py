#!/usr/bin/env python3
"""创意知识图谱截图。先启动 kg.py，再运行本脚本。"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "demo", "screenshots")
os.makedirs(OUT, exist_ok=True)

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 1000})

    page.goto("http://localhost:7861")
    page.wait_for_timeout(3000)
    page.screenshot(path=os.path.join(OUT, "kg-initial.png"), full_page=True)
    print("✓ kg-initial.png")

    page.locator("textarea").fill("Transformer")
    page.keyboard.press("Enter")
    page.wait_for_timeout(12000)
    page.screenshot(path=os.path.join(OUT, "kg-graph.png"), full_page=True)
    print("✓ kg-graph.png")

    page.locator("text=原始提取数据").click()
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(OUT, "kg-json.png"), full_page=True)
    print("✓ kg-json.png")

    browser.close()
    print("\n=== 完成 ===")
