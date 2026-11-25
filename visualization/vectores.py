"""Flechas y construcciones geométricas para vectores en 2D y 3D."""

import numpy as np

from .base import COLORES, SOLUCION, figura, malla, norma_estable, trazo


def flecha(dimension, vector, nombre, color, escala):
    extremo = np.asarray(vector, dtype=float)
    origen = np.zeros(dimension)
    longitud = norma_estable(extremo)
    if not longitud:
        return [
            trazo(
                dimension,
                [origen],
                mode="markers",
                name=f"{nombre} (nulo)",
                marker={"size": 8, "color": color, "symbol": "diamond-open"},
            )
        ]

    direccion = extremo / longitud
    altura = min(longitud * 0.23, escala * 0.08)
    base = extremo - direccion * altura
    trazo_flecha = trazo(
        dimension,
        [origen, extremo],
        mode="lines",
        name=nombre,
        line={"color": color, "width": 4},
        legendgroup=nombre,
        hovertemplate="%{fullData.name}<extra></extra>",
    )
    if dimension == 2:
        lateral = np.array([-direccion[1], direccion[0]]) * altura * 0.45
        punta = trazo(
            2,
            [extremo, base + lateral, base - lateral, extremo],
            mode="lines",
            fill="toself",
            fillcolor=color,
            line={"width": 0},
            hoverinfo="skip",
            showlegend=False,
            legendgroup=nombre,
        )
    else:
        u = np.cross(direccion, np.eye(3)[np.argmin(np.abs(direccion))])
        u = u / norma_estable(u) * altura * 0.46
        v = np.cross(direccion, u)
        punta = malla(
            [extremo, base + u, base + v, base - u, base - v],
            i=[0] * 4,
            j=[1, 2, 3, 4],
            k=[2, 3, 4, 1],
            color=color,
            showlegend=False,
            hoverinfo="skip",
            legendgroup=nombre,
        )
    return [trazo_flecha, punta]


def paralelogramo(dimension, u, v, nombre="Paralelogramo"):
    u, v = np.asarray(u, dtype=float), np.asarray(v, dtype=float)
    vertices = [np.zeros(dimension), u, u + v, v]
    contorno = trazo(
        dimension,
        vertices + vertices[:1],
        mode="lines",
        name=nombre,
        line={"dash": "dash", "color": "#52607a", "width": 2},
        hoverinfo="skip",
    )
    if dimension == 2:
        contorno.update(fill="toself", fillcolor="rgba(24, 92, 201, 0.13)")
        return [contorno]
    superficie = malla(
        vertices,
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        color=COLORES[0],
        opacity=0.24,
        hoverinfo="skip",
        showlegend=False,
    )
    return [superficie, contorno]


def construir_figura(u, v, grupos):
    dimension = len(u)
    grafica = figura(dimension)
    # Cada construcción conserva u y v. La vista se ajusta al alternar.
    cantidades = []
    for nombre, vector, extras in grupos:
        escala = max(
            norma_estable(np.asarray(fila, dtype=float))
            for fila in (u, v, vector)
        )
        trazos = extras + flecha(dimension, u, "u", COLORES[0], escala)
        trazos += flecha(dimension, v, "v", COLORES[1], escala)
        trazos += flecha(dimension, vector, nombre, SOLUCION, escala)
        cantidades.append(len(trazos))
        for elemento in trazos:
            elemento.visible = len(cantidades) == 1
            grafica.add_trace(elemento)

    if len(grupos) > 1:
        botones = []
        inicio = 0
        for (nombre, _, _), cantidad in zip(grupos, cantidades):
            botones.append(
                {
                    "label": nombre,
                    "method": "update",
                    "args": [
                        {
                            "visible": [
                                inicio <= i < inicio + cantidad
                                for i in range(len(grafica.data))
                            ]
                        }
                    ],
                }
            )
            inicio += cantidad
        grafica.update_layout(
            updatemenus=[
                {"buttons": botones, "x": 0.0, "y": 1.12, "xanchor": "left"}
            ],
            margin={"t": 62},
        )
    if dimension == 3:
        grafica.update_layout(scene_aspectmode="data")
    return grafica


def graficar_vectores(resultado):
    u, v = resultado["u"], resultado["v"]
    resta = trazo(
        len(u),
        [v, u],
        mode="lines",
        name="Traslado de v a u",
        line={"color": "#52607a", "dash": "dash", "width": 3},
    )
    return construir_figura(
        u,
        v,
        [
            ("u + v", resultado["suma"], paralelogramo(len(u), u, v)),
            ("u − v", resultado["resta"], [resta]),
            ("ku", resultado["escalado"], []),
        ],
    )


def graficar_cruz(resultado):
    u, v = resultado["u"], resultado["v"]
    return construir_figura(
        u,
        v,
        [
            ("u × v", resultado["vector"], paralelogramo(3, u, v)),
        ],
    )
