from fractions import Fraction

import pytest

from core.determinantes import detalle_determinante, determinantes_cramer
from tests.casos import CASO_C


def test_sarrus_caso_e():
    a = [fila[:3] for fila in CASO_C]
    d = detalle_determinante(a)
    assert d["valor"] == -14
    assert d["extendida"] == [
        [2, 1, -1, 2, 1],
        [1, -2, 3, 1, -2],
        [3, 1, 2, 3, 1],
    ]
    assert [p["producto"] for p in d["descendentes"]] == [-8, 9, -1]
    assert [p["producto"] for p in d["ascendentes"]] == [6, 2, 6]
    assert (d["suma_desc"], d["suma_asc"]) == (0, 14)


def test_sarrus_reutilizado_en_matrices_auxiliares():
    a = [fila[:3] for fila in CASO_C]
    b = [fila[-1] for fila in CASO_C]
    detalles = determinantes_cramer(a, b, -14)
    for columna, d in enumerate(detalles):
        assert [fila[columna] for fila in d["matriz"]] == b
        for otra in set(range(3)) - {columna}:
            assert [fila[otra] for fila in d["matriz"]] == [
                fila[otra] for fila in a
            ]
        assert len(d["descendentes"]) == len(d["ascendentes"]) == 3


def test_determinante_2x2_decimal_exacto():
    d = detalle_determinante([[Fraction("0.2"), -1], [Fraction("0.1"), 2]])
    assert d["valor"] == Fraction("0.5")


@pytest.mark.parametrize("a", [[[1]], [[1, 2], [3]]])
def test_dimension_determinante(a):
    with pytest.raises(ValueError, match="matriz cuadrada"):
        detalle_determinante(a)
