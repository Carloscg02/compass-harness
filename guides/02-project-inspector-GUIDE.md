# Guía de Mentoría #02: Modelado de Dominio Inmutable y Tests de Archivos con `tmp_path` (`02-project-inspector`)

> **Modo Mentor (`compass`)** · **Nivel**: Ingeniería de Software en Python (Dominio Puro y Testing)  
> **Objetivo**: Entender las técnicas de diseño profesional aplicadas en `src/compass_harness/core/inspector.py` y `tests/test_project_inspector.py`.

---

## 1. Por qué `inspector.py` es un Módulo de Dominio Puro

Si abres [`src/compass_harness/core/inspector.py`](../src/compass_harness/core/inspector.py), notarás lo que **NO** hay en él:
- No hay `import typer` ni `import rich`.
- No hay ni un solo `print()`.

Esta es la materialización práctica de la frontera que definimos en [`docs/brain/architecture.md`](../docs/brain/architecture.md). `inspect_project(target_dir)` recibe un `Path` y devuelve un objeto `ProjectInspection`. Gracias a eso, mañana podemos usar esta misma función para imprimir texto plano para un agente, dibujar una tabla en terminal, devolver un JSON o verificarla en `pytest` en 0.08 segundos.

---

## 2. Tres Patrones de Python Moderno usados en `inspector.py`

### A. `class ProjectState(str, Enum)` (Enumeraciones en vez de "Strings Mágicos")
Un principiante suele devolver cadenas de texto sueltas como `return "greenfield"`. El problema de eso es que si en otro archivo escribes por error `if state == "grenfield":` (con una sola *e*), Python no te avisa del error y la condición falla en silencio.
```python
class ProjectState(str, Enum):
    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"
```
* Al usar `Enum`, el editor te autocompleta `ProjectState.GREENFIELD` y cualquier error tipográfico falla al instante.
* Al heredar además de `str` (`(str, Enum)`), cada estado se comporta también como un `str` cuando necesitas serializarlo a JSON o mostrarlo en texto.

### B. `@dataclass(frozen=True)` e Inmutabilidad con `tuple`
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
* **`@dataclass`**: Genera automáticamente el constructor `__init__`, la comparación `__eq__` (vital para hacer `assert result == ...` en los tests) y la representación legible `__repr__`.
* **`frozen=True`**: Hace que el objeto sea **inmutable** (como una fotografía). Una vez que `inspect_project` devuelve el diagnóstico de la carpeta, ninguna otra parte del programa puede modificar sus campos por accidente.
* **`tuple[str, ...]` en lugar de `list[str]`**: En Python, una lista (`list`) es mutable (se le puede hacer `.append()`), mientras que una tupla (`tuple`) es inmutable. Para que un `dataclass(frozen=True)` sea verdaderamente inmutable de principio a fin, sus colecciones internas se declaran como tuplas.

### C. Poda en caliente de `os.walk` (`dirnames[:] = ...`)
Mira las líneas 89-90 de `inspector.py`:
```python
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
```
* **Qué problema resuelve**: Si un proyecto tiene una carpeta `.venv/` o `node_modules/` con 15.000 archivos dentro y recorres todo el árbol para luego filtrar con un `if`, tu programa tardará varios segundos leyendo miles de archivos inútiles.
* **Por qué se escribe `dirnames[:]` (con `[:]`) y no `dirnames =`**:
  En `os.walk`, modificar la lista `dirnames` **en el mismo sitio en memoria (*in-place*)** usando la notación de *slice* `dirnames[:] = ...` le indica a `os.walk` que **ni siquiera entre** en esas carpetas (como `.venv`, `.git` o `node_modules`). A esto se le llama **poda del árbol de búsqueda (*tree pruning*)**, y hace que el escaneo sea instantáneo.

---

## 3. Cómo probamos sistemas de archivos sin ensuciar tu disco: El fixture `tmp_path`

En [`tests/test_project_inspector.py`](../tests/test_project_inspector.py), todas las funciones de test reciben un argumento especial:
```python
def test_inspect_detects_manifest_as_brownfield(tmp_path: Path) -> None:
```
* **Qué es `tmp_path`**: Es un *fixture* integrado en `pytest`. Cuando `pytest` ve que tu función pide un parámetro llamado `tmp_path`, crea automáticamente una carpeta temporal única y vacía en `/tmp/pytest-of-carlos/...` solo para ese test, te pasa su objeto `Path`, y la limpia al terminar.
* Gracias a `tmp_path`, podemos crear carpetas falsas (`.venv`, `src/simulador_rf.py`, `pyproject.toml`), probar casos extremos y tener la certeza absoluta de que un test nunca contamina al siguiente ni toca los archivos reales de tu proyecto.
