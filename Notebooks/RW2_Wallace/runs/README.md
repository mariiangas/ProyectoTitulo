# Historial de corridas RW2

Abrir [indice.md](indice.md) para comparar corridas y acceder a sus fichas.
El índice muestra los parámetros que cambiaron respecto de la corrida anterior,
con el valor anterior y el nuevo. La comparación sigue el número de corrida y
usa las entradas guardadas en `parametros.json`. Cuando faltan registros, indica
que la comparación es parcial o que no está disponible.

## Uso desde el notebook

1. Editar entradas y el bloque **CONFIGURACIÓN DE CORRIDAS Y MEDICIONES LOCALES**.
2. Construir el modelo como antes.
3. Ejecutar **CREAR CORRIDA Y CONGELAR PARÁMETROS**: reserva `wallace_NNNN`,
   guarda parámetros y genera el Tcl con registradores locales.
4. Ejecutar **EJECUTAR CORRIDA** una sola vez. Para repetir un análisis, generar
   una nueva corrida; los resultados anteriores no se eliminan.
5. Seleccionar la corrida en **COMPARACIONES LOCALES**, o usar el bloque final
   **EXPORTAR Y ACTUALIZAR FICHA** para procesar todos sus resultados guardados.

Cada carpeta contiene `parametros.json`, `resumen.md`, Tcl, log,
respuesta `.ladruno`, archivos internos locales, sensores/IDs, datos CSV,
gráficos PNG/PDF. Los parámetros incluyen
valores derivados y comandos materiales realmente emitidos. La geometría no
se repite en las tablas del resumen; queda recuperable en el Tcl y la referencia
del modelo en el manifiesto.

La selección `ultima_completa` busca la carpeta de mayor número con respuesta
`.ladruno` y análisis completo registrado en `parametros.json`, o una importación
histórica con artefactos completos. La selección `ultima` busca la de mayor número
con respuesta `.ladruno` y parámetros, incluyendo corridas parciales o fallidas.
La búsqueda consulta directamente las carpetas `wallace_NNNN`.
Las importaciones históricas conservan la evidencia
disponible sin atribuirles un código de retorno ni parámetros de entrada que
no se guardaron originalmente.

Los gráficos y exportaciones posteriores se escriben dentro de la corrida
seleccionada. No asignan otro número ni modifican sus entradas congeladas.
Las referencias experimentales se leen desde `../DatosExperimentales/` y el código
de postproceso desde `../rw2_workflow.py`. Las correcciones de esos archivos se
aplican al volver a generar las comparaciones. Los hashes guardados en los
parámetros permiten identificar las versiones utilizadas en cada procesamiento.
Las copias de fuentes de las corridas anteriores se retiraron y sus parámetros
lo registran mediante `source_snapshot_available: false`. Los hashes históricos
identifican las versiones usadas entonces; las rutas compartidas apuntan a los
archivos vigentes del proyecto.

La ficha `resumen.md` enlaza todos
los datos y figuras y puede consultarse directamente en VS Code.
