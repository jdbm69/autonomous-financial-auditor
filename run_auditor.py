import os
from openai import OpenAI
from github import Github
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # ej: "jhonnybracho/autonomous-financial-auditor"


def read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

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

def contiene_errores(texto):
    palabras_clave = ["error", "inconsistencia", "anomalía", "problema", "diferencia", "falla"]
    texto_min = texto.lower()
    return any(palabra in texto_min for palabra in palabras_clave)

def crear_issue_en_github(titulo, cuerpo):
    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(GITHUB_REPO)
    
    # Evitar crear issues duplicados
    issues_abiertos = repo.get_issues(state="open")
    for issue in issues_abiertos:
        if titulo.lower() in issue.title.lower():
            print(f"ℹ️ Ya existe un issue similar: #{issue.number} - {issue.title}")
            return

    issue = repo.create_issue(title=titulo, body=cuerpo)
    print(f"✅ Issue creado: {issue.html_url}")

def run_audit():
    balance = read_csv("balance.csv")
    quarterly = read_csv("quarterly.csv")
    prompt = build_prompt(balance, quarterly)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    result = response.choices[0].message.content

    print("\n📊 Resultado de la auditoría:")
    print(result)

    if contiene_errores(result):
        print("\n🚨 Se detectaron problemas. Vamos a crear un Issue en GitHub...")
        crear_issue_en_github(
            titulo="🚨 Inconsistencias detectadas en auditoría financiera",
            cuerpo=result
        )
    else:
        print("\n✅ No se detectaron errores. No es necesario crear un Issue.")

if __name__ == "__main__":
    run_audit()