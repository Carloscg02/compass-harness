# Plan Técnico: 08-compass-update (Sincronización Determinista del Arnés)

## 1. Alineación con la Arquitectura
El diseño respeta estrictamente la arquitectura en 3 capas de Compass ([`docs/brain/architecture.md`](../../docs/brain/architecture.md)):
- **Capa Core (`src/compass_harness/core/updater.py`)**: Lógica pura desacoplada de la terminal. Funciones inmutables para extracción de configuración, cálculo del plan de actualización y aplicación en disco.
- **Capa CLI (`src/compass_harness/cli.py`)**: Subcomando `compass update` con Typer y Rich para dar formato a la salida y gestionar códigos de salida UNIX.
- **Capa Templates (`src/compass_harness/templates/`)**: Reutiliza `render_project_bundle` y los generadores existentes sin duplicar plantillas.

---

## 2. Consulta de ADRs (ADR Gate)
- Consultamos [`docs/brain/decisions/index.md`](../../docs/brain/decisions/index.md).
- Decisión: No se contradice ningún ADR existente. La introducción de `compass update` complementa `compass init` (ADR 0001) permitiendo la evolución del arnés en proyectos en marcha (*Brownfield harness maintenance*).

---

## 3. Diseño Detallado de Componentes

### 3.1. Módulo Core: `src/compass_harness/core/updater.py`

#### Modelado de Dominio:
```python
@dataclass(frozen=True)
class UpdatePlan:
    config: ProjectConfig
    files_to_update: tuple[str, ...]
    preserved_files: tuple[str, ...]
    symlinks_to_repair: tuple[SymlinkSpec, ...]

@dataclass(frozen=True)
class UpdateResult:
    updated_files: tuple[str, ...]
    skipped_files: tuple[str, ...]
    repaired_symlinks: tuple[str, ...]
    preserved_files: tuple[str, ...]
    config_saved: bool = False
```

#### Funciones Principales:
1. `extract_project_config(root: Path) -> ProjectConfig`:
   - Busca `.compass/config.json`. Si existe y es válido, lo parsea.
   - Si no existe, lee `docs/brain/index.md` con expresiones regulares para extraer nombre, objetivo, stack y dominio.
   - Lee `docs/brain/architecture.md` para extraer comandos de test (`test_command`, `lint_command`, `e2e_command`) y estilo arquitectónico.
   - Inspecciona directorios `.agents/skills`, `.claude/skills`, `.cursor/skills` para inferir `target_assistants`.
   - Lanza `FileNotFoundError` o `ValueError` si el proyecto no es un arnés Compass válido.
2. `save_project_config(root: Path, config: ProjectConfig) -> Path`:
   - Guarda `.compass/config.json` con formato legible.
3. `plan_update(root: Path, config: ProjectConfig) -> UpdatePlan`:
   - Genera el bundle completo con `_get_bundle_files(config)`.
   - Filtra los archivos actualizables (*Stateless*: `.compass/skills/*`, `AGENTS.md`, `CLAUDE.md`).
   - Identifica y lista los archivos protegidos (*Stateful*: `docs/brain/index.md`, `architecture.md`, `handoff.md`, `design.md`, `modules/`, etc.).
   - Calcula symlinks requeridos con `_compute_symlinks`.
4. `apply_update(root: Path, config: ProjectConfig, force: bool = False) -> UpdateResult`:
   - Sobrescribe los archivos actualizables en disco.
   - Re-crea o repara los symlinks relativos.
   - Guarda `.compass/config.json`.
   - Asegura la inmutabilidad de los archivos protegidos.

### 3.2. Capa CLI: `src/compass_harness/cli.py`
Añadir el comando `update`:
```python
@app.command("update")
def update(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Directorio raíz del proyecto."),
    preview: bool = typer.Option(False, "--preview", help="Muestra el plan de actualización sin escribir en disco."),
    apply: bool = typer.Option(False, "--apply", help="Aplica la actualización en disco."),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza la sobreescritura de skills locales."),
) -> None:
    ...
```
- Si no está inicializado: imprime `=== COMPASS_NOT_INITIALIZED ===` y sale con código 1.
- Sin flags: imprime `=== COMPASS_UPDATE_REQUIRED ===` y sale con código 0.
- `--preview`: imprime `=== COMPASS_UPDATE_PLAN ===` con lista de archivos a actualizar y protegidos.
- `--apply`: ejecuta `apply_update`, guarda config, corre `verify_harness` y muestra `=== COMPASS_UPDATE_APPLIED ===`.

---

## 4. Plan de Pruebas (Test Plan)
- **`tests/test_updater.py`**:
  - `test_extract_project_config_from_existing_brain`: Reconstruye configuración de un fixture con `index.md` y `architecture.md`.
  - `test_extract_project_config_not_initialized_raises`: Lanza error en carpeta vacía.
  - `test_plan_update_identifies_stateless_and_preserves_stateful`: Verifica que `modules/`, `handoff.md`, etc. figuran como protegidos.
  - `test_apply_update_updates_skills_and_preserves_custom_modules`: Comprueba que una ficha previa `docs/brain/modules/billing.md` y `handoff.md` no se tocan tras `apply_update`.
  - `test_cli_update_preview_and_apply`: Prueba los subcomandos de Typer mediante `CliRunner`.
