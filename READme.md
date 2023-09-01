### Notas de la Versión del Script de Procesamiento de Datos para la creacion de Reportes de Backlinks

---

**1. Configuración Inicial y Autenticación:**
   
- **Importaciones**: Se importan módulos esenciales como `pandas`, `openpyxl`, `nltk`, herramientas de autenticación y conexión con la API de Google, y utilidades personalizadas.
- **Autenticación en GSC**: Se implementa un proceso de autenticación y conexión con la API de Google Search Console, permitiendo el acceso y la consulta de datos.

---

**2. Procesamiento y Organización de Datos del Archivo Excel:**

- **Lectura de Archivo**: El script carga hojas con formato "mes-año" desde un archivo Excel especificado.
- **Filtrado de Datos**: Se reorganizan y filtran las columnas basadas en ciertos criterios.
- **Procesamiento de URLs**: Se extraen y procesan URLs específicas basadas en un dominio proporcionado por el usuario.

---

**3. Consultas a Google Search Console (GSC):**

- **Búsqueda de Datos de Backlinks**: Se utiliza la función `get_backlinks_data_gsc` para consultar datos específicos de backlinks desde GSC.
- **Extracción de Métricas Adicionales**: Se implementa la capacidad de contar palabras clave asociadas a URLs específicas.
- **Manejo de Fechas**: Se incorpora una corrección para asegurar que los datos se obtengan para el mes correcto.

---

**4. Integración y Guardado de Datos:**

- **Extracción de Datos por Dominio**: El script se adapta para operar en torno a un dominio específico, permitiendo filtrar y procesar datos solo para ese dominio.
- **Reorganización de Datos**: Se integra la capacidad de reorganizar y combinar datos de varias hojas de Excel basadas en ciertos criterios.
- **Guardado de Resultados**: Una vez procesados y combinados todos los datos, el script guarda los resultados en un nuevo archivo Excel.

---

**5. Manejo de Excepciones y Errores:**

- **Manejo de Errores HTTP**: Se implementa el manejo de errores para evitar interrupciones debido a errores HTTP al consultar la API de GSC.
- **Validaciones de Datos**: Se implementan validaciones para asegurarse de que solo se procesen las hojas y columnas deseadas.

---

**6. Utilidades y Funciones Auxiliares:**

- **Filtrado por Dominio**: Se implementa una función para filtrar URLs basadas en un dominio específico.
- **Utilidades de Fecha**: Se incorporan utilidades para manejar y procesar rangos de fechas para consultas a GSC.

---

Este script representa una herramienta robusta y adaptativa diseñada para extraer, procesar y analizar datos de backlinks desde un archivo Excel y Google Search Console. Las mejoras y correcciones realizadas en esta versión aseguran una mayor precisión, eficiencia y adaptabilidad en la extracción y análisis de datos.

1.	El ingreso de los backlinks es tedioso pues se debe ingresar url por url, quiero decir si se hicieron 10 backlinks de 10 medios diferentes a un mismo url se debe ingresar el mismo 10 veces
2.	Si por error humano se olvida ingresar 1 url el desarrollo anula el ingreso de las demás urls y se pierde el tiempo y trabajo realizado.
3.	Si el cliente empezó la estrategia de backlinks desde un tiempo atrás significativo por ejemplo Octubre 2021 hasta junio 2023 la herramienta no es capaz de mostrar toda la data porque son muchos meses, según el equipo de Desarrollo esto ocurre por un tema del servidor; para nosotros es importante poder ver los datos de todos los meses pues así es como lo necesita y lo solicita ver el cliente.

---

### Resolución de Errores y Mejoras - Notas de la Versión

**1. Procesamiento de Datos Excel:**
   - Se detectó la necesidad de procesar y reorganizar datos de un archivo Excel.
   - Se implementó una función (`reorganizar_datos_excel`) para extraer y reordenar los datos de las columnas relevantes.

**2. Consulta a Google Search Console (GSC):**
   - Se estableció la necesidad de consultar datos desde GSC utilizando la API de Google.
   - Se implementó una función (`get_backlinks_data_gsc`) que consulta a GSC para obtener métricas de backlinks.

**3. Integración de Datos:**
   - Se integró la respuesta de GSC con los datos procesados del archivo Excel.
   - Se implementó la función `guardar_resultados_en_excel` para guardar la data integrada en un archivo Excel nuevo.

**4. Mejoras en la Función GSC:**
   - Se optimizó la función GSC para manejar errores HTTP, evitando que el script se detenga debido a errores 403 o 400.
   - Se implementó una corrección para asegurarse de que los datos se obtengan para el mes correcto, y no el mes siguiente.

**5. Verificación de URLs en GSC:**
   - Se incorporó una función (`check_url_existence_in_gsc`) para verificar la existencia de URLs específicas en GSC y se agregó una columna adicional en el archivo Excel resultante para reflejar esta información.

**6. Corrección de Dimensiones GSC:**
   - Se corrigieron errores en las dimensiones solicitadas a GSC, reemplazando "referringPage" y "referringHost" por las dimensiones correctas.

**7. Extracción de Métricas Adicionales:**
   - Se incorporó una mejora para extraer y contar la cantidad de palabras clave asociadas a URLs específicas en GSC, y se añadió esta métrica en una columna adicional llamada "Query".

---

Estas notas de la versión reflejan las tareas, correcciones y mejoras realizadas para optimizar el script de procesamiento de datos y consulta a Google Search Console. Se espera que estas mejoras proporcionen una mayor eficiencia y precisión en la extracción y análisis de datos de backlinks.