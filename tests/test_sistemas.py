from fractions import Fraction

import numpy as np
import pytest

from tests.casos import CASO_C, CASO_D, INCOMPATIBLE_3D, PLANO_3D, RECTA_3D


@pytest.mark.parametrize(
    "filas, solucion, determinantes",
    [
        ([[1, 1, 5], [1, -1, 1]], [3, 2], [-2, -6, -4]),  # A, CP1
        (CASO_C, [2, 1, 3], [-14, -28, -14, -42]),  # C, CP2
        (CASO_D, [-4, 6, 1], [-1, 4, -6, -1]),  # D
    ],
)
def test_solucion_unica(resolver, filas, solucion, determinantes):
    resultado = resolver(filas, "cramer")
    assert resultado["estado"] == "unica"
    assert resultado["particular"] == solucion
    assert resultado["rango_a"] == resultado["rango_ampliada"] == len(filas)
    assert [resultado["determinante"]["valor"]] + [
        d["valor"] for d in resultado["cramer"]
    ] == determinantes
    assert [d["cociente"] for d in resultado["cramer"]] == solucion
    assert resultado["numpy"]["coincide"]
    assert np.linalg.solve(
        np.asarray(filas)[:, :-1], np.asarray(filas)[:, -1]
    ) == pytest.approx(solucion)
    for comprobacion in resultado["verificacion"]:
        assert comprobacion["expresion"] == [comprobacion["rhs"]]


@pytest.mark.parametrize(
    "filas",
    [
        [[1, 1, 2], [1, 1, 3]],  # B, CP1
        INCOMPATIBLE_3D,  # CP3
        [[0, 0, 7], [0, 0, 0]],
    ],
)
def test_incompatibles_y_cramer_singular(resolver, filas):
    resultado = resolver(filas, "cramer")
    assert resultado["estado"] == "sin_solucion"
    assert resultado["rango_ampliada"] == resultado["rango_a"] + 1
    assert resultado["determinante"]["valor"] == 0
    assert all(d["cociente"] is None for d in resultado["cramer"])
    for _, fila in resultado["incompatibles"]:
        assert not any(fila[:-1])
        assert fila[-1]
    assert resultado["incompatibles"]


@pytest.mark.parametrize(
    "filas, particular, direcciones, libres",
    [
        ([[1, -2, 3], [2, -4, 6]], [3, 0], [[2, 1]], [1]),
        (RECTA_3D, [3, 0, 0], [[-2, 1, 1]], [2]),  # CP2
        (PLANO_3D, [3, 0, 0], [[-1, 1, 0], [-1, 0, 1]], [1, 2]),
        (
            [[0, 1, 0, 2], [0, 0, 1, 3], [0, 0, 0, 0]],
            [0, 2, 3],
            [[1, 0, 0]],
            [0],
        ),
        ([[0, 0, 0], [0, 0, 0]], [0, 0], [[1, 0], [0, 1]], [0, 1]),
        (
            [[0, 0, 0, 0]] * 3,
            [0, 0, 0],
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [0, 1, 2],
        ),
    ],
)
def test_soluciones_parametricas(
    resolver, filas, particular, direcciones, libres
):
    r = resolver(filas)
    assert r["estado"] == "infinitas"
    assert r["particular"] == particular
    assert r["direcciones"] == direcciones
    assert r["libres"] == libres
    assert r["rango_ampliada"] == r["rango_a"] == len(filas) - len(libres)
    for comprobacion in r["verificacion"]:
        assert comprobacion["expresion"] == [comprobacion["rhs"]] + [0] * len(
            libres
        )


def test_pivoteo_y_matrices_despues_de_cada_operacion(resolver):
    r = resolver([[0, 2, 4], [3, 1, 5]])
    assert r["particular"] == [1, 2]
    assert [p["tipo"] for p in r["pasos"]] == [
        "intercambio",
        "escala",
        "escala",
    ]
    assert r["pasos"][0]["matriz"] == [[3, 1, 5], [0, 2, 4]]
    assert r["pasos"][1]["matriz"] == [
        [1, Fraction(1, 3), Fraction(5, 3)],
        [0, 2, 4],
    ]
    assert r["escalonada"] == [[1, Fraction(1, 3), Fraction(5, 3)], [0, 1, 2]]


def test_eliminacion_con_factor_negativo(resolver):
    r = resolver([[2, 1, 5], [-1, 1, 2]])
    paso = r["pasos"][0]
    assert (paso["tipo"], paso["factor"]) == ("eliminacion", Fraction(-1, 2))
    assert paso["matriz"][1] == [0, Fraction(3, 2), Fraction(9, 2)]
    assert r["particular"] == [1, 3]


def test_determinante_pequeno_no_es_cero(resolver):
    t = Fraction("0.0001")
    r = resolver([[t, 0, t], [0, t, -t]], "cramer")
    assert r["particular"] == [1, -1]
    assert [d["cociente"] for d in r["cramer"]] == [1, -1]
    assert r["determinante"]["valor"] == Fraction("0.00000001")


def test_rangos_con_termino_independiente_grande(resolver):
    r = resolver([[1, 0, 10**20], [0, 1, 1]])
    assert r["estado"] == "unica"
    assert r["rango_ampliada"] == 2


def test_numpy_aproximado_no_oculta_solucion_exacta(resolver):
    eps = Fraction("1e-16")
    r = resolver([[1, 1, 0], [1, 1 + eps, eps]], "numpy")
    assert r["particular"] == [-1, 1]
    assert not r["numpy"]["coincide"]


def test_dimension_del_sistema(resolver):
    with pytest.raises(ValueError, match="sistema cuadrado"):
        resolver([[1, 2], [1, 2, 3]])
