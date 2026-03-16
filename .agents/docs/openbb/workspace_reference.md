# OpenBB Workspace - Referencia para Desarrolladores (Maestra)

Este documento recopila las reglas, estructuras y mejores prácticas extraídas de la documentación oficial de OpenBB Workspace para facilitar el desarrollo de integraciones personalizadas. Basado en la documentación de [docs.openbb.co/workspace](https://docs.openbb.co/workspace).

---

## 1. Estructura del Backend (Data Integration)

Para integrar una fuente de datos, el backend debe exponer dos archivos de configuración principales:

1.  **`widgets.json`**: Define los widgets disponibles, sus endpoints y parámetros (obligatorio).
2.  **`apps.json`**: Define el diseño predeterminado (layout) de los dashboards (opcional).

### Configuración del API Server (FastAPI)
- Debe permitir CORS para `https://pro.openbb.co`.
- Endpoints requeridos: `GET /widgets.json` y `GET /apps.json`.
- Los endpoints de datos deben devolver JSON o Markdown según el tipo de widget.

---

## 2. Tipos de Widgets

### Markdown
- **Propósito**: Mostrar texto enriquecido, informes o explicaciones.
- **Respuesta API**: Puede ser un string simple con markdown o un objeto `{"markdown": "# Contenido"}` o `{"content": "# Contenido"}`.

### AgGrid Table (Tablas)
- **Propósito**: Mostrar datos tabulares interactivos.
- **Configuración**:
  ```json
  "table_id": { "chartType": "aggrid", "endpoint": "/api/data", "data": { "dataKey": "data" } }
  ```
- **Respuesta API**: Objeto con una lista de diccionarios: `{"data": [{"col1": "val1"}, ...]}`.

### Plotly Charts
- **Propósito**: Gráficos interactivos complejos (velas, líneas, etc.).
- **Respuesta API**: Objeto con `data` (lista de trazos Plotly) y `layout` (opciones de diseño).

---

## 3. Configuración del Widget (Widget Configuration)

### Tamaño del Grid (`gridWidth` y `gridHeight`)
- Los widgets se posicionan en una cuadrícula.
- `gridWidth`: Ancho del widget (típicamente de 1 a 48 o 60).
- `gridHeight`: Alto del widget.

### Botón de Ejecución (`runButton`)
- Si se establece en `true`, el widget no cargará datos automáticamente. Aparecerá un botón "Confirmar" o "Ejecutar". Muy útil para procesos costosos (como agentes de IA).

### Tiempo de Expiración (`staleTime`)
- Tiempo en milisegundos para mantener los datos en caché antes de volver a solicitarlos.

---

## 4. Parámetros (Widget Parameters)

Se definen en la sección `parameters` de cada widget en `widgets.json`.

### Dropdown (Desplegable)
```json
{
    "id": "instrument_type",
    "name": "Tipo",
    "type": "dropdown",
    "options": [{ "label": "Stocks", "value": "stocks" }],
    "default": "stocks"
}
```

### Dependent Dropdown
Permite que las opciones de un desplegable dependan de otro.
- Utiliza **`optionsEndpoint`** en el parámetro hijo para obtener las opciones dinámicamente basadas en el valor del padre.
- Ejemplo: Si cambias el país en un dropdown, el dropdown de "Ciudad" se actualiza llamando al endpoint con la query param `?country=...`.

### Text Input (Entrada de Texto)
```json
{ "id": "ticker", "name": "Símbolo", "type": "text", "default": "AAPL" }
```

### Cell Click Grouping
Permite que al hacer clic en una celda de una tabla, otros widgets se actualicen automáticamente.
- En el widget de la tabla:
  ```json
  "cell_click_grouping": { "id_del_parametro_destino": "columna_de_la_tabla" }
  ```

### Tabs (Pestañas)
Permite crear selectores de tipo pestaña para cambiar la vista de los datos.
```json
{
    "id": "view_type",
    "name": "Vista",
    "type": "tabs",
    "options": [
        { "label": "Anual", "value": "annually" },
        { "label": "Trimestral", "value": "quarterly" }
    ],
    "default": "annually"
}
```

---

## 5. Render Functions

Permiten personalizar cómo se ven las celdas en las tablas `aggrid`.

- **`columnColor`**: Cambia el color del texto basado en el valor.
- **`profit_loss`**: Similar a columnColor pero con formato de moneda.
- **`hoverCard`**: Muestra una tarjeta informativa al pasar el ratón.
- **`greenRed`**: Colorea basado en positivo/negativo.

---

## 6. Funcionalidades de IA (Copilot)

### Model Context Protocol (MCP) y Agentes
OpenBB Workspace puede mapear herramientas de MCP a widgets usando la sección `mcp` en `widgets.json`.

### Orchestrator Mode (Beta)
Permite al Copiloto detectar qué agentes son necesarios para una tarea y delegar subtareas a cada uno. Actívalo para flujos multi-agente complejos.

### Generative UI
El Copiloto puede actualizar parámetros de widgets existentes o incluso añadir nuevos widgets al dashboard basándose en la conversación.

---

## 7. Glosario de Widgets (Resumen)

| Tipo | Uso Principal | Endpoint Devuelve |
| :--- | :--- | :--- |
| `markdown` | Texto, informes, notas | String Markdown o `{"markdown": "..."}` |
| `aggrid` | Tablas de datos, filtrado | `{"data": [...]}` |
| `plotly` | Gráficos de velas, líneas | `{"data": [...], "layout": {...}}` |
| `metric` | KPIs, valores únicos | `{"value": 123, "label": "Precio"}` |
| `html` | Dashboards embebidos | `{"html": "<html>..."}` |
| `tabs` | Navegación interna | (Se usa como parámetro para filtrar vistas) |

---

## Enlaces de Referencia Rápidos
- [Estructura del Backend](https://docs.openbb.co/workspace/developers/data-integration)
- [Tipos de Parámetros](https://docs.openbb.co/workspace/developers/widget-parameters/dropdown)
- [Funcionalidades de IA](https://docs.openbb.co/workspace/analysts/ai-features/copilot-basics)
