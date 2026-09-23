"""Скриншоты сцен на 1440, 375 и в reduced-motion. python3 tools/shots.py"""
import sys, pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path('tmp/shots'); OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://localhost:8765/?shots=1'
# позиции в долях высоты экрана: сцена1 hold, сцена2 hold, 3, 4, стык с бронью, форма
STOPS = {'s1': 0.0, 's1b': 1.4, 's2': 3.2, 's3': 5.6, 's4': 8.0, 'book': 9.9, 'tail': 11.5}

def run(w, h, tag, reduce=False):
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1,
                            reduced_motion='reduce' if reduce else 'no-preference')
        pg = ctx.new_page()
        errs = []
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(1200)
        for name, k in STOPS.items():
            pg.evaluate(f'window.scrollTo(0, innerHeight*{k})'); pg.wait_for_timeout(900)
            pg.screenshot(path=str(OUT / f'{tag}-{name}.png'))
        sw = pg.evaluate('document.documentElement.scrollWidth'); cw = pg.evaluate('document.documentElement.clientWidth')
        print(tag, 'scrollWidth', sw, 'clientWidth', cw, 'errors:', errs or 'none')
        b.close()

run(1440, 900, 'd')
run(375, 812, 'm')
run(1440, 900, 'rm', reduce=True)
