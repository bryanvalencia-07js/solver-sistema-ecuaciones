import numpy as np


def determinante_sarrus(matriz):
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


A = np.array([
    [2, 1, -1],
    [1, -2, 3],
    [3, 1, 2]
], dtype=float)

b = np.array([
    2,
    9,
    13
], dtype=float)


# Determinante principal
D = determinante_sarrus(A)


# Matriz para Dx
Ax = A.copy()
Ax[:, 0] = b

Dx = determinante_sarrus(Ax)


# Matriz para Dy
Ay = A.copy()
Ay[:, 1] = b

Dy = determinante_sarrus(Ay)


# Matriz para Dz
Az = A.copy()
Az[:, 2] = b

Dz = determinante_sarrus(Az)


print("D  =", D)
print("Dx =", Dx)
print("Dy =", Dy)
print("Dz =", Dz)


x = Dx / D
y = Dy / D
z = Dz / D


print()
print("x =", x)
print("y =", y)
print("z =", z)