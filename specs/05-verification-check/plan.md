# Plan Técnico: `05-verification-check`

- **ID de Feature**: `05-verification-check`
- **Spec asociada**: `specs/05-verification-check/spec.md`
- **Estado**: Aprobado para Ejecución TDD

---

## 1. Architecture Alignment (Alineación con `docs/brain/architecture.md`)

1. **Separación de capas**:
   - `src/compass_harness/core/verifier.py`: Contiene toda la lógica determinista de auditoría (`SpecProgress`, `CheckIssue`, `HarnessReport`, `verify_harness(root: Path) -> HarnessReport`). No depende de `typer` ni de `rich`.
   - `src/compass_harness/cli.py`: Añade los subcomandos `@app.command("status")` y `@app.command("check")`, que llaman a `verify_harness(root)` y formatean la salida por consola (`COMPASS_STATUS`, `COMPASS_CHECK_PASSED`, `COMPASS_CHECK_FAILED`).
2. **Seams (Costuras públicas bajo prueba)**:
   - Nivel Core: `verify_harness(root: Path) -> HarnessReport` exportado en `compass_harness.core.verifier` y `compass_harness.core`.
   - Nivel CLI: `CliRunner().invoke(app, ["status", ...])` y `CliRunner().invoke(app, ["check", ...])`.
3. **ADR Gate**:
   - Implementa la auditoría automática de los invariantes establecidos en `0002` (Symlinks), `0003` (Observed Proof en TDD) y `0005` (Jerarquía del Cerebro y límites de líneas).

---

## 2. Diseño de Componentes

### 2.1 `src/compass_harness/core/verifier.py`

Constantes de reglas:
```python
REQUIRED_BRAIN_FILES: tuple[str, ...] = (
    "AGENTS.md",
    "docs/brain/index.md",
    "docs/brain/architecture.md",
    "docs/brain/handoff.md",
    "docs/brain/decisions/index.md",
)
AGENTS_MAX_LINES = 99  # < 100 líneas
HANDOFF_MAX_LINES = 30  # <= 30 líneas
ASSISTANT_SKILL_DIRS: tuple[str, ...] = (
    ".agents/skills",
    ".claude/skills",
    ".cursor/skills",
)
```

Modelos inmutables (`@dataclass(frozen=True)`):
- `SpecProgress`:
  - `spec_id: str`
  - `has_spec_md: bool`
  - `has_plan_md: bool`
  - `has_tasks_md: bool`
  - `total_tasks: int`
  - `completed_tasks: int`
  - `tasks_missing_proof: tuple[str, ...]`
- `CheckIssue`:
  - `code: str`
  - `path: str`
  - `message: str`
- `HarnessReport`:
  - `is_installed: bool`
  - `present_brain_files: tuple[str, ...]`
  - `missing_brain_files: tuple[str, ...]`
  - `installed_skills: tuple[str, ...]`
  - `active_symlinks: tuple[str, ...]`
  - `broken_symlinks: tuple[str, ...]`
  - `specs_progress: tuple[SpecProgress, ...]`
  - `issues: tuple[CheckIssue, ...]`
  - `@property def passed(self) -> bool`: devuelve `self.is_installed and len(self.issues) == 0`.

Algoritmo de `verify_harness(root: Path) -> HarnessReport`:
1. **Inspección de archivos del Cerebro**:
   - Comprueba cuáles de `REQUIRED_BRAIN_FILES` existen en `root`.
   - `is_installed` es `True` si al menos `AGENTS.md` o `docs/brain/index.md` existen en `root`.
   - Por cada archivo de `REQUIRED_BRAIN_FILES` que falte, añade un `CheckIssue(code="MISSING_BRAIN_FILE", path=rel_path, message=...)`.
