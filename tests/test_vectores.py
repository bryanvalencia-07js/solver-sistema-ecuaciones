from fractions import Fraction

import pytest

from core.vectores import operar_vectores, producto_cruz


def test_vectores_2d_caso_f_cp4():
    r = operar_vectores([3, 4], [1, 2], -2)
    assert r["suma"] == [4, 6]
    assert r["resta"] == [2, 2]
    assert r["escalado"] == [-6, -8]
    assert r["norma_u"] == 5
    assert r["norma_v"] == pytest.approx(5**0.5)
    assert r["dot"] == 11
    assert r["area"] == 2
    assert r["angulo"] == pytest.approx(10.30484647)


def test_vectores_3d_cp4():
    r = operar_vectores([1, 2, 3], [4, 5, 6], -2)
    assert r["suma"] == [5, 7, 9]
    assert r["resta"] == [-3, -3, -3]
    assert r["escalado"] == [-2, -4, -6]
    assert r["norma_u"] == pytest.approx(14**0.5)
    assert r["norma_v"] == pytest.approx(77**0.5)
    assert r["dot"] == 32
    assert r["area"] == pytest.approx(54**0.5)
    assert r["angulo"] == pytest.approx(12.93315449)


@pytest.mark.parametrize(
    "u, v, cruz, nulo",
    [
        ([1, 2, 3], [4, 5, 6], [-3, 6, -3], False),  # G, CP5
        ([1, 2, 3], [2, 4, 6], [0, 0, 0], False),  # H, CP5
        ([1, 2, 3], [0, 0, 0], [0, 0, 0], True),
    ],
)
def test_producto_cruz(u, v, cruz, nulo):
    r = producto_cruz(u, v)
    assert r["vector"] == cruz
    assert r["area"] == pytest.approx(sum(x * x for x in cruz) ** 0.5)
    assert r["triangulo"] == pytest.approx(r["area"] / 2)
    assert r["ortogonal_u"] == r["ortogonal_v"] == 0
    assert r["nulo"] == nulo


@pytest.mark.parametrize(
    "u, v, angulo, condicion",
    [
        ([0, 0], [-1, 2], None, "nulo"),
        ([1, 0, 0], [0, 0, -2], 90, "perpendiculares"),
        ([1, -2], [-2, 4], 180, "paralelos"),
        ([1, -2], [2, -4], 0, "paralelos"),
    ],
)
def test_angulos_especiales(u, v, angulo, condicion):
    r = operar_vectores(u, v, 0)
    assert r["angulo"] == angulo
    assert r[condicion]
    assert r["escalado"] == [0] * len(u)


def test_vectores_decimales_paralelos():
    u = [Fraction("-.1"), Fraction(".2"), Fraction("-.3")]
    r = operar_vectores(u, [3 * x for x in u], -2)
    assert r["paralelos"]
    assert r["cruz"]["vector"] == [0, 0, 0]


def test_dimensiones_de_vectores():
    with pytest.raises(ValueError, match="Ambos vectores"):
        operar_vectores([1, 2, 3], [4, 5], 2)
    with pytest.raises(ValueError, match="tres componentes"):
        producto_cruz([1, 2], [4, 5])
