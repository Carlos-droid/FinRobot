## 🟢 CORE ESTATAL
- **Model Integration**: Unified FinRobot and Smart-RAG under **Ollama v0.17.5** with **Qwen 3.5 9B** as the default reference model.
- **Database (hybrid-scraper)**: Schema updated in `records` table. Añadida columna `thematic_topic` para trazabilidad de raspado.
- **Infrastructure**: Implementados lanzadores de escritorio (`.desktop`) y scripts de automatización (`.sh`) para FinRobot y Smart-RAG.
- **Crawl4AI**: Instalado en HDD (`/storage/slow/crawl4ai`) y configurado como CLI global en `~/.local/bin/crawl4ai`.
- **OpenBB-Docs**: Clonado en HDD (`/storage/slow/openbb-docs`). Repositorio de documentación oficial.

## 📦 DEPS & CONFIG
- `Ollama` -> upgraded to **v0.17.5** (server & client).
- `.env` (FinRobot & Smart-RAG): `OLLAMA_MODEL` set to `qwen3.5:9b`.
- `docker-compose.yml` (Smart-RAG): Inyectada variable `OLLAMA_MODEL`.

## ⚙️ LOGIC & FUNCTIONS
- `SemanticEngine.__init__`: Ahora lee `OLLAMA_MODEL` dinámicamente.
- `ThermalFilter.__init__`: Ahora lee `OLLAMA_MODEL` dinámicamente.
- `DBClient.insert_record()`: Firma modificada. Añadido parámetro `thematic_topic`.
- `main.run_pipeline()` (Smart-RAG): Lógica actualizada para persistir el tema detectado.

## ⚠️ PENDING/DEBT
- **Performance**: Qwen 3.5 es más lento (CoT). Los reportes de FinRobot tardan ~5-8min. Monitorizar posibles timeouts en widgets.
- **Reprocess**: El script `reprocess_topics.py` en Smart-RAG podría requerir actualización para alinearse con el nuevo esquema de la BD.
