"""Entrada decimal exacta y límites para el cálculo y la visualización."""

import re
from decimal import Decimal
from fractions import Fraction

PATRON_NUMERO = re.compile(
    r"([+-]?)([0-9]+(?:[.,][0-9]*)?|[.,][0-9]+)(?:[eE]([+-]?[0-9]{1,3}))?"
)
MAXIMO = 10**20
MINIMO = Fraction(1, MAXIMO)
MAX_DIGITOS = 16


class ErrorEntrada(ValueError):
    """Dato de usuario que se puede corregir desde el formulario."""


def leer_numero(formulario, campo, etiqueta):
    valores = formulario.getlist(campo)
    if len(valores) > 1:
        raise ErrorEntrada(f"{etiqueta} se envió más de una vez.")
    texto = valores[0].strip() if valores else ""
    if not texto:
        raise ErrorEntrada(f"Completa el campo {etiqueta}.")
    coincidencia = PATRON_NUMERO.fullmatch(texto) if len(texto) <= 64 else None
    if not coincidencia:
        raise ErrorEntrada(f"{etiqueta} debe ser un número decimal finito.")
    decimal = Decimal(texto.replace(",", "."))
    digitos = "".join(map(str, decimal.as_tuple().digits)).rstrip("0")
    if len(digitos) > MAX_DIGITOS:
        raise ErrorEntrada(
            f"{etiqueta} admite hasta {MAX_DIGITOS} dígitos significativos."
        )
    numero = Fraction(decimal)
    if numero and not MINIMO <= abs(numero) <= MAXIMO:
        raise ErrorEntrada(
            f"{etiqueta} debe ser cero o tener magnitud entre 1e−20 y 1e20."
        )
    return numero


def leer_con_signo(formulario, campo, etiqueta):
    numero = leer_numero(formulario, campo, etiqueta)
    signos = formulario.getlist(f"sign_{campo}")
    if not signos:
        return numero
    if len(signos) != 1 or signos[0] not in ("1", "-1"):
        raise ErrorEntrada(f"Selecciona un signo válido para {etiqueta}.")
    if numero < 0:
        raise ErrorEntrada(
            f"Usa el selector de signo y escribe la magnitud de {etiqueta}."
        )
    return int(signos[0]) * numero
