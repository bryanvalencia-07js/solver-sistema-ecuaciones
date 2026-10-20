# ============================================================
# RESOLVEDOR DE SISTEMAS DE ECUACIONES LINEALES
# Sistemas 2x2 y 3x3
#
# Backend: Flask
# Matemáticas: NumPy
# Gráficas: Matplotlib
# ============================================================


# Flask permite crear el servidor web y comunicarnos con HTML.
from flask import Flask, render_template, request

# NumPy permite trabajar con matrices y álgebra lineal.
import numpy as np

# Matplotlib se utilizará para generar las gráficas.
import matplotlib

# "Agg" permite generar imágenes sin abrir una ventana gráfica.
# Es útil cuando Matplotlib se ejecuta dentro de un servidor Flask.
matplotlib.use("Agg")

import matplotlib.pyplot as plt

# Utilidades para convertir la gráfica en una imagen
# que después podremos mostrar directamente en HTML.
import io
import base64


# ============================================================
# CREACIÓN DE LA APLICACIÓN FLASK
# ============================================================

app = Flask(__name__)

def leer_valor_con_signo(formulario,nombre_campo):
    """
    Lee un valor del formulario separando:
    1. El signo (+1 o -1)
    2. La magnitud numérica

    Ejemplo esperado desde HTML:
        sign_a11 = "1" o "-1"
        a11 =      "3"

    Resultado:
        1 * 3 = 3
        -1 * 3 = -3
    """

    signo = int(formulario.get(f"sign_{nombre_campo}", "1"))
    magnitud = float(formulario.get(nombre_campo, 0))

    return signo * magnitud

# ============================================================
# FUNCIÓN: CLASIFICAR EL SISTEMA
# ============================================================

def clasificar_sistema(A, b):
    """
    Determina si un sistema tiene:

    1. Una única solución.
    2. Infinitas soluciones.
    3. Ninguna solución.

    Para hacerlo usamos el rango de matrices.

    A = matriz de coeficientes.
    b = vector de términos independientes.
    """

    # Número de incógnitas.
    n = A.shape[1]

    # Matriz aumentada [A | b]
    matriz_aumentada = np.column_stack((A, b))

    # Rango de la matriz de coeficientes.
    rango_A = np.linalg.matrix_rank(A)

    # Rango de la matriz aumentada.
    rango_aumentada = np.linalg.matrix_rank(matriz_aumentada)

    # Teorema de Rouché-Frobenius:
    #
    # rango(A) = rango(A|b) = número de incógnitas
    # -> solución única.

    if rango_A == rango_aumentada == n:
        estado = "unica"

    # Si los rangos son iguales pero menores que
    # el número de incógnitas, existen infinitas soluciones.
    elif rango_A == rango_aumentada < n:
        estado = "infinitas"

    # Si los rangos son diferentes, el sistema es incompatible.
    else:
        estado = "sin_solucion"

    return estado, rango_A, rango_aumentada

# ============================================================
# SARRUS
# ============================================================


def determinante_sarrus(matriz):
    """
    Calcula el determinante de una matriz 3x3
    utilizando la Regla de Sarrus.

    Matriz:

        | a  b  c |
        | d  e  f |
        | g  h  i |

    Determinante:

        D = aei + bfg + cdh
            - ceg - bdi - afh
    """

    # Verificamos que realmente sea una matriz 3x3.
    if matriz.shape != (3, 3):
        raise ValueError(
            "La regla de Sarrus solo funciona con matrices 3x3."
        )

    # Extraemos cada elemento de la matriz.
    a = matriz[0, 0]
    b = matriz[0, 1]
    c = matriz[0, 2]

    d = matriz[1, 0]
    e = matriz[1, 1]
    f = matriz[1, 2]

    g = matriz[2, 0]
    h = matriz[2, 1]
    i = matriz[2, 2]

    # Diagonales descendentes.
    positivas = (
        a * e * i
        + b * f * g
        + c * d * h
    )

    # Diagonales ascendentes.
    negativas = (
        c * e * g
        + b * d * i
        + a * f * h
    )

    determinante = positivas - negativas

    return determinante


# ============================================================
# MÉTODO DE CRAMER
# ============================================================

