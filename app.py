# ============================================================
# RESOLVEDOR DE SISTEMAS DE ECUACIONES LINEALES
# Sistemas 2x2, 3x3 y determinantes 3x3 por Sarrus
#
# Backend: Flask
# Matemáticas: NumPy
# Gráficas: Matplotlib
# ============================================================

from flask import Flask, render_template, request

import numpy as np

import matplotlib

# Permite utilizar Matplotlib desde Flask sin abrir
# una ventana gráfica del sistema operativo.
matplotlib.use("Agg")

import matplotlib.pyplot as plt

import io
import base64


# ============================================================
# CREACIÓN DE LA APLICACIÓN
# ============================================================

app = Flask(__name__)


# ============================================================
# LEER COEFICIENTE CON SIGNO
# ============================================================

def leer_valor_con_signo(formulario, nombre_campo):
    """
    Recibe por separado:

        signo
        magnitud

    Ejemplo:

        sign_a11 = -1
        a11 = 3

    Resultado:

        -3
    """

    signo = int(
        formulario.get(
            f"sign_{nombre_campo}",
            "1"
        )
    )

    magnitud = float(
        formulario.get(
            nombre_campo,
            0
        )
    )

    return signo * magnitud


# ============================================================
# CLASIFICAR SISTEMA
# ============================================================

def clasificar_sistema(A, b):
    """
    Clasifica el sistema utilizando los rangos de:

        A
        [A | b]

    Posibilidades:

    1. Solución única.
    2. Infinitas soluciones.
    3. Sin solución.
    """

    numero_incognitas = A.shape[1]

    matriz_aumentada = np.column_stack(
        (A, b)
    )

    rango_A = np.linalg.matrix_rank(A)

    rango_aumentada = np.linalg.matrix_rank(
        matriz_aumentada
    )

    # Solución única
    if (
        rango_A
        == rango_aumentada
        == numero_incognitas
    ):

        estado = "unica"

    # Infinitas soluciones
    elif (
        rango_A
        == rango_aumentada
        < numero_incognitas
    ):

        estado = "infinitas"

    # Sistema incompatible
    else:

        estado = "sin_solucion"

    return (
        estado,
        rango_A,
        rango_aumentada
    )


# ============================================================
# REGLA DE SARRUS
# ============================================================

def determinante_sarrus(matriz):
    """
    Calcula el determinante de una matriz 3x3
    mediante la Regla de Sarrus.

    Matriz:

        | a  b  c |
        | d  e  f |
        | g  h  i |

    D =
        aei + bfg + cdh
        - ceg - bdi - afh
    """

    if matriz.shape != (3, 3):

        raise ValueError(
            "La regla de Sarrus solo funciona "
            "con matrices 3x3."
        )

    # Primera fila
    a = matriz[0, 0]
    b = matriz[0, 1]
    c = matriz[0, 2]

    # Segunda fila
    d = matriz[1, 0]
    e = matriz[1, 1]
    f = matriz[1, 2]

    # Tercera fila
    g = matriz[2, 0]
    h = matriz[2, 1]
    i = matriz[2, 2]

    # Diagonales descendentes
    positivas = (
        a * e * i
        + b * f * g
        + c * d * h
    )

    # Diagonales ascendentes
    negativas = (
        c * e * g
        + b * d * i
        + a * f * h
    )

    determinante = (
        positivas
        - negativas
    )

    return determinante

