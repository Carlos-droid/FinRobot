# Guía de Contribución (CONTRIBUTING)

¡Gracias por tu interés en contribuir a FinRobot! Para mantener el proyecto escalable, coherente y robusto, seguimos ciertas normas básicas de estilo y administración de entornos.

## 1. Entorno Virtual y Dependencias (Recomendación `uv`)

Siempre garantizamos la aislación del sistema usando entornos virtuales. Utiliza `uv` (herramienta de Rust extremadamente rápida para Python) para la configuración.

### Instalación Básica de Entorno
En la raíz de tu proyecto:
```bash
# Crear entorno virtual
uv venv .venv

# Activar en Linux/Mac
source .venv/bin/activate

# Instalar los requirements base (y también resolver docker text)
uv pip install -r requirements.txt
uv pip install -e .
```

Si vas a desarrollar en el _backend_ dedicado a **OpenBB**, te recomendamos utilizar su propio entorno aislado en `finrobot-backend` o usar activadores similares.

## 2. Estándares de Código y Estilos

- **No usar `import *`**: Nunca utilices `from module import *`. Esto contamina el _namespace_ y rompe el autocompletado y análisis estático (flake8, ruff). Usa siempre importaciones explícitas de módulos o clases: `from .data_source import YFinanceUtils`.
- **Typing y Annotated**: FinRobot se basa pesadamente en la integración de Automagica y LLMs; documenta los parámetros usando `typing.Annotated`. Las descripciones allí dentro son literalmente los manuales que lee el Agente.
- **Errores**:
  - Evitar el uso persistente de variables globales para flujos y nunca dejes fallos de APIs externas pasar indiscriminadamente.
  - Asegura usar el bloque `try/except` para llamadas a Internet y `HTTPException` o logs en el backend, no un simple `print`.
- **Desacople I/O**: Cuando desarrolles lógicas en `finrobot.functional`, separa la extracción/cálculos numéricos de la impresión por pantalla o guardado duro a disco.

## 3. Cómo Proponer tus Cambios
1. Haz un branch dedicado para tu Feature: `git checkout -b feature/nueva-fuente-datos`
2. Cuando el código cumpla los estándares de esta guía, haz tus *commits*.
3. Crea tu Pull Request. Validaremos que la documentación haya sido actualizada si afecta a contratos del Backend o a la Arquitectura Central.
