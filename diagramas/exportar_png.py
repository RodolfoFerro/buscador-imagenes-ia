"""Convierte diagramas/svg/*.svg en PNG (2x) para insertarlos en el notebook.

Usa Google Chrome en modo headless, que dibuja el SVG con la tipografía
IBM Plex Mono (se descarga de Google Fonts al renderizar).

Uso:
    python diagramas/exportar_png.py
    python diagramas/exportar_png.py --chrome /ruta/a/chrome
"""
import argparse
import re
import subprocess
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CHROME_MAC = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

parser = argparse.ArgumentParser()
parser.add_argument("--chrome", default=CHROME_MAC, help="ejecutable de Chrome o Chromium")
args = parser.parse_args()

SALIDA = AQUI / "png"
SALIDA.mkdir(exist_ok=True)

PAGINA = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=block">
<style>html, body {{ margin: 0; background: #fff; }} svg {{ display: block; }}</style>
</head><body>{svg}</body></html>"""

with tempfile.TemporaryDirectory() as tmp:
    for archivo in sorted((AQUI / "svg").glob("*.svg")):
        contenido = archivo.read_text(encoding="utf-8")
        ancho, alto = map(int, re.search(r'viewBox="0 0 (\d+) (\d+)"', contenido).groups())
        html = Path(tmp) / f"{archivo.stem}.html"
        html.write_text(PAGINA.format(svg=contenido), encoding="utf-8")
        destino = SALIDA / f"{archivo.stem}.png"
        subprocess.run([
            args.chrome, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=2",
            f"--window-size={ancho},{alto}", "--virtual-time-budget=5000",
            f"--screenshot={destino}", html.as_uri(),
        ], check=True, capture_output=True)
        print(f"{destino.name}: {destino.stat().st_size // 1024} KB")
