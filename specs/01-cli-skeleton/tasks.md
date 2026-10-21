# Lista de Tareas TDD: `01-cli-skeleton`

- **ID de Feature**: `01-cli-skeleton`
- **Plan de Referencia**: [`plan.md`](plan.md)
- **Regla de Cierre**: Ninguna tarea puede marcarse como `[x]` sin incluir debajo su bloque de **Prueba Observada** (comando ejecutado y salida real).

---

## Tareas

- [x] **Tarea 1: Configurar `pyproject.toml`, estructura de carpetas `src/` y entorno virtual (`.venv`)**
  - Crear `/home/carlos/compass-harness/pyproject.toml`.
  - Crear carpetas `src/compass_harness/`, `src/compass_harness/core/`, `src/compass_harness/templates/` y `tests/`.
  - Preparar el entorno virtual e instalar `typer`, `rich` y `pytest`.
  - **Prueba Observada**:
    ```bash
    /home/carlos/compass-harness/.venv/bin/python -m pip list
    ```
    Salida obtenida:
    ```text
    Package        Version
    -------------- -------
    annotated-doc  0.0.5
    iniconfig      2.3.1
    markdown-it-py 4.2.0
    mdurl          0.1.2
    packaging      26.3
    pip            25.1.1
    pluggy         1.7.0
    Pygments       2.21.0
    pytest         9.1.1
    rich           15.0.0
    shellingham    1.5.4
    typer          0.27.3
    ```

- [x] **Tarea 2 (Ciclo TDD — CA-1): Versión del paquete (`__version__`)**
  - **RED**: Crear `tests/test_cli_skeleton.py` con `test_package_version` y verificar que falla antes de definir `__version__`.
  - **GREEN**: Implementar `__version__ = "0.1.0"` en `src/compass_harness/__init__.py` y verificar que `pytest` pasa.
  - **Prueba Observada**:
    - **Fallo en RED**:
      ```bash
      PYTHONPATH=/home/carlos/compass-harness/src /home/carlos/compass-harness/.venv/bin/pytest -c /home/carlos/compass-harness/pyproject.toml /home/carlos/compass-harness/tests
      ```
      Salida obtenida:
      ```text
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 1 item

      ../../../compass-harness/tests/test_cli_skeleton.py F                    [100%]

      =================================== FAILURES ===================================
      _____________________________ test_package_version _____________________________

          def test_package_version() -> None:
              """Verifica que el paquete exponga la version esperada 0.1.0 (CA-1)."""
              import compass_harness

      >       assert hasattr(compass_harness, "__version__")
      E       AssertionError: assert False
      E        +  where False = hasattr(<module 'compass_harness' (namespace) from ['/home/carlos/compass-harness/src/compass_harness', '/home/carlos/compass-harness/src/compass_harness']>, '__version__')

      ../../../compass-harness/tests/test_cli_skeleton.py:8: AssertionError
      =========================== short test summary info ============================
      FAILED ../../../compass-harness/tests/test_cli_skeleton.py::test_package_version
      ============================== 1 failed in 0.05s ===============================
      ```
    - **Éxito en GREEN**:
      ```bash
      PYTHONPATH=/home/carlos/compass-harness/src /home/carlos/compass-harness/.venv/bin/pytest -c /home/carlos/compass-harness/pyproject.toml /home/carlos/compass-harness/tests
      ```
      Salida obtenida:
      ```text
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 1 item

      ../../../compass-harness/tests/test_cli_skeleton.py .                    [100%]

      ============================== 1 passed in 0.02s ===============================
      ```

