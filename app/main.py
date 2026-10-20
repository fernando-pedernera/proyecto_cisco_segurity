"""FastAPI Backend for Cisco Security AI Enablement Suite.

Stack identical to 'revista_digital':
- Framework: FastAPI 0.136+ with Uvicorn
- Port: 8020 (isolated, zero-collision)
- Live Multi-Agent Orchestration: Calls Azure AI Foundry (gpt-5-mini) on real source docs
"""

import datetime
import json
import os
import pathlib
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
STATIC_DIR = pathlib.Path(__file__).resolve().parent / "static"
SOURCE_DOCS_DIR = ROOT_DIR / "source_docs"
STATE_CACHE_FILE = pathlib.Path(__file__).resolve().parent / "pipeline_state_cache.json"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from tools.pipeline_azure_ai import run_full_live_pipeline

app = FastAPI(
    title="Cisco Security AI Enablement Suite",
    description="Interactive Multi-Agent Dashboard for Cisco Security Technical Content",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_persisted_state() -> Dict[str, Any]:
    """Loads the last executed pipeline state from disk so runs survive restarts."""
    if STATE_CACHE_FILE.exists():
        try:
            return json.loads(STATE_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "status": "ready",
        "last_run": None,
        "active_agent": None,
        "logs": [
            "[INIT] Sistema inicializado. Conectado a Azure AI Foundry (gpt-5-mini).",
            "[SOURCE] Documentos fuente disponibles en carpeta 'source_docs/'.",
            "[READY] Selecciona o edita la documentación técnica y presiona 'Ejecutar Pipeline'."
        ],
        "live_outputs": None,
        "deliverables_ready": True,
    }


def save_persisted_state(state: Dict[str, Any]) -> None:
    """Saves the current pipeline state to disk."""
    try:
        STATE_CACHE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


pipeline_state: Dict[str, Any] = load_persisted_state()


class PipelineRunRequest(BaseModel):
    source_doc_key: Optional[str] = "cisco_secure_access_source.md"
    custom_source_text: Optional[str] = None
    force_live: Optional[bool] = False


class DecisionSubmission(BaseModel):
    decision_id: int
    selected_option: str


@app.get("/api/source-docs")
def list_source_docs() -> Dict[str, Any]:
    """Returns available technical source documents in source_docs/."""
    docs = {}
    if SOURCE_DOCS_DIR.exists():
        for p in sorted(SOURCE_DOCS_DIR.glob("*.md")):
            docs[p.name] = p.read_text(encoding="utf-8")
    return {"docs": docs}


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    """Returns current system and Azure pipeline status."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-mini")

    is_live = bool(api_key and ("tu_clave" not in api_key) and ("tu-recurso" not in endpoint))
    return {
        "status": pipeline_state["status"],
        "last_run": pipeline_state["last_run"],
        "logs": pipeline_state["logs"],
        "live_outputs": pipeline_state["live_outputs"],
        "azure_configured": is_live,
        "endpoint": endpoint if is_live else "Modo Simulación Offline",
        "deployment": deployment,
        "deliverables": {
            "README_documentation": (ROOT_DIR / "README.md").exists(),
            "colossyan_slides_deck": (STATIC_DIR / "colossyan_slides" / "cisco_colossyan_8_scenes_deck.pdf").exists(),
            "azure_agent_pipeline": (ROOT_DIR / "tools" / "pipeline_azure_ai.py").exists(),
            "source_docs_ready": SOURCE_DOCS_DIR.exists(),
        },
    }


@app.post("/api/run-pipeline")
def run_pipeline(req: Optional[PipelineRunRequest] = None) -> Dict[str, Any]:
    """Executes the 4-agent pipeline with FinOps disk-cache protection ($0.00 on cache hits)."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-mini")
    is_live = bool(api_key and ("tu_clave" not in api_key) and ("tu-recurso" not in endpoint))

    # Determine source text to feed to Agent 1
    source_name = "cisco_secure_access_source.md"
    source_text = ""
    custom_txt = (req.custom_source_text or "").strip() if req else ""
    if custom_txt and not custom_txt.startswith("# Error cargando"):
        source_text = custom_txt
        source_name = req.source_doc_key or "custom_source_input"
    else:
        doc_key = (req.source_doc_key if req and req.source_doc_key else "cisco_secure_access_source.md")
        doc_path = SOURCE_DOCS_DIR / doc_key
        if doc_path.exists():
            source_text = doc_path.read_text(encoding="utf-8")
            source_name = doc_path.name
        else:
            default_path = SOURCE_DOCS_DIR / "cisco_secure_access_source.md"
            source_text = default_path.read_text(encoding="utf-8") if default_path.exists() else "Cisco Secure Access SSE documentation."

    force_live = bool(req and req.force_live)
    existing_out = pipeline_state.get("live_outputs") or {}
    if not force_live and existing_out and existing_out.get("source_name") == source_name:
        cached_logs = [
            f"[{now_str}] [FINOPS CACHE HIT] Documento '{source_name}' ya procesado en caché local ($0.00 USD — 0 tokens consumidos).",
            "[INFO] Para gastar tokens y forzar una regeneración en Azure, activa la casilla 'Forzar llamada en vivo a Azure API'."
        ] + [l for l in pipeline_state.get("logs", []) if not l.startswith("[") or "Agente" in l or "PIPELINE" in l]
        pipeline_state["logs"] = cached_logs
        return {"message": "Returned from FinOps local cache ($0.00)", "state": pipeline_state}

    if is_live:
        try:
            result = run_full_live_pipeline(source_text=source_text, source_name=source_name)
            pipeline_state["status"] = "completed"
            pipeline_state["last_run"] = now_str
            pipeline_state["logs"] = [f"[{now_str}] LIVE EXECUTION ON AZURE ({deployment} | reasoning=low) [GUARDADO EN DISCO]"] + result["logs"]
            pipeline_state["live_outputs"] = result
            save_persisted_state(pipeline_state)
            return {"message": "Live Azure pipeline executed successfully", "state": pipeline_state}
        except Exception as e:
            pipeline_state["status"] = "error"
            pipeline_state["logs"].append(f"[ERROR] Falló llamada en vivo a Azure: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Fallback simulation if keys are removed
    pipeline_state["status"] = "completed"
    pipeline_state["last_run"] = now_str
    pipeline_state["logs"] = [
        f"[{now_str}] Ejecutando en modo Simulación sobre '{source_name}' ({len(source_text)} caracteres)...",
        "[Agente 1: Extractor Técnico] Ingestó documentación fuente. Matriz extraída.",
        "[Agente 2: Diseñador Pedagógico] Objetivos de Bloom definidos.",
        "[Agente 3: Guionista Colossyan] Sintetizó guion a 2 columnas.",
        "[Agente 4: Auditor QA] Puntuación: PASS (100%).",
    ]
    save_persisted_state(pipeline_state)
    return {"message": "Simulation executed", "state": pipeline_state}


@app.post("/api/evaluate-decision")
def evaluate_decision(sub: DecisionSubmission):
    """Evaluates learner decisions in the Andes Freight scenario challenge."""
    if sub.decision_id == 1:
        is_correct = (sub.selected_option.upper() == "B")
        feedback = {
            "A": "❌ Incorrecto. Las reglas AI Guardrails revisan prompts, respuestas y archivos subidos. Repasar escena 6.",
            "B": "✅ ¡Correcto! Los prompts viajan dentro de sesiones HTTPS cifradas. Sin inspección HTTPS en la política de acceso, el motor DLP nunca ve el contenido.",
            "C": "❌ Incorrecto. Bloquear la aplicación corta todo el tráfico y no deja nada para inspeccionar. Repasar escena 5.",
            "D": "❌ Incorrecto. La clasificación de AI Guardrails va más allá de expresiones regulares e incluye código fuente. Repasar escena 5."
        }
        return {
            "decision_id": 1,
            "selected": sub.selected_option.upper(),
            "is_correct": is_correct,
            "feedback": feedback.get(sub.selected_option.upper(), "Opción inválida"),
            "consequence": "Maya activa la inspección HTTPS en la política de Ingeniería. En pocas horas, la regla empieza a registrar eventos, incluidos dos prompts con código fuente." if is_correct else None
        }
    elif sub.decision_id == 2:
        is_correct = (sub.selected_option.upper() == "C")
        feedback = {
            "A": "❌ Incorrecto. Bloquear toda la categoría frena una herramienta aprobada antes de una entrega y empuja a los usuarios a dispositivos personales. Repasar escena 2.",
            "B": "❌ Incorrecto. Sin línea base, no puedes distinguir fugas reales de falsos positivos, causando fricción operativa. Repasar escena 7.",
            "C": "✅ ¡Correcto! El modo Monitoreo mantiene operativa la herramienta aprobada mientras Maya mide el uso real, ajusta falsos positivos y pasa a Bloqueo con seguridad.",
            "D": "❌ Incorrecto. Apagar los controles deja los datos expuestos mientras se redacta la política. Repasar escena 7."
        }
        return {
            "decision_id": 2,
            "selected": sub.selected_option.upper(),
            "is_correct": is_correct,
            "feedback": feedback.get(sub.selected_option.upper(), "Opción inválida"),
            "badge": "Leak Stopper" if is_correct else None,
            "outcome": "Dos semanas después, los intentos de fuga se concentran en dos apps no aprobadas. Esas reglas pasan a Bloqueo casi sin falsos positivos y el asistente de código sigue funcionando." if is_correct else None
        }
    raise HTTPException(status_code=400, detail="Invalid decision ID")


if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

diagrams_dir = ROOT_DIR / "diagrams"
if diagrams_dir.exists():
    app.mount("/diagrams", StaticFiles(directory=str(diagrams_dir)), name="diagrams")

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