def procedimiento_sarrus(matriz):
    """
    Gener los detalles paso a paso de la Regla de sarris.

    No sustituye a determinante_sarrus().
    Esta función existe para explicar visualmente
    Cómo se obtuvo el determinante
    """
    if matriz.shape != (3, 3):
        raise ValueError(
            "La regla de Sarrus solo funciona con matrices 3x3."
        )

    #-----------------------------------------------
    # EXTRAER ELEMENTOS
    #-----------------------------------------------
    a = matriz[0, 0]
    b = matriz[0, 1]
    c = matriz[0, 2]

    d = matriz[1, 0]
    e = matriz[1, 1]
    f = matriz[1, 2]

    g = matriz[2, 0]
    h = matriz[2, 1]
    i = matriz[2, 2]

    #-----------------------------------------------
    # DIAGONALES POSITIVAS
    #-----------------------------------------------

    positiva_1 = a * e * i
    positiva_2 = b * f * g
    positiva_3 = c * d * h

    suma_posoitivas = (
        positiva_1
        + positiva_2
        + positiva_3
    )

    #-----------------------------------------------
    # DIAGONALES NEGATIVAS
    #-----------------------------------------------

    negativa_1 = c * e * g
    negativa_2 = b * d * i
    negativa_3 = a * f * h

    suma_negativas = (
        negativa_1
        + negativa_2
        + negativa_3
    )

    #-----------------------------------------------
    # DETERMINANTE
    #-----------------------------------------------
    determinante = (
        suma_posoitivas
        - suma_negativas
    )

    return {
        "positivas": [
            {
                "factores": [a, e, i],
                "resultado": positiva_1
            },
            {
                "factores": [b, f, g],
                "resultado": positiva_2
            },
            {
                "factores": [c, d, h],
                "resultado": positiva_3
            }
        ],

        "negativas": [
            {
                "factores": [c, e, g],
                "resultado": negativa_1
            },
            {
                "factores": [b, d, i],
                "resultado": negativa_2
            },
            {
                "factores": [a, f, h],
                "resultado": negativa_3
            }
        ],

        "suma_positivas": float(suma_posoitivas),

        "suma_negativas": float(suma_negativas),

        "determinante": float(determinante)
    }

# ============================================================
# REGLA DE CRAMER
# ============================================================

def resolver_cramer(A, b):
    """
    Resuelve sistemas 2x2 y 3x3 mediante Cramer.

    Para matrices 3x3 los determinantes son
    calculados mediante nuestra implementación
    de Sarrus.
    """

    # --------------------------------------------------------
    # DETERMINANTE PRINCIPAL
    # --------------------------------------------------------

    if A.shape == (3, 3):

        metodo_determinante = (
            "Regla de Sarrus"
        )

        determinante_A = (
            determinante_sarrus(A)
        )

    else:

        metodo_determinante = (
            "Determinante 2x2"
        )

        determinante_A = (
            np.linalg.det(A)
        )

    # Cramer requiere D != 0.
    if np.isclose(
        determinante_A,
        0
    ):

        return None, None


    soluciones = []

    variables = [
        "x",
        "y",
        "z"
    ]


    # Información que enviaremos al HTML.
    detalles = {

        "metodo_determinante":
            metodo_determinante,

        "matriz_principal":
            A.tolist(),

        "determinante_principal":
            float(determinante_A),

        "matrices_variables":
            []
    }


    # --------------------------------------------------------
    # Dx, Dy, Dz
    # --------------------------------------------------------

    for columna in range(
        A.shape[1]
    ):

        # Copiamos la matriz original.
        Ai = A.copy()

        # Sustituimos una columna por b.
        Ai[:, columna] = b


        # Calculamos Di.
        if Ai.shape == (3, 3):

            Di = determinante_sarrus(
                Ai
            )

        else:

            Di = np.linalg.det(
                Ai
            )


        # Aplicamos Cramer:
        #
        # xi = Di / D

        xi = (
            Di
            / determinante_A
        )

        soluciones.append(
            xi
        )


        detalles[
            "matrices_variables"
        ].append({

            "variable":
                variables[columna],

            "nombre":
                f"D{variables[columna]}",

            "matriz":
                Ai.tolist(),

            "determinante":
                float(Di),

            "solucion":
                float(xi)
        })


    return (
        np.array(soluciones),
        detalles
    )


# ============================================================
# ELIMINACIÓN DE GAUSS
# ============================================================

