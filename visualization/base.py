"""Estilo compartido de las figuras interactivas."""

import numpy as np
import plotly.graph_objects as go

COLORES = ["#185cc9", "#b3441c", "#7043bf"]
SOLUCION = "#007758"


def figura(dimension, centro=None, radio=None):
    grafica = go.Figure()
    grafica.update_layout(
        template="plotly_white",
        font={"family": "system-ui, sans-serif", "color": "#21314a"},
        margin={"l": 48, "r": 18, "t": 20, "b": 36},
        legend={"orientation": "h", "y": -0.15},
        hoverlabel={"namelength": -1},
    )
    ejes = {}
    for indice, nombre in enumerate("xyz"[:dimension]):
        eje = {
            "title": nombre,
            "zerolinecolor": "#8798b1",
            "gridcolor": "#dbe3ef",
        }
        if centro is not None:
            eje["range"] = [
                float(centro[indice] - radio),
                float(centro[indice] + radio),
            ]
        ejes[f"{nombre}axis"] = eje
    if dimension == 2:
        ejes["yaxis"].update(scaleanchor="x", scaleratio=1)
        grafica.update_layout(**ejes)
    else:
        grafica.update_layout(
            scene={**ejes, "aspectmode": "cube", "dragmode": "orbit"},
            margin={"l": 12, "r": 12, "t": 20, "b": 35},
        )
    return grafica


def coordenadas(puntos):
    return dict(zip("xyz", np.asarray(puntos, dtype=float).T.tolist()))


def trazo(dimension, puntos, **opciones):
    clase = go.Scatter if dimension == 2 else go.Scatter3d
    return clase(**coordenadas(puntos), **opciones)


def malla(vertices, **opciones):
    return go.Mesh3d(**coordenadas(vertices), **opciones)


def norma_estable(vector):
    """Evita desbordamientos al elevar coordenadas grandes al cuadrado."""
    return float(np.hypot.reduce(vector))
