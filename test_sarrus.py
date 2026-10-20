import numpy as np

def determinante_sarrus(matriz):
    if matriz.shape != (3, 3):
        raise ValueError(
            "La regla de Sarrus solo funciona con matrices 3x3."
        )

    a = matriz[0, 0]
    b = matriz[0, 1]
    c = matriz[0, 2]

    d = matriz[1, 0]
    e = matriz[1, 1]
    f = matriz[1, 2]

    g = matriz[2, 0]
    h = matriz[2, 1]
    i = matriz[2, 2]

    positivas = (
        a * e * i
        + b * f * g
        + c * d * h
    )

    negativas = (
        c * e * g
        + b * d * i
        + a * f * h
    )

    return positivas - negativas


A_prueba = np.array([
    [2, 1, -1],
    [1, -2, 3],
    [3, 1, 2]
], dtype=float)

print(
    "Determinante por Sarrus:",
    determinante_sarrus(A_prueba)
)