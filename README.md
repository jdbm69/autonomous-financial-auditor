🧠 Autonomous Financial Auditor.
Este proyecto implementa un agente autónomo que compara dos reportes financieros (balance.csv y quarterly.csv) y detecta inconsistencias. Si encuentra errores, crea o actualiza un Issue en el repositorio de GitHub.



📂 Estructura del proyecto.
El proyecto está organizado así:

.github/workflows/: contiene los workflows de GitHub Actions (audit.yml y docker-audit.yml)

.env: variables de entorno necesarias

auditor.log: archivo de logs generados

balance.csv y quarterly.csv: archivos con datos financieros

run_auditor.py: script principal del auditor

Dockerfile y docker-compose.yml: para ejecutar el agente en Docker

requirements.txt: dependencias del proyecto



⚙️ Requisitos.
Python 3.11 o superior

Una cuenta de OpenAI y GitHub

Un archivo .env con las siguientes claves:
- OPENAI_API_KEY=tu_api_key
- GH_TOKEN=tu_token_de_github
- GH_REPO=usuario/nombre_del_repositorio



▶️ Ejecución local
1. Instalar las dependencias:

pip install -r requirements.txt

2. Ejecutar la auditoría:

python run_auditor.py



🐳 Ejecución con Docker
1. Construir la imagen:

docker build -t auditor .

2. Ejecutar el contenedor:

docker run --env-file .env auditor

O usando docker-compose:

docker-compose up --build



🧪 GitHub Actions
El proyecto incluye dos workflows:

- audit.yml: ejecuta el auditor directamente con Python.

- docker-audit.yml: ejecuta el auditor dentro de un contenedor Docker.

Ambos se activan automáticamente con cada push al branch main o manualmente desde la pestaña Actions.



🧠 Funcionalidad del Agente
1. Lee los archivos balance.csv y quarterly.csv.

2. Genera un prompt con ambos textos.

3. Consulta a OpenAI (GPT-4) para detectar inconsistencias.

4. Si hay errores, se crea un Issue en GitHub con el resumen.

5. Todos los eventos se registran en el archivo auditor.log.



📊 Observabilidad
- Los logs de auditoría se guardan en auditor.log.

- Se imprimen mensajes de estado en consola y archivo.

- Se usan niveles de logging (INFO, WARNING, ERROR).



✅ Resultado Esperado
- Si no hay errores: el log indica que todo está bien.

- Si se detectan inconsistencias: se crea (o actualiza) un Issue en GitHub con el análisis detallado.



👤 Autor
Jhonny Bracho – GitHub: https://github.com/jdbm69