"""Controladores Flask del laboratorio de álgebra lineal."""

import json
from fractions import Fraction
from pathlib import Path

import plotly
from flask import Flask, render_template, request, send_file

from core.determinantes import detalle_determinante
from core.sistemas import resolver_sistema
from core.validaciones import ErrorEntrada, leer_con_signo, leer_numero
from core.vectores import operar_vectores, producto_cruz
from visualization.sistemas import graficar_sistema
from visualization.vectores import graficar_cruz, graficar_vectores

app = Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=16 * 1024, MAX_FORM_MEMORY_SIZE=16 * 1024)

MODULOS = {
    "sistemas": (
        "Sistemas de ecuaciones",
        "Ax = b",
        "Resuelve sistemas 2×2 y 3×3.",
    ),
    "sarrus": (
        "Determinantes",
        "det A",
        "Desarrolla un determinante 3×3 por Sarrus.",
    ),
    "vectores_2d": ("Vectores 2D", "ℝ²", "Opera con vectores en el plano."),
    "vectores_3d": ("Vectores 3D", "ℝ³", "Opera con vectores en el espacio."),
    "cruz": (
        "Producto cruz",
        "u × v",
        "Calcula el vector perpendicular a u y v.",
    ),
}
METODOS = {
    "gauss": "Eliminación de Gauss",
    "cramer": "Regla de Cramer",
    "numpy": "NumPy Solve",
}
PLOTLY_JS = Path(plotly.__file__).parent / "package_data" / "plotly.min.js"

EJEMPLOS_SISTEMAS = {
    2: {
        "Solución única": [[1, 1, 5], [1, -1, 1]],
        "Rectas paralelas": [[1, 1, 2], [1, 1, 3]],
        "Rectas coincidentes": [[1, -2, 3], [2, -4, 6]],
    },
    3: {
        "Solución única": [[2, 1, -1, 2], [1, -2, 3, 9], [3, 1, 2, 13]],
        "Recta solución": [[1, 1, 1, 3], [2, 2, 2, 6], [0, 1, -1, 0]],
        "Plano solución": [[1, 1, 1, 3], [2, 2, 2, 6], [0, 0, 0, 0]],
        "Sistema incompatible": [[1, 1, 0, 2], [2, 2, 0, 5], [0, 0, 1, 1]],
        "Regresión de Cramer": [[3, 2, 1, 1], [5, 3, 4, 2], [1, 1, -1, 1]],
    },
}


@app.template_filter("numero")
def numero(valor):
    if isinstance(valor, Fraction) and valor.denominator == 1:
        return str(valor.numerator)
    if isinstance(valor, float):
        return f"{valor:.9g}"
    return str(valor)


@app.template_filter("afin")
def afin(expresion):
    partes = [numero(expresion[0])] if expresion[0] else []
    for indice, coeficiente in enumerate(expresion[1:], start=1):
        if coeficiente:
            magnitud = abs(coeficiente)
            termino = (
                f"t{indice}"
                if magnitud == 1
                else f"{numero(magnitud)}·t{indice}"
            )
            if partes:
                partes.append((" − " if coeficiente < 0 else " + ") + termino)
            else:
                partes.append(("−" if coeficiente < 0 else "") + termino)
    return "".join(partes) or "0"


@app.context_processor
def navegacion():
    return {"modulos": MODULOS, "variables": "xyz"}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template(
            "index.html", modulo="inicio", titulo="Solucionador visual"
        )
    # Conserva los envíos de formularios del punto de entrada original.
    operacion = request.form.get("operacion", "sistema")
    if operacion == "sistema":
        return sistemas()
    if operacion == "sarrus":
        return sarrus()
    return render_template(
        "index.html",
        modulo="inicio",
        titulo="Solucionador visual",
        error="Selecciona una operación conocida.",
    ), 400


