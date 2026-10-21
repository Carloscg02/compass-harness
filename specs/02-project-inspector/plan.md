# Plan Técnico: `02-project-inspector`

- **ID de Feature**: `02-project-inspector`
- **Spec de Referencia**: [`spec.md`](spec.md)

---

## 1. Verificación de Arquitectura y Decisiones (`Architecture & ADR Gate`)

- **Alineación con [`docs/brain/architecture.md`](../../docs/brain/architecture.md)**:
  - Capa afectada: **Capa de Dominio (`core/`)** -> `src/compass_harness/core/inspector.py`.
  - Cumplimiento de frontera: El módulo no importa `typer` ni `rich`, ni realiza llamadas a `print()`. Recibe un `pathlib.Path` y devuelve objetos inmutables (`Enum` y `@dataclass(frozen=True)`).
- **Control de Decisiones (`ADR Check`)**:
  - ¿Introduce una dependencia externa nueva o cambia la arquitectura? **No** (utiliza exclusivamente `pathlib`, ` enum` y `dataclasses` de la librería estándar de Python). No requiere crear un nuevo ADR en `docs/brain/decisions/`.

---

## 2. Diseño de Tipos y Funciones (`src/compass_harness/core/inspector.py`)

### 2.1 Enumeración `ProjectState`
```python
class ProjectState(str, Enum):
    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"
```
*(Heredar de `str` y `Enum` permite que `ProjectState.GREENFIELD.value` sea serializable directamente como `"greenfield"` cuando el CLI imprima el diagnóstico para el agente en el Paso 4).*

### 2.2 Dataclass Inmutable `ProjectInspection`
```python
@dataclass(frozen=True)
class ProjectInspection:
    root_path: Path
    state: ProjectState
    detected_stacks: tuple[str, ...]
    existing_dirs: tuple[str, ...]
    has_git: bool
    existing_harness_files: tuple[str, ...]
```

### 2.3 Reglas de Detección en `inspect_project(target_dir: Path) -> ProjectInspection`
1. **Validación de entrada**:
   - Si `not target_dir.exists()`: lanza `FileNotFoundError(f"Path does not exist: {target_dir}")`.
   - Si `not target_dir.is_dir()`: lanza `NotADirectoryError(f"Path is not a directory: {target_dir}")`.
   - Resuelve la ruta con `root = target_dir.resolve()`.
2. **Constantes de detección**:
   - `MANIFEST_TO_STACK`:
     - `"pyproject.toml": "python"`, `"requirements.txt": "python"`, `"setup.py": "python"`
     - `"package.json": "node"`
     - `"Cargo.toml": "rust"`
     - `"go.mod": "go"`
   - `EXTENSION_TO_STACK`:
     - `".py": "python"`
     - `".ts": "node"`, `".js": "node"`
     - `".rs": "rust"`
     - `".go": "go"`
     - `".c": "c/cpp"`, `".cpp": "c/cpp"`, `".h": "c/cpp"`
     - `".m": "matlab"`
   - `IGNORED_DIRS`: `{".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".compass", ".agents", ".claude"}`
   - `TRACKED_DIRS`: `("src", "tests", "docs", "specs", "guides")`
   - `HARNESS_MARKERS`: `("AGENTS.md", "CLAUDE.md", ".compass", ".agents", ".claude", "docs/brain")`
3. **Escaneo de archivos de código**:
   - Se comprueban primero los manifiestos en `root`.
   - Se escanean los archivos de primer nivel en `root` y dentro de subdirectorios no ignorados (como `src/`, `app/`, `lib/`, etc., excluyendo cualquier ruta que pase por `IGNORED_DIRS`) buscando extensiones en `EXTENSION_TO_STACK`.
   - Se mantiene el orden de aparición sin duplicados en `detected_stacks: tuple[str, ...]`.
4. **Cálculo de `state`**:
   - Si existe al menos un manifiesto reconocido o al menos un archivo de código fuente reconocido (fuera de `IGNORED_DIRS`), `state = ProjectState.BROWNFIELD`.
   - En caso contrario, `state = ProjectState.GREENFIELD`.

---

## 3. Estrategia de Tests (`tests/test_project_inspector.py`)

Utilizaremos el fixture nativo `tmp_path: Path` de `pytest` para construir escenarios en un directorio temporal real en cada test:
1. `test_inspect_empty_and_boilerplate_dir_is_greenfield` (CA-1)
2. `test_inspect_detects_manifest_as_brownfield` (CA-2)
3. `test_inspect_detects_source_files_and_existing_dirs_without_manifest` (CA-3)
4. `test_inspect_detects_existing_harness_files` (CA-4)
5. `test_inspect_raises_on_invalid_paths` (CA-5)
