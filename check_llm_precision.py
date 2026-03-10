import sys
import autogen
import datetime
from finrobot import get_ollama_config
from finrobot.data_source import YFinanceUtils
from finrobot.toolkits import register_toolkits

def test_llm_precision():
    print("Iniciando test de precisión determinista para Llama 3.1 8B...")
    
    # Cargará OLLAMA_MODEL y base_url de .env, que fijamos a llama3.1:8b, además de nuestro temperature=0, top_p=0.1, seed=42
    config_list = get_ollama_config()

    analyst = autogen.AssistantAgent(
        name="Financial_Analyst",
        system_message="""Eres un ejecutor de código técnico. Tu único propósito es devolver un bloque JSON llamando a la herramienta solicitada.
REGLAS CRÍTICAS DE PARÁMETROS:
1. DEBES utilizar EXACTAMENTE los nombres de parámetros descritos en la firma de la función.
2. Está TOTAL Y ESTRICTAMENTE PROHIBIDO usar las claves 'from' o 'to' dentro de arguments.
3. ESTÁS OBLIGADO a usar 'start_date' y 'end_date' como literales para indicar rangos de fechas. Fallar en esto equivale a un error crítico.
""",
        llm_config=config_list,
    )

    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1, # Solo queremos ver su primera invocación
    )

    register_toolkits(
        [YFinanceUtils.get_stock_data],
        caller=analyst,
        executor=user_proxy
    )

    today = datetime.date.today().isoformat()
    prompt = f"Por favor, obtén los datos históricos de AAPL desde 2023-01-01 hasta {today}."
    
    print(f"\nPrompt engañoso inyectado:\n> {prompt}\n")
    print("Evaluando qué claves JSON decide utilizar el modelo...\n" + "-"*50)
    
    user_proxy.initiate_chat(
        analyst,
        message=prompt
    )

if __name__ == "__main__":
    test_llm_precision()
