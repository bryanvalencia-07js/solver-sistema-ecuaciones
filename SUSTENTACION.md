# Guía de sustentación · Álgebra Visual

## Recorrido recomendado para la demostración

1. Abre **Sistemas de ecuaciones**, selecciona 2×2 y carga «Solución única». Explica por qué resolver Ax = b equivale aquí a encontrar el cruce de dos rectas.
2. Pasa a 3×3 y carga «Recta solución». Muestra la variable libre, el parámetro y la recta verde. Carga «Sistema incompatible» para señalar la fila contradictoria y el cambio de rango.
3. Selecciona Cramer y carga «Regresión de Cramer». Abre los desarrollos de D, Dx, Dy y Dz. Comprueba que `(−4, 6, 1)` satisface las tres ecuaciones originales.
4. Abre **Vectores 2D**, calcula y alterna entre suma y resta en la gráfica. Termina con **Producto cruz**, gira la figura y muestra la flecha perpendicular. Compara con el ejemplo «Paralelos».

## Del formulario al resultado

Flask es el servidor web de la aplicación. Una ruta vincula una URL y un método HTTP con una función de Python. Por ejemplo, `GET /sistemas?dimension=3` renderiza el formulario de 3×3. Al pulsar «Resolver sistema», el navegador envía un `POST /sistemas` con los campos con nombre, como `a11`, `sign_a11` y `b1`.

El controlador lee `request.form`, valida el método y la dimensión, transforma cada decimal en una fracción y organiza los datos como matriz A y vector b. Luego llama a la capa matemática y, con el resultado, a la capa de visualización. Si la entrada falla, la página devuelve HTTP 400 y un mensaje asociado al campo.

Jinja construye el HTML desde las plantillas. Sus bucles crean las filas, las matrices y los pasos que realmente devolvió Python. Sus condiciones eligen qué mostrar para cada clasificación. Los valores de `request.form` conservan lo escrito. La plantilla base reúne la navegación, el idioma y los archivos de estilos. JavaScript permite cargar ejemplos, anticipar validaciones y activar Plotly.

La arquitectura tiene tres capas. `core/` resuelve los problemas sin depender de Flask. `visualization/` toma esos resultados y devuelve figuras. `app.py`, `templates/` y `static/` gestionan la interacción con el usuario. Así es posible probar un determinante sin abrir un navegador.

## Eliminación de Gauss y clasificación

Se parte de la matriz aumentada `[A | b]`. Se puede intercambiar el orden de dos ecuaciones, multiplicar una por un escalar distinto de cero o sumar a una fila un múltiplo de otra. Las tres operaciones conservan las soluciones porque son reversibles.

El **pivoteo parcial** busca, en la columna activa, el coeficiente de mayor valor absoluto entre las filas disponibles. Si está en otra fila, las intercambia. Si toda la porción disponible de una columna es cero, pasa a la siguiente columna sin consumir una fila. Si encuentra pivote, elimina los términos debajo y después continúa. Al final divide cada fila pivote por su pivote y registra el cambio. En la aplicación la fracción exacta evita confundir un valor pequeño con cero. En implementaciones de punto flotante, el pivoteo parcial también reduce el riesgo de dividir por números muy pequeños en una misma columna.

En `x + y = 5` y `x − y = 1`, aplicar `F2 ← F2 − F1` da `[0, −2 | −4]`. Escalar F2 por −1/2 da `[0, 1 | 2]`. La última fila da `y = 2`. Sustituir arriba produce `x = (5 − 2)/1 = 3`. Comprobar ambos resultados en las ecuaciones originales da 5 y 1.

El rango de A es la cantidad de columnas con pivote durante la eliminación. El rango de `[A | b]` gana un pivote si queda una fila con todos los coeficientes cero y término independiente distinto de cero. La teoría de Rouché–Capelli da estas tres posibilidades.

| Relación entre rangos | Clasificación | Interpretación |
| --- | --- | --- |
| `r(A) = r([A \| b]) = n` | Compatible determinado | Hay un punto solución |
| `r(A) = r([A \| b]) < n` | Compatible indeterminado | Hay `n − r(A)` parámetros libres |
| `r(A) < r([A \| b])` | Incompatible | Hay una igualdad imposible como `0 = −1` |

Para una familia infinita, se toma cada variable sin pivote como un parámetro real. Por ejemplo, si las ecuaciones independientes son `x + y + z = 3` y `y − z = 0`, se elige `z = t`, luego `y = t` y finalmente `x = 3 − 2t`. El punto particular se obtiene con `t = 0`. El coeficiente vectorial de t, `(−2, 1, 1)`, da la dirección de la recta. Al sustituir en las ecuaciones originales se cancelan todos los términos con t, por lo que la comprobación vale para cualquier parámetro.

## Cramer y Sarrus

Cramer se aplica si `D = det(A) ≠ 0`. Se construye Dx sustituyendo la columna de x por b, Dy con la columna de y, y Dz con la de z en 3×3. Se divide cada determinante auxiliar por D. Si `D = 0`, Gauss distingue un sistema incompatible de uno con infinitas soluciones.

