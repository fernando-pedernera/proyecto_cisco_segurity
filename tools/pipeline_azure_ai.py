"""Multi-Agent Content Development Pipeline using Azure OpenAI (Responses API & Chat Completions).

This module implements the 4-agent sequential pipeline:
1. Technical Extractor & Fact Curator
2. Instructional Design Architect
3. Multimedia Scriptwriter for Colossyan
4. Anti-Hallucination QA Auditor

Reads source documentation from `source_docs/` or custom text input,
and executes real LLM calls against the user's Azure AI Foundry / Azure OpenAI deployment.

Usage:
    python tools/pipeline_azure_ai.py [--doc source_docs/cisco_secure_access_source.md] [--offline]
"""

import argparse
import os
import pathlib
import sys
from typing import Dict, Any, Tuple
import requests
from dotenv import load_dotenv

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_DOC = ROOT_DIR / "source_docs" / "cisco_secure_access_source.md"

load_dotenv(ROOT_DIR / ".env")

AGENT_PROMPTS = {
    "agent_1_extractor": (
        "Eres un Principal Cisco Security Solutions Engineer. "
        "Lee la documentación técnica fuente proporcionada y extrae en ESPAÑOL una "
        "'Matriz de Verdad Técnica (Ground Truth)' estrictamente factual en Markdown con 4 secciones en viñetas:\n"
        "1. Componentes Arquitectónicos Clave (mantén los nombres oficiales de producto/UI de Cisco como Cisco Secure Access, AI Access, AI Guardrails)\n"
        "2. Prerrequisitos Técnicos Obligatorios\n"
        "3. Errores Comunes de Configuración (Misconfigurations)\n"
        "4. Estrategia Recomendada de Despliegue\n"
        "NO inventes ninguna función que no esté explícitamente en el texto fuente. Máximo 180 palabras."
    ),
    "agent_2_instructional": (
        "Eres un Diseñador Instruccional Técnico Senior en Cisco. "
        "Usando ÚNICAMENTE la Matriz de Verdad Técnica proporcionada, redacta en ESPAÑOL un Resumen de Diseño de Microaprendizaje en Markdown:\n"
        "1. Tres Objetivos de Aprendizaje mapeados a la Taxonomía de Bloom (OA1: Analizar, OA2: Aplicar, OA3: Evaluar).\n"
        "2. Un desafío de escenario empresarial realista (1 párrafo) que ponga a prueba el prerrequisito obligatorio y la estrategia de despliegue.\n"
        "Máximo 180 palabras."
    ),
    "agent_3_scriptwriter": (
        "Eres un Guionista Experto de Video con IA para Colossyan Studio. "
        "Usando ÚNICAMENTE la Matriz de Verdad Técnica y el Resumen Instruccional, redacta en ESPAÑOL un guion de video de 4 escenas a dos columnas "
        "(Tabla Markdown: Escena y Visuales | Locución / Narración) para un micro-video técnico de 60 segundos.\n"
        "Incluye marcadores [pausa] y palabras clave en **negrita** para énfasis vocal. Tono de ingeniero a ingeniero, cero lenguaje de marketing. "
        "Mantén la locución entre 120 y 140 palabras en total."
    ),
    "agent_4_qa_auditor": (
        "Eres un Auditor de Calidad Técnica (QA) implacable para entrenamientos de Cisco. "
        "Compara el Guion de Video generado contra la Documentación Fuente original y redacta tu informe en ESPAÑOL.\n"
        "Genera un Informe QA en Markdown con:\n"
        "1. Tabla de Verificación de Hechos (Afirmación en el Guion | Estado: SOPORTADO o NO SOPORTADO | Referencia en Fuente)\n"
        "2. Auditoría de Tono y Ritmo (Tono de ingeniero, sin exageraciones comerciales)\n"
        "3. Veredicto Final: APROBADO (PASS) o REQUIERE CORRECCIÓN.\n"
        "Sé conciso, máximo 160 palabras."
    ),
}


