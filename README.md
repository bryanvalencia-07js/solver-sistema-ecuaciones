# Álgebra Visual

Aplicación web académica para resolver sistemas lineales, desarrollar determinantes y operar con vectores. Cada módulo muestra los cálculos y su interpretación geométrica. El objetivo es que yo como estudiante pueda comprobar un resultado y explicar cómo se obtuvo.

## Instalación en Linux y Windows

Se recomienda Python 3.11 o posterior. Si ya tienes el proyecto en tu equipo, abre una terminal en la carpeta `solver-sistema-ecuaciones`.

```sh
git clone https://github.com/bryanvalencia-07js/solver-sistema-ecuaciones.git
cd solver-sistema-ecuaciones
```

**Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run
```

Abre [http://127.0.0.1:5000](http://127.0.0.1:5000). También puedes iniciar con `python app.py` desde un entorno activado. La depuración está desactivada por defecto.

**Pruebas**

```bash
python -m pip install -r requirements-dev.txt
python -m compileall -q app.py core visualization tests
python -m pytest -q
```

En PowerShell, puedes sustituir `python` por `.\.venv\Scripts\python.exe` en esos tres comandos. El entorno virtual queda fuera de Git.

## Cómo usarlo

- **Sistemas de ecuaciones.** Selecciona 2×2 o 3×3, el método y los signos. Escribe 0 para cualquier coeficiente ausente. Con el ejemplo «Solución única» de 2×2, Gauss obtiene `x = 3, y = 2`. La gráfica marca el cruce de las rectas. El ejemplo 3×3 «Recta solución» muestra una variable libre y una familia de soluciones.
- **Determinantes.** Carga «Regla de Sarrus» para obtener −14 con la matriz del caso E. Las líneas azules recorren las diagonales descendentes y las naranjas las ascendentes.
- **Vectores 2D y 3D.** Carga «Vectores generales». En 2D, `u = (3, 4)` y `v = (1, 2)` dan una suma de `(4, 6)`, una resta de `(2, 2)` y un área de 2. Usa el selector de la gráfica para cambiar la construcción visible.
- **Producto cruz.** Con `u = (1, 2, 3)` y `v = (4, 5, 6)`, el resultado es `(−3, 6, −3)`. Gira la gráfica para observar la dirección perpendicular al paralelogramo.

## Tecnologías y arquitectura

Python implementa los cálculos. NumPy aporta una comprobación independiente para soluciones únicas. Flask recibe los formularios y Jinja genera el HTML. Plotly dibuja las gráficas, que se sirven localmente con JavaScript y CSS.

| Capa | Archivos | Responsabilidad |
| --- | --- | --- |
| Lógica matemática | `core/` | Entrada decimal, eliminación explícita, determinantes y operaciones vectoriales |
| Visualización | `visualization/` | Convierte resultados en puntos, rectas, planos, flechas y superficies de Plotly |
| Interfaz | `app.py`, `templates/`, `static/` | Atiende rutas, conserva los valores, muestra resultados y activa las interacciones |

```text
solver-sistema-ecuaciones/
├── app.py
├── core/
│   ├── determinantes.py
│   ├── sistemas.py
│   ├── validaciones.py
│   └── vectores.py
├── visualization/
│   ├── base.py
│   ├── sistemas.py
│   └── vectores.py
├── templates/
│   ├── base.html, componentes.html, index.html
│   ├── sistemas.html, sarrus.html, vectores.html
│   └── resultado_sistema.html, resultado_vectores.html, resultado_cruz.html
├── static/
│   ├── style.css
│   └── js/main.js
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── SUSTENTACION.md
```

## Algoritmos

- **Gauss.** Recorre las columnas, usa el mayor pivote absoluto disponible y aplica intercambios, restas de múltiplos y escalado de filas. Registra cada operación. Cuenta los pivotes de A para obtener su rango. Una fila con coeficientes nulos y término independiente distinto de cero aumenta en uno el rango de la matriz aumentada. En sistemas compatibles, la sustitución regresiva asigna un parámetro a cada variable libre y obtiene expresiones para las demás.
- **Cramer y Sarrus.** Para cada incógnita se reemplaza la columna correspondiente de A por b. Cramer divide el determinante auxiliar por D cuando D es distinto de cero. El mismo cálculo por diagonales se usa en Cramer 3×3 y en el módulo de Sarrus. En 2×2 se usa `ad − bc`. Cuando D vale cero, Gauss determina la clasificación.
- **Vectores.** Las operaciones por componente, el producto punto y el producto cruz se desarrollan con números racionales. Las normas y las áreas 3D se calculan a partir de sus cuadrados exactos. El ángulo usa `atan2(área, u · v)`, que distingue 0°, 90° y 180° sin dividir por las normas.
- **Precisión.** El formulario transforma los decimales en `Fraction`. El rango y la nulidad de un pivote se determinan por igualdad exacta. NumPy se usa en punto flotante y su solución se compara con la exacta con error relativo máximo de 10⁻⁹, usando la mayor magnitud de las componentes como escala.

## Cumplimiento RF1–RF6

| Requisito | Implementación | Verificación |
| --- | --- | --- |
| RF1 | Gauss 2×2, clasificación, parámetros, comprobación y gráfica de rectas | Sistemas únicos, incompatibles y coincidentes. Pivote inicial nulo y matrices por operación |
| RF2 | Gauss 3×3 con pivoteo, incompatibilidades, sustitución, NumPy, punto, recta y plano solución | Casos C/D y familias singulares. Rotación y zoom en Chromium |
| RF3 | Suma, resta, escala, normas, producto punto, ángulo y área en 2D | Caso F, vectores nulos, paralelos y construcciones del paralelogramo |
| RF4 | Operaciones vectoriales en 3D con figuras interactivas | Suma, resta, escalar negativo, perpendicularidad y cambio de construcción |
| RF5 | Cofactores, áreas, perpendicularidad y regla de la mano derecha | Casos G/H, vector nulo y flecha perpendicular en la gráfica |
| RF6 | Validación en JavaScript y Flask, errores por campo y detección de ecuaciones degeneradas | Campos vacíos, duplicados, decimales, NaN, infinito, magnitud, signos, dimensión y método |

## Resultados de regresión

| Caso | Resultado verificado |
| --- | --- |
| A | `(3, 2)` |
| B | Incompatible |
| C | `(2, 1, 3)`. `D = −14, Dx = −28, Dy = −14, Dz = −42` |
| D | `(−4, 6, 1)`. `D = −1, Dx = 4, Dy = −6, Dz = −1`. Las ecuaciones devuelven 1, 2 y 1 |
| E | Determinante de Sarrus `−14` |
| F | Suma `(4, 6)`, resta `(2, 2)`, norma de u `5`, producto punto `11`, área `2` |
| G | Producto cruz `(−3, 6, −3)`, perpendicular a u y v |
| H | Producto cruz `(0, 0, 0)`, área cero |

Los enunciados originales del taller no aparecieron en el repositorio, su historial ni el archivo entregado. CP1–CP5 se verificaron con **pruebas sustitutas**, pendientes de contrastar con los enunciados originales.

| Caso del profesor | Prueba sustituta aprobada |
| --- | --- |
| CP1 · Ejercicios 1 y 3 | A y B, sistemas 2×2 único e incompatible |
| CP2 · Ejercicios 5 y 7 | C y un sistema 3×3 de rango 2 con solución `(3 − 2t, t, t)` |
| CP3 · Ejercicio 8 | Un 3×3 incompatible cuya eliminación produce `[0, 0, 0 \| −1]` |
| CP4 · Ejercicios 10 y 13 | F en 2D y `u = (1, 2, 3), v = (4, 5, 6)` en 3D |
| CP5 · Ejercicios 15 y 18 | G y H, producto cruz general y de vectores paralelos |

## Límites de la aplicación

- Trabaja con sistemas cuadrados 2×2 y 3×3 y vectores de 2 o 3 componentes. Acepta coma o punto decimal y notación científica. Admite cero y valores con magnitud de 10⁻²⁰ a 10²⁰, con hasta 16 dígitos significativos y hasta 64 caracteres por campo.
- Las gráficas, las normas irracionales y el contraste con NumPy se aproximan en punto flotante. Al combinar magnitudes muy distintas, la resolución visual puede ocultar detalles que sí se distinguen en el cálculo exacto.
- Las figuras requieren JavaScript, y las 3D requieren WebGL. Los formularios y el procedimiento textual siguen disponibles si se desactiva JavaScript. Las figuras de rectas y planos muestran una región finita del conjunto geométrico.
