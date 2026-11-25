"""Operaciones vectoriales exactas y aproximaciones para normas y ángulos."""

from math import atan2, degrees, sqrt


def producto_punto(u, v):
    return sum(a * b for a, b in zip(u, v))


def producto_cruz(u, v):
    if len(u) != 3 or len(v) != 3:
        raise ValueError(
            "El producto cruz requiere dos vectores de tres componentes."
        )

    componentes = []
    for j, k, signo in ((1, 2, 1), (0, 2, -1), (0, 1, 1)):
        factores_p = (u[j], v[k])
        factores_q = (u[k], v[j])
        p = u[j] * v[k]
        q = u[k] * v[j]
        componentes.append(
            {
                "factores_p": factores_p,
                "factores_q": factores_q,
                "p": p,
                "q": q,
                "signo": signo,
                "valor": signo * (p - q),
            }
        )
    vector = [componente["valor"] for componente in componentes]
    norma_cuadrada = producto_punto(vector, vector)
    area = sqrt(norma_cuadrada)
    return {
        "u": u,
        "v": v,
        "componentes": componentes,
        "vector": vector,
        "norma_cuadrada": norma_cuadrada,
        "area": area,
        "triangulo": area / 2,
        "ortogonal_u": producto_punto(u, vector),
        "ortogonal_v": producto_punto(v, vector),
        "nulo": not any(u) or not any(v),
    }


def operar_vectores(u, v, k):
    if len(u) not in (2, 3) or len(u) != len(v):
        raise ValueError("Ambos vectores deben tener dos o tres componentes.")

    suma = [a + b for a, b in zip(u, v)]
    resta = [a - b for a, b in zip(u, v)]
    escalado = [k * a for a in u]
    cuadrado_u = producto_punto(u, u)
    cuadrado_v = producto_punto(v, v)
    dot = producto_punto(u, v)
    cruz = producto_cruz(u, v) if len(u) == 3 else None
    determinante = u[0] * v[1] - u[1] * v[0] if len(u) == 2 else None
    area = cruz["area"] if cruz is not None else abs(determinante)
    nulo = not cuadrado_u or not cuadrado_v
    # atan2(||u × v||, u · v) evita el redondeo del coseno cerca de ±1.
    angulo = None if nulo else degrees(atan2(area, dot))
    return {
        "u": u,
        "v": v,
        "k": k,
        "suma": suma,
        "resta": resta,
        "escalado": escalado,
        "norma_u": sqrt(cuadrado_u),
        "norma_v": sqrt(cuadrado_v),
        "cuadrado_u": cuadrado_u,
        "cuadrado_v": cuadrado_v,
        "dot": dot,
        "angulo": angulo,
        "area": area,
        "determinante": determinante,
        "cruz": cruz,
        "nulo": nulo,
        "paralelos": not nulo and not area,
        "perpendiculares": not nulo and not dot,
    }
