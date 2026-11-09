# Buscador de imágenes con IA 🛰️

**Embeddings, similitud y clasificación con pocos datos** · Taller de nivel intermedio

Taller de 1.5-2 horas para personas con Python básico y nociones de NumPy y pandas. Usando un modelo preentrenado (CLIP) e imágenes satelitales (EuroSAT), se construye un buscador de imágenes y un clasificador **sin entrenar ninguna red neuronal**.

> **Pregunta guía:** ¿basta un modelo de IA general para entender imágenes de un dominio específico, o necesitamos nuestros propios datos?

---

## Notebook

| Tema | Enlace |
|---|---|
| Buscador de imágenes con IA: embeddings, similitud y clasificación con pocos datos | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RodolfoFerro/buscador-imagenes-ia/blob/main/notebooks/Taller_Buscador_Imagenes_IA.ipynb) |

El cuaderno está completo y ya ejecutado: incluye explicaciones, interpretación de resultados, 3 ejercicios con solución propuesta, 11 diagramas y un glosario. Es autocontenido: cada concepto nuevo (embeddings, CLIP, similitud coseno, PCA, UMAP, *zero-shot*, métricas, regresión logística, sobreajuste, etc.) tiene un recuadro breve de uno de cuatro tipos: 📖 **Definición**, ⚙️ **Cómo funciona**, 💡 **Intuición** o ⚠️ **Cuidado**.

Las gráficas de resultados son interactivas (`plotly`); las figuras con imágenes usan `matplotlib` en alta resolución.

---

## Agenda

| Bloque | Tema | Tiempo |
|---|---|---|
| 1 | La imagen como dato | 10 min |
| 2 | ¿Qué es un *embedding*? | 15 min |
| 3 | Un mapa del dataset: PCA y UMAP | 15 min |
| 4 | Buscador de imágenes similares (✏️ ejercicio 1) | 15 min |
| 5 | Clasificación *zero-shot* con texto (✏️ ejercicio 2) | 15 min |
| 6 | Clasificación con pocos datos (✏️ ejercicio 3) | 20 min |
| 7 | Búsqueda con texto y cierre | 10 min |

Total: 100 minutos, más 15-20 de margen para preguntas.

---

## Cómo ejecutarlo

### Google Colab (recomendado)

Da clic en el botón **Open in Colab** y ejecuta las celdas en orden. El propio cuaderno descarga EuroSAT (~94 MB) y el modelo CLIP (~600 MB). Funciona con CPU; con GPU (*Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4 GPU*) es más rápido.

### Local

```bash
git clone https://github.com/RodolfoFerro/buscador-imagenes-ia.git
cd buscador-imagenes-ia
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter lab notebooks/
```

Los datos se descargan en `notebooks/datos/`, que está excluida del repositorio. En una laptop con CPU (Apple M2, 2 hilos), el cuaderno completo se ejecuta en menos de un minuto; el paso más lento es calcular los embeddings (~26 s).

---

## Resultados principales

Muestra de 2,000 imágenes (200 por clase); evaluación con 500 imágenes de prueba (50 por clase).

| Método | Datos etiquetados | Exactitud |
|---|---|---|
| Al azar | 0 | 10.0% |
| *Zero-shot* con el nombre de la clase | 0 | 36.6% |
| *Zero-shot* con *"a centered satellite photo of …"* | 0 | 44.8% |
| Regresión logística sobre embeddings | 5 por clase | 65.2% |
| Regresión logística sobre embeddings | 20 por clase | 77.1% |
| Regresión logística sobre embeddings | 150 por clase | 85.8% |

El buscador de imágenes similares alcanza una precisión en 5 de 78.8%.

---

## Diagramas

Los diagramas del cuaderno se generan con código, en [`diagramas/`](diagramas/):

```bash
python diagramas/generar.py        # escribe diagramas/svg/*.svg
python diagramas/exportar_png.py   # los convierte en diagramas/png/*.png (requiere Google Chrome)
python diagramas/actualizar_notebook.py   # vuelve a incrustar los PNG en el cuaderno
```

En el cuaderno van incrustados como imágenes adjuntas a las celdas de texto, así que no dependen de archivos externos. `generar.py --sitio <carpeta>` escribe además la versión que usa el blog, cuyos colores siguen el tema claro u oscuro del sitio.

---

## Referencias

- **Datos:** [EuroSAT](https://github.com/phelber/EuroSAT) (licencia MIT). Helber et al. (2019), *EuroSAT: A Novel Dataset and Deep Learning Benchmark for Land Use and Land Cover Classification*, IEEE JSTARS. Imágenes de Sentinel-2, programa Copernicus.
- **Modelo:** [CLIP ViT-B/32](https://huggingface.co/openai/clip-vit-base-patch32). Radford et al. (2021), *Learning Transferable Visual Models From Natural Language Supervision*, ICML.

---

## Instructor

**Rodolfo Ferro** · ferro@cimat.mx
