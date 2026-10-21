# Lista de Tareas TDD: `06-ui-design-governance`

- **ID de Feature**: `06-ui-design-governance`
- **Plan asociado**: `specs/06-ui-design-governance/plan.md`
- **Regla de Ejecución**: Cada tarea sigue estrictamente `RED -> GREEN -> REFACTOR` sobre los *Seams* públicos definidos en el plan. No se marca `[x]` sin registrar el bloque de **Prueba Observada** real.

---

## Tareas

- [x] **Tarea 1: Detección de señales de UI y contratos de diseño previos en `inspect_project` (CA-1)**
  - **RED**: Crear `tests/test_ui_design_governance.py` con tests que verifiquen que `inspect_project(tmp_path)` detecta `tailwind.config.js`, `components.json` y archivos `.tsx` en `detected_ui_signals`, y detecta `DESIGN.md` o `docs/brain/design.md` en `existing_design_files`, devolviendo tuplas vacías `()` cuando es un proyecto backend puro. Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Actualizar `ProjectInspection` e `inspect_project` en `src/compass_harness/core/inspector.py`. Ejecutar `pytest` y verificar el paso a verde.
  - **Prueba Observada**:
    - **Fallo inicial (RED)**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_ui_design_governance.py
      # Salida:
      # FAILED tests/test_ui_design_governance.py::test_inspect_project_backend_pure_has_empty_ui_signals_and_design_files - AttributeError: 'ProjectInspection' object has no attribute 'detected_ui_signals'
      # FAILED tests/test_ui_design_governance.py::test_inspect_project_detects_ui_signals_from_manifests_and_components - AttributeError: 'ProjectInspection' object has no attribute 'detected_ui_signals'
      # FAILED tests/test_ui_design_governance.py::test_inspect_project_detects_existing_design_files - AttributeError: 'ProjectInspection' object has no attribute 'existing_design_files'
      # 3 failed in 0.04s
      ```
    - **Paso a verde (GREEN)**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_ui_design_governance.py
      # Salida:
      # tests/test_ui_design_governance.py ... [100%]
      # 3 passed in 0.04s
      ```

- [x] **Tarea 2: La 5.ª Skill `ui-design` (`.compass/skills/ui-design/SKILL.md`), UI Gate en `AGENTS.md` / `sdd-workflow` y symlinks en `installer.py` (CA-2, CA-3 y CA-4)**
  - **RED**: Añadir tests en `tests/test_ui_design_governance.py` (y actualizar los asertos de conteo de rutas de 12 a 13 y symlinks de 4 a 5 en `tests/test_templates_and_skills.py` y `tests/test_agent_onboarding.py`) que comprueben:
    1. `render_project_bundle(config)` incluye `.compass/skills/ui-design/SKILL.md` con frontmatter YAML válido.
    2. `ui-design/SKILL.md` incluye el protocolo Brownfield vs Greenfield, la URL `https://ancient-prompt-design-flow.base44.app/`, los 4 arquetipos (`precision-dark`, `warm-editorial`, `telemetry-grid`, `neo-brutalist-craft`), la ley de los 4 estados (`Loading`, `Empty`, `Error`, `Populated`) y las reglas Anti-Slop (prohibición de colores hexadecimales sueltos y clichés de IA).
    3. `AGENTS.md` (< 100 líneas) y `sdd-workflow/SKILL.md` incluyen el **UI / Frontend Gate** apuntando a `ui-design` y `docs/brain/design.md`.
    4. `apply_installation` crea el enlace simbólico `.agents/skills/ui-design` apuntando a `.compass/skills/ui-design`.
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar `render_ui_design_skill` en `src/compass_harness/templates/compass_skills_assets.py`, actualizar `brain_assets.py`, `renderer.py` e `installer.py`. Ejecutar `pytest` y verificar el paso a verde.
  - **Prueba Observada**:
    - **Fallo inicial (RED)**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      # Salida:
      # FAILED tests/test_agent_onboarding.py::test_plan_installation_structure_and_conflicts - AssertionError: assert 12 == 13
      # FAILED tests/test_agent_onboarding.py::test_apply_installation_writes_bundle_and_creates_symlinks - AssertionError: assert 13 == 14
      # FAILED tests/test_agent_onboarding.py::test_cli_init_phase_3_apply_end_to_end - AssertionError
      # FAILED tests/test_templates_and_skills.py::test_render_project_bundle_contains_all_13_paths - AssertionError: assert 12 == 13
      # FAILED tests/test_templates_and_skills.py::test_all_skills_have_valid_yaml_frontmatter - KeyError: '.compass/skills/ui-design/SKILL.md'
      # FAILED tests/test_ui_design_governance.py::test_render_project_bundle_includes_ui_design_skill_with_frontmatter - AssertionError
      # FAILED tests/test_ui_design_governance.py::test_ui_design_skill_content_requirements - KeyError: '.compass/skills/ui-design/SKILL.md'
      # FAILED tests/test_ui_design_governance.py::test_agents_md_and_sdd_workflow_contain_ui_gate - AssertionError
      # FAILED tests/test_ui_design_governance.py::test_apply_installation_creates_ui_design_symlinks - AssertionError
      # 9 failed, 38 passed in 0.28s
      ```
    - **Paso a verde (GREEN)**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      # Salida:
      # tests/test_agent_onboarding.py ........ [ 17%]
      # tests/test_cli_skeleton.py ... [ 23%]
      # tests/test_project_inspector.py ...... [ 36%]
      # tests/test_templates_and_skills.py .......... [ 57%]
      # tests/test_ui_design_governance.py ....... [ 72%]
      # tests/test_verification_check.py ............. [100%]
      # 47 passed in 0.22s
      ```

