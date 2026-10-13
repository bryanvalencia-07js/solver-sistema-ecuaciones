# Resolución de Sistemas de Ecuaciones Lineales

Aplicación web desarrollada con **Python, Flask, HTML, CSS y Matplotlib** que permite resolver sistemas de ecuaciones lineales de 2x2 y 3x3 utilizando la **Regla de Cramer**.

El proyecto combina programación, álgebra lineal y desarrollo web para ofrecer una herramienta educativa que facilita la resolución de ecuaciones y la comprensión de sus resultados.

## Tecnologías utilizadas

- **Python:** lenguaje principal para realizar los cálculos matemáticos.
- **Flask:** framework que permite conectar Python con la interfaz web.
- **NumPy:** biblioteca para operaciones con matrices y determinantes.
- **Matplotlib:** biblioteca para la representación gráfica.
- **HTML5:** estructura de la interfaz.
- **CSS3:** diseño y presentación visual.

## Funcionalidades

- Resolución de sistemas de ecuaciones lineales 2x2.
- Resolución de sistemas de ecuaciones lineales 3x3.
- Aplicación de la Regla de Cramer.
- Cálculo de determinantes.
- Introducción de coeficientes y términos independientes.
- Selección de signos positivos y negativos.
- Visualización de resultados matemáticos.
- Representación gráfica mediante Matplotlib.
- Interfaz web para interactuar con la aplicación.

## Fundamento matemático

La Regla de Cramer permite resolver sistemas de ecuaciones lineales utilizando determinantes, siempre que el determinante de la matriz de coeficientes sea diferente de cero.

Para un sistema 2x2:

```text
ax + by = e
cx + dy = f
```

El determinante principal es:

```text
D = ad - bc
```

Los valores de las incógnitas se calculan mediante:

```text
x = Dx / D
y = Dy / D
```

Para sistemas 3x3 se utiliza el mismo principio, trabajando con matrices de tres filas y tres columnas.

## Estructura del proyecto

```text
proyecto/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   └── index.html
│
└── static/
    └── style.css
```

### Descripción de los archivos

**app.py:** contiene la aplicación Flask, las rutas HTTP y la lógica matemática para resolver los sistemas.

**index.html:** contiene la estructura de la interfaz web y los formularios donde el usuario introduce los valores de las ecuaciones.

**style.css:** define los estilos visuales, la distribución de los elementos y la presentación de los resultados.

**requirements.txt:** registra las dependencias necesarias para ejecutar el proyecto.

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/bryanvalencia-07js/solver-sistema-ecuaciones
cd solver-sistema-ecuaciones
```

### 2. Crear un entorno virtual

```bash
python3 -m venv .venv
```

### 3. Activar el entorno virtual

En Linux:

```bash
source .venv/bin/activate
```

En Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar las dependencias

```bash
python3 -m pip install flask numpy matplotlib
```

También puedes utilizar el archivo `requirements.txt`, si está configurado:

```bash
python3 -m pip install -r requirements.txt
```

### 5. Ejecutar la aplicación

```bash
python3 app.py
```

### 6. Abrir la aplicación

Desde el navegador, ingresar a:

```text
http://127.0.0.1:5000
```

## Ejemplo de funcionamiento

Sistema de ecuaciones 2x2:

```text
2x + 3y = 13
4x - y = 5
```

Resultado:

```text
x = 2
y = 3
```

Comprobación:

```text
2(2) + 3(3) = 13
4(2) - 3 = 5
```

## Objetivo académico

Este proyecto fue desarrollado con fines educativos para aplicar conocimientos de:

- Álgebra lineal.
- Programación en Python.
- Desarrollo web con Flask.
- Operaciones con matrices.
- Integración de frontend y backend.
- Representación gráfica de datos matemáticos.

## Posibles mejoras futuras

- Incorporar otros métodos de resolución, como Gauss y Gauss-Jordan.
- Mostrar el procedimiento matemático paso a paso.
- Permitir sistemas de mayor dimensión.
- Añadir validaciones matemáticas más avanzadas.
- Exportar los resultados a PDF.
- Incorporar nuevas visualizaciones interactivas.

## Estado del proyecto

Versión inicial funcional, desarrollada con fines académicos y de aprendizaje.

## Licencia

Proyecto educativo. La licencia de distribución está pendiente de definir.
