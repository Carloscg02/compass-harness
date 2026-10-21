# Lista de Tareas TDD: `02-project-inspector`

- **ID de Feature**: `02-project-inspector`
- **Plan de Referencia**: [`plan.md`](plan.md)
- **Regla de Cierre**: Ninguna tarea puede marcarse como `[x]` sin incluir debajo su bloque de **Prueba Observada** (comando ejecutado y salida real de `pytest` tanto en RED como en GREEN).

---

## Tareas

- [x] **Tarea 1 (Ciclo TDD — CA-1 y CA-5): Modelo base, validación de rutas y detección `GREENFIELD`**
  - **RED**: Crear `tests/test_project_inspector.py` con `test_inspect_empty_and_boilerplate_dir_is_greenfield` (directorio vacío y directorio con `.git/`, `README.md` y `.venv/lib/site.py`) y `test_inspect_raises_on_invalid_paths` (`FileNotFoundError` y `NotADirectoryError`). Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Crear `src/compass_harness/core/inspector.py` con `ProjectState`, `ProjectInspection` e `inspect_project` básico que pase estos dos tests.
  - **Prueba Observada**:
    - **RED** (`ModuleNotFoundError: No module named 'compass_harness.core.inspector'`):
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 3 items / 1 error

      ==================================== ERRORS ====================================
      _______________ ERROR collecting tests/test_project_inspector.py _______________
      ImportError while importing test module '/home/carlos/compass-harness/tests/test_project_inspector.py'.
      Hint: make sure your test modules/packages have valid Python names.
      Traceback:
      /usr/lib/python3.14/importlib/__init__.py:88: in import_module
          return _bootstrap._gcd_import(name[level:], package, level)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      ../../../compass-harness/tests/test_project_inspector.py:6: in <module>
          from compass_harness.core.inspector import (
      E   ModuleNotFoundError: No module named 'compass_harness.core.inspector'
      =========================== short test summary info ============================
      ERROR ../../../compass-harness/tests/test_project_inspector.py
      !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
      =============================== 1 error in 0.09s ===============================
      ```
    - **GREEN** (5 passed):
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 5 items

      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 60%]
      ../../../compass-harness/tests/test_project_inspector.py ..              [100%]

      ============================== 5 passed in 0.10s ===============================
      ```

- [x] **Tarea 2 (Ciclo TDD — CA-2 y CA-3): Detección `BROWNFIELD` por manifiestos, código fuente y carpetas (`existing_dirs`)**
  - **RED**: Añadir `test_inspect_detects_manifest_as_brownfield` (`pyproject.toml` -> `"python"`, `package.json` -> `"node"`) y `test_inspect_detects_source_files_and_existing_dirs_without_manifest` (`src/simulador_rf.py` y `tests/` -> `BROWNFIELD`, stack `"python"`, dirs `("src", "tests")`). Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar la detección de manifiestos, escaneo de extensiones excluyendo `IGNORED_DIRS` y detección de `existing_dirs` en `src/compass_harness/core/inspector.py`.
  - **Prueba Observada**:
    - **RED** (2 tests fallando al esperar `ProjectState.BROWNFIELD`):
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 7 items

      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 42%]
      ../../../compass-harness/tests/test_project_inspector.py ..FF            [100%]

      =================================== FAILURES ===================================
      _________________ test_inspect_detects_manifest_as_brownfield __________________

      tmp_path = PosixPath('/tmp/pytest-of-carlos/pytest-1/test_inspect_detects_manifest_0')

          def test_inspect_detects_manifest_as_brownfield(tmp_path: Path) -> None:
              """Verifica que la presencia de manifiestos clasifique como BROWNFIELD y detecte el stack (CA-2)."""
              # Proyecto Python con pyproject.toml
              py_proj = tmp_path / "py_project"
              py_proj.mkdir()
              (py_proj / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")
          
              result_py = inspect_project(py_proj)
      >       assert result_py.state == ProjectState.BROWNFIELD
      E       AssertionError: assert <ProjectState... 'greenfield'> == <ProjectState... 'brownfield'>
      E         
      E         - brownfield
      E         + greenfield

      ../../../compass-harness/tests/test_project_inspector.py:69: AssertionError
      _____ test_inspect_detects_source_files_and_existing_dirs_without_manifest _____

      tmp_path = PosixPath('/tmp/pytest-of-carlos/pytest-1/test_inspect_detects_source_fi0')

          def test_inspect_detects_source_files_and_existing_dirs_without_manifest(tmp_path: Path) -> None:
              """Verifica la deteccion de stacks por extensiones y carpetas existentes sin manifiesto (CA-3)."""
              rf_proj = tmp_path / "rf_project"
              rf_proj.mkdir()
              (rf_proj / "src").mkdir()
              (rf_proj / "src" / "simulador_rf.py").write_text("def simular(): pass\n", encoding="utf-8")
              (rf_proj / "tests").mkdir()
          
              result_rf = inspect_project(rf_proj)
      >       assert result_rf.state == ProjectState.BROWNFIELD
      E       AssertionError: assert <ProjectState... 'greenfield'> == <ProjectState... 'brownfield'>
      E         
      E         - brownfield
      E         + greenfield

      ../../../compass-harness/tests/test_project_inspector.py:91: AssertionError
      =========================== short test summary info ============================
      FAILED ../../../compass-harness/tests/test_project_inspector.py::test_inspect_detects_manifest_as_brownfield
      FAILED ../../../compass-harness/tests/test_project_inspector.py::test_inspect_detects_source_files_and_existing_dirs_without_manifest
      ========================= 2 failed, 5 passed in 0.10s ==========================
      ```
    - **GREEN** (7 passed):
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 7 items

      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 42%]
      ../../../compass-harness/tests/test_project_inspector.py ....            [100%]

      ============================== 7 passed in 0.09s ===============================
      ```

- [x] **Tarea 3 (Ciclo TDD — CA-4 y Refactor): Detección de instalaciones previas de agentes (`existing_harness_files`) y exportación en `core/__init__.py`**
  - **RED**: Añadir `test_inspect_detects_existing_harness_files` verificando la detección de `AGENTS.md`, `.agents/`, `.compass/` y `docs/brain/`. Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar la comprobación de `HARNESS_MARKERS` en `inspect_project`.
  - **REFACTOR**: Exportar `ProjectState`, `ProjectInspection` e `inspect_project` en `src/compass_harness/core/__init__.py`, revisar *type hints* y docstrings, y ejecutar la suite completa de tests (`tests/test_cli_skeleton.py` + `tests/test_project_inspector.py`).
  - **Prueba Observada**:
    - **RED** (`AssertionError: assert () == ('AGENTS.md', '.compass', '.agents', 'docs/brain')`):
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 8 items

      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 37%]
      ../../../compass-harness/tests/test_project_inspector.py ....F           [100%]

      =================================== FAILURES ===================================
      _________________ test_inspect_detects_existing_harness_files __________________

      tmp_path = PosixPath('/tmp/pytest-of-carlos/pytest-3/test_inspect_detects_existing_0')

          def test_inspect_detects_existing_harness_files(tmp_path: Path) -> None:
              """Verifica la deteccion de artefactos de harness preexistentes (CA-4)."""
              harness_proj = tmp_path / "harness_project"
              harness_proj.mkdir()
              (harness_proj / "AGENTS.md").write_text("# Agents configuration\n", encoding="utf-8")
              (harness_proj / ".agents").mkdir()
              (harness_proj / ".compass").mkdir()
              (harness_proj / "docs" / "brain").mkdir(parents=True)
          
              result = inspect_project(harness_proj)
      >       assert result.existing_harness_files == ("AGENTS.md", ".compass", ".agents", "docs/brain")
      E       AssertionError: assert () == ('AGENTS.md',... 'docs/brain')
      E         
      E         Right contains 4 more items, first extra item: 'AGENTS.md'
      E         Use -v to get more diff

      ../../../compass-harness/tests/test_project_inspector.py:106: AssertionError
      =========================== short test summary info ============================
      FAILED ../../../compass-harness/tests/test_project_inspector.py::test_inspect_detects_existing_harness_files
      ========================= 1 failed, 7 passed in 0.10s ==========================
      ```
    - **GREEN y REFACTOR** (9 passed):
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 9 items

      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 33%]
      ../../../compass-harness/tests/test_project_inspector.py ......          [100%]

      ============================== 9 passed in 0.09s ===============================
      ```
