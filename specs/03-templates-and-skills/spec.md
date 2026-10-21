# Especificación (Spec): `03-templates-and-skills`

- **ID de Feature**: `03-templates-and-skills`
- **Estado**: Borrador (Actualizada con la skill oficial `tdd` de Matt Pocock — Pendiente de aprobación humana)
- **Objetivo**: Construir el catálogo de plantillas parametrizables del Cerebro/Router, integrar la skill real `tdd` de Matt Pocock (`SKILL.md`, `tests.md`, `mocking.md`) junto con las 3 skills propias de Compass (`project-architect`, `sdd-workflow`, `mentor-guide`), e implementar el motor puro de renderizado (`src/compass_harness/core/renderer.py`).

---

## 1. Análisis de Reutilización de la Skill `tdd` de Matt Pocock

Se ha inspeccionado el contenido íntegro de `skills/engineering/tdd` en `https://github.com/mattpocock/skills`:
- **Archivos que componen la skill original**:
  1. `SKILL.md` (`name: tdd`): Define qué es un buen test, el concepto de **Seams** (costuras/fronteras públicas donde deben vivir los tests, acordadas antes de programar), los 3 anti-patrones (*Implementation-coupled*, *Tautological*, *Horizontal slicing* frente a *Vertical slices / Tracer bullets*) y las reglas del bucle (*Red before green*, *One slice at a time*).
  2. `tests.md`: Ejemplos de buenos tests (orientados a comportamiento vía interfaz pública) frente a malos tests (acoplados a implementación o tautológicos).
  3. `mocking.md`: Regla de hacer *mock* exclusivamente en las fronteras del sistema (*system boundaries*), inyección de dependencias e interfaces estilo SDK.
- **Encaje con `compass-harness`**:
  - Es **100% reutilizable y compatible** con el estándar de *skills* de Antigravity, Claude Code, Codex y Cursor.
  - Además, su concepto de **Seams** y **System Boundaries** encaja de forma nativa con **Arquitectura Hexagonal** (probar a través de los casos de uso/puertos públicos y solo hacer *mock* de adaptadores externos).
  - La incluiremos **íntegra** en `.compass/skills/tdd/` (`SKILL.md`, `tests.md`, `mocking.md`), mientras que nuestra skill `sdd-workflow` conectará los *Seams* con el archivo `plan.md` y exigirá registrar la **Prueba Observada** de cada ciclo vertical en `tasks.md`.

---

## 2. Alcance Funcional (Qué vamos a construir)

### 2.1 Modelo de Configuración (`ProjectConfig` en `src/compass_harness/core/renderer.py`)
Una estructura inmutable (`@dataclass(frozen=True)`) con los parámetros acordados en el onboarding:
- `project_name: str`: Nombre del proyecto.
- `project_goal: str`: Descripción breve del objetivo del proyecto.
- `tech_stack: str`: Stack tecnológico principal (ej. `"python"`, `"python + numpy"`, `"node"`, `"rust"`).
- `domain: str`: Dominio técnico y educativo para el Modo Mentor (ej. `"Telecomunicaciones y Procesamiento de Señal (RF/DSP)"`, `"Backend Web"`, `"Sistemas"`).
- `architecture_style: str`: Estilo acordado (`"hexagonal"` por defecto, o `"layered"`, `"mvc"`, `"script"`, `"existing"`).
- `model_strategy: str`: Estrategia de ejecución (`"subagent-fast"` por defecto, `"subagent-inherit"`, o `"single"`).
- `target_assistants: tuple[str, ...]`: Asistentes objetivo (por defecto `("antigravity",)`).

### 2.2 Plantillas del Router y del Cerebro (`src/compass_harness/templates/`)
1. **`AGENTS.md`**:
   - Menos de 100 líneas (*Directory Page Principle*).
   - Incluye el Decisor de 3 Carriles (`ANSWER`, `FTD`, `SDD`), la estrategia de modelos/subagentes seleccionada en `config.model_strategy` y el mapa de enlaces hacia `docs/brain/` y las skills instaladas (`project-architect`, `sdd-workflow`, `tdd`, `mentor-guide`).
2. **`docs/brain/index.md`**:
   - Mapa de Nivel 1 con identidad del proyecto (`project_name`, `project_goal`, `domain`), enlaces a `architecture.md` y `handoff.md`, enlace de **1 única línea** a `decisions/index.md` y sección de fichas de módulos `modules/`.
3. **`docs/brain/architecture.md`**:
   - Leyes arquitectónicas vigentes adaptadas al `architecture_style` elegido (`hexagonal`, `layered`, `mvc` o `script`).
   - Sección de **Verification Commands** simple y directa:
     - **Unit & Integration Tests (In-Loop TDD)**: comando principal de tests del proyecto (ej. `pytest`, `vitest`, `go test`) ejecutado en cada ciclo `RED -> GREEN -> REFACTOR` sobre los *Seams* públicos.
     - **Static / Lint Gate**: comando de tipado/linter del proyecto.
     - **E2E / Browser UI Tests (Optional)**: comando E2E (ej. `npx playwright test`, smoke test de CLI o `N/A` si el proyecto no tiene interfaz/E2E), ejecutado al cerrar una feature cuando el cambio toque interfaz de usuario o flujos end-to-end completos.
     - Todos estos comandos los ejecuta el subagente constructor (`flash` / fast tier cuando `model_strategy="subagent-fast"`).
