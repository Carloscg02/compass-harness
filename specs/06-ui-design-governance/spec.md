# Especificación (Spec): `06-ui-design-governance`

- **ID de Feature**: `06-ui-design-governance`
- **Estado**: Borrador (Pendiente de aprobación humana)
- **Objetivo**: Dotar a `compass-harness` de un sistema de gobernanza de UI/Frontend que permita a desarrolladores backend crear interfaces con personalidad y calidad de estudio sin caer en *AI Slop* ni *Zombie UI*, mediante: (1) detección automática de contexto visual/UI en el inspector, (2) una 5.ª skill dedicada (`.compass/skills/ui-design/SKILL.md`) con entrevista guiada de diseño, catálogo interactivo de referencia (`https://ancient-prompt-design-flow.base44.app/`), arquetipos con personalidad y reglas duras Anti-Slop, y (3) creación perezosa (*Just-In-Time*) y auditoría del contrato `docs/brain/design.md`.

---

## 1. Contexto y Problema

Cuando un desarrollador con perfil Backend pide a un agente de IA que construya una interfaz gráfica:
1. **En proyectos desde cero (Greenfield UI)**: Como el usuario no domina la jerga de diseño visual, el agente toma decisiones por defecto estadísticamente mediocres (*AI Slop*): fondos blancos puros o azules oscuros genéricos con gradientes morados/índigo, fuente *Inter* sin jerarquía, layouts clónicos de 3 tarjetas simétricas con iconos en círculos y espaciados inconsistentes.
2. **En la implementación de componentes (*Zombie UI*)**: El agente programa únicamente el *Happy Path* con datos estáticos, olvidando los estados de carga (*Skeleton*), vacío (*Empty State*) y error, metiendo colores hexadecimales hardcodeados (`#3b82f6`) en mitad del JSX/HTML en vez de usar Design Tokens semánticos.
3. **Riesgo de Sobreingeniería / Context Rot**: Si obligamos a definir un sistema de diseño durante el `compass init` de una librería Python de backend o cargamos reglas de CSS en cada turno, desperdiciamos tokens y ensuciamos proyectos sin interfaz.

### La Solución Arquitectónica (Ambiciosa en Diseño, Simple en Infraestructura)
- **Creación Perezosa (*Just-In-Time Design Contract*)**: En `AGENTS.md` se instala un **UI / Frontend Gate**. Mientras el proyecto solo toque backend/CLI, el coste de tokens de UI es **cero** y no existe archivo `design.md`. En el instante en que una tarea (`FTD` o `SDD`) va a crear o modificar interfaz visual, el Gate detiene al agente y le exige abrir `.compass/skills/ui-design/SKILL.md`.
- **Doble Modo en `ui-design` (Coherencia Brownfield vs. Entrevista de Personalidad Greenfield)**:
  - Si el proyecto ya tiene UI o un `DESIGN.md`, el agente extrae los tokens existentes y mantiene coherencia total.
  - Si se diseña desde cero, el agente entrevista al desarrollador en lenguaje claro, le ofrece apoyarse en el catálogo interactivo **`https://ancient-prompt-design-flow.base44.app/`** o elegir entre arquetipos visuales con fuerte personalidad, y materializa las respuestas en el contrato **`docs/brain/design.md`**.
- **Auditoría Determinista en `compass check` y `compass status`**: Si el proyecto tiene activo un contrato de diseño (`docs/brain/design.md` o `DESIGN.md`), el verificador audita que cumpla su presupuesto de contexto (`<= 80` líneas) y que contenga las secciones mínimas obligatorias de tokens y reglas de componentes.

---

## 2. Alcance Funcional (Qué vamos a construir)

### 2.1 Detección de Contexto UI en `src/compass_harness/core/inspector.py`
Ampliar `ProjectInspection` (manteniendo compatibilidad hacia atrás con valores por defecto `()`) con dos campos deterministas:
- `detected_ui_signals: tuple[str, ...] = ()`: Detecta pistas de frontend/UI presentes en la raíz del proyecto (ej. `tailwind.config.*`, `components.json` de shadcn/ui, `next.config.*`, `vite.config.*`, `astro.config.*`, `svelte.config.*`).
- `existing_design_files: tuple[str, ...] = ()`: Detecta si ya existe `DESIGN.md` o `docs/brain/design.md`.
- En la Fase 1 de `compass init`, si se detectan señales de UI o archivos de diseño previos, se muestran en el bloque `COMPASS_ONBOARDING_REQUIRED`.

### 2.2 La 5.ª Skill: `.compass/skills/ui-design/SKILL.md` (`src/compass_harness/templates/compass_skills_assets.py`)
Se añade `ui-design` como 5.ª skill oficial del bundle en `.compass/skills/ui-design/SKILL.md` (y en `SKILL_NAMES` de `installer.py` para que `compass init --apply` cree también su enlace simbólico en `.agents/skills/ui-design`, `.claude/skills/ui-design` y `.cursor/skills/ui-design`).

