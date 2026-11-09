"""Reemplaza en el notebook los diagramas adjuntos por los PNG actuales de diagramas/png/.

Busca en cada celda de texto las referencias `attachment:<nombre>.png` y vuelve
a incrustar el archivo correspondiente. No cambia el texto ni las salidas.

Uso:
    python diagramas/actualizar_notebook.py
"""
import base64
import re
from pathlib import Path

import nbformat

AQUI = Path(__file__).resolve().parent
NOTEBOOK = AQUI.parent / "notebooks" / "Taller_Buscador_Imagenes_IA.ipynb"

nb = nbformat.read(NOTEBOOK, as_version=4)
actualizados = []
for celda in nb.cells:
    if celda.cell_type != "markdown":
        continue
    for nombre in re.findall(r"attachment:([\w-]+\.png)", celda.source):
        png = AQUI / "png" / nombre
        celda.setdefault("attachments", {})[nombre] = {"image/png": base64.b64encode(png.read_bytes()).decode()}
        actualizados.append(nombre)

nbformat.write(nb, NOTEBOOK)
print(f"{len(actualizados)} diagramas actualizados: {', '.join(actualizados)}")