4. **`docs/brain/handoff.md`**:
   - Hoja de relevo inicial sobrescribible (límite de 30 líneas).
5. **`docs/brain/decisions/index.md` y `docs/brain/decisions/0001-initial-architecture.md`**:
   - Sub-índice de ADRs y primer ADR fundacional del proyecto.

### 2.3 Las 4 Skills instaladas en `.compass/skills/`
1. **`tdd` (Skill oficial de Matt Pocock en `.compass/skills/tdd/`)**:
   - `.compass/skills/tdd/SKILL.md`
   - `.compass/skills/tdd/tests.md`
   - `.compass/skills/tdd/mocking.md`
2. **`project-architect` (`.compass/skills/project-architect/SKILL.md`)**:
   - Guía al agente durante el onboarding: cómo proponer Arquitectura Hexagonal + DDD por defecto y cuándo negociar alternativas (`layered`, `mvc`, `script`), y cómo inspeccionar y documentar módulos existentes si el proyecto es *Brownfield*.
3. **`sdd-workflow` (`.compass/skills/sdd-workflow/SKILL.md`)**:
   - Define el flujo de `FTD` y `SDD` (`spec.md -> plan.md -> tasks.md`).
   - Exige leer `docs/brain/architecture.md`, definir en `plan.md` la sección `Architecture Alignment` y los **Seams** bajo prueba (conectando con la skill `tdd` de Matt Pocock para tests unitarios y de integración en costuras públicas), aplicar el **ADR Gate** hacia `docs/brain/decisions/index.md`, y registrar la **Prueba Observada** en `tasks.md`.
   - Incluye la regla de verificación proporcional: el subagente constructor (`flash` / fast tier) ejecuta los tests unitarios y de integración en cada tarea (`RED -> GREEN -> REFACTOR`), y si la feature modifica UI o flujos completos y el proyecto soporta **E2E / Playwright** en `docs/brain/architecture.md`, añade una tarea final de verificación E2E ejecutada también por el subagente ligero (sin inventar nunca un test runner no declarado en `architecture.md`).
4. **`mentor-guide` (`.compass/skills/mentor-guide/SKILL.md`)**:
   - Generador bajo demanda de `guides/<slug>-GUIDE.md` parametrizado con el `domain` del proyecto (doble lente: **Ingeniería de Software** + **Dominio Técnico**).

### 2.4 Función Pura `render_project_bundle(config: ProjectConfig) -> dict[str, str]`
- Recibe `ProjectConfig` y devuelve un diccionario `{ruta_relativa: contenido_markdown}` con todos los archivos del Cerebro/Router y todos los archivos de las 4 skills (incluyendo `tdd/SKILL.md`, `tdd/tests.md` y `tdd/mocking.md`).

---

## 3. Criterios de Aceptación (Requisitos para TDD)

Archivo de pruebas: `tests/test_templates_and_skills.py`:

- **CA-1 (Completitud del Bundle e inclusión de la skill completa `tdd` de Matt Pocock)**: `render_project_bundle(config)` devuelve todas las rutas del Cerebro/Router más `.compass/skills/tdd/SKILL.md`, `.compass/skills/tdd/tests.md`, `.compass/skills/tdd/mocking.md`, `.compass/skills/project-architect/SKILL.md`, `.compass/skills/sdd-workflow/SKILL.md` y `.compass/skills/mentor-guide/SKILL.md`.
- **CA-2 (Fidelidad de la skill `tdd` de Matt Pocock)**: `.compass/skills/tdd/SKILL.md` conserva su frontmatter `name: tdd` y sus secciones clave (`What a good test is`, `Seams: where tests go`, `Anti-patterns`, `Horizontal slicing` vs `vertical slices`, `Rules of the loop`), junto con `tests.md` y `mocking.md`.
- **CA-3 (Restricción de tamaño y contenido en `AGENTS.md`)**: El `AGENTS.md` renderizado tiene menos de 100 líneas, incluye los 3 carriles (`ANSWER`, `FTD`, `SDD`), apunta a `docs/brain/index.md` y adapta su sección de ejecución según `model_strategy` (`"subagent-fast"`, `"subagent-inherit"` o `"single"`).
- **CA-4 (Adaptación de `architecture.md`, comandos de verificación y jerarquía en `docs/brain/index.md`)**: `architecture.md` adapta sus reglas según `architecture_style` (`"hexagonal"` vs `"script"`), incluye la sección de comandos de verificación (Unit & Integration + E2E/Playwright opcional cuando aplique), y `docs/brain/index.md` enlaza a `decisions/index.md` en una sola línea.
- **CA-5 (Conexión entre `sdd-workflow`, `tdd`, E2E proporcional y `mentor-guide`)**: Todas las skills tienen frontmatter YAML válido (`name`, `description`), `sdd-workflow` referencia los *Seams* de la skill `tdd` (unit + integration), la ejecución de E2E/Playwright por el subagente ligero cuando el proyecto lo soporte y la feature toque UI/flujos completos, el *ADR Gate* y la *Prueba Observada*, y `mentor-guide` incluye el `domain` configurado.
