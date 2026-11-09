"""Genera los diagramas del taller "Buscador de imágenes con IA".

Cada diagrama se escribe en dos versiones:

- diagramas/svg/<nombre>.svg: SVG autocontenido con fondo claro (estilos y
  miniaturas incrustados). Es la base de los PNG que van en el notebook
  (ver exportar_png.py).
- <carpeta del sitio>/<nombre>.svg (opcional, con --sitio): SVG para insertar
  en línea en el blog. Sus clases d-* toman los colores de las variables CSS
  del sitio, así que siguen el tema claro/oscuro.

Uso:
    python diagramas/generar.py
    python diagramas/generar.py --sitio ../rodolfoferro.github.io/_includes/diagrams
"""
import argparse
import base64
import math
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--sitio", type=Path, help="carpeta _includes/diagrams del sitio")
ARGS = parser.parse_args()

SALIDA_SVG = AQUI / "svg"
SALIDA_SVG.mkdir(exist_ok=True)
if ARGS.sitio:
    ARGS.sitio.mkdir(parents=True, exist_ok=True)

MINI = "/assets/posts/buscador-imagenes-ia/miniaturas/"   # ruta de las miniaturas en el sitio
W = 960

# Colores del tema claro del sitio, para la versión autocontenida
CLARO = dict(bg="#FFFFFF", raised="#FFFFFF", inset="#E7E7EA", text="#101012", dim="#6A6A70",
             faint="#A6A6AC", rule="#D9D9DC", acc="#2a78d6", acc_soft="rgba(42, 120, 214, 0.14)",
             orange="#eb6834", green="#1baf7a")

ESTILO = """
text {{ font-family: "IBM Plex Mono", ui-monospace, Menlo, monospace; }}
.d-t {{ fill: {dim}; font-size: 13px; }}
.d-h {{ fill: {text}; font-size: 14px; font-weight: 600; }}
.d-faint {{ fill: {dim}; opacity: 0.8; font-size: 12px; }}
.d-acc-t {{ fill: {acc}; font-weight: 600; }}
.d-o-t {{ fill: {orange}; font-weight: 600; }}
.d-on-acc {{ fill: {raised}; font-weight: 600; }}
.d-box {{ fill: {inset}; stroke: {rule}; }}
.d-panel {{ fill: {raised}; stroke: {rule}; }}
.d-frame {{ fill: none; stroke: {rule}; }}
.d-enc {{ fill: {acc_soft}; stroke: {acc}; stroke-width: 1.5; }}
.d-frozen {{ fill: {inset}; stroke: {faint}; stroke-width: 1.5; stroke-dasharray: 6 4; }}
.d-mute {{ fill: {faint}; opacity: 0.55; }}
.d-chan-r {{ fill: rgba(220, 40, 40, 0.55); }}
.d-chan-g {{ fill: rgba(30, 170, 60, 0.55); }}
.d-chan-b {{ fill: rgba(40, 80, 220, 0.55); }}
.d-line {{ stroke: {faint}; stroke-width: 1.5; fill: none; }}
.d-thick {{ stroke-width: 2.5; }}
.d-dash {{ stroke-dasharray: 5 4; }}
.d-grid {{ stroke: rgba(255, 255, 255, 0.75); stroke-width: 1; }}
.d-edge {{ stroke: {faint}; stroke-width: 1; opacity: 0.8; }}
.d-acc-line {{ stroke: {acc}; stroke-width: 1.8; fill: none; }}
.d-o-line {{ stroke: {orange}; stroke-width: 1.8; fill: none; }}
.d-head {{ fill: {faint}; }}
.d-acc {{ fill: {acc}; }}
.d-o {{ fill: {orange}; }}
.d-g {{ fill: {green}; }}
.d-ring {{ stroke: {raised}; stroke-width: 2; }}
.d-pt {{ fill: {acc}; fill-opacity: 0.55; }}
.d-dot, .d-ink-dot {{ fill: {text}; }}
.d-halo {{ fill: {acc_soft}; stroke: {acc}; stroke-dasharray: 5 4; }}
.d-query {{ fill: {raised}; stroke: {text}; stroke-width: 3; }}
""".format(**CLARO)


