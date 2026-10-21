# Plan Técnico: `03-templates-and-skills`

- **ID de Feature**: `03-templates-and-skills`
- **Spec asociada**: `specs/03-templates-and-skills/spec.md`
- **Estado**: Aprobado para Ejecución TDD

---

## 1. Architecture Alignment (Alineación con `docs/brain/architecture.md`)

1. **Separación de capas**:
   - `src/compass_harness/templates/`: Catálogo estático de plantillas y constantes de texto para el Router (`AGENTS.md`), el Cerebro (`docs/brain/...`) y las 4 skills (`.compass/skills/...`), incluyendo el paquete íntegro de la skill oficial `tdd` de Matt Pocock (`SKILL.md`, `tests.md`, `mocking.md`).
   - `src/compass_harness/core/renderer.py`: Lógica pura de dominio (`ProjectConfig` y `render_project_bundle(config) -> dict[str, str]`). Recibe un objeto inmutable `ProjectConfig` y devuelve un diccionario en memoria `{ruta_relativa: contenido}` sin escribir nada en el sistema de ficheros ni depender de `typer` o `rich`.
2. **Seams (Costuras públicas bajo prueba)**:
   - El Seam público que probarán nuestros tests en `tests/test_templates_and_skills.py` es `ProjectConfig` + `render_project_bundle(config)` exportados en `compass_harness.core.renderer` y `compass_harness.core`.
3. **ADR Gate**:
   - No contradice ningún ADR existente; implementa en código los ADRs `0002` (Meta-Harness Agnostic Design), `0003` (Model Routing & Fast Subagent Delegation) y `0005` (3-Tier Brain Hierarchy & ADR Gate).

---

## 2. Diseño de Componentes

### 2.1 `src/compass_harness/templates/tdd_skill_assets.py`
Contiene las 3 cadenas literales exactas de la skill oficial `tdd` de Matt Pocock (`https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd`):
- `TDD_SKILL_MD`: Contenido de `.compass/skills/tdd/SKILL.md` (`name: tdd`, `What a good test is`, `Seams: where tests go`, `Anti-patterns`, `Horizontal slicing` vs `vertical slices`, `Rules of the loop`).
- `TDD_TESTS_MD`: Contenido de `.compass/skills/tdd/tests.md` (ejemplos de tests acoplados a implementación y tautológicos frente a tests orientados a comportamiento público).
- `TDD_MOCKING_MD`: Contenido de `.compass/skills/tdd/mocking.md` (regla de hacer mock solo en *system boundaries*, inyección de dependencias e interfaces estilo SDK).

### 2.2 `src/compass_harness/templates/compass_skills_assets.py`
Funciones generadoras para las 3 skills propias de Compass:
- `render_project_architect_skill(config: ProjectConfig) -> str`:
  - `.compass/skills/project-architect/SKILL.md` con frontmatter YAML (`name: project-architect`, `description: ...`).
  - Guía la negociación de arquitectura (`hexagonal` por defecto frente a `layered`, `mvc`, `script`) y el análisis de proyectos `GREENFIELD` vs `BROWNFIELD`.
- `render_sdd_workflow_skill(config: ProjectConfig) -> str`:
  - `.compass/skills/sdd-workflow/SKILL.md` con frontmatter YAML (`name: sdd-workflow`, `description: ...`).
  - Define el flujo `FTD` y `SDD` (`spec.md -> plan.md -> tasks.md`).
  - Conecta explícitamente con los **Seams** de la skill `tdd` de Matt Pocock (tests unitarios y de integración entre módulos reales), incluye el **ADR Gate** (`docs/brain/decisions/index.md`), exige **Observed Proof** en `tasks.md`, y define la regla de verificación proporcional: el subagente constructor (`flash` / fast tier) ejecuta los tests unitarios/integración en cada ciclo y, cuando la feature toque UI o flujos completos y el proyecto soporte **E2E / Playwright** en `docs/brain/architecture.md`, añade una tarea final de verificación E2E ejecutada también por el subagente ligero sin inventar nunca un runner no declarado.
- `render_mentor_guide_skill(config: ProjectConfig) -> str`:
  - `.compass/skills/mentor-guide/SKILL.md` con frontmatter YAML (`name: mentor-guide`, `description: ...`).
  - Define cómo generar bajo demanda `guides/<slug>-GUIDE.md` con doble lente: Ingeniería de Software + Dominio Técnico (`config.domain`).

### 2.3 `src/compass_harness/templates/brain_assets.py`
Funciones generadoras para el Router y el Cerebro de 3 niveles:
- `render_agents_md(config: ProjectConfig) -> str`:
  - `AGENTS.md` con `< 100` líneas, los 3 carriles (`ANSWER`, `FTD`, `SDD`), puntero a `docs/brain/index.md`, estrategia de ejecución adaptada a `config.model_strategy` (`"subagent-fast"`, `"subagent-inherit"`, `"single"`) y enlaces a las 4 skills.
- `render_brain_index_md(config: ProjectConfig) -> str`:
  - `docs/brain/index.md` con nombre, objetivo, dominio, stack, enlaces a `architecture.md` y `handoff.md`, enlace de **1 única línea** a `decisions/index.md` y sección de módulos `modules/`.
- `render_architecture_md(config: ProjectConfig) -> str`:
  - `docs/brain/architecture.md` adaptando las reglas de capas según `config.architecture_style` (`"hexagonal"`, `"layered"`, `"mvc"`, `"script"`) e incluyendo la sección **Verification Commands** (Unit & Integration In-Loop TDD, Static/Lint Gate y E2E / Browser UI Tests opcionales con Playwright o CLI smoke test ejecutados por el subagente ligero).
- `render_handoff_md(config: ProjectConfig) -> str`:
  - `docs/brain/handoff.md` inicial (< 30 líneas).
- `render_decisions_index_md(config: ProjectConfig) -> str` y `render_initial_adr_md(config: ProjectConfig) -> str`:
  - `docs/brain/decisions/index.md` y `docs/brain/decisions/0001-initial-architecture.md`.

### 2.4 `src/compass_harness/core/renderer.py`
- `@dataclass(frozen=True) class ProjectConfig`:
  - `project_name: str`
  - `project_goal: str`
  - `tech_stack: str`
  - `domain: str = "General Software Engineering"`
  - `architecture_style: str = "hexagonal"`
  - `model_strategy: str = "subagent-fast"`
  - `target_assistants: tuple[str, ...] = ("antigravity",)`
  - `test_command: str = "pytest"`
  - `lint_command: str = "ruff check"`
  - `e2e_command: str = "N/A"`
- `def render_project_bundle(config: ProjectConfig) -> dict[str, str]`:
  - Ensambla y devuelve el diccionario completo con las 12 rutas relativas esperadas.