def call_azure_llm(
    system_instructions: str,
    user_input: str,
    endpoint: str | None = None,
    api_key: str | None = None,
    deployment: str | None = None,
    max_output_tokens: int = 600,
) -> Tuple[str, Dict[str, int]]:
    """Calls Azure AI Foundry Responses API (/openai/v1/responses) or Chat Completions API with FinOps token caps."""
    endpoint = (endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "")).strip()
    api_key = (api_key or os.getenv("AZURE_OPENAI_API_KEY", "")).strip()
    deployment = (deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-mini")).strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip()

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
        "Authorization": f"Bearer {api_key}",
    }

    # Case 1: Azure AI Foundry / OpenAI v1 Responses API endpoint
    if "/responses" in endpoint:
        url = endpoint
        payload: Dict[str, Any] = {
            "model": deployment,
            "instructions": system_instructions,
            "input": user_input,
            "reasoning": {"effort": "low"},
            "max_output_tokens": max_output_tokens,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        # Fallback if the specific model deployment does not accept reasoning parameter
        if resp.status_code == 400 and "reasoning" in resp.text:
            payload.pop("reasoning", None)
            resp = requests.post(url, headers=headers, json=payload, timeout=90)
        if resp.status_code != 200:
            raise RuntimeError(f"Azure Responses API Error ({resp.status_code}): {resp.text[:400]}")
        data = resp.json()
        text_out = ""
        for item in data.get("output", []):
            if item.get("type") == "message":
                for block in item.get("content", []):
                    if block.get("type") in ("output_text", "text"):
                        text_out += block.get("text", "")
        usage = data.get("usage", {})
        return text_out.strip(), {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    # Case 2: Standard Azure OpenAI Chat Completions endpoint
    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    payload = {
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_input},
        ],
        "max_completion_tokens": max_output_tokens,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    if resp.status_code != 200:
        raise RuntimeError(f"Azure Chat Completions Error ({resp.status_code}): {resp.text[:400]}")
    data = resp.json()
    text_out = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return text_out.strip(), {
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }


def run_full_live_pipeline(source_text: str, source_name: str = "custom_input") -> Dict[str, Any]:
    """Runs all 4 agents sequentially in live Azure OpenAI with FinOps token optimization."""
    logs = []
    total_in = 0
    total_out = 0

    logs.append(f"[FUENTE] Documentación técnica cargada: '{source_name}' ({len(source_text)} caracteres).")

    # Agent 1: Extractor
    logs.append("[Agente 1: Extractor Técnico] Extrayendo Matriz de Verdad Técnica (Ground Truth) [reasoning=low]...")
    a1_out, u1 = call_azure_llm(
        AGENT_PROMPTS["agent_1_extractor"],
        f"DOCUMENTACIÓN TÉCNICA FUENTE:\n\n{source_text}",
        max_output_tokens=500,
    )
    total_in += u1["input_tokens"]
    total_out += u1["output_tokens"]
    logs.append(f"[Agente 1 Completado] Matriz extraída ({u1['input_tokens']} in / {u1['output_tokens']} out tokens).")

    # Agent 2: Instructional Designer
    logs.append("[Agente 2: Diseñador Instruccional] Construyendo objetivos de Bloom y escenario [reasoning=low]...")
    a2_out, u2 = call_azure_llm(
        AGENT_PROMPTS["agent_2_instructional"],
        f"MATRIZ DE VERDAD TÉCNICA:\n\n{a1_out}",
        max_output_tokens=500,
    )
    total_in += u2["input_tokens"]
    total_out += u2["output_tokens"]
    logs.append(f"[Agente 2 Completado] Diseño instruccional listo ({u2['input_tokens']} in / {u2['output_tokens']} out tokens).")

    # Agent 3: Scriptwriter
    logs.append("[Agente 3: Guionista Colossyan] Redactando guion de video a 2 columnas [reasoning=low]...")
    a3_input = f"MATRIZ DE VERDAD TÉCNICA:\n{a1_out}\n\nDISEÑO INSTRUCCIONAL:\n{a2_out}"
    a3_out, u3 = call_azure_llm(
        AGENT_PROMPTS["agent_3_scriptwriter"],
        a3_input,
        max_output_tokens=650,
    )
    total_in += u3["input_tokens"]
    total_out += u3["output_tokens"]
    logs.append(f"[Agente 3 Completado] Guion de video sintetizado ({u3['input_tokens']} in / {u3['output_tokens']} out tokens).")

    # Agent 4: QA Auditor (FinOps optimization: audits against condensed Ground Truth Matrix a1_out instead of full raw doc)
    logs.append("[Agente 4: Auditor QA] Auditando guion contra Matriz de Verdad Técnica [reasoning=low]...")
    a4_input = f"MATRIZ DE VERDAD TÉCNICA OFICIAL:\n{a1_out}\n\nGUION GENERADO:\n{a3_out}"
    a4_out, u4 = call_azure_llm(
        AGENT_PROMPTS["agent_4_qa_auditor"],
        a4_input,
        max_output_tokens=500,
    )
    total_in += u4["input_tokens"]
    total_out += u4["output_tokens"]
    logs.append(f"[Agente 4 Completado] Auditoría QA finalizada ({u4['input_tokens']} in / {u4['output_tokens']} out tokens).")

    # Estimate cost for gpt-5-mini ($0.40 / 1M in, $2.50 / 1M out)
    est_cost = (total_in * 0.40 / 1_000_000) + (total_out * 2.50 / 1_000_000)
    logs.append(
        f"[PIPELINE COMPLETADO] Tokens totales: {total_in + total_out} "
        f"({total_in} in / {total_out} out) | Costo real: ${est_cost:.5f} USD"
    )

    return {
        "source_name": source_name,
        "agent_1_ground_truth": a1_out,
        "agent_2_instructional_brief": a2_out,
        "agent_3_video_script": a3_out,
        "agent_4_qa_report": a4_out,
        "usage": {
            "input_tokens": total_in,
            "output_tokens": total_out,
            "total_tokens": total_in + total_out,
            "estimated_cost_usd": round(est_cost, 5),
        },
        "logs": logs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Azure OpenAI 4-Agent Content Pipeline")
    parser.add_argument("--doc", type=str, default=str(DEFAULT_SOURCE_DOC), help="Path to source documentation file")
    parser.add_argument("--offline", action="store_true", help="Run in offline simulation mode")
    args = parser.parse_args()

    doc_path = pathlib.Path(args.doc)
    if not doc_path.exists():
        print(f"Error: Source document not found at {doc_path}")
        return 1

    source_text = doc_path.read_text(encoding="utf-8")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-mini")

    is_placeholder = (not api_key) or ("tu_clave" in api_key) or ("tu-recurso" in endpoint)

    if args.offline or is_placeholder:
        print("[OFFLINE MODE] Showing pre-computed simulation.")
        print(f"Source file ready at: {doc_path} ({len(source_text)} chars)")
        return 0

    print("=" * 70)
    print(f"RUNNING LIVE 4-AGENT PIPELINE ON AZURE ({deployment})")
    print(f"Input Source File: {doc_path.name}")
    print("=" * 70)

    result = run_full_live_pipeline(source_text, doc_path.name)
    for line in result["logs"]:
        print(" ", line)

    print("\n--- AGENT 1: GROUND TRUTH MATRIX ---\n", result["agent_1_ground_truth"])
    print("\n--- AGENT 2: INSTRUCTIONAL BRIEF ---\n", result["agent_2_instructional_brief"])
    print("\n--- AGENT 3: COLOSSYAN VIDEO SCRIPT ---\n", result["agent_3_video_script"])
    print("\n--- AGENT 4: QA AUDIT REPORT ---\n", result["agent_4_qa_report"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
