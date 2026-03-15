"""
Generador de llm_config para pyautogen.

Soporta dos proveedores:
  1. Ollama (local) — rápido, gratis, <8B parámetros
  2. NVIDIA NIM (cloud) — fallback para tareas complejas

Ambos exponen API compatible con OpenAI, por lo que pyautogen
puede usarlos directamente via base_url en config_list.

Patrón basado en: naval-rag/src/query/query_pipeline.py
"""

import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)


def get_ollama_config(
    model: str | None = None,
    temperature: float = 0.3,
) -> dict:
    """
    Genera llm_config para pyautogen usando Ollama.

    Ollama expone /v1/chat/completions compatible con OpenAI.
    No requiere API key real.

    Returns:
        dict compatible con pyautogen llm_config
    """
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model = model or os.getenv("OLLAMA_MODEL", "qwen3.5:9b-simple")

    config = {
        "config_list": [
            {
                "model": ollama_model,
                "base_url": f"{ollama_url.rstrip('/')}/v1",
                "api_key": "ollama",  # Ollama no requiere key, pero pyautogen la exige
            }
        ],
        "temperature": 0.0,
        "top_p": 0.1,
        "seed": 42,
    }

    log.info("Ollama config: model=%s, url=%s", ollama_model, ollama_url)
    return config


def get_nim_config(
    model: str | None = None,
    temperature: float = 0.3,
) -> dict:
    """
    Genera llm_config para pyautogen usando NVIDIA NIM.

    Usa OpenAI SDK contra https://integrate.api.nvidia.com/v1
    Requiere NVIDIA_API_KEY en .env

    Returns:
        dict compatible con pyautogen llm_config
    """
    api_key = os.getenv("NVIDIA_API_KEY", "")
    nim_model = model or os.getenv("NIM_TEXT_MODEL", "meta/llama-3.3-70b-instruct")
    
    # Referencia a smartRAG: Añadimos un pequeño delay si se solicita NIM 
    # para evitar ráfagas que bloqueen ambos proyectos.
    delay = float(os.getenv("NIM_RATE_LIMIT_DELAY", "0")) / 1000.0
    if delay > 0:
        log.info("NIM Rate Limit: esperando %.2fs...", delay)
        time.sleep(delay)

    if not api_key:
        log.warning(
            "NVIDIA_API_KEY no definida. NIM no estará disponible. "
            "Obtener en: https://build.nvidia.com"
        )

    config = {
        "config_list": [
            {
                "model": nim_model,
                "base_url": "https://integrate.api.nvidia.com/v1",
                "api_key": api_key,
            }
        ],
        "temperature": temperature,
    }

    log.info("NIM config: model=%s, key_set=%s", nim_model, bool(api_key))
    return config


def get_auto_config(
    prefer_local: bool = False,
    temperature: float = 0.3,
) -> dict:
    """
    Selección automática de LLM config.

    Si prefer_local=True (default):
      - Usa Ollama si está disponible
      - Fallback a NIM si NVIDIA_API_KEY está configurada

    Si prefer_local=False:
      - Usa NIM como primario
      - Fallback a Ollama
    """
    nim_key = os.getenv("NVIDIA_API_KEY", "")

    if prefer_local:
        config = get_ollama_config(temperature=temperature)
        # Añadir NIM como fallback si la key existe
        if nim_key:
            nim = get_nim_config(temperature=temperature)
            config["config_list"].extend(nim["config_list"])
            log.info("Auto config: Ollama + NIM fallback")
        else:
            log.info("Auto config: Ollama only (no NIM key)")
    else:
        if nim_key:
            config = get_nim_config(temperature=temperature)
            ollama = get_ollama_config(temperature=temperature)
            config["config_list"].extend(ollama["config_list"])
            log.info("Auto config: NIM + Ollama fallback")
        else:
            config = get_ollama_config(temperature=temperature)
            log.info("Auto config: Ollama only (NIM preferred but no key)")

    return config