Contenido estructurado de `.compass/skills/ui-design/SKILL.md`:
1. **Protocolo de Activación (Just-In-Time UI Gate)**:
   - Antes de escribir cualquier línea de HTML, CSS, Tailwind, React, Vue, Svelte o componente visual, comprobar si existe `docs/brain/design.md` (o `DESIGN.md` en la raíz).
2. **Camino A — Coherencia en Proyectos con UI Existente (Brownfield UI)**:
   - Si ya existen componentes, `tailwind.config.*`, `globals.css`, `components.json` o `DESIGN.md`, inspeccionar primero la paleta, tipografía, radios de borde y librería de componentes existentes y documentarlos en `docs/brain/design.md` para garantizar coherencia absoluta sin introducir un segundo estilo paralelo.
3. **Camino B — Entrevista de Diseño desde Cero para Desarrolladores Backend (Greenfield UI)**:
   - Prohibido escribir código visual sin antes consensuar la identidad con el usuario mediante 3 preguntas directas en el chat:
     1. **Propósito y Sensación**: Qué problema resuelve la interfaz y qué atmósfera debe transmitir (herramienta de precisión para ingenieros, producto editorial limpio, consola de telemetría/datos en vivo, producto comercial atrevido).
     2. **Exploración Visual Guiada**:
        - Ofrecer al usuario consultar o importar un prompt/sistema desde **`https://ancient-prompt-design-flow.base44.app/`** (o aportar cualquier URL/referencia que le guste).
        - O elegir uno de los **4 Arquetipos con Personalidad** predefinidos en la skill:
          - **`precision-dark` / `precision-light` (Estilo Linear / Raycast / Vercel)**: Superficies monocromáticas profundas, bordes de `1px` de bajo contraste, tipografía geométrica + monoespaciada (`tabular-nums`) para métricas, foco en velocidad y atajos de teclado.
          - **`warm-editorial` (Estilo Anthropic / Stripe Press / Read.cv)**: Superficies cálidas color papel/piedra (`#FAF8F5` / `#141413`, nunca `#FFFFFF` puro), titulares con serifa o sans humanista de alto contraste, mucho aire y ritmo de lectura.
          - **`telemetry-grid` (Estilo Grafana / Bloomberg / Industrial RF)**: Alta densidad de datos, rejillas visibles con separadores técnicos, código de colores semántico estricto (OK/Warn/Crit), cero ornamentos innecesarios.
          - **`neo-brutalist-craft` (Estilo Gumroad / Teen Engineering)**: Bordes sólidos (`2px`), sombras duras desplazadas sin desenfoque (`box-shadow: 4px 4px 0px`), acentos de alto impacto y micro-interacciones mecánicas.
     3. **Modo de Color y Stack de Componentes**: Tema oscuro, claro o adaptativo, y confirmación de primitivos (ej. `Tailwind` + `shadcn/ui` / `Radix`).
   - Tras la respuesta del usuario, generar **`docs/brain/design.md`** (máximo 80 líneas) y enlazarlo en `docs/brain/index.md`.
4. **Las 5 Leyes Duras Anti-Slop y Anti-Zombie UI (Obligatorias en cada tarea visual)**:
   - **Ley 1 — Prohibición de Clichés de IA (*Anti-Slop Ban List*)**: Prohibidos los gradientes morados/índigo/cian por defecto sobre blanco o azul marino; prohibido el layout clónico de "Hero centrado + 3 tarjetas iguales con icono circular"; prohibido usar únicamente la fuente por defecto sin definir pareja tipográfica (`--font-sans` / `--font-display` + `--font-mono` con `font-variant-numeric: tabular-nums` para datos numéricos).
   - **Ley 2 — Cero Valores Mágicos (*Design Tokens Only*)**: Prohibido hardcodear colores hexadecimales (`#3b82f6`) o píxeles arbitrarios en los componentes; todo debe consumir los tokens semánticos declarados en `docs/brain/design.md` (`surface`, `surface-elevated`, `text-primary`, `text-muted`, `border-subtle`, `accent-primary`).
   - **Ley 3 — Los 4 Estados Obligatorios (*Anti-Zombie UI*)**: Todo componente o vista asíncrona/con datos debe implementar explícitamente los 4 estados: **`Loading`** (skeletons que respeten la geometría final), **`Empty`** (estado vacío diseñado y útil), **`Error`** (con acción de recuperación) y **`Populated`**.
   - **Ley 4 — Jerarquía Espacial y Micro-interacciones**: Ritmo espacial en múltiplos de `4px`/`8px`, estados `:hover`, `:active` y `:focus-visible` distinguibles en todo elemento interactivo, transiciones rápidas con propósito (`150ms–220ms cubic-bezier(0.16, 1, 0.3, 1)`) y respeto a `prefers-reduced-motion`.
   - **Ley 5 — Estructura del Contrato `docs/brain/design.md`**: Debe incluir las secciones `## 1. Aesthetic Direction`, `## 2. Design Tokens`, `## 3. Typography & Spacing` y `## 4. Component & Anti-Slop Rules`.

