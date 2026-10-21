# Módulo: `project-inspector`

- **Feature origen**: [`specs/02-project-inspector/`](../../../specs/02-project-inspector/spec.md)
- **Archivos principales**:
  - [`src/compass_harness/core/inspector.py`](../../../src/compass_harness/core/inspector.py):
    - `ProjectState(str, Enum)`: `GREENFIELD = "greenfield"`, `BROWNFIELD = "brownfield"`.
    - `ProjectInspection`: Dataclass inmutable con `root_path`, `state`, `detected_stacks`, `existing_dirs`, `has_git`, `existing_harness_files`.
    - `inspect_project(target_dir: Path) -> ProjectInspection`: Analiza de forma determinista el directorio excluyendo `IGNORED_DIRS`.
  - [`src/compass_harness/core/__init__.py`](../../../src/compass_harness/core/__init__.py): Re-exporta `ProjectState`, `ProjectInspection` e `inspect_project`.
- **Tests**: [`tests/test_project_inspector.py`](../../../tests/test_project_inspector.py) (6 tests con `tmp_path`).
- **Quién lo consume**: El futuro módulo de onboarding (`04-agent-onboarding`) al ejecutar `compass init` para diagnosticar el estado del proyecto antes de lanzar las preguntas al agente.
