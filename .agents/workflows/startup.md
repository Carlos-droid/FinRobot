# Startup Workflow: FinRobot + OpenBB Platform

Este workflow documenta los pasos necesarios para arrancar tanto el backend de FinRobot como la plataforma de datos de OpenBB, asegurando que ambos operen sin conflictos y optimizados para NVIDIA NIM.

## Requisitos Previos
- Entorno virtual en `/home/ia/FinRobot-master/OpenBB/.venv` activado.
- API Key de NVIDIA configurada en el `.env` de la raíz.

---

## 1. Arranque del Backend de FinRobot
El backend actúa como puente entre los agentes de FinRobot y los widgets de OpenBB.

// turbo
1. Navegar al directorio del backend e iniciar con uvicorn:
```bash
cd /home/ia/FinRobot-master/finrobot-backend
source ../OpenBB/.venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &
```

2. Verificar que el servidor responde:
```bash
curl http://localhost:8080/
```

---

## 2. Arranque de OpenBB Platform API
Para que los widgets de FinRobot puedan consultar datos de mercado reales localmente.

// turbo
3. Iniciar la API de OpenBB Platform:
```bash
cd /home/ia/FinRobot-master/
source OpenBB/.venv/bin/activate
nohup openbb-api > openbb_api.log 2>&1 &
```

4. Verificar que la API de OpenBB está levantada (Puerto 8000 por defecto):
```bash
curl http://localhost:8000/docs
```

---

## 3. Configuración en OpenBB Pro (Frontend)
Una vez ambos servicios estén corriendo:

1. Abrir [OpenBB Pro Workspace](https://pro.openbb.co/).
2. Ir a **Data Integrations** (icono de engranaje).
3. Añadir la siguiente URL como **Widget Integration**:
   - `http://localhost:8080/widgets.json`
4. Añadir la siguiente URL como **App Integration**:
   - `http://localhost:8080/apps.json`
5. Abrir la App **FinRobot Central** para ver el Dashboard completo.

---

## Notas de Mantenimiento
- **NVIDIA NIM Rate Limits**: El sistema tiene un delay de 1.5s entre peticiones para no colisionar con smartRAG. No reducir `NIM_RATE_LIMIT_DELAY` en el `.env` a menos que sea necesario.
- **Logs**:
    - FinRobot: `/home/ia/FinRobot-master/finrobot-backend/server.log`
    - OpenBB API: `/home/ia/FinRobot-master/openbb_api.log`
