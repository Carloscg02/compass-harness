# Especificación (Spec): `02-project-inspector`

- **ID de Feature**: `02-project-inspector`
- **Estado**: Aprobado
- **Objetivo**: Construir el módulo de dominio puro (`src/compass_harness/core/inspector.py`) encargado de analizar de forma determinista cualquier directorio de proyecto y determinar si es un proyecto nuevo (*Greenfield*) o existente (*Brownfield*), qué lenguajes/manifiestos utiliza, qué estructura de carpetas posee y si ya tiene archivos de agentes o harness instalados.

---

## 1. Contexto y Por Qué es Necesario

En el **Paso 4 (`compass init`)**, cuando el usuario le diga al agente *"Instala compass en este proyecto"*, el agente ejecutará `compass init` sin argumentos.
Antes de hacer preguntas al usuario en el chat, `compass` necesita inspeccionar la carpeta actual para:
1. Saber si está ante un proyecto vacío (*Greenfield*) o un proyecto con código existente (*Brownfield*).
2. Detectar pistas objetivas (por ejemplo, si existe `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, carpetas `src/`, `tests/`, `.git`) para que el agente no haga preguntas obvias y adapte su propuesta de arquitectura al proyecto real.
3. Detectar si ya existe una instalación previa (`.compass/`, `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.claude/`) para no sobrescribir nada sin permiso.

Siguiendo nuestra arquitectura de 3 capas ([`docs/brain/architecture.md`](../../docs/brain/architecture.md)), este inspector vive en `core/inspector.py`, **no imprime nada en consola** y devuelve estructuras de datos tipadas e inmutables fáciles de probar con `pytest`.

---

## 2. Alcance Funcional (Qué vamos a construir)

En `src/compass_harness/core/inspector.py`:

1. **Enumeración `ProjectState`**:
   - `GREENFIELD`: Directorio vacío, o que solo contiene archivos de inicialización básicos de repositorio (`.git`, `.gitignore`, `README.md`, `LICENSE`, `.venv`) sin manifiestos de paquetes ni carpetas/archivos de código fuente.
   - `BROWNFIELD`: Directorio que ya contiene al menos un manifiesto de proyecto reconocido o archivos/carpetas de código fuente.

2. **Modelo de Datos `ProjectInspection` (`dataclass(frozen=True)`)**:
   - `root_path: Path`: Ruta absoluta inspeccionada.
   - `state: ProjectState`: `GREENFIELD` o `BROWNFIELD`.
   - `detected_stacks: tuple[str, ...]`: Stacks/lenguajes detectados por sus manifiestos en la raíz:
     - `pyproject.toml` o `requirements.txt` o `setup.py` -> `"python"`
     - `package.json` -> `"node"`
     - `Cargo.toml` -> `"rust"`
     - `go.mod` -> `"go"`
     - Archivos `*.py`, `*.ts`, `*.js`, `*.rs`, `*.go`, `*.c`, `*.cpp`, `*.m` en la raíz o en `src/` cuando no hay manifiesto.
   - `existing_dirs: tuple[str, ...]`: Carpetas relevantes presentes en la raíz (ej. `"src"`, `"tests"`, `"docs"`, `"specs"`, `"guides"`).
   - `has_git: bool`: `True` si existe `.git` en la raíz.
   - `existing_harness_files: tuple[str, ...]`: Archivos o carpetas de agentes ya presentes en la raíz (entre `"AGENTS.md"`, `"CLAUDE.md"`, `".compass"`, `".agents"`, `".claude"`, `"docs/brain"`).

3. **Función Pura `inspect_project(target_dir: Path) -> ProjectInspection`**:
   - Recibe un `Path`, valida que exista y sea un directorio (lanzando `FileNotFoundError` o `NotADirectoryError` en caso contrario).
   - Ignora directorios de entorno o caché (`.venv`, `venv`, `node_modules`, `__pycache__`, `.pytest_cache`, `.git`) al buscar archivos de código para no confundir un entorno virtual vacío con código del usuario.
   - Devuelve la instancia `ProjectInspection` con todos los campos calculados de forma determinista.

---

## 3. Fuera de Alcance (Qué NO entra en este paso)

- Conectar todavía el inspector al comando `compass init` en `cli.py` (eso pertenece al Paso 4 `04-agent-onboarding`).
- Analizar el contenido interno del código con un LLM (eso lo hará el Agente guiado por la skill `project-architect` cuando `state == ProjectState.BROWNFIELD`).

---

## 4. Criterios de Aceptación (Requisitos para TDD)

Archivo de pruebas: `tests/test_project_inspector.py` (usando el fixture `tmp_path` de `pytest` para crear directorios de prueba aislados):

- **CA-1 (Detección Greenfield en carpeta vacía o solo con Git/README/venv)**:
  - Si `target_dir` está vacío o solo contiene `.git/`, `README.md`, `.gitignore` y `.venv/` (incluso con archivos `.py` dentro de `.venv/`), `inspect_project(target_dir)` devuelve `state == ProjectState.GREENFIELD` y `detected_stacks == ()`.
- **CA-2 (Detección Brownfield por manifiesto de lenguaje)**:
  - Si `target_dir` contiene `pyproject.toml` (o `package.json`), devuelve `state == ProjectState.BROWNFIELD` e incluye `"python"` (o `"node"`) en `detected_stacks`.
- **CA-3 (Detección Brownfield por código fuente sin manifiesto y detección de carpetas)**:
  - Si `target_dir` no tiene `pyproject.toml` pero tiene una carpeta `src/` con un script `simulador_rf.py` y una carpeta `tests/`, devuelve `state == ProjectState.BROWNFIELD`, `"python"` en `detected_stacks`, y `("src", "tests")` en `existing_dirs`.
- **CA-4 (Detección de instalaciones previas de agentes/harness)**:
  - Si en `target_dir` ya existen `AGENTS.md` y `.agents/`, `existing_harness_files` los incluye exactamente para que el onboarding lo sepa.
- **CA-5 (Manejo de rutas inválidas)**:
  - Si `target_dir` no existe, lanza `FileNotFoundError`; si apunta a un archivo en lugar de un directorio, lanza `NotADirectoryError`.