def resolver_cramer(A, b):
    """
    Resuelve un sistema usando la Regla de Cramer.

    Funciona cuando el determinante de A es diferente de 0.

    Fórmula general:

        xi = Di / D

    donde:

        D  = determinante de A
        Di = determinante reemplazando una columna por b
    """

    if A.shape == (3, 3):
        determinante_A = determinante_sarrus(A)
    else:
        determinante_A = np.linalg.det(A)

    # Debido a que trabajamos con números decimales,
    # usamos np.isclose() en lugar de comparar directamente con 0.
    if np.isclose(determinante_A, 0):
        return None, None

    soluciones = []

    determinantes = []

    # Recorremos cada columna de A.
    for columna in range(A.shape[1]):

        # Copiamos A para no modificar la matriz original.
        Ai = A.copy()

        # Sustituimos la columna actual por b.
        Ai[:, columna] = b

        # Calculamos el determinante de la nueva matriz.
        if Ai.shape == (3, 3):
            Di = determinante_sarrus(Ai)
        else:
            Di = np.linalg.det(Ai)

        determinantes.append(Di)

        # Aplicamos:
        #
        # xi = Di / D

        xi = Di / determinante_A

        soluciones.append(xi)

    return np.array(soluciones), determinantes


# ============================================================
# MÉTODO DE ELIMINACIÓN DE GAUSS
# ============================================================

def resolver_gauss(A, b):
    """
    Resuelve el sistema mediante Eliminación Gaussiana.

    El objetivo es transformar la matriz aumentada en una
    matriz triangular superior.

    Ejemplo:

        [a b c | d]
        [0 e f | g]
        [0 0 h | i]

    Después usamos sustitución hacia atrás.
    """

    # Número de filas / incógnitas.
    n = len(b)

    # Creamos matriz aumentada [A | b].
    matriz = np.column_stack((A.astype(float), b.astype(float)))

    # --------------------------------------------------------
    # FASE 1: ELIMINACIÓN
    # --------------------------------------------------------

    for pivote in range(n):

        # Buscamos el mayor valor disponible en la columna.
        #
        # Esto se llama pivoteo parcial.
        fila_maxima = pivote + np.argmax(
            np.abs(matriz[pivote:, pivote])
        )

        # Intercambiamos filas si es necesario.
        if fila_maxima != pivote:
            matriz[[pivote, fila_maxima]] = matriz[
                [fila_maxima, pivote]
            ]

        # Verificamos que el pivote no sea 0.
        if np.isclose(matriz[pivote, pivote], 0):
            return None, matriz

        # Eliminamos los números debajo del pivote.
        for fila in range(pivote + 1, n):

            factor = (
                matriz[fila, pivote]
                / matriz[pivote, pivote]
            )

            matriz[fila] = (
                matriz[fila]
                - factor * matriz[pivote]
            )

    # --------------------------------------------------------
    # FASE 2: SUSTITUCIÓN HACIA ATRÁS
    # --------------------------------------------------------

    solucion = np.zeros(n)

    for fila in range(n - 1, -1, -1):

        suma = np.dot(
            matriz[fila, fila + 1:n],
            solucion[fila + 1:n]
        )

        solucion[fila] = (
            matriz[fila, -1] - suma
        ) / matriz[fila, fila]

    return solucion, matriz


# ============================================================
# MÉTODO NUMPY
# ============================================================

def resolver_numpy(A, b):
    """
    NumPy incluye un algoritmo especializado para resolver:

        A · x = b

    usando:

        np.linalg.solve(A, b)

    Internamente utiliza métodos numéricos eficientes de
    álgebra lineal.
    """

    return np.linalg.solve(A, b)


# ============================================================
# GRÁFICA PARA SISTEMA 2x2
# ============================================================

def graficar_2x2(A, b, solucion=None):
    """
    Grafica dos ecuaciones lineales de dos variables:

        ax + by = c

    Cada ecuación representa una recta.

    El punto donde se intersectan representa la solución.
    """

    # --------------------------------------------------------
    # DEFINIR ÁREA DE LA GRÁFICA
    # --------------------------------------------------------

    if solucion is not None:

        centro_x = solucion[0]
        centro_y = solucion[1]

        # Ajustamos automáticamente el tamaño de visualización.
        rango = max(
            10,
            abs(centro_x) * 0.5 + 5,
            abs(centro_y) * 0.5 + 5
        )

    else:

        centro_x = 0
        centro_y = 0
        rango = 10

    # Creamos valores para los ejes.
    x = np.linspace(
        centro_x - rango,
        centro_x + rango,
        400
    )

    y = np.linspace(
        centro_y - rango,
        centro_y + rango,
        400
    )

    # Creamos una cuadrícula.
    X, Y = np.meshgrid(x, y)

    # Nueva figura.
    plt.figure(figsize=(8, 6))

    # --------------------------------------------------------
    # GRAFICAR CADA ECUACIÓN
    # --------------------------------------------------------

    for i in range(2):

        a = A[i, 0]
        b_coef = A[i, 1]
        c = b[i]

        # Representamos:
        #
        # ax + by - c = 0

        Z = a * X + b_coef * Y - c

        # contour dibuja los puntos donde:
        #
        # Z = 0
        #
        # Es decir:
        #
        # ax + by = c
        #
        # Esta técnica también funciona con rectas verticales.

        plt.contour(
            X,
            Y,
            Z,
            levels=[0],
            linewidths=2
        )

    # --------------------------------------------------------
    # MOSTRAR SOLUCIÓN
    # --------------------------------------------------------

    if solucion is not None:

        plt.scatter(
            solucion[0],
            solucion[1],
            s=100,
            zorder=5
        )

        plt.annotate(
            f"({solucion[0]:.2f}, {solucion[1]:.2f})",
            (solucion[0], solucion[1]),
            xytext=(10, 10),
            textcoords="offset points"
        )

    # Ejes cartesianos.
    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.xlabel("X")
    plt.ylabel("Y")

    plt.title("Representación gráfica del sistema 2x2")

    plt.grid(True)

    # Convertimos la gráfica a Base64.
    imagen = convertir_grafica_base64()

    return imagen


