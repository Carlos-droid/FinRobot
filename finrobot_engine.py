import os
import datetime
import autogen
from finrobot import get_auto_config, get_ollama_config, get_nim_config
from finrobot.toolkits import register_toolkits
from finrobot.data_source import YFinanceUtils, FMPUtils, FinnHubUtils

def run_finrobot_analysis(ticker, name, model_type="local"):
    """
    Ejecuta el flujo de agentes FinRobot para un ticker específico y guarda el resultado en un archivo .md.
    model_type: "local" (Ollama) o "nim" (Nvidia NIM)
    """
    print(f"\n[FinRobot Engine] Iniciando análisis para: {name} ({ticker}) usando modelo {model_type}")
    
    # Selección de configuración de LLM
    if model_type == "nim":
        llm_config = get_nim_config(temperature=0.1)
    else:
        llm_config = get_ollama_config(temperature=0.1)

    # Always use local config for data gathering because NIM doesn't support tools properly
    ollama_config = get_ollama_config(temperature=0.1)

    # Determine the current date to give context and prevent hallucinating old years
    current_date = datetime.date.today().isoformat()
    current_year = datetime.date.today().year

    # Contexto por sector
    sector_prompt = ""
    ticker_upper = ticker.upper()
    
    if ticker_upper in ["SAN.MC", "BBVA.MC", "CABK.MC", "ALV.DE", "BNP.PA"]:
        sector_prompt = f"""
<OBJECTIVE_AND_PERSONA>
Actúa como un Analista de Riesgos y Valoración Bancaria. Tu objetivo es auditar la solvencia y rentabilidad de una entidad financiera basándote en su última cuenta de resultados.
</OBJECTIVE_AND_PERSONA>

<CONTEXT>
El sector bancario europeo está condicionado por los tipos de interés del BCE y la calidad de los activos. Analiza los datos de la entidad: <ENTITY>{name}</ENTITY>.
</CONTEXT>

<INSTRUCTIONS>
Desglosa el análisis en estos puntos críticos:
1. **Solvencia:** Calcula y explica el Ratio CET1 (Common Equity Tier 1). ¿Está por encima de los requisitos regulatorios?
2. **Rentabilidad:** Detalla el ROE (Return on Equity) y el ROTE (Return on Tangible Equity). Compara con la media del sector (aprox. 12-15%).
3. **Márgenes:** Analiza el Margen de Intereses (NIM) y cómo le afecta la curva de tipos actual.
4. **Calidad de Activos:** Indica la Tasa de Morosidad (NPL Ratio) y el nivel de provisiones.
5. **Eficiencia:** Ratio de eficiencia operativa (gastos/ingresos).
</INSTRUCTIONS>

<OUTPUT_FORMAT>
- Tabla comparativa de Ratios Solvencia vs Rentabilidad.
- Resumen de 3 puntos sobre la sostenibilidad del dividendo.
</OUTPUT_FORMAT>
"""
    elif ticker_upper in ["IBE.MC", "ELE.MC", "ENEL.MI", "TTE.PA", "ENGI.PA"]:
        sector_prompt = f"""
<OBJECTIVE_AND_PERSONA>
Actúa como un Consultor de Energía y Analista de Infraestructuras. Evalúa la capacidad de generación de caja y la transición renovable de la compañía.
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
Analiza los siguientes pilares para <COMPANY>{name}</COMPANY>:
1. **Deuda y Apalancamiento:** Ratio Deuda Neta / EBITDA. ¿Es sostenible dado su CapEx?
2. **Base de Activos Regulados (RAB):** Importancia de los ingresos regulados frente a los liberalizados.
3. **Mix de Generación:** Porcentaje de energía renovable vs. fósil y potencia instalada (MW).
4. **Retribución:** Sostenibilidad del Pay-out y rentabilidad por dividendo (Dividend Yield).
</INSTRUCTIONS>

<CONSTRAINTS>
- Diferencia claramente entre EBITDA recurrente y extraordinarios.
- Considera el impacto de los marcos regulatorios nacionales.
</CONSTRAINTS>
"""
    elif ticker_upper in ["ITX.MC", "MC.PA", "ADS.DE", "OR.PA", "RMS.PA"]:
        sector_prompt = f"""
<OBJECTIVE_AND_PERSONA>
Actúa como un Analista de Consumo Discrecional. Tu enfoque debe estar en los márgenes operativos y la eficiencia del inventario.
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
Para la empresa <RETAILER>{name}</RETAILER>, evalúa:
1. **Ventas LFL (Like-for-Like):** Crecimiento de ventas en tiendas comparables.
2. **Margen Bruto:** Capacidad de fijación de precios (Pricing Power).
3. **Gestión de Stock:** Rotación de inventario y Ciclo de Conversión de Efectivo.
4. **Presencia Online:** Penetración del e-commerce sobre las ventas totales.
5. **Exposición Geográfica:** Impacto de mercados clave.
</INSTRUCTIONS>

<OUTPUT_FORMAT>
Markdown con una sección dedicada al "Foso Económico" (Moat) de la marca.
</OUTPUT_FORMAT>
"""
    elif ticker_upper in ["ACS.MC", "FER.MC", "DG.PA", "SU.PA", "SIE.DE"]:
        sector_prompt = f"""
<OBJECTIVE_AND_PERSONA>
Eres un Analista de Operaciones Industriales. Tu objetivo es medir la visibilidad de ingresos futuros y la eficiencia en la ejecución de proyectos.
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
Analiza para <FIRM>{name}</FIRM>:
1. **Backlog (Cartera de pedidos):** Volumen total de contratos firmados y meses de visibilidad de ingresos que representa.
2. **Book-to-Bill Ratio:** Relación entre pedidos recibidos y facturados (debe ser > 1 para crecimiento).
3. **Flujo de Caja Libre (FCF):** Capacidad de convertir el EBITDA en caja real tras inversiones.
4. **Working Capital:** Gestión de pagos a proveedores y cobros de clientes en grandes proyectos.
</INSTRUCTIONS>
"""
    elif ticker_upper in ["AMS.MC", "CLNX.MC", "ASML.AS", "SAP.DE", "TEF.MC", "NOKIA.HE"]:
        sector_prompt = f"""
<OBJECTIVE_AND_PERSONA>
Actúa como un Analista de Equity en Tecnología y Telecomunicaciones. Enfócate en la recurrencia y la escalabilidad.
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
Para <TECH>{name}</TECH>, analiza:
1. **Ingresos Recurrentes:** % de ingresos por suscripción o mantenimiento.
2. **Churn Rate:** Tasa de cancelación de clientes (si aplica).
3. **Inversión en R&D:** Gasto en I+D sobre ventas totales para mantener la ventaja competitiva.
4. **Métricas específicas:**
   - Para Telcos: ARPU (Ingreso medio por usuario).
   - Para Infraestructuras: Ratio de compartición de torres (Tenancy ratio).
</INSTRUCTIONS>
"""
    elif ticker_upper in ["MRL.MC", "COL.MC", "VNA.DE"]:
        sector_prompt = f"""
<OBJECTIVE_AND_PERSONA>
Actúa como un Gestor de Fondos Inmobiliarios. Tu misión es valorar el valor real de los activos frente al precio de mercado.
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
Para <SOCIMI>{name}</SOCIMI>, analiza:
1. **NAV (Net Asset Value):** Valor neto de los activos por acción. Compara con la cotización actual (¿cotiza con descuento?).
2. **LTV (Loan to Value):** Nivel de deuda sobre el valor de las propiedades (ideal < 40%).
3. **Ocupación:** Porcentaje de activos alquilados y duración media de los contratos (WAULT).
4. **Yield:** Rentabilidad bruta y neta de las rentas cobradas.
</INSTRUCTIONS>
"""
    else:
        sector_prompt = f"""
<OBJECTIVE_AND_PERSONA>
Eres un Analista Financiero Senior evaluando {name} a fecha de {current_date}.
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
Redacta un reporte estructurado en ESPAÑOL con Resumen, Tendencias, Análisis Fundamental y Recomendación final.
</INSTRUCTIONS>
"""

    # Calculate 30 days ago
    date_30_days_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()

    # 1. Definir los agentes
    data_agent = autogen.AssistantAgent(
        name="Data_Agent",
        system_message=f"""Eres el Agente de Datos Financieros para {name} ('{ticker}').
Hoy es la fecha de la petición: {current_date}.
Busca la información financiera más reciente (año {current_year} o el más cercano disponible) de la empresa y su cotización.
Para el análisis de la cotización, noticias y tendencias, DEBES utilizar el periodo de al menos los últimos 30 días (desde {date_30_days_ago} hasta {current_date}).

REGLAS ESTRICTAS E INQUEBRANTABLES:
1. NO PUEDES INVENTAR NI DEDUCIR ningún dato (cotizaciones, métricas, noticias).
2. ESTÁS OBLIGADO a usar las funciones/herramientas (get_stock_data, get_financial_metrics, get_company_news, get_stock_info) en tus mensajes.
3. Para ejecutar una herramienta, DEBES escribir ÚNICAMENTE un bloque JSON con este formato exacto y esperar a que el sistema te devuelva los datos:
```json
{{"name": "nombre_de_la_herramienta", "arguments": {{"parametro": "valor"}}}}
```
4. No respondas con excusas. Si no tienes datos, usa las herramientas. Tu único objetivo es recopilar los DATOS CRUDOS y NUMÉRICOS recibidos y devolverlos al Analyst_Agent.
5. REGLA DE NOMENCLATURA CRÍTICA DE PARÁMETROS: DEBES utilizar EXACTAMENTE los nombres de parámetros definidos en las herramientas. NUNCA uses la palabra `from` o `to` como clave JSON. Es OBLIGATORIO usar `start_date` y `end_date` estrictamente, de lo contrario causarás un CRASH FATAL.
Máximo 8 llamadas a herramientas. 
""",
        llm_config=ollama_config,
    )

    analyst_agent = autogen.AssistantAgent(
        name="Analyst_Agent",
        system_message=f"""{sector_prompt}

<CONSTRAINTS>
Base tu análisis estrictamente en los datos reales proveídos por el Data_Agent. No inventes años pasados si los datos son actuales.
El informe DEBE estar en ESPAÑOL.
</CONSTRAINTS>
""",
        llm_config=llm_config,
    )

    manager_agent = autogen.AssistantAgent(
        name="Manager_Agent",
        system_message="""Director de Análisis. Revisa el informe en español.
Si es correcto y profesional, escribe TERMINATE. Máximo 2 iteraciones.
""",
        llm_config=llm_config,
    )

    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    )

    # 2. Herramientas
    register_toolkits(
        [
            YFinanceUtils.get_stock_info,
            YFinanceUtils.get_stock_data,
            YFinanceUtils.get_income_stmt,
            YFinanceUtils.get_balance_sheet,
            FMPUtils.get_financial_metrics,
            FMPUtils.get_historical_market_cap,
            FinnHubUtils.get_company_news
        ],
        caller=data_agent,
        executor=user_proxy
    )

    # 3. Group Chat
    groupchat = autogen.GroupChat(
        agents=[user_proxy, data_agent, analyst_agent, manager_agent],
        messages=[],
        max_round=10,
        speaker_selection_method="round_robin"
    )
    chat_manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # 4. Iniciar Tarea
    task = f"Prepara un reporte de análisis exhaustivo de {name} ({ticker}). En español."
    
    # Almacenaremos el historial para extraer el reporte final
    chat_results = user_proxy.initiate_chat(
        chat_manager,
        message=task,
        summary_method="reflection_with_llm",
    )

    # Extraer el reporte del historial (usualmente el penúltimo mensaje antes de TERMINATE)
    # O simplemente guardamos el chat_result.summary si el LLM hace un buen trabajo resumiendo
    final_report = chat_results.summary
    
    # Guardar en archivo diferenciado por modelo
    safe_ticker = ticker.replace(".", "_")
    output_path = f"/home/ia/FinRobot-master/reporte_{safe_ticker}_{model_type}.md"
    
    with open(output_path, "w") as f:
        f.write(f"# Reporte FinRobot: {name} ({ticker})\n\n")
        f.write(final_report)
    
    print(f"[FinRobot Engine] Reporte guardado en: {output_path}")
    return output_path, final_report

if __name__ == "__main__":
    # Test rápido si se ejecuta directamente
    import sys
    if len(sys.argv) > 1:
        ticker_arg = sys.argv[1]
        name_arg = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
        model_arg = sys.argv[3] if len(sys.argv) > 3 else "local"
        run_finrobot_analysis(ticker_arg, name_arg, model_arg)