2. **Chequeo de Presupuesto de Contexto (`BUDGET_EXCEEDED`)**:
   - Si `AGENTS.md` existe y `len(lines) >= 100`: añade `CheckIssue(code="BUDGET_EXCEEDED", path="AGENTS.md", message=...)`.
   - Si `docs/brain/handoff.md` existe y `len(lines) > 30`: añade `CheckIssue(code="BUDGET_EXCEEDED", path="docs/brain/handoff.md", message=...)`.
3. **Chequeo de Aislamiento $O(1)$ de ADRs en `docs/brain/index.md` (`ADR_INDEX_BLOAT`)**:
   - Si `docs/brain/index.md` existe: cuenta cuántas líneas contienen referencias a `decisions/` (ej. `decisions/`). Si no enlaza a `decisions/index.md` o si hay más de 1 línea enlazando a archivos dentro de `decisions/`, añade `CheckIssue(code="ADR_INDEX_BLOAT", path="docs/brain/index.md", message=...)`.
4. **Inspección de Skills y Enlaces Simbólicos (`BROKEN_SYMLINK`)**:
   - Lista las skills presentes en `.compass/skills/<name>/SKILL.md`.
   - Escanea `.agents/skills`, `.claude/skills` y `.cursor/skills` si existen:
     - Si una entrada `entry.is_symlink()`:
       - Si `not entry.exists()` (enlace simbólico roto cuyos destino no existe), lo añade a `broken_symlinks` y registra `CheckIssue(code="BROKEN_SYMLINK", path=rel_path, message=...)`.
       - Si `entry.exists()`, lo añade a `active_symlinks`.
5. **Auditoría de `specs/*/tasks.md` (`MISSING_OBSERVED_PROOF`)**:
   - Si `root / "specs"` existe y es directorio, recorre sus subdirectorios ordenados alfabéticamente.
   - Para cada `<spec_dir>`:
     - Comprueba `spec.md`, `plan.md`, `tasks.md`.
     - Si `tasks.md` existe, parsea los bloques de tarea usando expresión regular para cabeceras de tarea `- \[( |x|X)\] (.*)`:
       - Divide el archivo por cada línea que empieza por `- [ ]` o `- [x]` / `- [X]`.
       - Por cada tarea completada (`[x]` / `[X]`):
         - Inspecciona el cuerpo de esa tarea hasta la siguiente tarea (o final del fichero).
         - Comprueba que contenga `"Prueba Observada"` o `"Observed Proof"`.
         - Extrae el texto posterior a `"Prueba Observada"` / `"Observed Proof"` y verifica que no esté vacío ni contenga `*(Pendiente)*` o `*(Pending)*`.
         - Si falla, añade el título de la tarea a `tasks_missing_proof` y registra un `CheckIssue(code="MISSING_OBSERVED_PROOF", path=f"specs/{spec_id}/tasks.md", message=...)`.

### 2.2 Subcomandos CLI (`status` y `check`) en `src/compass_harness/cli.py`

1. `@app.command("status")`:
   - Recibe `--path: Path = typer.Option(Path("."), "--path", help="Directorio del proyecto objetivo.")`.
   - Ejecuta `report = verify_harness(root)`.
   - Imprime `=== COMPASS_STATUS ===`, estado general (`HEALTHY`, `ISSUES_FOUND` o `NOT_INITIALIZED`), conteo de archivos del cerebro (`len(present)/5`), skills instaladas, symlinks activos/rotos y listado de `specs_progress` (`<spec_id>: <completed>/<total> tareas completadas`).
   - Termina con `raise typer.Exit(code=0)`.
2. `@app.command("check")`:
   - Recibe `--path: Path = typer.Option(Path("."), "--path", help="Directorio del proyecto objetivo.")`.
   - Ejecuta `report = verify_harness(root)`.
   - Si `report.passed`: imprime `=== COMPASS_CHECK_PASSED ===`, resumen de checks superados y termina con `raise typer.Exit(code=0)`.
   - Si `not report.passed`: imprime `=== COMPASS_CHECK_FAILED ===`, lista cada `issue` en formato `[{issue.code}] {issue.path}: {issue.message}` y termina con `raise typer.Exit(code=1)`.
