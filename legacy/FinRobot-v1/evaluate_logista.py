import os
import sys

# Ensure FinRobot is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import autogen
from finrobot import get_auto_config
from finrobot.toolkits import register_toolkits
from finrobot.data_source import YFinanceUtils, MarketStackUtils

# Configuraciones de LLM locales (Ollama/NIM)
# Utilizamos get_auto_config que prefiere NVIDIA NIM como fallback si Ollama no carga un modelo pesado local.
llm_config = get_auto_config(prefer_local=True, temperature=0.1)

# Forzar el modelo Ollama que tenemos configurado, limitando un poco la temperatura
# si preferimos gemma, etc. 
# En OAI_CONFIG_LIST tenemos ambas opciones
# llm_config es un dict con `config_list`

print("==== Evaluando empresa Logista (LOG.MC) ====")

# 1. Definir los agentes

# Data Agent: Encargado de obtener la información financiera
data_agent = autogen.AssistantAgent(
    name="Data_Agent",
    system_message="""Eres el Agente de Datos Financieros.
Tienes permitido MÁXIMO 2 llamadas a herramientas. 
Busca la información básica de la empresa ('LOG.MC') y su cotización.
Inmediatamente después de usar tus herramientas 1 o 2 veces como máximo, DEBES dejar de usarlas.
En tu mensaje, resume la información que has recopilado con claridad para el Analyst_Agent.
No emitas juicios de valor.
""",
    llm_config=llm_config,
)

# Analyst Agent: Redacta el reporte
analyst_agent = autogen.AssistantAgent(
    name="Analyst_Agent",
    system_message="""Eres un Analista Financiero Senior.
Revisas la información que te provee el Data_Agent. Con base en esos números y noticias,
redactas un reporte de análisis estructurado, en español.
El reporte debe contener:
- Resumen Ejecutivo
- Análisis de cotización y tendencias (basado en historia reciente)
- Fortalezas y Debilidades
- Conclusión con recomendación (Comprar/Mantener/Vender)
Debes apoyarte *estrictamente* en los datos provistos por el Data_Agent.
""",
    llm_config=llm_config,
)

# Manager Agent: Revisa y aprueba
manager_agent = autogen.AssistantAgent(
    name="Manager_Agent",
    system_message="""Eres el Director de Análisis (Manager).
Tu trabajo es revisar críticamente el informe redactado por el Analyst_Agent.
Si el informe es sólido, está bien redactado en español y tiene lógica, debes agregar una breve línea de "APROBADO" y escribir TERMINATE.
Si le faltan datos cruciales o el análisis es pobre, pídele al Analyst_Agent que lo mejore.
Máximo 2 iteraciones de revisión.
""",
    llm_config=llm_config,
)

# User Proxy: Simula al usuario interactuando con el grupo o ejecutando el código (si fuera necesario)
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    system_message="Un usuario humano que solicita un reporte sobre una empresa específica.",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
)

# 2. Registrar Toolkits al Data_Agent
# Permitimos al Data Agent que ejecute las herramientas definidas en YFinance y MarketStack
# Ojo: Autogen ejecuta la función en el `executor` (el UserProxy). El `caller` (quien decide qué tool llamar) es `data_agent`.
register_toolkits(
    [
        YFinanceUtils.get_stock_info,
        YFinanceUtils.get_stock_data,
        YFinanceUtils.get_income_stmt,
        YFinanceUtils.get_balance_sheet
    ],
    caller=data_agent,
    executor=user_proxy
)

# 3. Preparar el Group Chat
groupchat = autogen.GroupChat(
    agents=[user_proxy, data_agent, analyst_agent, manager_agent],
    messages=[],
    max_round=10,
    speaker_selection_method="round_robin" # Para asegurar que todos hablen en orden
)

# Manager del GroupChat
chat_manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# 4. Iniciar la tarea
task = """
Por favor, prepara un reporte de análisis exhaustivo de la empresa Compañía de Distribución Integral Logista Holdings, S.A.
El ticker en la bolsa de Madrid es 'LOG.MC'. 
Paso 1: El Data_Agent obtendrá los datos financieros (balance, cotización, etc) usando las funciones dadas. NUNCA escribas TERMINATE.
Paso 2: El Analyst_Agent evaluará los números y redactará el análisis completo en español. NUNCA escribas TERMINATE.
Paso 3: El Manager_Agent aprobará el reporte final. Solo el Manager_Agent escribirá TERMINATE cuando el análisis sea completo y bueno.
"""

print("🚀 Iniciando la ejecución del Group Chat...")
user_proxy.initiate_chat(
    chat_manager,
    message=task,
    summary_method="reflection_with_llm",
)
