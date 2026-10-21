# Lista de Tareas TDD: `03-templates-and-skills`

- **ID de Feature**: `03-templates-and-skills`
- **Plan asociado**: `specs/03-templates-and-skills/plan.md`
- **Regla de Ejecución**: Cada tarea sigue estrictamente `RED -> GREEN -> REFACTOR` sobre los *Seams* públicos definidos en el plan. No se marca `[x]` sin registrar el bloque de **Prueba Observada** real.

---

## Tareas

- [x] **Tarea 1: Modelo `ProjectConfig`, esqueleto de `render_project_bundle` e inclusión íntegra de la skill `tdd` de Matt Pocock (CA-1 y CA-2)**
  - **RED**: Crear `tests/test_templates_and_skills.py` con tests que instancien `ProjectConfig` y verifiquen que `render_project_bundle(config)` devuelve las 12 rutas relativas esperadas (incluyendo `.compass/skills/tdd/SKILL.md`, `.compass/skills/tdd/tests.md`, `.compass/skills/tdd/mocking.md`) y que `tdd/SKILL.md` contiene `name: tdd`, `What a good test is`, `Seams: where tests go`, `Anti-patterns`, `Horizontal slicing` y `Rules of the loop`, además del contenido clave de `tests.md` y `mocking.md`. Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Crear `src/compass_harness/templates/__init__.py`, `src/compass_harness/templates/tdd_skill_assets.py` (copiando los 3 archivos de la skill `tdd` de Matt Pocock guardados en `/home/carlos/.gemini/antigravity/brain/6a7ffd6c-9b7c-45f1-b57f-bd208bf48218/scratch/mattpocock_tdd/`) y `src/compass_harness/core/renderer.py`. Ejecutar `pytest` y verificar el paso a verde.
  - **Prueba Observada**:
    - **RED**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ModuleNotFoundError: No module named 'compass_harness.core.renderer'
      ERROR tests/test_templates_and_skills.py - 1 error in 0.09s
      ```
    - **GREEN**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      collected 11 items
      tests/test_cli_skeleton.py ... [ 27%]
      tests/test_project_inspector.py ...... [ 81%]
      tests/test_templates_and_skills.py .. [100%]
      11 passed in 0.09s
      ```

- [x] **Tarea 2: Plantillas parametrizadas del Router (`AGENTS.md`) y del Cerebro (`docs/brain/...`) con Comandos de Verificación y enlace O(1) a ADRs (CA-3 y CA-4)**
  - **RED**: Añadir tests en `tests/test_templates_and_skills.py` que comprueben:
    1. `AGENTS.md` tiene menos de 100 líneas, incluye los 3 carriles (`ANSWER`, `FTD`, `SDD`), apunta a `docs/brain/index.md` y cambia su sección de delegación según `model_strategy` (`"subagent-fast"` vs `"single"`).
    2. `docs/brain/index.md` incluye los datos del proyecto y enlaza a `decisions/index.md` en una única línea (sin listar ADRs individuales).
    3. `docs/brain/architecture.md` adapta sus reglas según `architecture_style` (`"hexagonal"` vs `"script"`) e incluye la sección de **Verification Commands** con Unit & Integration Tests (`test_command`), Static/Lint Gate (`lint_command`) y E2E / Browser UI Tests opcional (`e2e_command`, por ejemplo `npx playwright test` o `N/A`).
    4. `docs/brain/handoff.md` tiene menos de 30 líneas.
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar `src/compass_harness/templates/brain_assets.py` y conectarlo en `render_project_bundle`. Ejecutar `pytest` y verificar el paso a verde.
  - **Prueba Observada**:
    - **RED**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      FAILED tests/test_templates_and_skills.py::test_agents_md_structure_and_model_strategies
      FAILED tests/test_templates_and_skills.py::test_brain_index_md_contents_and_o1_adr_link
      FAILED tests/test_templates_and_skills.py::test_architecture_md_style_and_verification_commands
      FAILED tests/test_templates_and_skills.py::test_handoff_and_decisions_assets
      4 failed, 11 passed in 0.12s
      ```
    - **GREEN**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      collected 15 items
      tests/test_cli_skeleton.py ... [ 20%]
      tests/test_project_inspector.py ...... [ 60%]
      tests/test_templates_and_skills.py ...... [100%]
      15 passed in 0.09s
      ```

- [x] **Tarea 3: Skills propias de Compass (`project-architect`, `sdd-workflow`, `mentor-guide`) y re-exportación en `compass_harness.core` (CA-5)**
  - **RED**: Añadir tests en `tests/test_templates_and_skills.py` que verifiquen:
    1. Todas las `SKILL.md` en `.compass/skills/` tienen frontmatter YAML válido (`name:` y `description:`).
    2. `.compass/skills/sdd-workflow/SKILL.md` referencia los `Seams` de la skill `tdd` (unit & integration), la verificación E2E/Playwright opcional cuando el proyecto lo soporte y la feature toque UI/flujos completos ejecutada por el subagente ligero (`flash` / fast tier), el `ADR Gate` (`decisions/index.md`) y `Observed Proof`.
    3. `.compass/skills/mentor-guide/SKILL.md` inyecta el `domain` configurado en `ProjectConfig`.
    4. `ProjectConfig` y `render_project_bundle` se pueden importar directamente desde `compass_harness.core`.
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar `src/compass_harness/templates/compass_skills_assets.py`, conectarlo en `renderer.py` y exportar `ProjectConfig` y `render_project_bundle` en `src/compass_harness/core/__init__.py`. Ejecutar toda la suite `pytest` y verificar que el 100% de tests del proyecto pasa en verde.
  - **Prueba Observada**:
    - **RED**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      FAILED tests/test_templates_and_skills.py::test_all_skills_have_valid_yaml_frontmatter
      FAILED tests/test_templates_and_skills.py::test_sdd_workflow_skill_content
      FAILED tests/test_templates_and_skills.py::test_mentor_guide_skill_injects_domain
      FAILED tests/test_templates_and_skills.py::test_core_package_reexports_renderer_symbols
      4 failed, 15 passed in 0.14s
      ```
    - **GREEN**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      collected 19 items
      tests/test_cli_skeleton.py ... [ 15%]
      tests/test_project_inspector.py ...... [ 47%]
      tests/test_templates_and_skills.py .......... [100%]
      19 passed in 0.09s
      ```
