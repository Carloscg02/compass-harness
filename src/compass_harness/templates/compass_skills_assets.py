"""Plantillas generadoras para las skills propias de Compass."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compass_harness.core.renderer import ProjectConfig


def render_project_architect_skill(config: "ProjectConfig") -> str:
    """Genera .compass/skills/project-architect/SKILL.md."""
    return f"""---
name: project-architect
description: Negociacion de arquitectura de software y diagnostico Greenfield vs Brownfield.
---

# Project Architect Skill

Guia al agente en la negociacion arquitectonica y estructuracion inicial para `{config.project_name}`.

## 1. Principio Rector: Hexagonal por Defecto pero Adaptable
- Por defecto, propone Arquitectura Hexagonal / Puertos y Adaptadores con separacion estricta entre Dominio e I/O.
- Evalua la naturaleza y tamano real del proyecto. Si una arquitectura en capas (`layered`), MVC (`mvc`) o script modular (`script`) es mas idonea, acuerda el cambio antes de escribir codigo.
- Registra el estilo acordado (`{config.architecture_style}`) en `docs/brain/architecture.md`.
- Genera el ADR fundacional en `docs/brain/decisions/0001-initial-architecture.md`.

## 2. Diagnostico Greenfield vs Brownfield y Regla de Granularidad de `modules/`
- Si el proyecto es **Greenfield**: inicializa el cerebro limpio con politicas de testing y carpetas base.
- Si el proyecto es **Brownfield**: inspecciona dependencias, tests existentes y estructura previa sin sobreescribir la logica de negocio.
- **Regla Estricta para `docs/brain/modules/` (Vertical Domain Slices, NUNCA Capas Horizontales)**:
  - **PROHIBIDO** crear fichas de modulos por capas tecnicas horizontales como `domain.md`, `application.md`, `adapters.md`, `controllers.md` o `models.md`. La explicacion de las capas horizontales vive unicamente en `docs/brain/architecture.md`.
  - **OBLIGATORIO**: Agrupa `docs/brain/modules/<capacidad>.md` por **Subsistemas Funcionales o Capacidades de Dominio** (Bounded Contexts / Feature Domains, por ejemplo: `auth-and-users.md`, `tax-calculation-engine.md`, `invoice-ai-extraction.md`, `market-valuation.md`, `property-and-lease-management.md`, `frontend-ui.md`).
  - Cada ficha funcional en `docs/brain/modules/<capacidad>.md` debe mapear el corte vertical completo de esa capacidad:
    1. Que entidades/puertos de dominio usa.
    2. Que casos de uso ejecuta.
    3. Que adaptadores concretos (DB, APIs externas, IA, PDF) y rutas HTTP/UI involucra.
    4. Donde estan sus tests especificos.
- **Consolidacion de Contratos UI y Archivos Legacy en Brownfield**:
  - Si existe un `DESIGN.md` en la raiz del proyecto, sintetiza sus tokens, tipografia y reglas en `docs/brain/design.md` (`<= 80` lineas) durante el onboarding para que el contrato UI quede activo en el Cerebro.
  - Si existen archivos de arneses antiguos (`agents.md` en minusculas, `SDD-WoW.md`, `.agent/`), advierte al usuario y consolida su conocimiento util en el nuevo Cerebro para no dejar dos routers contradictorios (`AGENTS.md` vs `agents.md`).
"""


def render_sdd_workflow_skill(config: "ProjectConfig") -> str:
    """Genera .compass/skills/sdd-workflow/SKILL.md."""
    return f"""---
name: sdd-workflow
description: Flujo formal Spec-Driven Development (spec -> plan -> tasks) con Seams, ADR Gate, Puerta de Auditoria y verificacion proporcional.
---

# SDD Workflow Skill

Define el flujo formal de trabajo guiado por especificacion para `{config.project_name}`.

## 1. Fases del Flujo SDD
1. **Especificacion (`specs/<feature>/spec.md`)**:
   - Requerimientos funcionales, contexto del problema y Criterios de Aceptacion (CA) numerados.
   - Identificacion preliminar de Seams.
2. **Plan Tecnico (`specs/<feature>/plan.md`)**:
   - **Architecture Alignment**: Alineacion con `docs/brain/architecture.md`.
   - **ADR Gate**: Consulta obligatoria a `docs/brain/decisions/index.md` antes de introducir patrones nuevos.
   - **UI / Frontend Gate**: Si la feature toca interfaz visual, alinear con `docs/brain/design.md` (creandolo antes con la skill `ui-design` si no existe) y comprobar en `docs/brain/architecture.md` si `E2E / Browser UI Tests` sigue en `N/A`; si es `N/A`, ofrecer e incluir como Tarea 1 de la feature el Auto-Bootstrap de `Agent Eyes` (Playwright + `ariaSnapshot` + Responsive Overflow Check) definido en `ui-design`.
   - **Seams bajo Prueba**: Acuerda costuras publicas de prueba apoyandose en la skill `tdd` (tests unitarios y de integracion entre modulos reales, sin acoplamiento a detalles internos).
