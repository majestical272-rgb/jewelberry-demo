# -*- coding: utf-8 -*-
"""Замер плавности скролла в настоящем Chrome с GPU.

    python3 tools/bench.py <url> [метка]

Скролл и учёт кадров идут внутри страницы одним evaluate: round-trip на каждый
шаг измеряет харнес, а не сайт. Headless не использовать — он растеризует
софтварно и врёт в обе стороны. Норма: long>33 = 0%, средний кадр ~13 мс."""
import sys, io, statistics
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/'
LABEL = sys.argv[2] if len(sys.argv) > 2 else ''
SCRIPT = """() => new Promise(res => {
  const frames = []; let y = 0, last = performance.now();
  const step = now => {
    frames.push([now - last, y]); last = now;
    y += 34;                      /* ~2 экрана в секунду */
    scrollTo(0, y);
    if (y < 9900) requestAnimationFrame(step); else res(frames.slice(3));
  };
  scrollTo(0, 0); requestAnimationFrame(step);
})"""
def show(tag, f):
    d = [x for x, _ in f]; long_ = [x for x in d if x > 33]
    b = {}
    for v, y in f:
        if v > 33: b[int(y // 900)] = b.get(int(y // 900), 0) + 1
    print(f"{LABEL} {tag:9} avg={statistics.mean(d):5.1f}ms p95={sorted(d)[int(len(d)*.95)]:5.1f}ms "
          f"long>33={100*len(long_)/len(d):4.1f}% max={max(d):4.0f}ms  по экранам: {dict(sorted(b.items()))}")
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=False, args=["--window-size=1600,1000"]); pg = b.new_context(viewport={'width':1440,'height':900}).new_page()
    pg.goto(URL); pg.wait_for_timeout(1500)
    show('холодный', pg.evaluate(SCRIPT))
    pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(1000)
    show('прогрет', pg.evaluate(SCRIPT))
    b.close()