def resolver_gauss(A, b):
    """
    Resuelve el sistema mediante eliminación
    Gaussiana con pivoteo parcial.
    """

    n = len(b)

    # Matriz aumentada [A | b]
    matriz = np.column_stack(
        (
            A.astype(float),
            b.astype(float)
        )
    )


    # --------------------------------------------------------
    # ELIMINACIÓN HACIA ADELANTE
    # --------------------------------------------------------

    for pivote in range(n):

        # Elegimos como pivote el mayor valor absoluto
        # disponible en la columna.
        fila_maxima = (
            pivote
            + np.argmax(
                np.abs(
                    matriz[
                        pivote:,
                        pivote
                    ]
                )
            )
        )


        # Intercambio de filas.
        if fila_maxima != pivote:

            matriz[
                [pivote, fila_maxima]
            ] = matriz[
                [fila_maxima, pivote]
            ]


        if np.isclose(
            matriz[pivote, pivote],
            0
        ):

            return None, matriz


        # Eliminamos elementos debajo del pivote.
        for fila in range(
            pivote + 1,
            n
        ):

            factor = (
                matriz[fila, pivote]
                / matriz[pivote, pivote]
            )

            matriz[fila] = (
                matriz[fila]
                - factor
                * matriz[pivote]
            )


    # --------------------------------------------------------
    # SUSTITUCIÓN HACIA ATRÁS
    # --------------------------------------------------------

    solucion = np.zeros(n)

    for fila in range(
        n - 1,
        -1,
        -1
    ):

        suma = np.dot(

            matriz[
                fila,
                fila + 1:n
            ],

            solucion[
                fila + 1:n
            ]
        )

        solucion[fila] = (
            matriz[fila, -1]
            - suma
        ) / matriz[
            fila,
            fila
        ]


    return (
        solucion,
        matriz
    )


# ============================================================
# NUMPY SOLVE
# ============================================================

def resolver_numpy(A, b):
    """
    Resuelve:

        A · x = b

    mediante NumPy.
    """

    return np.linalg.solve(
        A,
        b
    )


# ============================================================
# GRÁFICA 2x2
# ============================================================

def graficar_2x2(
    A,
    b,
    solucion=None
):
    """
    Cada ecuación 2x2 representa una recta.

    La intersección de las rectas representa
    la solución del sistema.
    """

    if solucion is not None:

        centro_x = solucion[0]
        centro_y = solucion[1]

        rango = max(
            10,
            abs(centro_x) * 0.5 + 5,
            abs(centro_y) * 0.5 + 5
        )

    else:

        centro_x = 0
        centro_y = 0
        rango = 10


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


    X, Y = np.meshgrid(
        x,
        y
    )


    plt.figure(
        figsize=(8, 6)
    )


    # Dibujamos ambas ecuaciones.
    for fila in range(2):

        a = A[fila, 0]
        b_coef = A[fila, 1]
        c = b[fila]

        # ax + by - c = 0
        Z = (
            a * X
            + b_coef * Y
            - c
        )

        plt.contour(
            X,
            Y,
            Z,
            levels=[0],
            linewidths=2
        )


    # Punto solución
    if solucion is not None:

        plt.scatter(
            solucion[0],
            solucion[1],
            s=100,
            zorder=5
        )

        plt.annotate(

            (
                f"({solucion[0]:.2f}, "
                f"{solucion[1]:.2f})"
            ),

            (
                solucion[0],
                solucion[1]
            ),

            xytext=(10, 10),
            textcoords="offset points"
        )


    plt.axhline(
        0,
        linewidth=0.8
    )

    plt.axvline(
        0,
        linewidth=0.8
    )

    plt.xlabel("X")
    plt.ylabel("Y")

    plt.title(
        "Representación gráfica del sistema 2x2"
    )

    plt.grid(True)


    return convertir_grafica_base64()


# ============================================================
# GRÁFICA 3x3
# ============================================================