3. **Lista de Tareas (`specs/<feature>/tasks.md`)**:
   - Tareas verticales siguiendo el ciclo estricto `RED -> GREEN -> REFACTOR`.
   - Exigencia de **Prueba Observada** (Observed Proof) en consola para cada tarea completada.
   - En tareas de UI, verificar en la **Prueba Observada** los 4 estados (Loading, Empty, Error, Populated), ausencia de colores hardcodeados fuera de tokens y la inspeccion semantica en vivo (`ariaSnapshot` + Responsive Check en `375px` y `1280px`).
4. **Implementacion TDD (Builder Subagent)**:
   - Delegacion en subagente con modelo rapido (`flash` / fast tier) ejecutando el bucle RED-GREEN-REFACTOR de forma aislada.
5. **Puerta de Auditoria Independiente (Auditor Subagent)**:
   - Evaluacion adversarial con contexto limpio (*clean context*) y modelo rapido (`flash` / fast tier) aplicando la Rubrica de 4 Puntos.
6. **Consolidacion de Cerebro y Modo Mentor (Main Agent)**:
   - Actualizacion de `docs/brain/index.md`, `modules/`, `handoff.md` y redaccion de guia didactica en `guides/`.

## 2. Puerta de Auditoria Independiente (Auditor Subagent)
Para prevenir la ceguera de taller (*Builder Blindness*) y la degradacion de contexto acumulado, una vez completadas las tareas en `tasks.md`, el Main Agent invoca un **Auditor Subagent** efimero con contexto limpio (*clean context*).

### Protocolo de Invocacion:
- **Entrada Minima**: `specs/<feature>/spec.md`, `specs/<feature>/plan.md`, `specs/<feature>/tasks.md` y el diff de cambios.
- **Rol de Solo Lectura**: El Auditor Subagent **no edita codigo**. Unicamente analiza, ejecuta comandos de verificacion y emite un veredicto estructurado.

### Rubrica de 4 Puntos de Auditoria:
1. **Trazabilidad de Criterios de Aceptacion (CA-X)**:
   - Mapear cada Criterio de Aceptacion de `spec.md` contra aserciones reales en los tests y componentes del codigo.
   - Ningun CA puede quedar sin verificacion comprobable.
2. **Ejecucion Determinista de Comandos**:
   - Ejecutar obligatoriamente `{config.test_command}` y `{config.lint_command}`.
   - Si aplica harness o verificador propio, ejecutar `compass check` o la herramienta oficial del proyecto.
   - Comprobar que todos los comandos finalizan con exito (exit code 0).
3. **Inspeccion de Anti-Patrones de IA**:
   - Ausencia de mocks sobre el sistema bajo prueba (SUT). Solo se mockean fronteras externas declaradas.
   - Ausencia de tests tautologicos, asserts vacios o pruebas triviales que no validan comportamiento real.
   - Ausencia de bloques `except: pass` silenciosos, prints residuales de depuracion o branches incompletos.
4. **Veredicto Binario Estructurado**:
   - El reporte debe concluir obligatoriamente con uno de los dos veredictos:
     - `VERDICT: APPROVED`: Todos los CAs trazados, comandos en verde y cero anti-patrones.
     - `VERDICT: REJECTED`: Lista procesable y numerada de hallazgos especificos (archivo, linea y causa de rechazo).

### Bucle de Retroalimentacion (Feedback Loop):
- Si el veredicto es `VERDICT: REJECTED`, el Auditor retorna el informe al Main Agent sin modificar ningun archivo.
- El Main Agent crea tareas de correccion puntuales y despacha nuevamente al Builder Subagent.
- Tras la correccion, se re-invoca al Auditor Subagent hasta obtener `VERDICT: APPROVED`.

## 3. Regla de Verificacion Proporcional
- El subagente constructor con modelo rapido (`flash` / fast tier) ejecuta los tests unitarios e integracion (`{config.test_command}`) en cada ciclo vertical.
- Si la feature modifica la interfaz de usuario o flujos completos de aplicacion y el proyecto declara soporte para Playwright / E2E (`{config.e2e_command}`) en `docs/brain/architecture.md`, anade una tarea final de verificacion E2E ejecutada tambien por el subagente ligero.
- Nunca inventar un test runner que no este declarado en `docs/brain/architecture.md`.
"""


def render_mentor_guide_skill(config: "ProjectConfig") -> str:
    """Genera .compass/skills/mentor-guide/SKILL.md."""
    return f"""---