- [x] **Tarea 3 (Ciclo TDD — CA-2 y CA-3): CLI Base con `--version`, `-v` y `--help`**
  - **RED**: Añadir `test_cli_version_flag` y `test_cli_help_flag` en `tests/test_cli_skeleton.py` y ejecutar `pytest` para observar el fallo.
  - **GREEN**: Implementar `app` y `version_callback` en `src/compass_harness/cli.py` y ejecutar `pytest` hasta que los 3 tests estén en verde.
  - **REFACTOR**: Revisar *type hints*, docstrings y limpieza en `src/compass_harness/cli.py` manteniendo los tests en verde.
  - **Prueba Observada**:
    - **Fallo en RED**:
      ```bash
      PYTHONPATH=/home/carlos/compass-harness/src /home/carlos/compass-harness/.venv/bin/pytest -c /home/carlos/compass-harness/pyproject.toml /home/carlos/compass-harness/tests
      ```
      Salida obtenida:
      ```text
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 3 items

      ../../../compass-harness/tests/test_cli_skeleton.py .FF                  [100%]

      =================================== FAILURES ===================================
      ____________________________ test_cli_version_flag _____________________________

          def test_cli_version_flag() -> None:
              """Verifica que las opciones --version y -v retornen la version del paquete (CA-2)."""
      >       from compass_harness.cli import app
      E       ModuleNotFoundError: No module named 'compass_harness.cli'

      ../../../compass-harness/tests/test_cli_skeleton.py:18: ModuleNotFoundError
      ______________________________ test_cli_help_flag ______________________________

          def test_cli_help_flag() -> None:
              """Verifica que la opcion --help muestre la ayuda y descripcion general (CA-3)."""
      >       from compass_harness.cli import app
      E       ModuleNotFoundError: No module named 'compass_harness.cli'

      ../../../compass-harness/tests/test_cli_skeleton.py:31: ModuleNotFoundError
      =========================== short test summary info ============================
      FAILED ../../../compass-harness/tests/test_cli_skeleton.py::test_cli_version_flag
      FAILED ../../../compass-harness/tests/test_cli_skeleton.py::test_cli_help_flag
      ========================= 2 failed, 1 passed in 0.08s ==========================
      ```
    - **Éxito en GREEN y REFACTOR**:
      ```bash
      PYTHONPATH=/home/carlos/compass-harness/src /home/carlos/compass-harness/.venv/bin/pytest -c /home/carlos/compass-harness/pyproject.toml /home/carlos/compass-harness/tests
      ```
      Salida obtenida:
      ```text
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 3 items

      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [100%]

      ============================== 3 passed in 0.14s ===============================
      ```

- [x] **Tarea 4 (Verificación End-to-End — CA-4): Instalación editable y prueba del ejecutable `compass`**
  - Instalar el paquete en modo editable (`pip install -e .` en `.venv`) y ejecutar el binario real `compass --version` y `compass --help`.
  - **Prueba Observada**:
    - **Instalación editable**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pip install -e /home/carlos/compass-harness
      ```
      Salida obtenida:
      ```text
      Obtaining file:///home/carlos/compass-harness
        Installing build dependencies ... done
        Checking if build backend supports build_editable ... done
        Getting requirements to build editable ... done
        Preparing editable metadata (pyproject.toml) ... done
      Requirement already satisfied: typer>=0.9.0 in /home/carlos/compass-harness/.venv/lib/python3.14/site-packages (from compass-harness==0.1.0) (0.27.3)
      Requirement already satisfied: rich>=13.0.0 in /home/carlos/compass-harness/.venv/lib/python3.14/site-packages (from compass-harness==0.1.0) (15.0.0)
      Building wheels for collected packages: compass-harness
        Building editable for compass-harness (pyproject.toml) ... done
        Created wheel for compass-harness: filename=compass_harness-0.1.0-0.editable-py3-none-any.whl size=1706 sha256=478098cb5062fd3e4b468e1316cf193815d368d32878a3a251c361307962f235
      Successfully built compass-harness
      Installing collected packages: compass-harness
      Successfully installed compass-harness-0.1.0
      ```
    - **Ejecución `compass --version`**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/compass --version
      ```
      Salida obtenida:
      ```text
      compass-harness v0.1.0
      ```
    - **Ejecución `compass -v`**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/compass -v
      ```
      Salida obtenida:
      ```text
      compass-harness v0.1.0
      ```
    - **Ejecución `compass --help`**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/compass --help
      ```
      Salida obtenida:
      ```text
       Usage: compass [OPTIONS] COMMAND [ARGS]...

       Compass: Meta-Harness agnostico y educativo para desarrollo con agentes.

      ╭─ Options ────────────────────────────────────────────────────────────────────╮
      │ --version             -v        Muestra la version de compass-harness y      │
      │                                 termina.                                     │
      │ --install-completion            Install completion for the current shell.    │
      │ --show-completion               Show completion for the current shell, to    │
      │                                 copy it or customize the installation.       │
      │ --help                          Show this message and exit.                  │
      ╰──────────────────────────────────────────────────────────────────────────────╯
      ```
    - **Suite de pruebas final**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ```
      Salida obtenida:
      ```text
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 3 items

      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [100%]

      ============================== 3 passed in 0.12s ===============================
      ```