def _miniaturas_incrustadas(s):
    # Reemplaza las rutas del sitio por data URIs, para que el SVG no dependa de archivos externos
    for f in sorted((AQUI / "miniaturas").glob("*.jpg")):
        datos = base64.b64encode(f.read_bytes()).decode()
        s = s.replace(f"{MINI}{f.name}", f"data:image/jpeg;base64,{datos}")
    return s


# ---------- utilidades ----------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(nombre, h, titulo, cuerpo):
    pid = nombre
    defs = f"""<defs>
<marker id="{pid}-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="d-head"/></marker>
<marker id="{pid}-fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="d-acc"/></marker>
<marker id="{pid}-fo" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="d-o"/></marker>
</defs>"""
    body = "\n".join(x for x in cuerpo if x)
    body = body.replace("MARK-F", f"url(#{pid}-f)").replace("MARK-A", f"url(#{pid}-fa)").replace("MARK-O", f"url(#{pid}-fo)")

    # 1) versión para el sitio (colores desde las variables CSS)
    if ARGS.sitio:
        s = (f'<svg class="d-svg" viewBox="0 0 {W} {h}" role="img" aria-labelledby="{pid}-t" xmlns="http://www.w3.org/2000/svg">'
             f'<title id="{pid}-t">{esc(titulo)}</title>\n{defs}\n{body}\n</svg>\n')
        s = "\n".join(l for l in s.splitlines() if l.strip())   # sin líneas en blanco: kramdown lo trata como HTML
        (ARGS.sitio / f"{nombre}.svg").write_text(s + "\n", encoding="utf-8")

    # 2) versión autocontenida con fondo claro
    s = (f'<svg viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" xmlns="http://www.w3.org/2000/svg">'
         f'<title>{esc(titulo)}</title>\n<style>{ESTILO}</style>\n{defs}\n'
         f'<rect width="{W}" height="{h}" fill="{CLARO["bg"]}"/>\n{body}\n</svg>\n')
    (SALIDA_SVG / f"{nombre}.svg").write_text(_miniaturas_incrustadas(s), encoding="utf-8")


def t(x, y, s, cls="d-t", anchor="middle", size=None, extra=""):
    st = f' style="font-size:{size}px"' if size else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{st}{extra}>{esc(s)}</text>'