name: mentor-guide
description: Generador bajo demanda de guias educativas tecnicas (guides/<slug>-GUIDE.md) con doble lente.
---

# Mentor Guide Skill

Define el protocolo para redactar guias didacticas profundas en `guides/` para el proyecto `{config.project_name}`.

## 1. Disparador
Se activa cuando el usuario solicita una explicacion profunda, un tutorial o cuando se cierra un hito relevante y se requiere transferir conocimiento pedagogico.

## 2. Enfoque de Doble Lente
Cada guia generada en `guides/<slug>-GUIDE.md` debe combinar dos perspectivas:
1. **Lente de Ingenieria de Software**:
   - Principios de diseno, modularidad, patrones de arquitectura limpia y testing riguroso (TDD).
   - Analisis de trade-offs, mantenibilidad y robustez de codigo.
2. **Lente de Dominio Tecnico**:
   - Dominio especifico del proyecto: `{config.domain}`.
   - Conceptos teoricos y practicos propios de dicho dominio aplicados en el codigo del repositorio.

## 3. Estructura Didactica
- Introduccion y contextualizacion del problema.
- Fundamentos teoricos (diagramas Mermaid cuando aporten claridad).
- Diseccion del codigo implementado en el repositorio (referenciando archivos y funciones).
- Lecciones aprendidas y buenas practicas recomendadas.
"""


def render_ui_design_skill(config: "ProjectConfig") -> str:
    """Genera .compass/skills/ui-design/SKILL.md."""
    return f"""---
name: ui-design
description: Gobernanza de diseno UI/Frontend, entrevista guiada, arquetipos con personalidad y reglas duras Anti-Slop.
---

# UI Design Skill: `{config.project_name}`

Gobernanza de interfaz grafica y diseno para evitar AI Slop y Zombie UI en `{config.project_name}`.

## 1. Protocolo de Activacion (Just-In-Time UI Gate)
Antes de escribir o modificar codigo de interfaz visual (HTML, CSS, Tailwind, React, Vue, Svelte o componentes), comprobar si existe `docs/brain/design.md` (o `DESIGN.md` en la raiz). Si no existe, detenerse inmediatamente y ejecutar este protocolo antes de programar componentes.

## 2. Camino A — Coherencia en Proyectos con UI Existente (Brownfield UI)
Si el proyecto ya contiene componentes frontend, configuraciones de Tailwind/PostCSS (`tailwind.config.*`), `globals.css`, `components.json` o un `DESIGN.md` previo:
1. Inspeccionar la paleta de colores, tipografia, radios de borde y libreria de componentes existentes.
2. Extraer y formalizar estos acuerdos en `docs/brain/design.md` respetando la direccion visual previa para evitar estilos paralelos inconsistentes.

## 3. Camino B — Entrevista de Diseno desde Cero (Greenfield UI)
Prohibido generar codigo visual por defecto sin antes consensuar la direccion con el desarrollador mediante 3 preguntas breves en el chat:
1. **Proposito y Sensacion**: Que problema resuelve la interfaz y que atmosfera debe transmitir (precision tecnica, calidez editorial, telemetria industrial, o audacia neo-brutalista).
2. **Exploracion Visual Guiada**:
   - Ofrecer consultar o importar estilos desde el catalogo interactivo de referencia: `https://ancient-prompt-design-flow.base44.app/`
   - O elegir uno de los 4 Arquetipos con Personalidad:
     - `precision-dark` / `precision-light`: Superficies monocromaticas oscuras/claras (estilo Linear / Raycast / Vercel), bordes de 1px de bajo contraste, tipografia geometrica y monoespaciada (`tabular-nums`) para metricas.
     - `warm-editorial`: Superficies calidas color papel/piedra (`#FAF8F5` / `#141413`, nunca blanco puro), titulares con serifa o sans humanista de alto contraste, aire y ritmo de lectura amplio (estilo Anthropic / Stripe Press / Read.cv).
     - `telemetry-grid`: Alta densidad de datos, rejillas tecnicas visibles, codigo de color semantico estricto (OK/Warn/Crit) sin ornamentos superfluos (estilo Grafana / Bloomberg / Industrial RF).
     - `neo-brutalist-craft`: Bordes solidos de 2px, sombras duras desplazadas sin desenfoque (`box-shadow: 4px 4px 0px`), acentos de alto impacto y micro-interacciones mecanicas (estilo Gumroad / Teenage Engineering).
3. **Modo de Color y Stack de Componentes**: Modo oscuro, claro o adaptativo, y primitivos de componentes (ej. Tailwind CSS + Radix / shadcn-ui).

Tras acordar las respuestas, generar `docs/brain/design.md` (presupuesto maximo: 80 lineas) y registrar su enlace en `docs/brain/index.md`.

