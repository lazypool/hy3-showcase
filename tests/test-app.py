"""Web 界面集成测试 — 启动 app.py 并用 Playwright 验证交互。"""
import os, sys, subprocess, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright


def test_app_chat():
    env = {**os.environ, "HY3_MOCK": "true"}
    proc = subprocess.Popen(
        [sys.executable, "app.py"], env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(4)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://localhost:7860")
            page.wait_for_timeout(1000)
            assert "Hy3 Showcase" in page.title()

            page.locator("textarea").fill("你好")
            page.keyboard.press("Enter")
            page.wait_for_timeout(8000)

            body = page.locator("body").inner_text()
            assert "Hy3" in body

            browser.close()
    finally:
        proc.terminate()
        proc.wait()
