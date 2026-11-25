import numpy as np
import pytest

from core.vectores import operar_vectores, producto_cruz
from tests.casos import CASO_C, INCOMPATIBLE_3D, PLANO_3D, RECTA_3D
from visualization.sistemas import graficar_sistema
from visualization.vectores import graficar_cruz, graficar_vectores


@pytest.mark.parametrize(
    "filas, nombre, tipo",
    [
        ([[1, 0, 3], [0, 1, 2]], "Intersección", "scatter"),
        ([[1, -2, 3], [2, -4, 6]], "Recta solución", "scatter"),
        ([[1, 1, 2], [1, 1, 3]], None, None),
        (CASO_C, "Intersección", "scatter3d"),
        (RECTA_3D, "Recta solución", "scatter3d"),
        (PLANO_3D, "Plano solución", "mesh3d"),
        (INCOMPATIBLE_3D, None, None),
    ],
)
def test_figura_sistema(resolver, filas, nombre, tipo):
    grafica = graficar_sistema(resolver(filas))
    indice = 0
    for fila in filas:
        if not any(fila[:-1]):
            continue
        dato = grafica.data[indice]
        puntos = (
            [dato.x, dato.y, dato.z] if len(filas) == 3 else [dato.x, dato.y]
        )
        assert np.asarray(fila[:-1]) @ np.asarray(puntos) == pytest.approx(
            [fila[-1]] * len(dato.x)
        )
        indice += 1
    assert len(grafica.data) == indice + bool(nombre)
    if nombre:
        assert (grafica.data[-1].name, grafica.data[-1].type) == (nombre, tipo)
        traza = grafica.data[-1]
        coordenadas = (
            [traza.x, traza.y, traza.z]
            if len(filas) == 3
            else [traza.x, traza.y]
        )
        for fila in filas:
            assert np.asarray(fila[:-1]) @ np.asarray(
                coordenadas
            ) == pytest.approx([fila[-1]] * len(traza.x))


@pytest.mark.parametrize("u, v", [([3, 4], [1, 2]), ([1, 2, 3], [4, 5, 6])])
def test_grafica_de_vectores(u, v):
    grafica = graficar_vectores(operar_vectores(u, v, -2))
    assert {d.name for d in grafica.data if d.visible} >= {
        "u",
        "v",
        "u + v",
        "Paralelogramo",
    }
    assert [b.label for b in grafica.layout.updatemenus[0].buttons] == [
        "u + v",
        "u − v",
        "ku",
    ]
    assert any(d.name == "Traslado de v a u" for d in grafica.data)


def test_grafica_de_cruz():
    grafica = graficar_cruz(producto_cruz([1, 2, 3], [4, 5, 6]))
    normal = next(d for d in grafica.data if d.name == "u × v")
    assert [normal.x[-1], normal.y[-1], normal.z[-1]] == [-3, 6, -3]
    assert grafica.layout.scene.dragmode == "orbit"


def test_grafica_sin_ecuaciones_geometricas(resolver):
    figura = graficar_sistema(resolver([[0, 0, 0], [0, 0, 0]]))
    assert "Todo ℝ² es solución" in figura.layout.annotations[0].text