## 4. Las 5 Leyes Duras Anti-Slop y Anti-Zombie UI
1. **Ley 1 — Prohibicion de Cliches de IA (Anti-Slop Ban List)**: Prohibidos los gradientes morados/indigo/cian por defecto sobre blanco o azul marino; prohibido el layout clonico de 'Hero centrado + 3 tarjetas con iconos circulares'; obligatoria la pareja tipografica con `tabular-nums` para datos numericos.
2. **Ley 2 — Cero Valores Magicos (Design Tokens Only)**: Prohibido hardcodear colores hexadecimales sueltos (`#3b82f6`) o pixeles arbitrarios en componentes. Todo elemento debe consumir tokens semanticos declarados en `docs/brain/design.md` (`surface`, `surface-elevated`, `text-primary`, `text-muted`, `border-subtle`, `accent-primary`).
3. **Ley 3 — Los 4 Estados Obligatorios (Anti-Zombie UI)**: Todo componente o vista asincrona con datos debe implementar explicitamente los 4 estados: `Loading` (skeletons con la geometria final), `Empty` (vacio util y disenado), `Error` (mensaje claro con accion de recuperacion) y `Populated`.
4. **Ley 4 — Jerarquia Espacial y Micro-interacciones**: Ritmo en multiplos de 4px/8px, estados `:hover`, `:active` y `:focus-visible` nitidos, transiciones de 150ms-220ms y respeto a `prefers-reduced-motion`.
5. **Ley 5 — Estructura Obligatoria de `docs/brain/design.md`**: El contrato debe contener obligatoriamente:
   - `## 1. Aesthetic Direction`
   - `## 2. Design Tokens`
   - `## 3. Typography & Spacing`
   - `## 4. Component & Anti-Slop Rules`

## 5. Semantic DOM & Live UI Inspection ("Agent Eyes")
Un agente que escribe UI sin inspeccionar el DOM vivo trabaja a ciegas; pero usar capturas de pantalla gigantes o HTML crudo agota el contexto. Siempre que se cree o modifique UI:

### 5.1 Auto-Bootstrap cuando el Proyecto empieza desde Cero o no tiene Navegador Configurado
Al activarse esta skill (tanto en un proyecto Greenfield donde se introduce UI por primera vez como en un proyecto Brownfield sin E2E), revisa `docs/brain/architecture.md`:
- Si `E2E / Browser UI Tests` esta en `N/A` y no dispones de una herramienta nativa de inspeccion semantica (`egolite`, Playwright MCP o Browser DOM Tool), **propon activamente al usuario configurarlo por el**:
  > "Detecto que vamos a desarrollar interfaz visual pero el proyecto aun no tiene configurado el verificador semantico de navegador ('Agent Eyes'). Como perfil backend no necesitas configurarlo a mano: si me das el OK, instalo Playwright ligero, creo el test base de Snapshot Semantico (`ariaSnapshot`) + chequeo responsive (`375px` y `1280px`) y actualizo `docs/brain/architecture.md`."
- Tras el OK del usuario, el agente ejecuta la configuracion segun el stack:
  - **Node / TypeScript / Next / Vite**: Instalar `@playwright/test` (`npm i -D @playwright/test && npx playwright install chromium`), crear `tests/e2e/ui-health.spec.ts` y actualizar `E2E / Browser UI Tests` en `docs/brain/architecture.md` a `npx playwright test`.
  - **Python (FastAPI / Flask / Django / Streamlit)**: Instalar `pytest-playwright` (`pip install pytest-playwright && playwright install chromium`), crear `tests/e2e/test_ui_health.py` y actualizar `docs/brain/architecture.md`.

### 5.2 Regla de Verificacion Visual en 3 Puntos (Pre-Completion Check)
Antes de marcar cualquier tarea de UI como `[x]` en `tasks.md`, el subagente constructor (`flash` / fast tier) debe verificar sobre el DOM renderizado y registrar en **Prueba Observada**:
1. **Semantic Accessibility Tree (`ariaSnapshot` / DOM Roles)**: Capturar el arbol semantico (`await page.locator('body').ariaSnapshot()` o equivalente en `egolite`/MCP) confirmando que existen los headings en jerarquia (`h1 -> h2`), botones/inputs con etiqueta accesible y los estados requeridos.
2. **Responsive Viewport & Overflow Check (`375x812` Mobile y `1280x800` Desktop)**: Evaluar en ambos tamanos de ventana que `document.documentElement.scrollWidth <= document.documentElement.clientWidth` (cero desbordamiento horizontal roto ni solapamientos).
3. **Zero Runtime / Console Errors**: Confirmar 0 errores en `page.on('pageerror')` y `console.error` al renderizar la vista.
"""
