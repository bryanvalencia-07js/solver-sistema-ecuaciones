"""Gráficas de las ecuaciones y del conjunto solución de un sistema."""

from math import hypot

import numpy as np

from .base import COLORES, SOLUCION, figura, malla, trazo


def proyectar(punto, coeficientes, rhs):
    """Proyecta ortogonalmente un punto sobre una ecuación no degenerada."""
    norma2 = sum(coef * coef for coef in coeficientes)
    factor = (rhs - sum(x * a for x, a in zip(punto, coeficientes))) / norma2
    return [x + factor * a for x, a in zip(punto, coeficientes)]


def unitario(vector):
    escala = max(abs(x) for x in vector)
    relativo = [float(x / escala) for x in vector]
    return np.asarray(relativo) / hypot(*relativo)


def base_plano(normal):
    normal = unitario(normal)
    eje = np.eye(3)[np.argmin(np.abs(normal))]
    primero = unitario(np.cross(normal, eje))
    return primero, np.cross(normal, primero)


def recta(
    dimension, centro, direccion, radio, nombre, color, ancho, guion="solid"
):
    delta = unitario(direccion) * radio * 1.75
    return trazo(
        dimension,
        [centro - delta, centro + delta],
        mode="lines",
        name=nombre,
        line={"color": color, "width": ancho, "dash": guion},
        hovertemplate="%{fullData.name}<extra></extra>",
    )


def plano(centro, normal, radio, nombre, color, opacidad):
    u, v = base_plano(normal)
    u, v = (radio * 1.75) * u, (radio * 1.75) * v
    return malla(
        [centro - u - v, centro + u - v, centro + u + v, centro - u + v],
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        name=nombre,
        color=color,
        opacity=opacidad,
        showlegend=True,
        hovertemplate="%{fullData.name}<extra></extra>",
    )


def graficar_sistema(resultado):
    dimension = len(resultado["a"])
    particular = resultado.get("particular", [0] * dimension)
    ecuaciones = [
        (i, a, proyectar(particular, a, b))
        for i, (a, b) in enumerate(zip(resultado["a"], resultado["b"]))
        if any(a)
    ]
    centro = np.asarray(particular, dtype=float)
    radio = max(
        [5, *(abs(x) * 0.12 for x in centro)]
        + [
            1.25 * max(abs(np.asarray(punto, dtype=float) - centro))
            for _, _, punto in ecuaciones
        ]
    )
    grafica = figura(dimension, centro, radio)
    for indice, a, punto in ecuaciones:
        punto = np.asarray(punto, dtype=float)
        nombre = f"Ecuación {indice + 1}"
        if dimension == 2:
            grafica.add_trace(
                recta(
                    2,
                    punto,
                    [-a[1], a[0]],
                    radio,
                    nombre,
                    COLORES[indice],
                    ancho=5 if indice == 0 else 3,
                    guion="solid" if indice == 0 else "dash",
                )
            )
        else:
            grafica.add_trace(
                plano(punto, a, radio, nombre, COLORES[indice], 0.32)
            )

    if resultado["estado"] == "unica":
        grafica.add_trace(
            trazo(
                dimension,
                [centro],
                mode="markers",
                name="Intersección",
                marker={
                    "color": SOLUCION,
                    "size": 8,
                    "line": {"color": "white", "width": 1},
                },
            )
        )
    elif resultado["estado"] == "infinitas":
        direcciones = resultado["direcciones"]
        if len(direcciones) == 1:
            grafica.add_trace(
                recta(
                    dimension,
                    centro,
                    direcciones[0],
                    radio,
                    "Recta solución",
                    SOLUCION,
                    ancho=2 if dimension == 2 else 7,
                    guion="dot" if dimension == 2 else "solid",
                )
            )
        elif len(direcciones) == 2 and dimension == 3:
            normal = next(a for a in resultado["a"] if any(a))
            grafica.add_trace(
                plano(centro, normal, radio, "Plano solución", SOLUCION, 0.42)
            )
        else:
            grafica.add_annotation(
                text=f"Todo ℝ{'²' if dimension == 2 else '³'} es solución",
                xref="paper",
                yref="paper",
                x=0.5,
                y=1,
                showarrow=False,
                bgcolor="#d8f4ea",
                font={"color": SOLUCION},
            )
    if not grafica.data:
        grafica.add_trace(
            trazo(
                dimension,
                [centro],
                mode="markers",
                marker={"opacity": 0},
                showlegend=False,
                hoverinfo="skip",
            )
        )
    return grafica
