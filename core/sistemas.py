"""Eliminación explícita con pivoteo parcial y sustitución regresiva."""

from fractions import Fraction

import numpy as np

from .determinantes import detalle_determinante, determinantes_cramer


def sustitucion(matriz, pivotes, n):
    """Representa cada incógnita por su constante y sus coeficientes libres."""
    libres = [col for col in range(n) if col not in pivotes]
    expresiones = [[Fraction(0)] * (1 + len(libres)) for _ in range(n)]
    for indice, columna in enumerate(libres, start=1):
        expresiones[columna][indice] = Fraction(1)

    pasos = []
    for fila, columna in reversed(list(enumerate(pivotes))):
        valores = matriz[fila]
        terminos = [
            (valores[j], j, expresiones[j])
            for j in range(columna + 1, n)
            if valores[j]
        ]
        numerador = [
            (valores[-1] if componente == 0 else 0)
            - sum(
                factor * expresion[componente]
                for factor, _, expresion in terminos
            )
            for componente in range(1 + len(libres))
        ]
        expresiones[columna] = [
            valor / valores[columna] for valor in numerador
        ]
        pasos.append(
            {
                "variable": columna,
                "pivote": valores[columna],
                "terminos": terminos,
                "rhs": valores[-1],
                "numerador": numerador,
                "expresion": expresiones[columna],
            }
        )
    return libres, expresiones, pasos


def resolver_gauss(a, b):
    """Escalona [A | b] con fracciones exactas, aun si A es singular."""
    n = len(a)
    if n not in (2, 3) or len(b) != n or any(len(fila) != n for fila in a):
        raise ValueError("Se requiere un sistema cuadrado 2×2 o 3×3.")
    matriz = [
        [Fraction(valor) for valor in fila] + [Fraction(termino)]
        for fila, termino in zip(a, b)
    ]
    pasos = []
    pivotes = []

    def registrar(tipo, fila, otra=None, factor=None):
        pasos.append(
            {
                "tipo": tipo,
                "fila": fila + 1,
                "otra": otra + 1 if otra is not None else None,
                "factor": factor,
                "matriz": [r.copy() for r in matriz],
            }
        )

    for columna in range(n):
        fila_pivote = len(pivotes)
        mayor = max(
            range(fila_pivote, n), key=lambda f: abs(matriz[f][columna])
        )
        if not matriz[mayor][columna]:
            continue
        if mayor != fila_pivote:
            matriz[mayor], matriz[fila_pivote] = (
                matriz[fila_pivote],
                matriz[mayor],
            )
            registrar("intercambio", fila_pivote, mayor)

        pivote = matriz[fila_pivote][columna]
        for fila in range(fila_pivote + 1, n):
            factor = matriz[fila][columna] / pivote
            if factor:
                matriz[fila] = [
                    valor - factor * base
                    for valor, base in zip(matriz[fila], matriz[fila_pivote])
                ]
                registrar("eliminacion", fila, fila_pivote, factor)
        pivotes.append(columna)

    incompatibles = [
        (fila + 1, valores)
        for fila, valores in enumerate(matriz)
        if not any(valores[:-1]) and valores[-1]
    ]
    # Normalizar al final conserva el criterio de selección de pivotes.
    for fila, columna in enumerate(pivotes):
        pivote = matriz[fila][columna]
        if pivote != 1:
            matriz[fila] = [valor / pivote for valor in matriz[fila]]
            registrar("escala", fila, factor=1 / pivote)

    rango = len(pivotes)
    resultado = {
        "rango_a": rango,
        "rango_ampliada": rango + bool(incompatibles),
        "incompatibles": incompatibles,
        "estado": (
            "sin_solucion"
            if incompatibles
            else "unica"
            if rango == n
            else "infinitas"
        ),
        "pasos": pasos,
        "escalonada": matriz,
    }
    if not incompatibles:
        libres, expresiones, regresiva = sustitucion(matriz, pivotes, n)
        resultado.update(
            libres=libres,
            expresiones=expresiones,
            regresiva=regresiva,
            particular=[fila[0] for fila in expresiones],
            direcciones=[
                [fila[i] for fila in expresiones]
                for i in range(1, len(libres) + 1)
            ],
        )
    return resultado


def contrastar_numpy(a, b, exacta):
    """Compara la solución exacta con el resultado en punto flotante."""
    a_float = np.asarray(a, dtype=float)
    b_float = np.asarray(b, dtype=float)
    try:
        calculada = np.linalg.solve(a_float, b_float)
    except np.linalg.LinAlgError:
        return {"coincide": False, "valores": None}

    objetivo = np.asarray(exacta, dtype=float)
    escala = max(np.max(np.abs(objetivo)), np.finfo(float).tiny)
    error = float(np.max(np.abs(calculada - objetivo)) / escala)
    finita = bool(np.all(np.isfinite(calculada)))
    return {
        "coincide": finita and error <= 1e-9,
        "valores": calculada.tolist() if finita else None,
    }


def resolver_sistema(a, b, metodo):
    resultado = resolver_gauss(a, b)
    resultado["a"] = a
    resultado["b"] = b
    resultado["aumentada"] = [list(fila) + [rhs] for fila, rhs in zip(a, b)]
    resultado["degeneradas"] = [
        (i + 1, rhs)
        for i, (fila, rhs) in enumerate(zip(a, b))
        if not any(fila)
    ]
    principal = detalle_determinante(a)
    resultado["determinante"] = principal
    resultado["metodo"] = metodo
    if metodo == "cramer":
        resultado["cramer"] = determinantes_cramer(a, b, principal["valor"])

    if resultado["estado"] != "sin_solucion":
        expresiones = resultado["expresiones"]
        resultado["verificacion"] = [
            {
                "expresion": [
                    sum(
                        coef * valor[i]
                        for coef, valor in zip(fila, expresiones)
                    )
                    for i in range(len(expresiones[0]))
                ],
                "rhs": rhs,
            }
            for fila, rhs in zip(a, b)
        ]

    if resultado["estado"] == "unica":
        resultado["numpy"] = contrastar_numpy(a, b, resultado["particular"])
    return resultado
