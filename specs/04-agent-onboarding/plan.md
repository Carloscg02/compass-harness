# Plan Técnico: `04-agent-onboarding`

- **ID de Feature**: `04-agent-onboarding`
- **Spec asociada**: `specs/04-agent-onboarding/spec.md`
- **Estado**: Aprobado para Ejecución TDD

---

## 1. Architecture Alignment (Alineación con `docs/brain/architecture.md`)

1. **Separación de capas**:
   - `src/compass_harness/core/installer.py`: Contiene la lógica del motor de onboarding e instalación (`InstallationPlan`, `InstallationResult`, `plan_installation`, `apply_installation`), combinando `inspect_project` y `render_project_bundle`. No depende de `typer` ni de `rich`.
   - `src/compass_harness/cli.py`: Añade el subcomando `@app.command("init")` que parsea las opciones de línea de comandos, invoca a `inspect_project`, `plan_installation` o `apply_installation` según las banderas (`--preview`, `--apply`, `--force`) y formatea la salida estructurada (`COMPASS_ONBOARDING_REQUIRED`, `COMPASS_ONBOARDING_PLAN`, `COMPASS_ONBOARDING_APPLIED`).
   - **Nota sobre `Typer` al pasar de 0 a 1+ subcomandos**: En `Typer`, cuando una app no tiene `@app.command()` y solo tiene `@app.callback()`, invocar `compass` procesa el callback directamente. Al registrar el primer `@app.command("init")`, para que `compass --version` siga funcionando sin requerir un subcomando, `@app.callback(invoke_without_command=True)` ya está cubierto por `is_eager=True` en `--version` y `no_args_is_help=True` en `Typer`. Todos los tests de `tests/test_cli_skeleton.py` deben seguir pasando en verde.
2. **Seams (Costuras públicas bajo prueba)**:
   - Nivel Core: `plan_installation(root: Path, config: ProjectConfig) -> InstallationPlan` y `apply_installation(root: Path, config: ProjectConfig, force: bool = False) -> InstallationResult` en `compass_harness.core.installer` (y re-exportados en `compass_harness.core`).
   - Nivel CLI: `CliRunner().invoke(app, ["init", ...])` sobre `compass_harness.cli.app`.
3. **ADR Gate**:
   - Implementa directamente los ADRs `0002` (Symlinks agnósticos) y `0004` (Protocolo de onboarding en 3 pasos). No requiere un nuevo ADR.

---

## 2. Diseño de Componentes

### 2.1 `src/compass_harness/core/installer.py`

Constantes de mapeo de asistentes:
```python
ASSISTANT_SKILL_DIRS: dict[str, str] = {
    "antigravity": ".agents/skills",
    "codex": ".agents/skills",
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
}
SKILL_NAMES: tuple[str, ...] = (
    "tdd",
    "project-architect",
    "sdd-workflow",
    "mentor-guide",
)
```

Modelos inmutables de resultado:
- `@dataclass(frozen=True) class SymlinkSpec`:
  - `link_path: str` (ej. `".agents/skills/tdd"`)
  - `target_path: str` (ej. `".compass/skills/tdd"`)
- `@dataclass(frozen=True) class InstallationPlan`:
  - `config: ProjectConfig`
  - `files_to_create: tuple[str, ...]`
  - `existing_conflicts: tuple[str, ...]`
  - `symlinks_to_create: tuple[SymlinkSpec, ...]`
  - `directories_to_ensure: tuple[str, ...]` (`"docs/brain/modules"`, `"specs"`, `"guides"`)
- `@dataclass(frozen=True) class InstallationResult`:
  - `written_files: tuple[str, ...]`
  - `skipped_files: tuple[str, ...]`
  - `created_symlinks: tuple[str, ...]`
  - `ensured_directories: tuple[str, ...]`

Funciones públicas:
1. `plan_installation(root: Path, config: ProjectConfig) -> InstallationPlan`:
   - Llama a `render_project_bundle(config)`. Si `"claude"` está en `config.target_assistants`, añade también `"CLAUDE.md"` al conjunto de archivos del bundle (con un puntero conciso a `AGENTS.md` y `docs/brain/index.md`).
   - Comprueba qué rutas ya existen en `root`: las que no existen van a `files_to_create` y las que ya existen van a `existing_conflicts`.
   - Calcula los `SymlinkSpec` únicos (sin duplicar `.agents/skills` si tanto `antigravity` como `codex` están presentes) para las 4 skills.