def rect(x, y, w, h, cls="d-box", rx=4, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" class="{cls}"{extra}/>'


def line(x1, y1, x2, y2, cls="d-line", mark="MARK-F", extra=""):
    m = f' marker-end="{mark}"' if mark else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"{m}{extra}/>'


def img(x, y, s, archivo, extra=""):
    return (f'<image href="{MINI}{archivo}.jpg" x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" '
            f'preserveAspectRatio="none"{extra}/>' + rect(x, y, s, s, "d-frame", 2))


def vector(x, y, n, w=18, h=30, seed=0, cls="d-acc", gap=3, puntos=True):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        a = 0.15 + 0.85 * rng.random()
        out.append(rect(x + i * (w + gap), y, w, h, cls, 2, f' fill-opacity="{a:.2f}"'))
    xe = x + n * (w + gap)
    if puntos:
        out.append(t(xe + 10, y + h / 2 + 5, "…", "d-t", size=16))
    return "\n".join(out), xe + (22 if puntos else 0)


# ---------- 1. imagen -> vector ----------
def d_imagen_a_vector():
    c = []
    # pila de canales detrás de la imagen
    c.append(rect(76, 34, 150, 150, "d-chan-b", 3))
    c.append(rect(63, 47, 150, 150, "d-chan-g", 3))
    c.append(rect(50, 60, 150, 150, "d-chan-r", 3))
    c.append(img(50, 60, 150, "annualcrop_656"))
    c.append(t(138, 240, "Imagen: 64 × 64 × 3", "d-h"))
    c.append(t(138, 260, "12,288 números (pixeles)"))
    c.append(line(250, 135, 318, 135))
    # codificador (trapecio: comprime)
    c.append('<polygon points="330,55 500,95 500,175 330,215" class="d-enc"/>')
    c.append(t(412, 130, "CLIP", "d-h", size=16))
    c.append(t(412, 150, "codificador", size=12))
    c.append(t(412, 165, "de imágenes", size=12))
    c.append(line(512, 135, 580, 135))
    v, xe = vector(595, 120, 12, seed=3)
    c.append(v)
    v2, _ = vector(xe + 4, 120, 2, seed=8, puntos=False)
    c.append(v2)
    c.append(t(760, 100, "Embedding", "d-h"))
    c.append(t(760, 182, "[0.009, −0.000, 0.024, −0.033, …]", size=12))
    c.append(t(760, 240, "512 números que resumen", "d-h"))
    c.append(t(760, 260, "el contenido de la imagen"))
    svg("imagen-a-vector", 285, "Una imagen de 64 × 64 × 3 pasa por el codificador de CLIP y se convierte en un vector de 512 números", c)


# ---------- 2. espacio de embeddings ----------
def d_espacio():
    c = [rect(30, 20, 900, 330, "d-panel", 6)]
    s = 58
    grupos = {
        "Bosque": [(130, 70, "forest_1"), (205, 108, "forest_3"), (120, 150, "forest_7")],
        "Mar o lago": [(300, 205, "sealake_1"), (365, 245, "sealake_5")],
        "Residencial": [(690, 60, "residential_2"), (770, 95, "residential_3"), (705, 140, "residential_12")],
        "Industrial": [(790, 230, "industrial_4")],
    }
    for nombre, ims in grupos.items():
        for x, y, f in ims:
            c.append(img(x, y, s, f))
    c.append(t(185, 235, "Bosque", "d-h"))
    c.append(t(372, 330, "Mar o lago", "d-h"))
    c.append(t(752, 222, "Residencial", "d-h"))
    c.append(t(819, 312, "Industrial", "d-h"))
    # distancias
    c.append(line(160, 128, 223, 137, "d-acc-line", "MARK-A", ' marker-start="MARK-A"'))
    c.append(t(118, 50, "cerca: contenido parecido", "d-acc-t", "start", 12))
    c.append(line(240, 112, 685, 95, "d-o-line d-dash", "MARK-O", ' marker-start="MARK-O"'))
    c.append(t(462, 92, "lejos: contenido distinto", "d-o-t", size=12))
    c.append(t(910, 340, "(2 de las 512 dimensiones, como ilustración)", "d-t", "end", 11))
    svg("espacio-embeddings", 360, "En el espacio de embeddings, las imágenes de bosque quedan juntas y lejos de las zonas residenciales", c)


# ---------- 3. ViT y patches ----------
def d_vit():
    c = []
    c.append(img(20, 118, 52, "annualcrop_656"))
    c.append(t(46, 192, "64 × 64", size=12))
    c.append(line(80, 144, 118, 144))
    c.append(t(99, 165, "ampliar", size=10))
    x0, y0, L = 128, 46, 196
    c.append(img(x0, y0, L, "annualcrop_656"))
    for k in range(1, 7):
        p = x0 + k * L / 7
        c.append(line(p, y0, p, y0 + L, "d-grid", None))
        q = y0 + k * L / 7
        c.append(line(x0, q, x0 + L, q, "d-grid", None))
    c.append(t(x0 + L / 2, 268, "224 × 224 → 7 × 7 = 49 cuadros", "d-h", size=13))
    c.append(line(338, 144, 380, 144))
    # secuencia de cuadros (recortes reales de la imagen ampliada)
    px, ps = 392, 40
    celdas = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
    for i, (cx, cy) in enumerate(celdas):
        xx = px + i * (ps + 8)
        c.append(f'<svg x="{xx}" y="76" width="{ps}" height="{ps}" viewBox="{cx * 32} {cy * 32} 32 32" preserveAspectRatio="none">'
                 f'<image href="{MINI}annualcrop_656.jpg" width="224" height="224" preserveAspectRatio="none"/></svg>')
        c.append(rect(xx, 76, ps, ps, "d-frame", 2))
        c.append(t(xx + ps / 2, 68, str(i + 1), size=11))
        c.append(line(xx + ps / 2, 120, xx + ps / 2, 160, "d-line", "MARK-F"))
    xe = px + 6 * (ps + 8)
    c.append(t(xe + 12, 101, "…", size=16))
    c.append(t(xe + 40, 68, "49", size=11))
    c.append(rect(xe + 26, 76, ps * 0.7, ps, "d-box", 2))
    c.append(rect(392, 166, 330, 60, "d-enc", 6))
    c.append(t(557, 192, "Transformer", "d-h", size=15))
    c.append(t(557, 212, "¿cómo se relaciona cada cuadro con los demás?", size=11))
    c.append(line(730, 196, 768, 196))
    v, xe2 = vector(776, 181, 5, w=16, seed=3)
    c.append(v)
    c.append(t(852, 238, "Embedding (512)", "d-h", size=13))
    svg("vit-patches", 285, "El Vision Transformer amplía la imagen a 224 × 224, la corta en 49 cuadros de 32 × 32 y analiza cómo se relacionan entre sí", c)


# ---------- 4. CLIP contrastivo ----------
def d_clip():
    c = []
    textos = ["\"a forest\"", "\"a river\"", "\"a city\"", "\"a highway\""]
    ims = ["forest_1", "river_2", "residential_2", "highway_1"]
    x0, y0, cw, ch = 290, 115, 104, 62
    c.append(t(x0 + 2 * cw, 30, "Codificador de texto → un vector por descripción", "d-h", size=13))
    for j, s in enumerate(textos):
        c.append(rect(x0 + j * cw + 6, 48, cw - 12, 34, "d-box", 4))
        c.append(t(x0 + j * cw + cw / 2, 70, s, size=12))
        c.append(line(x0 + j * cw + cw / 2, 84, x0 + j * cw + cw / 2, y0 - 6, "d-line"))
    c.append(t(150, 30, "Codificador de", "d-h", size=13))
    c.append(t(150, 48, "imágenes", "d-h", size=13))
    for i, f in enumerate(ims):
        y = y0 + i * ch
        c.append(img(205, y + 6, 50, f))
        c.append(line(260, y + ch / 2, x0 - 6, y + ch / 2, "d-line"))
        for j in range(4):
            x = x0 + j * cw
            if i == j:
                c.append(rect(x + 3, y + 3, cw - 6, ch - 6, "d-acc", 4))
                c.append(t(x + cw / 2, y + ch / 2 + 5, "acercar", "d-on-acc", size=13))
            else:
                c.append(rect(x + 3, y + 3, cw - 6, ch - 6, "d-box", 4))
                c.append(t(x + cw / 2, y + ch / 2 + 5, "alejar", "d-faint", size=12))
    lx = x0 + 4 * cw + 30
    c.append(rect(lx, 150, 22, 22, "d-acc", 3))
    c.append(t(lx + 32, 166, "par correcto:", "d-t", "start", 12))
    c.append(t(lx + 32, 184, "se acercan", "d-t", "start", 12))
    c.append(rect(lx, 214, 22, 22, "d-box", 3))
    c.append(t(lx + 32, 230, "par incorrecto:", "d-t", "start", 12))
    c.append(t(lx + 32, 248, "se alejan", "d-t", "start", 12))
    c.append(t(lx, 300, "En el entrenamiento", "d-faint", "start", 11))
    c.append(t(lx, 316, "real, cada lote tiene", "d-faint", "start", 11))
    c.append(t(lx, 332, "~32,000 pares.", "d-faint", "start", 11))
    svg("clip-contrastivo", 375, "Aprendizaje contrastivo: en una matriz de imágenes contra textos, los pares correctos de la diagonal se acercan y el resto se aleja", c)


# ---------- 5. similitud coseno ----------
def d_coseno():
    c = []
    casos = [(20, 50, "θ pequeño", "sim ≈ 0.9", "parecidos"),
             (0, 90, "θ = 90°", "sim = 0", "sin relación"),
             (0, 180, "θ = 180°", "sim = −1", "opuestos")]
    for k, (a1, a2, th, sim, lab) in enumerate(casos):
        cx = 160 + k * 320
        ox, oy = (cx - 70, 170) if k < 2 else (cx, 170)
        r = 125
        for ang, cls, mk in [(a1, "d-acc-line", "MARK-A"), (a2, "d-o-line", "MARK-O")]:
            ex = ox + r * math.cos(math.radians(ang))
            ey = oy - r * math.sin(math.radians(ang))
            c.append(line(ox, oy, ex, ey, cls + " d-thick", mk))
        rr = 38
        x1, y1 = ox + rr * math.cos(math.radians(a1)), oy - rr * math.sin(math.radians(a1))
        x2, y2 = ox + rr * math.cos(math.radians(a2)), oy - rr * math.sin(math.radians(a2))
        large = 1 if (a2 - a1) > 180 else 0
        c.append(f'<path d="M{x1:.1f},{y1:.1f} A{rr},{rr} 0 {large} 0 {x2:.1f},{y2:.1f}" class="d-line"/>')
        mid = math.radians((a1 + a2) / 2)
        c.append(t(ox + (rr + 16) * math.cos(mid), oy - (rr + 16) * math.sin(mid) + 5, "θ", "d-h", size=13))
        c.append(f'<circle cx="{ox}" cy="{oy}" r="3" class="d-dot"/>')
        c.append(t(cx, 215, th, size=13))
        c.append(t(cx, 237, sim, "d-h", size=15))
        c.append(t(cx, 257, lab, size=13))
    svg("similitud-coseno", 275, "Similitud coseno: vectores con ángulo pequeño tienen similitud cercana a 1, perpendiculares 0 y opuestos −1", c)


# ---------- 6. PCA ----------
def d_pca():
    rng = np.random.default_rng(4)
    n = 110
    z = rng.normal(size=(n, 2)) * [1.0, 0.33]
    ang = math.radians(28)
    R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    pts = z @ R.T
    c = []
    # panel A
    c.append(rect(20, 20, 440, 290, "d-panel", 6))
    cx, cy, s = 240, 165, 62
    for (px, py) in pts:
        c.append(f'<circle cx="{cx + px * s:.1f}" cy="{cy - py * s:.1f}" r="3.2" class="d-pt"/>')
    # sombras de algunos puntos sobre PC1
    u = np.array([math.cos(ang), math.sin(ang)])
    for idx in [3, 17, 40, 66, 90]:
        p = pts[idx]
        pr = (p @ u) * u
        c.append(line(cx + p[0] * s, cy - p[1] * s, cx + pr[0] * s, cy - pr[1] * s, "d-line d-dash", None))
    L1, L2 = 2.6, 0.95
    c.append(line(cx, cy, cx + L1 * s * u[0], cy - L1 * s * u[1], "d-acc-line d-thick", "MARK-A"))
    v = np.array([-u[1], u[0]])
    c.append(line(cx, cy, cx + L2 * s * v[0], cy - L2 * s * v[1], "d-o-line d-thick", "MARK-O"))
    c.append(f'<circle cx="{cx}" cy="{cy}" r="5" class="d-ink-dot"/>')
    c.append(t(cx + L1 * s * u[0] + 6, cy - L1 * s * u[1] - 6, "PC1", "d-acc-t", "start", 13))
    c.append(t(cx + L2 * s * v[0] - 8, cy - L2 * s * v[1] - 6, "PC2", "d-o-t", "end", 13))
    c.append(t(40, 46, "1–3. Centrar y buscar las direcciones", "d-h", "start", 13))
    c.append(t(40, 64, "de mayor dispersión", "d-h", "start", 13))
    c.append(t(440, 296, "promedio = centro; punteado = proyección", "d-faint", "end", 11))
    c.append(line(472, 165, 508, 165))
    # panel B: coordenadas nuevas
    c.append(rect(520, 20, 420, 290, "d-panel", 6))
    bx, by = 730, 170
    c.append(line(545, by, 920, by, "d-acc-line", "MARK-A"))
    c.append(line(bx, 285, bx, 75, "d-o-line", "MARK-O"))
    c.append(t(918, by + 20, "PC1", "d-acc-t", "end", 13))
    c.append(t(bx + 8, 88, "PC2", "d-o-t", "start", 13))
    for (a, b) in z:
        c.append(f'<circle cx="{bx + a * 62:.1f}" cy="{by - b * 62:.1f}" r="3.2" class="d-pt"/>')
    c.append(t(540, 46, "4. Proyectar: las nuevas coordenadas", "d-h", "start", 13))
    c.append(t(540, 64, "son los componentes principales", "d-h", "start", 13))
    svg("pca", 325, "PCA: se centra la nube de puntos, se encuentran las direcciones de mayor dispersión (PC1 y PC2) y se proyectan los datos sobre ellas", c)


# ---------- 7. UMAP ----------
def d_umap():
    rng = np.random.default_rng(11)
    centros = np.array([[0.0, 0.0], [2.6, 1.0], [1.0, 2.6]])
    pts = np.concatenate([centros[k] + rng.normal(scale=0.45, size=(7, 2)) for k in range(3)])
    grupo = np.repeat([0, 1, 2], 7)
    # aristas: 3 vecinos más cercanos
    D = np.linalg.norm(pts[:, None] - pts[None], axis=-1)
    aristas = set()
    for i in range(len(pts)):
        for j in np.argsort(D[i])[1:4]:
            aristas.add(tuple(sorted((i, int(j)))))
    azar = rng.uniform(-1, 1, size=pts.shape) * 1.9 + 1.3
    final = np.concatenate([np.array([[0.2, 2.8], [2.8, 2.6], [1.5, 0.1]])[k] + rng.normal(scale=0.28, size=(7, 2)) for k in range(3)])
    paneles = [(pts, "1. Grafo de vecinos", "(en el espacio de 512-D)"),
               (azar, "2. Posiciones al azar", "en 2-D"),
               (final, "3. Acercar vecinos,", "alejar no vecinos")]
    cls = ["d-acc", "d-o", "d-g"]
    c = []
    for k, (P, l1, l2) in enumerate(paneles):
        x0 = 20 + k * 315
        c.append(rect(x0, 20, 290, 300, "d-panel", 6))
        mn, mx = P.min(0), P.max(0)
        f = lambda p: (x0 + 35 + (p[0] - mn[0]) / (mx[0] - mn[0]) * 220, 280 - (p[1] - mn[1]) / (mx[1] - mn[1]) * 170)
        for i, j in aristas:
            a, b = f(P[i]), f(P[j])
            c.append(line(a[0], a[1], b[0], b[1], "d-edge", None))
        for i, p in enumerate(P):
            a = f(p)
            c.append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="5" class="{cls[grupo[i]]} d-ring"/>')
        c.append(t(x0 + 145, 50, l1, "d-h", size=13))
        c.append(t(x0 + 145, 68, l2, size=12))
        if k < 2:
            c.append(line(x0 + 293, 170, x0 + 312, 170))
    c.append(t(940, 340, "Los colores solo sirven para seguir a cada grupo: UMAP no conoce las clases.", "d-faint", "end", 11))
    svg("umap", 350, "UMAP: construye un grafo de vecinos, coloca los puntos al azar en 2-D y los mueve para acercar a los vecinos y alejar al resto", c)


# ---------- 8. buscador y precisión en k ----------
def d_busqueda():
    c = []
    c.append(img(30, 95, 90, "forest_1"))
    c.append(t(75, 82, "Consulta", "d-h", size=13))
    c.append(t(75, 210, "su embedding q", size=12))
    c.append(line(132, 140, 200, 140))
    c.append(t(166, 128, "X @ q", "d-acc-t", size=12))
    # similitudes desordenadas
    sims = ["0.81", "0.95", "0.78", "0.93", "0.84", "0.94"]
    c.append(t(262, 40, "Similitud con", "d-h", size=13))
    c.append(t(262, 58, "las 2,000 imágenes", "d-h", size=13))
    for i, s in enumerate(sims):
        y = 72 + i * 24
        c.append(rect(212, y, 100, 19, "d-box", 3))
        c.append(t(262, y + 14, s, size=12))
    c.append(t(262, 232, "…", size=16))
    c.append(line(325, 140, 393, 140))
    c.append(t(359, 128, "ordenar", size=12))
    res = [("forest_3", True, "0.95"), ("forest_7", True, "0.94"), ("forest_9", True, "0.93"), ("sealake_1", False, "0.93"), ("forest_7", True, "0.92")]
    res[4] = ("forest_2", True, "0.92")
    c.append(t(640, 40, "Los 5 resultados más parecidos", "d-h", size=13))
    for i, (f, ok, s) in enumerate(res):
        x = 410 + i * 94
        c.append(img(x, 70, 80, f))
        c.append(t(x + 40, 172, s, size=12))
        c.append(t(x + 40, 198, "✓" if ok else "✗", "d-acc-t" if ok else "d-o-t", size=18))
    c.append(t(640, 238, "precisión en 5 = 4 / 5 = 80%", "d-h", size=14))
    svg("busqueda", 260, "El buscador compara el embedding de la consulta con todas las imágenes, las ordena por similitud y devuelve las 5 más parecidas", c)


# ---------- 9. zero-shot ----------
def d_zero_shot():
    c = []
    frases = ["forest", "river", "sea or lake", "highway"]
    c.append(t(20, 30, "Una frase por clase", "d-h", "start", 13))
    for i, s in enumerate(frases):
        y = 44 + i * 30
        c.append(rect(20, y, 300, 24, "d-box", 3))
        c.append(t(30, y + 17, f"a centered satellite photo of {s}.", "d-t", "start", 11))
    c.append(t(170, 180, "… (10 frases)", size=12))
    c.append(line(330, 100, 368, 100))
    c.append(rect(376, 72, 120, 56, "d-enc", 6))
    c.append(t(436, 96, "codificador", size=12))
    c.append(t(436, 112, "de texto", size=12))
    c.append(line(504, 100, 540, 100))
    for i in range(4):
        v, _ = vector(548, 50 + i * 26, 6, w=12, h=18, seed=20 + i, cls="d-o", gap=2, puntos=False)
        c.append(v)
    c.append(t(593, 168, "T: 10 vectores", size=12))
    # imagen
    c.append(img(120, 222, 70, "forest_1"))
    c.append(line(200, 257, 368, 257))
    c.append(rect(376, 229, 120, 56, "d-enc", 6))
    c.append(t(436, 253, "codificador", size=12))
    c.append(t(436, 269, "de imágenes", size=12))
    c.append(line(504, 257, 540, 257))
    v, _ = vector(548, 248, 6, w=12, h=18, seed=3, gap=2, puntos=False)
    c.append(v)
    c.append(t(593, 292, "x: 1 vector", size=12))
    # similitudes
    c.append(line(650, 200, 688, 200))
    c.append(t(800, 30, "Similitud de x con cada frase", "d-h", size=13))
    vals = [("Bosque", 0.29), ("Mar o lago", 0.26), ("Río", 0.24), ("Autopista", 0.22)]
    for i, (n, s) in enumerate(vals):
        y = 60 + i * 40
        w = (s - 0.18) / 0.11 * 105
        best = i == 0
        c.append(t(790, y + 15, n, "d-h" if best else "d-t", "end", 12))
        c.append(rect(800, y, w, 22, "d-acc" if best else "d-mute", 3))
        c.append(t(806 + w, y + 16, f"{s:.2f}", "d-t", "start", 12))
    c.append(t(800, 242, "…", "d-t", "start", 16))
    c.append(t(800, 282, "Predicción: la frase", "d-h", size=13))
    c.append(t(800, 300, "más similar → Bosque", "d-acc-t", size=13))
    svg("zero-shot", 315, "Clasificación zero-shot: se compara el embedding de la imagen con el de una frase por clase y gana la más similar", c)


# ---------- 10. linear probe vs fine-tuning ----------
def d_linear_probe():
    c = []
    filas = [("Linear probe", "d-frozen", "congelado", "regresión logística"),
             ("Fine-tuning", "d-enc", "se entrena", "capa de clasificación")]
    for k, (titulo, cls_clip, estado, cabeza) in enumerate(filas):
        y = 40 + k * 135
        c.append(t(20, y - 8, titulo, "d-h", "start", 14))
        c.append(img(20, y + 10, 64, "forest_1"))
        c.append(line(92, y + 42, 128, y + 42))
        c.append(rect(136, y + 4, 200, 76, cls_clip, 6))
        c.append(t(236, y + 36, "CLIP", "d-h", size=15))
        c.append(t(236, y + 58, f"({estado})", "d-acc-t" if k else "d-t", size=12))
        c.append(line(344, y + 42, 380, y + 42))
        v, xe = vector(388, y + 30, 6, w=12, h=24, seed=3, gap=2, puntos=False)
        c.append(v)
        c.append(line(xe + 8, y + 42, xe + 44, y + 42))
        c.append(rect(xe + 52, y + 4, 220, 76, "d-enc", 6))
        c.append(t(xe + 162, y + 36, cabeza, "d-h", size=13))
        c.append(t(xe + 162, y + 58, "(se entrena)", "d-acc-t", size=12))
        c.append(line(xe + 280, y + 42, xe + 316, y + 42))
        c.append(t(xe + 324, y + 47, "Bosque", "d-h", "start", 14))
    c.append(rect(20, 300, 22, 16, "d-enc", 3))
    c.append(t(50, 313, "se entrena con nuestros datos", "d-t", "start", 12))
    c.append(rect(300, 300, 22, 16, "d-frozen", 3))
    c.append(t(330, 313, "congelado: solo se usa para calcular embeddings", "d-t", "start", 12))
    svg("linear-probe", 330, "Linear probe: CLIP queda congelado y solo se entrena una regresión logística encima. Fine-tuning: también se entrena CLIP", c)


# ---------- 11. k-NN ----------
def d_knn():
    rng = np.random.default_rng(5)
    A = rng.normal(size=(11, 2)) * 0.55 + [-0.7, 0.2]     # bosque
    B = rng.normal(size=(9, 2)) * 0.5 + [0.75, -0.25]     # mar o lago
    C = rng.normal(size=(8, 2)) * 0.45 + [0.2, 1.5]       # río
    pts = np.concatenate([A, B, C])
    lab = np.array([0] * len(A) + [1] * len(B) + [2] * len(C))
    # consulta en la frontera: buscamos una posición donde la votación quede 3 contra 2
    q = None
    for qx_ in np.linspace(-0.4, 0.6, 41):
        for qy_ in np.linspace(-0.3, 0.6, 37):
            cand = np.array([qx_, qy_])
            v5 = lab[np.argsort(np.linalg.norm(pts - cand, axis=1))[:5]]
            if sorted(np.bincount(v5, minlength=3))[-2:] == [2, 3] and (v5 == 0).sum() == 3:
                q = cand
                break
        if q is not None:
            break
    d = np.linalg.norm(pts - q, axis=1)
    vec = np.argsort(d)[:5]
    orden = np.argsort(d)
    radio = (d[orden[4]] + d[orden[5]]) / 2   # el círculo contiene exactamente 5 puntos
    mn, mx = pts.min(0), pts.max(0)
    s = min(470 / (mx[0] - mn[0]), 240 / (mx[1] - mn[1]))
    cx = 290 - (mn[0] + mx[0]) / 2 * s
    cy = 200 + (mn[1] + mx[1]) / 2 * s
    P = lambda p: (cx + p[0] * s, cy - p[1] * s)
    cls = ["d-acc", "d-g", "d-o"]
    nombres = ["Bosque", "Mar o lago", "Río"]
    c = [rect(20, 20, 540, 340, "d-panel", 6)]
    qx, qy = P(q)
    c.append(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="{radio * s:.1f}" class="d-halo"/>')
    for i in vec:
        a = P(pts[i])
        c.append(line(qx, qy, a[0], a[1], "d-edge", None))
    for i, p in enumerate(pts):
        a = P(p)
        c.append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="6" class="{cls[lab[i]]} d-ring"/>')
    c.append(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="8" class="d-query"/>')
    c.append(t(qx, qy - 16, "¿?", "d-h", size=13))
    for k, n in enumerate(nombres):
        c.append(f'<circle cx="{44 + k * 130}" cy="338" r="6" class="{cls[k]} d-ring"/>')
        c.append(t(56 + k * 130, 343, n, "d-t", "start", 12))
    # votación
    conteo = {k: int((lab[vec] == k).sum()) for k in range(3)}
    ganador = max(conteo, key=conteo.get)
    c.append(t(600, 60, "Los k = 5 vecinos más", "d-h", "start", 13))
    c.append(t(600, 78, "cercanos votan:", "d-h", "start", 13))
    y = 115
    for k in sorted(conteo, key=lambda k: -conteo[k]):
        if conteo[k] == 0:
            continue
        for m in range(conteo[k]):
            c.append(f'<circle cx="{612 + m * 22}" cy="{y}" r="7" class="{cls[k]} d-ring"/>')
        c.append(t(612 + 3 * 22 + 8, y + 5, f"{nombres[k]}: {conteo[k]}", "d-t", "start", 13))
        y += 34
    c.append(t(600, y + 30, f"Predicción: {nombres[ganador]}", "d-acc-t", "start", 14))
    c.append(t(600, y + 64, "Es el buscador de la parte I", "d-faint", "start", 12))
    c.append(t(600, y + 82, "más una votación.", "d-faint", "start", 12))
    svg("knn", 370, "k vecinos más cercanos: los 5 puntos más cercanos a la consulta votan y gana la clase más común", c)
    return conteo


for f in [d_imagen_a_vector, d_espacio, d_vit, d_clip, d_coseno, d_pca, d_umap, d_busqueda, d_zero_shot, d_linear_probe, d_knn]:
    r = f()
    if r:
        print(f.__name__, r)
print("Diagramas:", ", ".join(sorted(p.stem for p in SALIDA_SVG.glob("*.svg"))))
