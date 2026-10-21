# Plan Técnico: `01-cli-skeleton`

- **ID de Feature**: `01-cli-skeleton`
- **Spec de Referencia**: [`spec.md`](spec.md)

---

## 1. Diseño Técnico y Archivos a Crear

### 1.1 Configuración de Empaquetado (`/home/carlos/compass-harness/pyproject.toml`)
Utilizaremos `setuptools` (estándar PEP 621) con soporte de layout `src/`:
- **Nombre del paquete**: `compass-harness`
- **Versión**: `0.1.0`
- **Dependencias**:
  - `typer>=0.9.0`
  - `rich>=13.0.0`
- **Dependencias opcionales (`[project.optional-dependencies]`)**:
  - `dev = ["pytest>=7.0.0"]`
- **Script ejecutable (`[project.scripts]`)**:
  - `compass = "compass_harness.cli:app"`
- **Configuración de `pytest` (`[tool.pytest.ini_options]`)**:
  - `testpaths = ["tests"]`
  - `pythonpath = ["src"]`

### 1.2 Paquete Base (`/home/carlos/compass-harness/src/compass_harness/__init__.py`)
- Define `__all__ = ["__version__"]` y `__version__ = "0.1.0"`.
- Se crearán también los paquetes vacíos iniciales `src/compass_harness/core/__init__.py` y `src/compass_harness/templates/__init__.py` respetando la arquitectura en 3 capas definida en [`docs/brain/architecture.md`](../../docs/brain/architecture.md).

### 1.3 Interfaz CLI (`/home/carlos/compass-harness/src/compass_harness/cli.py`)
- Instancia principal `app = typer.Typer(name="compass", help="Compass: Meta-Harness agnóstico y educativo para desarrollo con agentes.", no_args_is_help=True)`.
- Implementa un `@app.callback()` con el parámetro opcional:
  - `version: Optional[bool] = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True, help="Muestra la versión de compass-harness y termina.")`
- La función `version_callback(value: bool)` imprime `f"compass-harness v{__version__}"` y lanza `raise typer.Exit(code=0)` cuando `value` es `True`.

---

## 2. Estrategia de Tests (TDD Vertical Slices)

Archivo de pruebas: `/home/carlos/compass-harness/tests/test_cli_skeleton.py`

1. **Test 1 (`test_package_version`) — Cubre CA-1**:
   - Verifica que `from compass_harness import __version__` sea igual a `"0.1.0"`.
2. **Test 2 (`test_cli_version_flag`) — Cubre CA-2**:
   - Usa `typer.testing.CliRunner` para invocar `app` con `["--version"]` y `["-v"]`.
   - Comprueba `result.exit_code == 0` y `"compass-harness v0.1.0" in result.stdout`.
3. **Test 3 (`test_cli_help_flag`) — Cubre CA-3**:
   - Invoca `app` con `["--help"]`.
   - Comprueba `result.exit_code == 0` y que la descripción `"Meta-Harness"` esté presente en `result.stdout`.

---

## 3. Entorno de Ejecución y Verificación (CA-4)
- Se utilizará un entorno virtual `.venv` dentro de `/home/carlos/compass-harness/.venv` (o el gestor `uv` / `python3 -m venv` disponible en el sistema) e instalación editable (`pip install -e ".[dev]"`).
- Comprobación final ejecutando `/home/carlos/compass-harness/.venv/bin/compass --version` y `/home/carlos/compass-harness/.venv/bin/pytest`.
