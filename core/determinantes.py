"""Desarrollos de determinantes compartidos por Cramer y Sarrus."""

from fractions import Fraction
from math import prod


def detalle_determinante(matriz):
    """Conserva los factores, los productos y los subtotales por diagonal."""
    matriz = [[Fraction(valor) for valor in fila] for fila in matriz]
    n = len(matriz)
    if n not in (2, 3) or any(len(fila) != n for fila in matriz):
        raise ValueError(
            "El determinante requiere una matriz cuadrada 2×2 o 3×3."
        )

    def productos(sentido):
        inicios = range(n) if n == 3 else [0 if sentido == 1 else 1]
        diagonales = []
        for inicio in inicios:
            indices = [(inicio + sentido * fila) % n for fila in range(n)]
            factores = [
                matriz[fila][columna] for fila, columna in enumerate(indices)
            ]
            diagonales.append(
                {"factores": factores, "producto": prod(factores)}
            )
        return diagonales

    descendentes = productos(1)
    ascendentes = productos(-1)
    suma_desc = sum(paso["producto"] for paso in descendentes)
    suma_asc = sum(paso["producto"] for paso in ascendentes)
    return {
        "matriz": matriz,
        "extendida": [fila + fila[:2] for fila in matriz] if n == 3 else None,
        "descendentes": descendentes,
        "ascendentes": ascendentes,
        "suma_desc": suma_desc,
        "suma_asc": suma_asc,
        "valor": suma_desc - suma_asc,
    }


def determinantes_cramer(a, b, principal):
    """Sustituye una columna por b en cada matriz auxiliar."""
    resultados = []
    for columna, variable in enumerate("xyz"[: len(a)]):
        sustituida = [list(fila) for fila in a]
        for fila, termino in zip(sustituida, b):
            fila[columna] = termino
        detalle = detalle_determinante(sustituida)
        detalle["variable"] = variable
        detalle["cociente"] = (
            detalle["valor"] / principal if principal else None
        )
        resultados.append(detalle)
    return resultados