### 2.3 Conexión en `AGENTS.md` y `sdd-workflow/SKILL.md` (`src/compass_harness/templates/`)
- En `AGENTS.md`:
  - Añadir la referencia a `[ui-design](.compass/skills/ui-design/SKILL.md)` en el catálogo de skills instaladas.
  - Incluir la regla de **UI / Frontend Gate**: cuando una tarea toque interfaz visual, exigir abrir `ui-design` y consultar/crear `docs/brain/design.md`.
- En `sdd-workflow/SKILL.md`:
  - Indicar que cuando una feature toque UI/Frontend, `plan.md` debe alinear el diseño con `docs/brain/design.md` (creándolo antes mediante la entrevista de `ui-design` si aún no existe) y `tasks.md` debe verificar en su **Prueba Observada** el cumplimiento de los 4 estados (*Loading, Empty, Error, Populated*), la ausencia de colores hardcodeados fuera de tokens y la ejecución de Playwright/E2E si aplica.

### 2.4 Auditoría del Contrato `design.md` en `src/compass_harness/core/verifier.py` y `cli.py`
- Ampliar `HarnessReport` con `has_design_contract: bool = False`.
- Si existe `docs/brain/design.md` en el proyecto:
  1. Verificar que no supere el presupuesto de **80 líneas** (`DESIGN_MAX_LINES = 80`); si lo supera, emitir `CheckIssue(code="BUDGET_EXCEEDED", path="docs/brain/design.md", ...)`.
  2. Verificar que contenga al menos la definición de **Design Tokens** (`Tokens` o `Paleta`) y **Typography** (`Typography` o `Tipografia`); si está vacío o incompleto, emitir `CheckIssue(code="INCOMPLETE_DESIGN_CONTRACT", path="docs/brain/design.md", ...)`.
- En `compass status`: mostrar si el contrato de diseño UI está activo (`Contrato UI (design.md): Activo` o `No requerido / Inactivo`).

---

## 3. Criterios de Aceptación (Requisitos para TDD)

Archivo de pruebas: `tests/test_ui_design_governance.py` (y actualización coherente del conteo de rutas del bundle de 12 a 13 en los tests existentes):

- **CA-1 (Detección de señales de UI y `DESIGN.md` en `inspect_project`)**: Si un directorio contiene `tailwind.config.js`, `components.json` o `DESIGN.md`, `inspect_project(root)` los reporta en `detected_ui_signals` y `existing_design_files`.
- **CA-2 (Inclusión de la 5.ª skill `ui-design` en el bundle y symlinks)**: `render_project_bundle(config)` incluye `.compass/skills/ui-design/SKILL.md` (con frontmatter YAML válido) y `apply_installation` crea el symlink `.agents/skills/ui-design` (y equivalentes para `claude`/`cursor`).
- **CA-3 (Contenido de `ui-design/SKILL.md` — Entrevista, URL de referencia, Arquetipos y Leyes Anti-Slop)**: `.compass/skills/ui-design/SKILL.md` incluye el protocolo Brownfield vs Greenfield, la URL de referencia `https://ancient-prompt-design-flow.base44.app/`, los 4 arquetipos con personalidad, la ley de los 4 estados (`Loading`, `Empty`, `Error`, `Populated`) y la prohibición de valores hexadecimales mágicos/clichés de IA.
- **CA-4 (Inyección del UI Gate en `AGENTS.md` y `sdd-workflow/SKILL.md` sin romper el presupuesto de `< 100` líneas)**: Tanto `AGENTS.md` como `sdd-workflow/SKILL.md` enlazan a `ui-design` y `docs/brain/design.md`, manteniendo `AGENTS.md` por debajo de 100 líneas.
- **CA-5 (Auditoría de `docs/brain/design.md` en `verify_harness` y `compass status` / `compass check`)**:
  - Si `docs/brain/design.md` no existe (proyecto backend puro), `verify_harness` pasa en verde (`has_design_contract=False`).
  - Si `docs/brain/design.md` existe y cumple el formato y `<= 80` líneas, `verify_harness` pasa en verde (`has_design_contract=True`) y `compass status` lo muestra como `Activo`.
  - Si `docs/brain/design.md` excede las 80 líneas o está incompleto (sin sección de Tokens/Typography), `verify_harness` falla con `BUDGET_EXCEEDED` o `INCOMPLETE_DESIGN_CONTRACT` y `compass check` devuelve código de salida `1`.
