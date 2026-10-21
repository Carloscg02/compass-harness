# Plan Técnico: `06-ui-design-governance`

- **ID de Feature**: `06-ui-design-governance`
- **Spec asociada**: `specs/06-ui-design-governance/spec.md`
- **Estado**: Aprobado para Ejecución TDD

---

## 1. Architecture Alignment (Alineación con `docs/brain/architecture.md`)

1. **Separación de capas**:
   - `src/compass_harness/core/inspector.py`: Añade detección determinista de señales de UI (`detected_ui_signals`) y contratos de diseño existentes (`existing_design_files`) en `ProjectInspection`.
   - `src/compass_harness/templates/compass_skills_assets.py` y `brain_assets.py`: Añade `render_ui_design_skill(config)` (`.compass/skills/ui-design/SKILL.md`), actualiza `AGENTS.md` con el **UI / Frontend Gate** y la referencia a `ui-design` (manteniendo `< 100` líneas), y conecta `sdd-workflow` con el contrato `docs/brain/design.md`.
   - `src/compass_harness/core/renderer.py` e `installer.py`: Registra `.compass/skills/ui-design/SKILL.md` en `render_project_bundle` (pasando de 12 a 13 rutas base del bundle) y añade `"ui-design"` a `SKILL_NAMES` en `installer.py` (creando el 5.º enlace simbólico por asistente).
   - `src/compass_harness/core/verifier.py` y `cli.py`: Audita opcionalmente `docs/brain/design.md` cuando existe en el proyecto (`has_design_contract`, límite `DESIGN_MAX_LINES = 80` -> `BUDGET_EXCEEDED`, y secciones de Tokens y Typography -> `INCOMPLETE_DESIGN_CONTRACT`).
2. **Seams (Costuras públicas bajo prueba)**:
   - `inspect_project(root)` (`detected_ui_signals`, `existing_design_files`).
   - `render_project_bundle(config)` y `apply_installation(root, config)`.
   - `verify_harness(root)` y los comandos CLI `compass init`, `compass status` y `compass check`.

---

## 2. Diseño Detallado de Componentes

### 2.1 `src/compass_harness/core/inspector.py`
- Constantes nuevas:
  ```python
  UI_SIGNAL_FILES: dict[str, str] = {
      "tailwind.config.js": "tailwind",
      "tailwind.config.ts": "tailwind",
      "tailwind.config.mjs": "tailwind",
      "postcss.config.js": "postcss",
      "components.json": "shadcn-ui",
      "next.config.js": "nextjs",
      "next.config.ts": "nextjs",
      "next.config.mjs": "nextjs",
      "vite.config.ts": "vite",
      "vite.config.js": "vite",
      "astro.config.mjs": "astro",
      "svelte.config.js": "svelte",
  }
  UI_EXTENSIONS: set[str] = {".tsx", ".jsx", ".vue", ".svelte", ".css"}
  DESIGN_CONTRACT_FILES: tuple[str, ...] = ("DESIGN.md", "docs/brain/design.md")
  ```
- En `ProjectInspection`:
  - `detected_ui_signals: tuple[str, ...] = ()`
  - `existing_design_files: tuple[str, ...] = ()`
  - Si existen archivos en `UI_SIGNAL_FILES` o se encuentran archivos con extensión en `UI_EXTENSIONS` durante el `os.walk` (registrando p. ej. `"frontend-components"`), se incluyen en `detected_ui_signals`.

### 2.2 `src/compass_harness/templates/compass_skills_assets.py` (`render_ui_design_skill`)
Genera `.compass/skills/ui-design/SKILL.md` con frontmatter YAML (`name: ui-design`, `description: ...`) y las siguientes secciones:
1. **Just-In-Time UI Gate**: Si una tarea toca interfaz visual y no existe `docs/brain/design.md` (ni `DESIGN.md`), detenerse antes de escribir código.
2. **Camino A — Coherencia Brownfield**: Si el proyecto ya tiene UI o `DESIGN.md`, extraer paleta, tipografía y librería de componentes a `docs/brain/design.md` manteniendo coherencia total.
3. **Camino B — Entrevista de Diseño desde Cero (Greenfield UI)**:
   - Hacer 3 preguntas breves al desarrollador (Propósito/Sensación, Dirección Visual y Tema/Stack).
   - Ofrecer como recurso interactivo de exploración **`https://ancient-prompt-design-flow.base44.app/`** o elegir uno de los 4 arquetipos con personalidad:
     - `precision-dark` / `precision-light` (Estilo Linear / Raycast / Vercel)
     - `warm-editorial` (Estilo Anthropic / Stripe Press / Read.cv)
     - `telemetry-grid` (Estilo Grafana / Bloomberg / Industrial RF)
     - `neo-brutalist-craft` (Estilo Gumroad / Teenage Engineering)
   - Generar `docs/brain/design.md` (`<= 80` líneas) y enlazarlo en `docs/brain/index.md`.
4. **Las 5 Leyes Anti-Slop y Anti-Zombie UI**:
   - Prohibición de clichés de IA (gradientes morados/índigo por defecto, layout clónico de 3 tarjetas con icono circular, fuente única sin `tabular-nums`).
   - Cero valores mágicos (prohibido hardcodear colores hexadecimales o píxeles fuera de Design Tokens).
   - Ley de los 4 Estados obligatorios: `Loading`, `Empty`, `Error`, `Populated`.
   - Jerarquía espacial (`4px`/`8px`) y micro-interacciones (`150ms-220ms`, `:focus-visible`, `prefers-reduced-motion`).
   - Estructura obligatoria de `docs/brain/design.md` (`## 1. Aesthetic Direction`, `## 2. Design Tokens`, `## 3. Typography & Spacing`, `## 4. Component & Anti-Slop Rules`).

### 2.3 `src/compass_harness/core/verifier.py` y `cli.py`
- `DESIGN_MAX_LINES = 80`.
- En `HarnessReport`: añadir campo `has_design_contract: bool = False`.
- Si `(root_path / "docs/brain/design.md").is_file()`:
  - `has_design_contract = True`.
  - Si `len(lines) > DESIGN_MAX_LINES` -> `CheckIssue(code="BUDGET_EXCEEDED", path="docs/brain/design.md", ...)`.
  - Si el contenido (en minúsculas) no menciona `"token"`/`"paleta"` o no menciona `"typograph"`/`"tipograf"` -> `CheckIssue(code="INCOMPLETE_DESIGN_CONTRACT", path="docs/brain/design.md", ...)`.
- En `cli.py`:
  - En `compass init` (Fase 1): mostrar `Señales UI detectadas` y `Contratos de diseño previos` si existen.
  - En `compass status`: imprimir `Contrato UI (design.md): Activo` si `report.has_design_contract` es `True`, o `No requerido / Inactivo` en caso contrario.