def graficar_3x3(
    A,
    b,
    solucion=None
):
    """
    Cada ecuación 3x3 representa un plano.
    """

    figura = plt.figure(
        figsize=(9, 7)
    )

    ax = figura.add_subplot(
        111,
        projection="3d"
    )


    if solucion is not None:

        centro = solucion

        rango = max(
            8,
            np.max(
                np.abs(solucion)
            ) * 0.5 + 5
        )

    else:

        centro = np.array(
            [0, 0, 0]
        )

        rango = 8


    valores = np.linspace(
        -rango,
        rango,
        25
    )


    for fila in range(3):

        a = A[fila, 0]
        b_coef = A[fila, 1]
        c = A[fila, 2]

        d = b[fila]


        # --------------------------------------------
        # DESPEJAR Z
        # --------------------------------------------

        if not np.isclose(
            c,
            0
        ):

            X, Y = np.meshgrid(

                valores
                + centro[0],

                valores
                + centro[1]
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


        # --------------------------------------------
        # DESPEJAR Y
        # --------------------------------------------

        elif not np.isclose(
            b_coef,
            0
        ):

            X, Z = np.meshgrid(

                valores
                + centro[0],

                valores
                + centro[2]
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


        # --------------------------------------------
        # DESPEJAR X
        # --------------------------------------------

        elif not np.isclose(
            a,
            0
        ):

            Y, Z = np.meshgrid(

                valores
                + centro[1],

                valores
                + centro[2]
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


    # Punto de intersección.
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


    return convertir_grafica_base64()


# ============================================================
# CONVERTIR MATPLOTLIB A BASE64
# ============================================================

def convertir_grafica_base64():
    """
    Convierte la gráfica de Matplotlib en una
    cadena Base64 para mostrarla directamente
    dentro del HTML.
    """

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format="png",
        bbox_inches="tight"
    )

    plt.close()

    buffer.seek(0)

    imagen_base64 = (
        base64
        .b64encode(
            buffer.getvalue()
        )
        .decode("utf-8")
    )

    return imagen_base64


# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def index():

    resultado = None

    resultado_sarrus = None

    grafica = None

    error = None

    # Operación por defecto.
    operacion = "sistema"


    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        try:

            operacion = request.form.get(
                "operacion",
                "sistema"
            )


            # =================================================
            # OPERACIÓN 1:
            # DETERMINANTE POR SARRUS
            # =================================================

            if operacion == "sarrus":

                matriz_sarrus = np.array([

                    [
                        float(
                            request.form.get(
                                "s11"
                            )
                        ),

                        float(
                            request.form.get(
                                "s12"
                            )
                        ),

                        float(
                            request.form.get(
                                "s13"
                            )
                        )
                    ],

                    [
                        float(
                            request.form.get(
                                "s21"
                            )
                        ),

                        float(
                            request.form.get(
                                "s22"
                            )
                        ),

                        float(
                            request.form.get(
                                "s23"
                            )
                        )
                    ],

                    [
                        float(
                            request.form.get(
                                "s31"
                            )
                        ),

                        float(
                            request.form.get(
                                "s32"
                            )
                        ),

                        float(
                            request.form.get(
                                "s33"
                            )
                        )
                    ]

                ], dtype=float)


                determinante = (
                    determinante_sarrus(
                        matriz_sarrus
                    )
                )

                procedimiento = (
                    procedimiento_sarrus(
                        matriz_sarrus
                    )
                )


                resultado_sarrus = {

                    "matriz":
                        matriz_sarrus.tolist(),

                    "determinante":
                        float(determinante),

                    "procedimiento":
                        procedimiento
                }


            # =================================================
            # OPERACIÓN 2:
            # SISTEMA DE ECUACIONES
            # =================================================

            elif operacion == "sistema":

                dimension = int(
                    request.form.get(
                        "dimension"
                    )
                )


                if dimension not in (
                    2,
                    3
                ):

                    raise ValueError(
                        "Dimensión no válida."
                    )


                metodo = request.form.get(
                    "metodo",
                    "cramer"
                )


                if metodo not in (
                    "cramer",
                    "gauss",
                    "numpy"
                ):

                    raise ValueError(
                        "Método no válido."
                    )


                # ---------------------------------------------
                # MATRIZ A
                # ---------------------------------------------

                A = np.zeros(
                    (
                        dimension,
                        dimension
                    ),
                    dtype=float
                )


                # ---------------------------------------------
                # VECTOR b
                # ---------------------------------------------

                b = np.zeros(
                    dimension,
                    dtype=float
                )


                # ---------------------------------------------
                # LEER DATOS DEL FORMULARIO
                # ---------------------------------------------

                for fila in range(
                    dimension
                ):

                    for columna in range(
                        dimension
                    ):

                        nombre = (
                            f"a"
                            f"{fila + 1}"
                            f"{columna + 1}"
                        )

                        A[
                            fila,
                            columna
                        ] = (
                            leer_valor_con_signo(
                                request.form,
                                nombre
                            )
                        )


                    nombre_b = (
                        f"b{fila + 1}"
                    )

                    b[fila] = (
                        leer_valor_con_signo(
                            request.form,
                            nombre_b
                        )
                    )


                # ---------------------------------------------
                # MATRIZ AUMENTADA
                # ---------------------------------------------

                matriz_aumentada = (
                    np.column_stack(
                        (A, b)
                    )
                )


                # ---------------------------------------------
                # DETERMINANTE PRINCIPAL
                # ---------------------------------------------

                if dimension == 3:

                    determinante = (
                        determinante_sarrus(
                            A
                        )
                    )

                else:

                    determinante = (
                        np.linalg.det(
                            A
                        )
                    )


                # ---------------------------------------------
                # CLASIFICAR SISTEMA
                # ---------------------------------------------

                (
                    estado,
                    rango_A,
                    rango_aumentada
                ) = clasificar_sistema(
                    A,
                    b
                )


                solucion = None

                detalles_metodo = None


                # =============================================
                # SOLUCIÓN ÚNICA
                # =============================================

                if estado == "unica":


                    # -----------------------------------------
                    # CRAMER
                    # -----------------------------------------

                    if metodo == "cramer":

                        (
                            solucion,
                            detalles_metodo
                        ) = resolver_cramer(
                            A,
                            b
                        )


                    # -----------------------------------------
                    # GAUSS
                    # -----------------------------------------

                    elif metodo == "gauss":

                        (
                            solucion,
                            matriz_triangular
                        ) = resolver_gauss(
                            A,
                            b
                        )

                        detalles_metodo = {

                            "matriz_triangular":
                                matriz_triangular.tolist()
                        }


                    # -----------------------------------------
                    # NUMPY
                    # -----------------------------------------

                    elif metodo == "numpy":

                        solucion = (
                            resolver_numpy(
                                A,
                                b
                            )
                        )

                        detalles_metodo = {

                            "algoritmo":
                                "numpy.linalg.solve"
                        }


                # =============================================
                # GENERAR GRÁFICA
                # =============================================

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


                # ---------------------------------------------
                # RESULTADO PARA EL HTML
                # ---------------------------------------------

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
                        int(
                            rango_aumentada
                        ),

                    "estado":
                        estado,

                    "solucion":
                        (
                            solucion.tolist()
                            if solucion
                            is not None
                            else None
                        ),

                    "detalles":
                        detalles_metodo
                }


        # =====================================================
        # ERRORES
        # =====================================================

        except (ValueError, TypeError):

            error = (
                "Todos los campos deben contener "
                "valores numéricos válidos."
            )


        except np.linalg.LinAlgError:

            error = (
                "No fue posible realizar la "
                "operación de álgebra lineal."
            )


        except Exception as e:

            print(
                "ERROR:",
                e
            )

            error = (
                "Ocurrió un error procesando "
                "la operación."
            )


    # ========================================================
    # HTML
    # ========================================================

    return render_template(

        "index.html",

        resultado=
            resultado,

        resultado_sarrus=
            resultado_sarrus,

        grafica=
            grafica,

        error=
            error,

        operacion=
            operacion
    )


# ============================================================
# EJECUTAR FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )