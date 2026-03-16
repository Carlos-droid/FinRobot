---
name: openbb_workspace
description: Expert in OpenBB Workspace developer integrations, including custom backend data, widget configuration, and AI Copilot integration.
---

# Expertise in OpenBB Workspace Integrations

This skill enables the AI assistant to expertly configure, debug, and expand integrations within the OpenBB Workspace. It leverages official documentation to ensure all custom widgets, apps, and parameters follow the latest OpenBB standards.

## Key Knowledge Areas

1.  **Backend Data Integration**:
    - Configuring `widgets.json` to define endpoints, chart types, and metadata.
    - Handling `apps.json` for custom dashboard layouts.
    - Implementing CORS and robust routing for the OpenBB Frontend (`pro.openbb.co`).

2.  **Widget Types and Configurations**:
    - **AgGrid Tables**: Using `dataKey`, `renderFunctions` (like `columnColor`, `greenRed`), and `cell_click_grouping` to make interactive data tables.
    - **Plotly Charts**: Formatting API responses for interactive financial charts (candlesticks, line graphs).
    - **Markdown Widgets**: Serving data-rich markdown for reports and analysis summaries.
    - **Input Forms**: Creating complex parameter structures with `dropdowns`, `text inputs`, and `run buttons`.

3.  **AI Copilot & Orchestrator Integration**:
    - Configuring **MCP (Model Context Protocol)** tools within `widgets.json`.
    - Optimizing widgets for the **Orchestrator Mode** and **Generative UI**.
    - Managing context and tool mapping for assistant-driven data exploration.

## Consult Detailed Documentation

For specific implementation details, refer to the master documentation file:
- **`[workspace_reference.md](file:///home/ia/FinRobot-master/.agents/docs/openbb/workspace_reference.md)`**

## Common Tasks and Best Practices

- **Avoid 404s**: When adding a backend to OpenBB Pro via a full URL like `.../widgets.json`, ensure the server handles the `/widgets.json/` prefix for all sub-endpoints.
- **Table Parsing**: Use `"dataKey": "data"` in `widgets.json` if your API returns `{"data": [...]}`. Use `null` or `""` if the response is a raw array.
- **Run Button**: Use `"runButton": true` for long-running processes (e.g., AI analysis agents) to prevent timeouts and provide a better UX.
- **Grid Layout**: Plan `gridWidth` (max ~48-60) and `gridHeight` according to the content complexity.
