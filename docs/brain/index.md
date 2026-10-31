# Cerebro del Proyecto: `compass-harness`

> **Propósito de este archivo**: Ser el mapa central del proyecto (Nivel 1). El agente lee este índice al arrancar y abre únicamente los documentos de Nivel 2 que necesite para la tarea actual.

---

## 1. Identidad del Proyecto
- **Nombre del Paquete / Repo**: `compass-harness` (Comando CLI: `compass`)
- **Qué es**: Meta-Harness Agnóstico y Educativo en Python con memoria persistente, flujo SDD, TDD estricto, delegación en subagentes y Modo Mentor bajo demanda (`GUIDE.md`).

---

## 2. Documentos del Cerebro (Nivel 2 — Abrir según tarea)
- **[`architecture.md`](architecture.md)** — Estilo arquitectónico (3 capas: `cli` / `core` / `templates`), estructura `src/` y reglas de código. *(Lectura obligatoria en `FTD` y `SDD`)*.
- **[`handoff.md`](handoff.md)** — Estado del turno actual y siguiente paso inmediato (máximo 30 líneas, se sobrescribe en cada sesión).
- **[`decisions/index.md`](decisions/index.md)** — Sub-índice de decisiones técnicas irreversibles (ADRs). *(Consultar solo si se cuestiona una decisión arquitectónica o al registrar un ADR nuevo)*.

---

## 3. Módulos Implementados (`docs/brain/modules/`)
- **[`modules/cli-skeleton.md`](modules/cli-skeleton.md)** — Configuración del paquete (`pyproject.toml`), versión (`__version__`) y aplicación raíz `Typer` (`cli.py` con `--version` y `--help`).
- **[`modules/project-inspector.md`](modules/project-inspector.md)** — Inspector determinista en `core/inspector.py` (`ProjectState`, `ProjectInspection`, `inspect_project`) para detectar proyectos *Greenfield* vs. *Brownfield*, stacks, señales de UI y archivos de harness previos.
- **[`modules/templates-and-skills.md`](modules/templates-and-skills.md)** — Motor puro de renderizado en `core/renderer.py` (`ProjectConfig`, `render_project_bundle`) y activos en `templates/` con la skill `tdd` oficial de Matt Pocock y las 4 skills propias de Compass (`project-architect`, `sdd-workflow`, `mentor-guide`, `ui-design`).
- **[`modules/agent-onboarding.md`](modules/agent-onboarding.md)** — Motor de instalación en `core/installer.py` (`plan_installation`, `apply_installation`) y comando `compass init` en 3 fases (`COMPASS_ONBOARDING_REQUIRED`, `--preview`, `--apply`) con symlinks agnósticos relativos.
- **[`modules/verification-check.md`](modules/verification-check.md)** — Auditor determinista en `core/verifier.py` (`verify_harness`) y subcomandos `compass status` y `compass check`.
- **[`modules/ui-design-governance.md`](modules/ui-design-governance.md)** — Gobernanza de UI/Frontend con activación perezosa (*Just-In-Time UI Gate*), entrevista guiada con catálogo interactivo y arquetipos, 5 leyes Anti-Slop y auditoría de `docs/brain/design.md`.
- **[`modules/auditor-subagent.md`](modules/auditor-subagent.md)** — Puerta de auditoría independiente en flujo SDD, mitigación de *Builder Blindness*, rúbrica de 4 puntos y feedback loop.

---

## 4. Hoja de Ruta v1.1 (Progreso: 7 / 7 — COMPLETADA)
- [x] **Paso 1 (`01-cli-skeleton`)**: Esqueleto del paquete Python y comando base `compass` ([Spec](../../specs/01-cli-skeleton/spec.md)).
- [x] **Paso 2 (`02-project-inspector`)**: Detector determinista de contexto Greenfield vs. Brownfield ([Spec](../../specs/02-project-inspector/spec.md)).
- [x] **Paso 3 (`03-templates-and-skills`)**: Motor de plantillas y las Skills maestras ([Spec](../../specs/03-templates-and-skills/spec.md)).
- [x] **Paso 4 (`04-agent-onboarding`)**: Comando `compass init` (Protocolo en 3 fases para el agente + symlinks) ([Spec](../../specs/04-agent-onboarding/spec.md)).
- [x] **Paso 5 (`05-verification-check`)**: Comandos `compass status` y `compass check` (auditoría de Prueba Observada) ([Spec](../../specs/05-verification-check/spec.md)).
- [x] **Paso 6 (`06-ui-design-governance`)**: Gobernanza de UI/Frontend, skill `ui-design`, entrevista y contrato `design.md` Anti-Slop ([Spec](../../specs/06-ui-design-governance/spec.md)).
- [x] **Paso 7 (`07-auditor-subagent`)**: Puerta de Auditoría Independiente en Flujo SDD con contexto limpio y modelo rápido ([Spec](../../specs/07-auditor-subagent/spec.md)).

---

## 5. Guías de Aprendizaje Generadas (`guides/`)
- **[`00-cli-and-architecture-GUIDE.md`](../../guides/00-cli-and-architecture-GUIDE.md)** — Fundamentos de una CLI en Python, `pyproject.toml`, Entry Points, `Typer` vs `argparse` y arquitectura en capas.
- **[`01-cli-skeleton-GUIDE.md`](../../guides/01-cli-skeleton-GUIDE.md)** — Disección de `cli.py` (`@app.callback`, `is_eager`, códigos de salida) y testing con `CliRunner`.
- **[`02-project-inspector-GUIDE.md`](../../guides/02-project-inspector-GUIDE.md)** — Modelado de dominio inmutable (`@dataclass(frozen=True)`, `Enum`), poda de árboles en `os.walk` y testing de archivos con `tmp_path`.
- **[`03-templates-and-skills-GUIDE.md`](../../guides/03-templates-and-skills-GUIDE.md)** — Patrón Functional Core en el motor de plantillas (`dict[str, str]`), `TYPE_CHECKING` y disección de la skill `tdd` de Matt Pocock (*Seams*, *Vertical Slices* y verificación proporcional).
- **[`04-agent-onboarding-GUIDE.md`](../../guides/04-agent-onboarding-GUIDE.md)** — Máquina de estados CLI para agentes (sin `input()` bloqueante), enlaces simbólicos relativos POSIX (`os.path.relpath`) e idempotencia.
- **[`05-verification-check-GUIDE.md`](../../guides/05-verification-check-GUIDE.md)** — Puertas de calidad deterministas fuera del LLM, expresiones regulares precompiladas (`re.compile`), semántica de códigos de salida (`status` vs `check`) y *dogfooding*.
- **[`06-ui-design-governance-GUIDE.md`](../../guides/06-ui-design-governance-GUIDE.md)** — Gobernanza de UI/Frontend para desarrolladores backend, patrón *Just-In-Time Design Contract* y las 4 reglas objetivas contra el *AI Slop*.
- **[`07-auditor-subagent-GUIDE.md`](../../guides/07-auditor-subagent-GUIDE.md)** — El patrón Maker-Checker en ingeniería de arneses, mitigación de sesgos de contexto en subagentes y diseño de rúbricas adversariales para modelos rápidos.
- **[`harness-engineering-audit-rubric.md`](../../guides/harness-engineering-audit-rubric.md)** — Marco de auditoría y checklist de 10 puntos para evaluar harnesses existentes según los estándares de Anthropic, `rsc-harness`, OpenAI y `learn-harness-engineering`.
