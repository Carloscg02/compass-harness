# Lista de Tareas TDD: `05-verification-check`

- **ID de Feature**: `05-verification-check`
- **Plan asociado**: `specs/05-verification-check/plan.md`
- **Regla de Ejecución**: Cada tarea sigue estrictamente `RED -> GREEN -> REFACTOR` sobre los *Seams* públicos definidos en el plan. No se marca `[x]` sin registrar el bloque de **Prueba Observada** real.

---

## Tareas

- [x] **Tarea 1: Motor `verify_harness` para archivos del Cerebro, presupuestos de líneas (`AGENTS.md` y `handoff.md`), enlace O(1) de ADRs y enlaces simbólicos rotos (CA-1, CA-2 y CA-3)**
  - **RED**: Crear `tests/test_verification_check.py` con tests unitarios y de integración sobre `verify_harness`:
    1. En un directorio inicializado con `apply_installation(tmp_path, config)`, `verify_harness(tmp_path).passed` es `True` y `issues` está vacío.
    2. En un directorio vacío sin inicializar, `verify_harness(tmp_path).is_installed` es `False`, `passed` es `False` y reporta `MISSING_BRAIN_FILE`.
    3. Si `AGENTS.md` tiene 105 líneas o `docs/brain/handoff.md` tiene 35 líneas, `verify_harness(tmp_path).passed` es `False` y reporta `BUDGET_EXCEEDED`.
    4. Si `docs/brain/index.md` lista múltiples enlaces a `decisions/0001...` y `decisions/0002...`, reporta `ADR_INDEX_BLOAT`.
    5. Si `.agents/skills/tdd` apunta a un destino inexistente (`shutil.rmtree(tmp_path / ".compass/skills/tdd")`), reporta `BROKEN_SYMLINK`.
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar `src/compass_harness/core/verifier.py` con estas validaciones. Ejecutar `pytest` y verificar el paso a verde.
  - **Prueba Observada**:
    - **Fase RED**:
      Comando ejecutado:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_verification_check.py
      ```
      Salida de fallo observada:
      ```text
      ImportError while importing test module '/home/carlos/compass-harness/tests/test_verification_check.py'.
      Hint: make sure your test modules/packages have valid Python names.
      Traceback:
      /usr/lib/python3.14/importlib/__init__.py:88: in import_module
          return _bootstrap._gcd_import(name[level:], package, level)
      /home/carlos/compass-harness/tests/test_verification_check.py:9: in <module>
          from compass_harness.core.verifier import (
      E   ModuleNotFoundError: No module named 'compass_harness.core.verifier'
      =========================== short test summary info ============================
      ERROR tests/test_verification_check.py
      !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
      =============================== 1 error in 0.09s ===============================
      ```
    - **Fase GREEN**:
      Comando ejecutado:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_verification_check.py
      ```
      Salida de exito observada:
      ```text
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 5 items

      tests/test_verification_check.py .....                                   [100%]

      ============================== 5 passed in 0.03s ===============================
      ```

- [x] **Tarea 2: Auditoría de Prueba Observada en `specs/*/tasks.md` dentro de `verify_harness` (CA-4)**
  - **RED**: Añadir tests en `tests/test_verification_check.py` que creen una carpeta `specs/01-demo/tasks.md` dentro de un proyecto inicializado:
    1. Si una tarea está marcada `- [x] **Tarea 1: Demo**` pero su bloque dice `- **Prueba Observada**: *(Pendiente)*` (o no menciona `Prueba Observada`), `verify_harness` devuelve `passed == False`, incluye `"MISSING_OBSERVED_PROOF"` en `issues` y refleja la tarea en `specs_progress[0].tasks_missing_proof`.
    2. Si la tarea está en `- [ ] **Tarea 2: Demo**` con `*(Pendiente)*`, NO reporta error (porque aún no se ha marcado como completada) y cuenta `total_tasks=2, completed_tasks=1`.
    3. Cuando la Tarea 1 `[x]` tiene un bloque real de Prueba Observada con la salida del comando (sin `*(Pendiente)*`), `verify_harness` devuelve `passed == True`.
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar el parser de `specs/*/tasks.md` en `src/compass_harness/core/verifier.py` y re-exportar `SpecProgress`, `CheckIssue`, `HarnessReport` y `verify_harness` en `src/compass_harness/core/__init__.py`. Ejecutar `pytest` y verificar el paso a verde.
  - **Prueba Observada**:
    - **Fase RED**:
      Comando ejecutado:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_verification_check.py
      ```
      Salida de fallo observada:
      ```text
      FAILED tests/test_verification_check.py::test_verify_harness_detects_missing_observed_proof_in_completed_tasks - AssertionError: assert True is False
      FAILED tests/test_verification_check.py::test_verify_harness_fails_when_completed_task_has_no_observed_proof_keyword - AssertionError: assert True is False
      FAILED tests/test_verification_check.py::test_verify_harness_passes_when_completed_tasks_have_real_observed_proof - AssertionError: assert 0 == 1
      FAILED tests/test_verification_check.py::test_core_reexports_verifier_symbols - ImportError: cannot import name 'CheckIssue' from 'compass_harness.core'
      ========================= 4 failed, 5 passed in 0.06s ==========================
      ```
    - **Fase GREEN**:
      Comando ejecutado:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_verification_check.py
      ```
      Salida de exito observada:
      ```text
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 9 items

      tests/test_verification_check.py .........                               [100%]

      ============================== 9 passed in 0.03s ===============================
      ```

- [x] **Tarea 3: Subcomandos CLI `compass status` y `compass check` + Dogfooding sobre `/home/carlos/compass-harness` (CA-5)**
  - **RED**: Añadir tests en `tests/test_verification_check.py` usando `CliRunner`:
    1. `compass status --path <tmp_path>` devuelve exit code `0` e imprime `COMPASS_STATUS`, `HEALTHY` y el progreso de specs (`1/2`).
    2. `compass check --path <tmp_path>` devuelve exit code `0` e imprime `COMPASS_CHECK_PASSED` cuando el proyecto está sano, y devuelve exit code `1` con `COMPASS_CHECK_FAILED` y el código del issue cuando hay una infracción.
    3. Test de Dogfooding real: invocar `compass check --path /home/carlos/compass-harness` (teniendo en cuenta que esta misma Tarea 3 en `specs/05-verification-check/tasks.md` se marcará `[x]` al cerrar o mientras está `[ ]`) debe devolver exit code `0` (`COMPASS_CHECK_PASSED`).
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar `@app.command("status")` y `@app.command("check")` en `src/compass_harness/cli.py`, ejecutar `pytest`, actualizar `specs/05-verification-check/tasks.md` con todos los bloques de Prueba Observada y ejecutar el binario real `/home/carlos/compass-harness/.venv/bin/compass check --path /home/carlos/compass-harness` y `/home/carlos/compass-harness/.venv/bin/compass status --path /home/carlos/compass-harness` para verificar que nuestro propio repositorio pasa su auditoría en verde.
  - **Prueba Observada**:
    - **Fase RED**:
      Comando ejecutado:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_verification_check.py
      ```
      Salida de fallo observada:
      ```text
      FAILED tests/test_verification_check.py::test_cli_status_command_reports_healthy_and_specs_progress - assert 2 == 0
      FAILED tests/test_verification_check.py::test_cli_check_command_passes_on_healthy_project - assert 2 == 0
      FAILED tests/test_verification_check.py::test_cli_check_command_fails_on_broken_project - assert 2 == 1
      FAILED tests/test_verification_check.py::test_cli_dogfooding_on_compass_harness_repository - assert 2 == 0
      ========================= 4 failed, 9 passed in 0.13s ==========================
      ```
    - **Fase GREEN**:
      Comando ejecutado:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_verification_check.py
      ```
      Salida de exito observada:
      ```text
      ============================= test session starts ==============================
      platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
      rootdir: /home/carlos/compass-harness
      configfile: pyproject.toml
      collecting ... collected 13 items

      tests/test_verification_check.py .............                           [100%]

      ============================== 13 passed in 0.08s ==============================
      ```
    - **Ejecucion del binario real (`compass check` y `compass status`)**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/compass check --path /home/carlos/compass-harness
      ```
      Salida:
      ```text
      === COMPASS_CHECK_PASSED ===
      Proyecto verificado correctamente en: /home/carlos/compass-harness
      - Archivos del Cerebro: 5/5 presentes
      - Presupuestos de contexto respetados (AGENTS.md y handoff.md)
      - Aislamiento O(1) de decisiones tecnicas respetado
      - Enlaces simbolicos: 0 activos, 0 rotos
      - Tareas con Prueba Observada auditadas: 16 completadas validas
      ```
      ```bash
      /home/carlos/compass-harness/.venv/bin/compass status --path /home/carlos/compass-harness
      ```
      Salida:
      ```text
      === COMPASS_STATUS ===
      Estado general: HEALTHY
      Archivos del Cerebro: 5/5 presentes
      Skills instaladas: Ninguna
      Enlaces simbolicos: 0 activos, 0 rotos
      Progreso de Specs:
        - 01-cli-skeleton: 4/4 tareas completadas
        - 02-project-inspector: 3/3 tareas completadas
        - 03-templates-and-skills: 3/3 tareas completadas
        - 04-agent-onboarding: 3/3 tareas completadas
        - 05-verification-check: 3/3 tareas completadas
      ```
