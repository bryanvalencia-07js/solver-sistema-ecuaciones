import pytest

from app import app
from core.sistemas import resolver_sistema


@pytest.fixture
def cliente():
    with app.test_client() as cliente:
        yield cliente


@pytest.fixture
def resolver():
    def calcular(filas, metodo="gauss"):
        return resolver_sistema(
            [fila[:-1] for fila in filas], [fila[-1] for fila in filas], metodo
        )

    return calcular


@pytest.fixture
def datos_sistema():
    def preparar(filas, metodo="gauss"):
        dimension = len(filas)
        datos = {"dimension": str(dimension), "metodo": metodo}
        for i, fila in enumerate(filas, start=1):
            for j, valor in enumerate(fila, start=1):
                nombre = f"a{i}{j}" if j <= dimension else f"b{i}"
                datos[nombre] = str(valor)
        return datos

    return preparar
