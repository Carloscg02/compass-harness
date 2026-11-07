# Lista de Tareas: 08-compass-update (Sincronización Determinista del Arnés)

- [x] Tarea 1: Implementar extractor y planificador de actualización en `core/updater.py` (TDD Red -> Green)
  - Escribir tests en `tests/test_updater.py` para `extract_project_config`, `save_project_config` y `plan_update`.
  - Crear `src/compass_harness/core/updater.py` con `UpdatePlan`, `UpdateResult`, extracción regex de `index.md`/`architecture.md` y lectura/escritura de `.compass/config.json`.
  - Exportar símbolos en `src/compass_harness/core/__init__.py`.
  - Ejecutar `.venv/bin/pytest tests/test_updater.py` y verificar que pasa en verde.
  - **Prueba Observada**:
    ```text
    Fase Roja:
    ImportError while importing test module '/home/carlos/compass-harness/tests/test_updater.py'.
    E   ModuleNotFoundError: No module named 'compass_harness.core.updater'
    1 error in 0.13s

    Fase Verde:
    tests/test_updater.py .....                                              [100%]
    5 passed in 0.06s
    ```

- [x] Tarea 2: Implementar ejecución atómica `apply_update` con preservación de memoria viva (TDD Red -> Green)
  - Añadir tests en `tests/test_updater.py` que verifiquen que `apply_update` actualiza skills y `AGENTS.md`, pero **no toca** `docs/brain/modules/*.md`, `docs/brain/handoff.md` ni `docs/brain/decisions/*.md`.
  - Implementar `apply_update` en `src/compass_harness/core/updater.py`.
  - Ejecutar `.venv/bin/pytest tests/test_updater.py` y verificar paso a verde.
  - **Prueba Observada**:
    ```text
    Fase Roja:
    FAILED tests/test_updater.py::test_apply_update_updates_skills_and_agents_and_preserves_living_memory - NameError: name 'apply_update' is not defined
    FAILED tests/test_updater.py::test_apply_update_idempotency_and_force - NameError: name 'apply_update' is not defined
    FAILED tests/test_updater.py::test_apply_update_repairs_broken_symlinks - NameError: name 'apply_update' is not defined
    3 failed, 5 passed in 0.11s

    Fase Verde:
    tests/test_updater.py ........                                           [100%]
    8 passed in 0.10s
    ```

- [x] Tarea 3: Integrar subcomando `compass update` en CLI y validar integración (TDD Red -> Green)
  - Añadir comando `update` en `src/compass_harness/cli.py` con `--path`, `--preview`, `--apply` y `--force`.
  - Escribir tests CLI en `tests/test_updater.py` con `CliRunner` validando `COMPASS_UPDATE_REQUIRED`, `--preview`, `--apply` y el error `COMPASS_NOT_INITIALIZED`.
  - Ejecutar toda la suite de pruebas (`.venv/bin/pytest`) y `compass check`.
  - **Prueba Observada**:
    ```text
    Fase Roja:
    FAILED tests/test_updater.py::test_cli_update_not_initialized - assert 2 == 1
    FAILED tests/test_updater.py::test_cli_update_both_preview_and_apply - assert 2 == 1
    FAILED tests/test_updater.py::test_cli_update_required_info_screen - assert 2 == 0
    FAILED tests/test_updater.py::test_cli_update_preview - assert 2 == 0
    FAILED tests/test_updater.py::test_cli_update_apply_and_health_summary - assert 2 == 0
    FAILED tests/test_updater.py::test_cli_update_apply_force - assert 2 == 0
    6 failed, 8 passed in 0.21s

    Fase Verde:
    ============================== 66 passed in 0.29s ==============================

    === COMPASS_CHECK_PASSED ===
    Proyecto verificado correctamente en: /home/carlos/compass-harness
    - Archivos del Cerebro: 5/5 presentes
    - Presupuestos de contexto respetados (AGENTS.md y handoff.md)
    - Aislamiento O(1) de decisiones tecnicas respetado
    - Enlaces simbolicos: 0 activos, 0 rotos
    - Tareas con Prueba Observada auditadas: 25 completadas validas
    ```