- [x] **Tarea 3: Auditoría de `docs/brain/design.md` en `verify_harness`, `compass status` y `compass check` (CA-5)**
  - **RED**: Añadir tests en `tests/test_ui_design_governance.py` que verifiquen:
    1. En un proyecto sin `docs/brain/design.md`, `verify_harness(tmp_path).has_design_contract` es `False` y `passed` es `True`.
    2. En un proyecto con un `docs/brain/design.md` válido (`<= 80` líneas, con secciones `Design Tokens` y `Typography`), `has_design_contract` es `True`, `passed` es `True` y `compass status` muestra `Contrato UI (design.md): Activo`.
    3. Si `docs/brain/design.md` tiene más de 80 líneas, reporta `BUDGET_EXCEEDED` y `compass check` devuelve exit code `1`.
    4. Si `docs/brain/design.md` está incompleto (sin sección de Tokens ni Typography), reporta `INCOMPLETE_DESIGN_CONTRACT` y `compass check` devuelve exit code `1`.
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Actualizar `src/compass_harness/core/verifier.py` y `src/compass_harness/cli.py`, ejecutar `pytest`, registrar todas las Pruebas Observadas en `specs/06-ui-design-governance/tasks.md` y verificar con `compass check --path /home/carlos/compass-harness` que todo el repositorio sigue pasando al 100%.
  - **Prueba Observada**:
    - **Fallo inicial (RED)**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests/test_ui_design_governance.py
      # Salida:
      # FAILED tests/test_ui_design_governance.py::test_verify_harness_without_design_contract_passes - AttributeError: 'HarnessReport' object has no attribute 'has_design_contract'
      # FAILED tests/test_ui_design_governance.py::test_verify_harness_with_valid_design_contract - AttributeError: 'HarnessReport' object has no attribute 'has_design_contract'
      # FAILED tests/test_ui_design_governance.py::test_verify_harness_design_contract_budget_exceeded - AttributeError: 'HarnessReport' object has no attribute 'has_design_contract'
      # FAILED tests/test_ui_design_governance.py::test_verify_harness_design_contract_incomplete - AttributeError: 'HarnessReport' object has no attribute 'has_design_contract'
      # 4 failed, 7 passed in 0.10s
      ```
    - **Paso a verde (GREEN)**:
      ```bash
      /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      # Salida:
      # tests/test_agent_onboarding.py ........ [ 15%]
      # tests/test_cli_skeleton.py ... [ 21%]
      # tests/test_project_inspector.py ...... [ 33%]
      # tests/test_templates_and_skills.py .......... [ 52%]
      # tests/test_ui_design_governance.py ........... [ 74%]
      # tests/test_verification_check.py ............. [100%]
      # 51 passed in 0.22s
      ```