# ============================================================
# GRÁFICA PARA SISTEMA 3x3
# ============================================================

def graficar_3x3(A, b, solucion=None):
    """
    En un sistema 3x3 cada ecuación representa un plano:

        ax + by + cz = d

    Tres planos pueden intersectarse en un único punto.
    """

    figura = plt.figure(figsize=(9, 7))

    ax = figura.add_subplot(
        111,
        projection="3d"
    )

    # --------------------------------------------------------
    # DEFINIR RANGO
    # --------------------------------------------------------

    if solucion is not None:

        centro = solucion

        rango = max(
            8,
            np.max(np.abs(solucion)) * 0.5 + 5
        )

    else:

        centro = np.array([0, 0, 0])
        rango = 8

    valores = np.linspace(-rango, rango, 25)

    # --------------------------------------------------------
    # GRAFICAR CADA PLANO
    # --------------------------------------------------------

    for i in range(3):

        a = A[i, 0]
        b_coef = A[i, 1]
        c = A[i, 2]

        d = b[i]

        # Elegimos qué variable despejar dependiendo
        # de qué coeficiente sea diferente de cero.

        # ----------------------------------------------------
        # CASO 1: podemos despejar Z
        # ----------------------------------------------------

        if not np.isclose(c, 0):

            X, Y = np.meshgrid(
                valores + centro[0],
                valores + centro[1]
            )

            Z = (
                d
                - a * X
                - b_coef * Y
            ) / c

            ax.plot_surface(
                X,
                Y,
                Z,
                alpha=0.35
            )

        # ----------------------------------------------------
        # CASO 2: despejamos Y
        # ----------------------------------------------------

        elif not np.isclose(b_coef, 0):

            X, Z = np.meshgrid(
                valores + centro[0],
                valores + centro[2]
            )

            Y = (
                d
                - a * X
                - c * Z
            ) / b_coef

            ax.plot_surface(
                X,
                Y,
                Z,
                alpha=0.35
            )

        # ----------------------------------------------------
        # CASO 3: despejamos X
        # ----------------------------------------------------

        elif not np.isclose(a, 0):

            Y, Z = np.meshgrid(
                valores + centro[1],
                valores + centro[2]
            )

            X = (
                d
                - b_coef * Y
                - c * Z
            ) / a

            ax.plot_surface(
                X,
                Y,
                Z,
                alpha=0.35
            )

    # --------------------------------------------------------
    # PUNTO DE INTERSECCIÓN
    # --------------------------------------------------------

    if solucion is not None:

        ax.scatter(
            solucion[0],
            solucion[1],
            solucion[2],
            s=100
        )

        ax.text(
            solucion[0],
            solucion[1],
            solucion[2],
            (
                f"({solucion[0]:.2f}, "
                f"{solucion[1]:.2f}, "
                f"{solucion[2]:.2f})"
            )
        )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_title(
        "Representación gráfica del sistema 3x3"
    )

    imagen = convertir_grafica_base64()

    return imagen


# ============================================================
# CONVERTIR MATPLOTLIB A IMAGEN BASE64
# ============================================================

def convertir_grafica_base64():
    """
    Guarda temporalmente la gráfica en memoria.

    Después la convierte a Base64 para poder enviarla
    directamente al navegador sin guardar archivos .png.
    """

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format="png",
        bbox_inches="tight"
    )

    # Cerramos la gráfica para liberar memoria.
    plt.close()

    # Movemos el cursor al inicio del archivo temporal.
    buffer.seek(0)

    imagen_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return imagen_base64


# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():
    """
    GET:
        Muestra la página.

    POST:
        Recibe los valores escritos por el usuario,
        construye las matrices y resuelve el sistema.
    """

    resultado = None

    grafica = None

    error = None

    # --------------------------------------------------------
    # CUANDO EL USUARIO ENVÍA EL FORMULARIO
    # --------------------------------------------------------

    if request.method == "POST":

        try:

            # Número de incógnitas:
            # 2 para sistema 2x2
            # 3 para sistema 3x3
            dimension = int(
                request.form.get("dimension")
            )

            # Método seleccionado desde HTML.
            metodo = request.form.get(
                "metodo",
                "cramer"
            )

            # ------------------------------------------------
            # CONSTRUIR MATRIZ A
            # ------------------------------------------------

            A = np.zeros(
                (dimension, dimension),
                dtype=float
            )

            # Vector independiente.
            b = np.zeros(
                dimension,
                dtype=float
            )

            # Ejemplo:
            #
            # a11 a12
            # a21 a22
            #
            # o:
            #
            # a11 a12 a13
            # a21 a22 a23
            # a31 a32 a33
    
            for fila in range(dimension):

                for columna in range(dimension):

                    nombre = f"a{fila + 1}{columna + 1}"

                    A[fila, columna]  = leer_valor_con_signo(request.form, nombre)

                nombre_b = f"b{fila + 1}"

                b[fila] =  leer_valor_con_signo(request.form, nombre_b)

            # ------------------------------------------------
            # MATRIZ AUMENTADA
            # ------------------------------------------------

            matriz_aumentada = np.column_stack(
                (A, b)
            )

            # ------------------------------------------------
            # DETERMINANTE
            # ------------------------------------------------

            determinante = np.linalg.det(A)

            # ------------------------------------------------
            # CLASIFICACIÓN
            # ------------------------------------------------

            (
                estado,
                rango_A,
                rango_aumentada
            ) = clasificar_sistema(A, b)

            solucion = None

            detalles_metodo = None

            # ------------------------------------------------
            # SOLUCIÓN ÚNICA
            # ------------------------------------------------

            if estado == "unica":

                # --------------------------------------------
                # CRAMER
                # --------------------------------------------

                if metodo == "cramer":

                    solucion, determinantes = (
                        resolver_cramer(A, b)
                    )

                    detalles_metodo = {
                        "determinante_principal":
                            determinante,

                        "determinantes_variables":
                            determinantes
                    }

                # --------------------------------------------
                # GAUSS
                # --------------------------------------------

                elif metodo == "gauss":

                    solucion, matriz_triangular = (
                        resolver_gauss(A, b)
                    )

                    detalles_metodo = {
                        "matriz_triangular":
                            matriz_triangular.tolist()
                    }

                # --------------------------------------------
                # NUMPY
                # --------------------------------------------

                else:

                    solucion = resolver_numpy(A, b)

                    detalles_metodo = {
                        "algoritmo":
                            "numpy.linalg.solve"
                    }

                # --------------------------------------------
                # GRÁFICA
                # --------------------------------------------

                if dimension == 2:

                    grafica = graficar_2x2(
                        A,
                        b,
                        solucion
                    )

                elif dimension == 3:

                    grafica = graficar_3x3(
                        A,
                        b,
                        solucion
                    )

            # ------------------------------------------------
            # SISTEMA SIN SOLUCIÓN O INFINITO
            # ------------------------------------------------

            else:

                if dimension == 2:

                    grafica = graficar_2x2(
                        A,
                        b
                    )

                elif dimension == 3:

                    grafica = graficar_3x3(
                        A,
                        b
                    )

            # ------------------------------------------------
            # DATOS QUE ENVIAREMOS AL HTML
            # ------------------------------------------------

            resultado = {

                "dimension":
                    dimension,

                "metodo":
                    metodo,

                "matriz_A":
                    A.tolist(),

                "vector_b":
                    b.tolist(),

                "matriz_aumentada":
                    matriz_aumentada.tolist(),

                "determinante":
                    float(determinante),

                "rango_A":
                    int(rango_A),

                "rango_aumentada":
                    int(rango_aumentada),

                "estado":
                    estado,

                "solucion":
                    (
                        solucion.tolist()
                        if solucion is not None
                        else None
                    ),

                "detalles":
                    detalles_metodo
            }

        # ----------------------------------------------------
        # MANEJO DE ERRORES
        # ----------------------------------------------------

        except (ValueError, TypeError):

            error = (
                "Todos los campos deben contener "
                "valores numéricos válidos."
            )

        except np.linalg.LinAlgError:

            error = (
                "No fue posible realizar la operación "
                "de álgebra lineal."
            )

        except Exception as e:

            # Durante desarrollo es útil ver el error.
            print("ERROR:", e)

            error = (
                "Ocurrió un error procesando el sistema."
            )

    # --------------------------------------------------------
    # MOSTRAR HTML
    # --------------------------------------------------------

    return render_template(
        "index.html",
        resultado=resultado,
        grafica=grafica,
        error=error
    )


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