Sarrus solo se aplica a matrices 3×3. Se copian a la derecha las dos primeras columnas. Se multiplican los tres valores de cada diagonal descendente y se suman los tres productos. Se repite con las ascendentes y se resta el segundo subtotal del primero. En el caso E, los productos descendentes son −8, 9 y −1, y los ascendentes suman 14. El determinante es `0 − 14 = −14`. Cramer y el módulo independiente llaman a la misma función para mostrar estas multiplicaciones.

## Vectores y producto cruz

Un vector describe un desplazamiento con componentes, magnitud y, si es distinto de cero, dirección. La suma y la resta operan componente a componente. Geométricamente, la suma es la diagonal del paralelogramo y la resta va desde la punta de v hasta la punta de u con origen común. Multiplicar por k cambia la longitud por `|k|` e invierte el sentido si k es negativo.

La norma euclídea es `√(Σ uᵢ²)`. El producto punto es `Σ uᵢvᵢ` y mide la proyección de un vector sobre el otro, multiplicada por la norma del segundo. Si ambos vectores son no nulos, un producto punto cero indica perpendicularidad. El ángulo se obtiene con `atan2(área, u · v)` porque el área equivale a `‖u‖‖v‖ sin θ` y el producto punto a `‖u‖‖v‖ cos θ`. Con un vector nulo el ángulo queda indefinido.

En 3D, el producto cruz usa los cofactores de la matriz con primera fila i, j, k. Los signos alternan `+, −, +`, así que el menor de j lleva signo negativo. Por ejemplo, para `u = (1, 2, 3)` y `v = (4, 5, 6)`, la componente j es `−(1·6 − 3·4) = 6`. El resultado completo es `(−3, 6, −3)`. Cada producto punto con los vectores originales da cero. La regla de la mano derecha indica el sentido del vector. Su norma es el área del paralelogramo y la mitad de esa norma da el área del triángulo. Para u y v paralelos, el área y el producto cruz se anulan.

## Cómo se construyen las gráficas

Para una ecuación con coeficientes distintos de cero se proyecta un punto de referencia sobre la ecuación. En 2D, si el vector normal es `(a, b)`, la dirección de la recta es `(−b, a)`. En 3D se eligen dos direcciones ortogonales a la normal, con las que se construye una porción del plano. Cada ecuación tiene su color. El punto particular y las direcciones libres permiten añadir el punto, la recta o el plano solución en verde.

Para vectores, cada flecha lleva un segmento desde el origen y una punta. El paralelogramo usa los vértices `0, u, u + v, v`. La resta añade el segmento de la punta de v a la punta de u. Plotly recibe los datos y el estilo como JSON en la página. Dibuja el 3D mediante WebGL y maneja la rotación y el zoom en el navegador.

## Pruebas automatizadas

Ejecuta `python -m pytest -q`. Las pruebas del núcleo comparan soluciones, determinantes, verificaciones, variables libres y operaciones de fila contra valores conocidos. Las pruebas de visualización comprueban que los puntos de las trazas satisfacen las ecuaciones y que aparecen las construcciones requeridas. El cliente de pruebas de Flask envía formularios sin levantar un servidor y permite comprobar códigos HTTP, HTML y datos de Plotly. Al probar en Chromium con Flask en ejecución se comprueba también la parte que requiere JavaScript, como rotar una gráfica 3D.

## Preguntas que puede hacer el profesor

| Pregunta | Respuesta |
| --- | --- |
| ¿Por qué no usaste solo NumPy? | Gauss registra cada operación para poder explicarla. NumPy comprueba la aproximación de las soluciones únicas y está disponible como método. |
| ¿Qué significa que el determinante sea cero? | A es singular. El sistema puede tener cero o infinitas soluciones, según el rango de la ampliada. |
| ¿Cómo detectas una fila incompatible? | Los coeficientes son todos cero y el término independiente es distinto de cero. Esa ecuación no puede cumplirse. |
| ¿Qué significa una ecuación `0 = 0`? | Es redundante y no restringe el conjunto solución. |
| ¿Por qué puedes escalar una fila? | Multiplicar una igualdad por un número no nulo es reversible. |
| ¿Cómo verificas una familia de soluciones? | Sustituyes cada expresión en las ecuaciones originales y compruebas que desaparece la dependencia de todos los parámetros. |
| ¿Por qué el ángulo con el vector cero es indefinido? | El vector cero no determina una dirección. En la fórmula aparecen área y producto punto iguales a cero. |
| ¿Qué cambia al calcular v × u? | Se invierte el signo del vector y el área conserva su magnitud. |
| ¿Qué causaba el error de Cramer 3×3? | Con JavaScript desactivado se enviaban las dos matrices juntas. Flask tomaba el primer campo repetido, que estaba vacío, y la conversión a número fallaba. Cada dimensión ahora tiene un solo conjunto de campos. |
| ¿Qué valores son aproximados? | Las normas irracionales, los ángulos, la comparación con NumPy y las coordenadas de la gráfica. Los rangos, las soluciones y los determinantes de los decimales admitidos se calculan exactamente. |