2. `apply_installation(root: Path, config: ProjectConfig, force: bool = False) -> InstallationResult`:
   - Asegura los directorios base (`docs/brain/modules`, `specs`, `guides`).
   - Escribe los archivos del bundle en `root`:
     - Si el archivo ya existe y `force=False`, lo añade a `skipped_files` sin tocarlo.
     - Si no existe o `force=True`, crea sus directorios padre, escribe el contenido UTF-8 y lo añade a `written_files`.
   - Para cada `SymlinkSpec`:
     - Crea el directorio padre (ej. `root / ".agents/skills"`).
     - Si el destino del symlink ya existe (sea symlink o carpeta) y `force=True` (o si es un symlink roto/previo), lo reemplaza; si no existe, crea un symlink relativo (`os.path.relpath(target_abs, link_abs.parent)`) apuntando a `root / ".compass/skills/<skill>"`.

### 2.2 Subcomando `compass init` en `src/compass_harness/cli.py`

Opciones de `@app.command("init")`:
- `--path`: `Path = typer.Option(Path("."), "--path", help="Directorio del proyecto objetivo.")`
- `--name`: `Optional[str] = typer.Option(None, "--name", help="Nombre del proyecto.")`
- `--goal`: `str = typer.Option("Desarrollo asistido por agentes con Compass", "--goal", help="Objetivo del proyecto.")`
- `--stack`: `Optional[str] = typer.Option(None, "--stack", help="Stack tecnologico principal.")`
- `--domain`: `str = typer.Option("General Software Engineering", "--domain", help="Dominio tecnico y educativo.")`
- `--arch`: `str = typer.Option("hexagonal", "--arch", help="Estilo arquitectonico (hexagonal, layered, mvc, script).")`
- `--model-strategy`: `str = typer.Option("subagent-fast", "--model-strategy", help="Estrategia de modelos (subagent-fast, subagent-inherit, single).")`
- `--assistants`: `str = typer.Option("antigravity", "--assistants", help="Asistentes objetivo separados por coma (antigravity,claude,cursor,codex).")`
- `--test-cmd`: `str = typer.Option("pytest", "--test-cmd", help="Comando para tests unitarios e integracion.")`
- `--lint-cmd`: `str = typer.Option("ruff check", "--lint-cmd", help="Comando para linter y chequeo estatico.")`
- `--e2e-cmd`: `str = typer.Option("N/A", "--e2e-cmd", help="Comando para tests E2E / Playwright opcional.")`
- `--preview`: `bool = typer.Option(False, "--preview", help="Fase 2: Muestra el plan de instalacion sin escribir en disco.")`
- `--apply`: `bool = typer.Option(False, "--apply", help="Fase 3: Escribe los archivos y crea los symlinks en disco.")`
- `--force`: `bool = typer.Option(False, "--force", help="Sobrescribe archivos existentes al usar --apply.")`

Flujo de `init`:
1. Si `preview and apply`: imprime error de conflicto y lanza `raise typer.Exit(code=1)`.
2. Resuelve `root = path.resolve()`.
3. Ejecuta `inspection = inspect_project(root)`.
4. Si `not preview and not apply` (**Fase 1**):
   - Imprime `COMPASS_ONBOARDING_REQUIRED`, `project_state`, `detected_stacks`, `existing_tracked_dirs`, `existing_harness_files`, guía de preguntas para el agente (distinguiendo `GREENFIELD` vs `BROWNFIELD`) y el comando sugerido `compass init --preview ...`.
5. Construye `ProjectConfig` resolviendo valores por defecto (`name = name or root.name`, `stack = stack or (", ".join(inspection.detected_stacks) if inspection.detected_stacks else "python")`, `assistants_tuple = tuple(a.strip().lower() for a in assistants.split(",") if a.strip())`).
6. Si `preview` (**Fase 2**):
   - Llama a `plan = plan_installation(root, config)` e imprime `COMPASS_ONBOARDING_PLAN` con los archivos a crear, conflictos detectados, symlinks y el comando `compass init --apply ...`.
7. Si `apply` (**Fase 3**):
   - Llama a `result = apply_installation(root, config, force=force)` e imprime `COMPASS_ONBOARDING_APPLIED` con el listado de `written_files`, `skipped_files` y `created_symlinks`.
