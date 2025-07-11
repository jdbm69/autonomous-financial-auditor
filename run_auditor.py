import os
import logging
from openai import OpenAI
from github import Github
from dotenv import load_dotenv
import sys

#-----------Configurar consola para UTF-8 si es posible
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass  # En caso de que falle en entornos que no tienen reconfigure

#-----------Cargar variables de entorno
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GITHUB_TOKEN = os.getenv("GH_TOKEN")
GITHUB_REPO = os.getenv("GH_REPO")

#-----------Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("auditor.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

#-----------Lectura de documentos
def read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

#-----------Instrucciones para IA
def build_prompt(balance_text, quarterly_text):
    return f"""
Eres un auditor financiero experto. Se te presentan dos reportes:

=== BALANCE GENERAL ===
{balance_text}

=== INFORME TRIMESTRAL ===
{quarterly_text}

Tu tarea es:

1. Analizar ambos documentos.
2. Detectar diferencias, errores, omisiones o inconsistencias entre ellos.
3. Explicar si hay anomalías o si todo está correcto.
4. Finaliza con una conclusión clara y profesional.

No ignores detalles importantes y responde como si esto fuera para un reporte oficial.
"""

#-----------Observador de inconsistencias
def contiene_errores(texto):
    palabras_clave = ["error", "inconsistencia", "anomalía", "problema", "diferencia", "falla"]
    texto_min = texto.lower()
    return any(palabra in texto_min for palabra in palabras_clave)

#-----------Creador de issue (si lo hay)
def crear_issue_en_github(titulo, cuerpo):
    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(GITHUB_REPO)

    issues_abiertos = repo.get_issues(state="open")
    for issue in issues_abiertos:
        if titulo.lower() in issue.title.lower():
            logging.info(f"Issue similar ya existe: #{issue.number} - {issue.title}")
            return

    issue = repo.create_issue(title=titulo, body=cuerpo)
    logging.info(f"Issue creado: {issue.html_url}")

#-----------Funcion de auditoria
def run_audit():
    logging.info("Iniciando proceso de auditoría...")

    try:
        balance = read_csv("balance.csv")
        quarterly = read_csv("quarterly.csv")
        logging.info("Archivos leídos correctamente.")
    except Exception as e:
        logging.error(f"Error al leer archivos CSV: {e}")
        return

    prompt = build_prompt(balance, quarterly)
    logging.info("Prompt generado para análisis.")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        result = response.choices[0].message.content
        logging.info("Respuesta del modelo recibida.")
    except Exception as e:
        logging.error(f"Error al consultar OpenAI: {e}")
        return

    print("\nResultado de la auditoría:")
    print(result)

    if contiene_errores(result):
        logging.warning("Se detectaron posibles inconsistencias.")
        print("\nSe detectaron problemas. Vamos a crear un Issue en GitHub...")
        try:
            crear_issue_en_github(
                titulo="Inconsistencias detectadas en auditoría financiera",
                cuerpo=result
            )
        except Exception as e:
            logging.error(f"Error al crear el issue en GitHub: {e}")
    else:
        logging.info("No se detectaron errores relevantes.")

#--------------------------------------------
if __name__ == "__main__":
    run_audit()