@app.route("/sistemas", methods=["GET", "POST"])
def sistemas():
    formulario = request.form
    dimension_texto = (
        formulario.get("dimension", request.args.get("dimension", "2"))
        if request.method == "POST"
        else request.args.get("dimension", "2")
    )
    dimension_valida = dimension_texto in ("2", "3")
    dimension = int(dimension_texto) if dimension_valida else 2
    metodo = formulario.get("metodo", "gauss")
    resultado = grafica = error = None
    try:
        if not dimension_valida:
            raise ErrorEntrada("Selecciona un sistema de dimensión 2×2 o 3×3.")
        if request.method == "POST":
            if metodo not in METODOS:
                raise ErrorEntrada(
                    "Selecciona un método de resolución conocido."
                )
            a = [
                [
                    leer_con_signo(
                        formulario,
                        f"a{i}{j}",
                        f"F{i}, coeficiente de {variable}",
                    )
                    for j, variable in enumerate("xyz"[:dimension], start=1)
                ]
                for i in range(1, dimension + 1)
            ]
            b = [
                leer_con_signo(
                    formulario, f"b{i}", f"F{i}, término independiente"
                )
                for i in range(1, dimension + 1)
            ]
            resultado = resolver_sistema(a, b, metodo)
            grafica = json.loads(graficar_sistema(resultado).to_json())
    except ErrorEntrada as exc:
        error = str(exc)

    ejemplos = {}
    for nombre, filas in EJEMPLOS_SISTEMAS[dimension].items():
        ejemplos[nombre] = {
            (f"a{i}{j}" if j <= dimension else f"b{i}"): valor
            for i, fila in enumerate(filas, start=1)
            for j, valor in enumerate(fila, start=1)
        }
    return render_template(
        "sistemas.html",
        modulo="sistemas",
        titulo=MODULOS["sistemas"][0],
        dimension=dimension,
        metodo=metodo,
        metodos=METODOS,
        ejemplos=ejemplos,
        resultado=resultado,
        grafica=grafica,
        error=error,
    ), 400 if error else 200


@app.route("/determinantes", methods=["GET", "POST"])
def sarrus():
    resultado = error = None
    if request.method == "POST":
        try:
            matriz = [
                [
                    leer_numero(
                        request.form, f"s{i}{j}", f"fila {i}, columna {j}"
                    )
                    for j in range(1, 4)
                ]
                for i in range(1, 4)
            ]
            resultado = detalle_determinante(matriz)
        except ErrorEntrada as exc:
            error = str(exc)
    ejemplo = {
        f"s{i}{j}": valor
        for i, fila in enumerate(
            EJEMPLOS_SISTEMAS[3]["Solución única"], start=1
        )
        for j, valor in enumerate(fila[:3], start=1)
    }
    return render_template(
        "sarrus.html",
        modulo="sarrus",
        titulo=MODULOS["sarrus"][0],
        resultado=resultado,
        error=error,
        ejemplos={"Regla de Sarrus": ejemplo},
    ), 400 if error else 200


@app.route("/vectores/2d", methods=["GET", "POST"])
def vectores_2d():
    return pagina_vectores("vectores_2d", 2)


@app.route("/vectores/3d", methods=["GET", "POST"])
def vectores_3d():
    return pagina_vectores("vectores_3d", 3)


@app.route("/producto-cruz", methods=["GET", "POST"])
def cruz():
    return pagina_vectores("cruz", 3)


def pagina_vectores(modulo, dimension):
    es_cruz = modulo == "cruz"
    resultado = grafica = error = None
    if request.method == "POST":
        try:
            u, v = [
                [
                    leer_numero(
                        request.form, f"{nombre}{eje}", f"{nombre}{eje}"
                    )
                    for eje in "xyz"[:dimension]
                ]
                for nombre in "uv"
            ]
            if es_cruz:
                resultado = producto_cruz(u, v)
                grafica = json.loads(graficar_cruz(resultado).to_json())
            else:
                k = leer_numero(request.form, "k", "escalar k")
                resultado = operar_vectores(u, v, k)
                grafica = json.loads(graficar_vectores(resultado).to_json())
        except ErrorEntrada as exc:
            error = str(exc)

    ejemplos = {
        "Vectores generales": [3, 4, 1, 2]
        if dimension == 2
        else [1, 2, 3, 4, 5, 6],
        "Paralelos": [1, 2, 2, 4] if dimension == 2 else [1, 2, 3, 2, 4, 6],
        "Perpendiculares": [1, 0, 0, 2]
        if dimension == 2
        else [1, 0, 0, 0, 2, 0],
        "Vector nulo": [0] * dimension + [1] * dimension,
    }
    campos = [f"{nombre}{eje}" for nombre in "uv" for eje in "xyz"[:dimension]]
    datos = {
        nombre: dict(zip(campos, valores))
        for nombre, valores in ejemplos.items()
    }
    if not es_cruz:
        for valores in datos.values():
            valores["k"] = -2
    return render_template(
        "vectores.html",
        modulo=modulo,
        titulo=MODULOS[modulo][0],
        dimension=dimension,
        es_cruz=es_cruz,
        ejemplos=datos,
        resultado=resultado,
        grafica=grafica,
        error=error,
    ), 400 if error else 200


@app.get("/plotly.min.js")
def plotly_js():
    """Sirve Plotly desde la dependencia instalada, sin acceso a una CDN."""
    return send_file(PLOTLY_JS, max_age=3600)


if __name__ == "__main__":
    app.run()
