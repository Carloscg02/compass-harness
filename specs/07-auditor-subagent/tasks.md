# Lista de Tareas: 07-auditor-subagent (Puerta de Auditoría Independiente)

- [x] Tarea 1: Escribir tests para el Auditor Subagent en plantillas y skills (TDD Red)
  - Añadir aserciones en `tests/test_templates_and_skills.py` para validar la presencia del rol Auditor, la secuencia de 6 pasos en `AGENTS.md` y la Rúbrica de 4 Puntos en `sdd-workflow/SKILL.md`.
  - Ejecutar `.venv/bin/pytest tests/test_templates_and_skills.py` y verificar que falla (Fase Roja).
  - **Prueba Observada**:
    ```text
    FAILED tests/test_templates_and_skills.py::test_agents_md_structure_and_model_strategies - AssertionError: assert 'builder' in ...
    FAILED tests/test_templates_and_skills.py::test_sdd_workflow_skill_includes_auditor_gate_and_rubric - AssertionError: assert 'Auditor Subagent' in ...
    2 failed, 9 passed in 0.07s
    ```

- [x] Tarea 2: Implementar la sección del Auditor Subagent en `render_sdd_workflow_skill` y `render_agents_md` (TDD Green)
  - Modificar `src/compass_harness/templates/compass_skills_assets.py` para incluir la Puerta de Auditoría, la Rúbrica de 4 Puntos y el Feedback Loop en `sdd-workflow`.
  - Modificar `src/compass_harness/templates/brain_assets.py` para documentar la Tríada de roles y el paso de auditoría en `AGENTS.md`, respetando `< 99` líneas.
  - Ejecutar `.venv/bin/pytest tests/test_templates_and_skills.py` y verificar que pasa en verde (Fase Verde).
  - **Prueba Observada**:
    ```text
    tests/test_templates_and_skills.py ...........                           [100%]
    11 passed in 0.02s
    AGENTS.md line count: 38 (presupuesto < 99 lineas cumplido)
    ```

- [x] Tarea 3: Actualizar el router del proyecto (`AGENTS.md`) y verificar invariantes con `compass check`
  - Actualizar [`AGENTS.md`](../../AGENTS.md) del repositorio para incorporar el rol del Auditor Subagent y la secuencia de 6 pasos en `[LANE: SDD]`.
  - Ejecutar `.venv/bin/pytest` en toda la suite.
  - Ejecutar `.venv/bin/python3 -m compass_harness.cli check` y registrar la salida limpia.
  - **Prueba Observada**:
    ```text
    ============================== 52 passed in 0.19s ==============================
    === COMPASS_CHECK_PASSED ===
    Proyecto verificado correctamente en: /home/carlos/compass-harness
    - Archivos del Cerebro: 5/5 presentes
    - Presupuestos de contexto respetados (AGENTS.md y handoff.md)
    - Aislamiento O(1) de decisiones tecnicas respetado
    - Enlaces simbolicos: 0 activos, 0 rotos
    - Tareas con Prueba Observada auditadas: 22 completadas validas
    ```

