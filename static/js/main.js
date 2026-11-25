"use strict";

const decimal = /^([+-]?)([0-9]+(?:[.,][0-9]*)?|[.,][0-9]+)(?:[eE]([+-]?[0-9]{1,3}))?$/;

function validarNumero(campo) {
    const texto = campo.value.trim();
    const coincidencia = texto.match(decimal);
    let error = "";

    if (texto && !coincidencia) {
        error = "Escribe un número decimal finito.";
    } else if (coincidencia) {
        const valor = Number(texto.replace(",", "."));
        const digitos = coincidencia[2].replace(/[.,]/g, "").replace(/^0+|0+$/g, "");
        if (digitos.length > 16) {
            error = "Escribe hasta 16 dígitos significativos.";
        } else if (digitos && (!Number.isFinite(valor) || Math.abs(valor) < 1e-20 || Math.abs(valor) > 1e20)) {
            error = "Escribe cero o una magnitud entre 1e−20 y 1e20.";
        } else if (campo.hasAttribute("data-magnitud") && valor < 0) {
            error = "Elige el signo en el selector y escribe una magnitud positiva o cero.";
        }
    }
    campo.setCustomValidity(error);
}

document.querySelectorAll("form").forEach((formulario) => {
    formulario.querySelectorAll("[data-numero]").forEach((campo) => {
        campo.addEventListener("input", () => validarNumero(campo));
        validarNumero(campo);
    });

    const selector = formulario.querySelector("[data-ejemplos]");
    if (!selector) return;
    selector.parentElement.hidden = false;
    const datos = JSON.parse(formulario.querySelector("[data-datos-ejemplos]").textContent);

    selector.addEventListener("change", () => {
        if (!selector.value) return;
        for (const [nombre, valor] of Object.entries(datos[selector.value])) {
            const campo = formulario.elements.namedItem(nombre);
            const signo = formulario.elements.namedItem(`sign_${nombre}`);
            if (signo) signo.value = valor < 0 ? "-1" : "1";
            campo.value = signo ? Math.abs(valor) : valor;
            validarNumero(campo);
        }
        selector.value = "";
    });
});

const contenedor = document.querySelector("[data-grafica]");
if (contenedor) {
    const mostrarError = () => {
        contenedor.textContent = "La gráfica interactiva no está disponible en este navegador.";
        contenedor.classList.add("alert");
        contenedor.setAttribute("role", "status");
    };
    if (window.Plotly) {
        const datos = JSON.parse(document.querySelector("[data-datos-grafica]").textContent);
        if (datos.layout.scene) {
            const canvas = document.createElement("canvas");
            const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
            if (gl) gl.getExtension("WEBGL_lose_context")?.loseContext();
            else mostrarError();
        }
        if (!contenedor.classList.contains("alert")) {
            window.Plotly.newPlot(contenedor, datos.data, datos.layout, {
                responsive: true, displaylogo: false, scrollZoom: Boolean(datos.layout.scene), locale: "es",
            }).catch((error) => {
                mostrarError();
                console.error(error);
            });
        }
    } else {
        mostrarError();
    }
}
