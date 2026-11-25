import json
import re

import pytest
from werkzeug.datastructures import MultiDict

from tests.casos import CASO_C, CASO_D, INCOMPATIBLE_3D, PLANO_3D, RECTA_3D


@pytest.mark.parametrize(
    "ruta,titulo",
    [
        ("/", "Solucionador visual"),
        ("/sistemas", "Sistemas de ecuaciones"),
        ("/sistemas?dimension=3", "Sistemas de ecuaciones"),
        ("/determinantes", "Determinantes"),
        ("/vectores/2d", "Vectores 2D"),
        ("/vectores/3d", "Vectores 3D"),
        ("/producto-cruz", "Producto cruz"),
    ],
)
def test_get_plantilla(cliente, ruta, titulo):
    respuesta = cliente.get(ruta)
    assert respuesta.status_code == 200
    assert f"<title>{titulo} · Álgebra Visual</title>" in respuesta.get_data(
        as_text=True
    )


def test_dimension_renderiza_un_solo_control_por_coeficiente(cliente):
    for n in (2, 3):
        pagina = cliente.get(f"/sistemas?dimension={n}").get_data(as_text=True)
        coeficientes = re.findall(r'name="(a[1-3][1-3]|b[1-3])"', pagina)
        assert len(coeficientes) == len(set(coeficientes)) == n * (n + 1)


@pytest.mark.parametrize(
    "filas, contenido",
    [
        (
            CASO_C,
            ["Dx = -28", "Dy = -14", "Dz = -42", "x = 2", "y = 1", "z = 3"],
        ),
        (CASO_D, ["Dx = 4", "Dy = -6", "Dz = -1", "x = -4", "y = 6", "z = 1"]),
        (
            RECTA_3D,
            ["Infinitas soluciones", "z = t1", "3 − 2·t1", "Recta solución"],
        ),
        (PLANO_3D, ["Infinitas soluciones", "Plano solución", "redundante"]),
        (INCOMPATIBLE_3D, ["Ninguna solución", "D = 0", "0 = -1"]),
    ],
)
def test_sistemas_post(cliente, datos_sistema, filas, contenido):
    respuesta = cliente.post("/sistemas", data=datos_sistema(filas, "cramer"))
    assert respuesta.status_code == 200
    cuerpo = respuesta.get_data(as_text=True)
    for fragmento in contenido:
        assert fragmento in cuerpo
    assert cuerpo.count('class="sarrus-diagrama"') == 4


def test_numpy_y_valores_con_signo(cliente):
    datos = {
        "dimension": "2",
        "metodo": "numpy",
        "a11": "1",
        "a12": "1",
        "b1": "5",
        "a21": "1",
        "a22": "1",
        "b2": "1",
        "sign_a22": "-1",
    }
    r = cliente.post("/", data=datos)
    assert r.status_code == 200
    texto = r.get_data(as_text=True)
    assert "numpy.linalg.solve(A, b)" in texto
    assert '<option value="-1" selected>' in texto


def test_sarrus_post_y_ruta_original(cliente):
    datos = {"operacion": "sarrus"}
    datos.update(
        {
            f"s{i}{j}": valor
            for i, fila in enumerate(CASO_C, 1)
            for j, valor in enumerate(fila[:3], 1)
        }
    )
    respuesta = cliente.post("/", data=datos)
    assert respuesta.status_code == 200
    html = respuesta.get_data(as_text=True)
    assert "det A = -14" in html
    assert html.count("<line ") == 6


@pytest.mark.parametrize(
    "ruta, extra, esperado",
    [
        ("/vectores/2d", {"k": -2}, "Resultado = <strong>(5, 7)</strong>"),
        (
            "/vectores/3d",
            {"k": -2, "uz": 3, "vz": 6},
            "Resultado = <strong>(5, 7, 9)</strong>",
        ),
        ("/producto-cruz", {"uz": 3, "vz": 6}, "u × v = (-3, 6, -3)"),
    ],
)
def test_vectores_post_json_plotly(cliente, ruta, extra, esperado):
    r = cliente.post(ruta, data={"ux": 1, "uy": 2, "vx": 4, "vy": 5, **extra})
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert esperado in html
    figura = json.loads(
        re.search(r"data-datos-grafica>(.*?)</script>", html, re.S)[1]
    )
    assert figura["data"]
    assert (ruta != "/vectores/2d") == ("scene" in figura["layout"])


@pytest.mark.parametrize(
    "valor, mensaje",
    [
        ("", "Completa el campo ux"),
        ("texto", "número decimal finito"),
        ("NaN", "número decimal finito"),
        ("Infinity", "número decimal finito"),
        ("1e999", "magnitud entre"),
        ("0.12345678901234567", "16 dígitos significativos"),
        ("1e-21", "magnitud entre"),
    ],
)
def test_validacion_numerica(cliente, valor, mensaje):
    r = cliente.post(
        "/vectores/2d", data={"ux": valor, "uy": 0, "vx": 0, "vy": 0, "k": 1}
    )
    assert r.status_code == 400
    assert mensaje in r.get_data(as_text=True)


def test_validacion_modo_y_dimension(cliente):
    for ruta, datos, mensaje in [
        ("/", {"operacion": "otra"}, "operación conocida"),
        ("/sistemas", {"dimension": "4"}, "dimensión 2×2 o 3×3"),
        (
            "/sistemas",
            {"dimension": "2", "metodo": "otro"},
            "método de resolución conocido",
        ),
        ("/sistemas", {"a11": "1", "sign_a11": "2"}, "signo válido"),
        ("/sistemas", {"a11": "-1", "sign_a11": "-1"}, "selector de signo"),
        (
            "/sistemas",
            MultiDict([("a11", ""), ("a11", "3")]),
            "se envió más de una vez",
        ),
    ]:
        r = cliente.post(ruta, data=datos)
        assert r.status_code == 400
        assert mensaje in r.get_data(as_text=True)


def test_decimal_coma_negativo_y_vector_nulo(cliente):
    r = cliente.post(
        "/vectores/2d",
        data={"ux": "-1,5", "uy": ".5", "vx": "0", "vy": "0", "k": "-2"},
    )
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "ángulo es indefinido" in html
    assert 'value="-1,5"' in html
    assert "<strong>(3, -1)</strong>" in html


def test_bundle_plotly_local(cliente):
    r = cliente.get("/plotly.min.js")
    assert r.status_code == 200
    assert b"plotly.js" in r.data[:500]
