import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
from github import Github
from beeai_framework.backend.chat import ChatModel
from beeai_framework.workflows.agent import AgentWorkflow, AgentWorkflowInput

# Config UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Cargar variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GH_TOKEN")
GITHUB_REPO = os.getenv("GH_REPO")

# Config logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Solo mensaje, sin fecha ni nivel
    handlers=[
        logging.FileHandler("auditor_beeai.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.getLogger("litellm").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)


# Leer CSV
def read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# Detectar inconsistencias
def contiene_errores(texto):
    claves = ["error", "inconsistencia", "anomalía", "problema", "diferencia", "falla"]
    return any(p in texto.lower() for p in claves)

# Crear issue en GitHub
def crear_issue_en_github(titulo, cuerpo):
    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(GITHUB_REPO)
    for issue in repo.get_issues(state="open"):
        if titulo.lower() in issue.title.lower():
            logging.info(f"✅ Issue ya existente: #{issue.number}")
            return
    issue = repo.create_issue(title=titulo, body=cuerpo)
    logging.info(f"Issue creado: {issue.html_url}")

# Main workflow
async def main():
    logging.info("\n🚀 Ejecutando auditoría financiera con BeeAI...\n")

    llm = ChatModel.from_name("openai:gpt-4-turbo")
    workflow = AgentWorkflow(name="Auditor Financiero")

    balance_text = read_csv("balance.csv")
    quarterly_text = read_csv("quarterly.csv")
    "📄 Documentos CSV cargados correctamente."
    logging.info("📄 Documentos CSV cargados correctamente.\n")

    # Agentes
    workflow.add_agent(
        name="ReaderAgent",
        role="Asistente financiero",
        instructions="Confirma que los documentos han sido recibidos correctamente. Sé breve.",
        llm=llm,
    )

    workflow.add_agent(
        name="AuditorAgent",
        role="Auditor técnico",
        instructions="Analiza ambos documentos y detecta inconsistencias, errores u omisiones. Sé claro y conciso.",
        llm=llm,
    )

    workflow.add_agent(
        name="ReportAgent",
        role="Redactor de informe",
        instructions="Redacta un informe profesional y corto con base en el análisis técnico anterior. Incluye recomendaciones si es necesario.",
        llm=llm,
    )

    # Entradas del workflow
    inputs = [
        AgentWorkflowInput(
            agent="ReaderAgent",
            prompt=f"""Balance General:\n{balance_text}\n\nInforme Trimestral:\n{quarterly_text}"""
        ),
        AgentWorkflowInput(
            agent="AuditorAgent",
            prompt="Analiza los dos documentos anteriores y presenta hallazgos técnicos breves y claros."
        ),
        AgentWorkflowInput(
            agent="ReportAgent",
            prompt="Redacta un informe breve basado en el análisis anterior. Incluye problemas detectados y sugerencias."
        ),
    ]

    # Ejecutar workflow
    result = await workflow.run(inputs=inputs).on(
        "success",
        lambda data, event: print(
            f"✅ '{data.step}': Paso completado.\n{data.state.final_answer}\n"
        ),
    )
    
    final_text = result.state.final_answer  # Resultado de ReportAgent
    print("\n✅ Informe final:\n")
    print(final_text)

    # Verificar inconsistencias y crear issue
    if contiene_errores(final_text):
        logging.warning("\n⚠️  Se detectaron inconsistencias. Creando Issue en GitHub...\n")
        crear_issue_en_github("📝 Inconsistencias detectadas en auditoría financiera\n", final_text)
    else:
        logging.info("✅ No se detectaron problemas relevantes.\n")

if __name__ == "__main__":
    asyncio.run(main())
