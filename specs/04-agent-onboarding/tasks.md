# Lista de Tareas TDD: `04-agent-onboarding`

- **ID de Feature**: `04-agent-onboarding`
- **Plan asociado**: `specs/04-agent-onboarding/plan.md`
- **Regla de Ejecución**: Cada tarea sigue estrictamente `RED -> GREEN -> REFACTOR` sobre los *Seams* públicos definidos en el plan. No se marca `[x]` sin registrar el bloque de **Prueba Observada** real.

---

## Tareas

- [x] **Tarea 1: Motor de instalación en `core/installer.py` (`plan_installation` y `apply_installation`) con Symlinks Agnósticos y Protección de Sobrescritura (CA-2, CA-3, CA-4 a nivel Core)**
  - **RED**: Crear `tests/test_agent_onboarding.py` con tests sobre `plan_installation` y `apply_installation` usando `tmp_path`:
    1. Verificar que `plan_installation(tmp_path, config)` no escribe nada en disco, lista los 12 archivos del bundle (o 13 cuando `"claude"` está en `target_assistants`, incluyendo `CLAUDE.md`), detecta archivos ya existentes en `existing_conflicts` y genera los `SymlinkSpec` para `.agents/skills/` y `.claude/skills/`.
    2. Verificar que `apply_installation(tmp_path, config)` escribe todos los archivos en disco, crea las carpetas `docs/brain/modules`, `specs` y `guides`, y crea enlaces simbólicos funcionales en `.agents/skills/{tdd,project-architect,sdd-workflow,mentor-guide}` y `.claude/skills/{tdd,project-architect,sdd-workflow,mentor-guide}` tales que `(tmp_path / ".agents/skills/tdd/SKILL.md").read_text()` contiene `name: tdd`.
    3. Verificar que si `AGENTS.md` ya existe en `tmp_path`, `apply_installation(..., force=False)` no lo sobrescribe y lo reporta en `skipped_files`, mientras que `apply_installation(..., force=True)` sí lo actualiza.
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar `src/compass_harness/core/installer.py` y re-exportar sus símbolos públicos en `src/compass_harness/core/__init__.py`. Ejecutar `pytest` y verificar el paso a verde.
  - **Prueba Observada**:
    - **Fallo observado (RED)**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      ImportError while importing test module '/home/carlos/compass-harness/tests/test_agent_onboarding.py'.
      E   ModuleNotFoundError: No module named 'compass_harness.core.installer'
      =========================== short test summary info ============================
      ERROR ../../../compass-harness/tests/test_agent_onboarding.py
      !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
      =============================== 1 error in 0.12s ===============================
      ```
    - **Paso a verde (GREEN)**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      collected 22 items

      ../../../compass-harness/tests/test_agent_onboarding.py ...              [ 13%]
      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 27%]
      ../../../compass-harness/tests/test_project_inspector.py ......          [ 54%]
      ../../../compass-harness/tests/test_templates_and_skills.py ..........   [100%]

      ============================== 22 passed in 0.15s ==============================
      ```

- [x] **Tarea 2: Subcomando CLI `compass init` — Fase 1 (`COMPASS_ONBOARDING_REQUIRED`) y Fase 2 (`--preview` -> `COMPASS_ONBOARDING_PLAN`) (CA-1, CA-2 y CA-5)**
  - **RED**: Añadir tests en `tests/test_agent_onboarding.py` usando `CliRunner` contra `app`:
    1. `compass init --path <tmp_path>` en directorio Greenfield y en directorio Brownfield devuelve exit code `0`, no crea archivos nuevos, e imprime `COMPASS_ONBOARDING_REQUIRED`, el estado (`GREENFIELD` / `BROWNFIELD`) y `--preview`.
    2. `compass init --path <tmp_path> --name demo --goal "Demo" --assistants antigravity,claude --preview` devuelve exit code `0`, no escribe archivos en `<tmp_path>`, e imprime `COMPASS_ONBOARDING_PLAN`, `.agents/skills/tdd`, `.claude/skills/tdd` y `--apply`.
    3. `compass init --path <tmp_path> --preview --apply` devuelve exit code `!= 0`.
    Ejecutar `pytest` y observar el fallo.
  - **GREEN**: Implementar el comando `@app.command("init")` en `src/compass_harness/cli.py` asegurándose de mantener compatibilidad total con `compass --version` y `compass --help` (`tests/test_cli_skeleton.py`). Ejecutar `pytest` y verificar el paso a verde.
  - **Prueba Observada**:
    - **Fallo observado (RED)**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      collected 25 items

      ../../../compass-harness/tests/test_agent_onboarding.py ...FF.           [ 24%]
      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 36%]
      ../../../compass-harness/tests/test_project_inspector.py ......          [ 60%]
      ../../../compass-harness/tests/test_templates_and_skills.py ..........   [100%]

      =================================== FAILURES ===================================
      FAILED ../../../compass-harness/tests/test_agent_onboarding.py::test_cli_init_phase_1_greenfield_and_brownfield
      FAILED ../../../compass-harness/tests/test_agent_onboarding.py::test_cli_init_phase_2_preview_mode
      ========================= 2 failed, 23 passed in 0.23s =========================
      ```
    - **Paso a verde (GREEN)**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      collected 25 items

      ../../../compass-harness/tests/test_agent_onboarding.py ......           [ 24%]
      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 36%]
      ../../../compass-harness/tests/test_project_inspector.py ......          [ 60%]
      ../../../compass-harness/tests/test_templates_and_skills.py ..........   [100%]

      ============================== 25 passed in 0.18s ==============================
      ```

- [x] **Tarea 3: Subcomando CLI `compass init --apply` y `--force` extremo a extremo (CA-3 y CA-4 via CLI)**
  - **RED**: Añadir tests en `tests/test_agent_onboarding.py` usando `CliRunner`:
    1. `compass init --path <tmp_path> --name demo --goal "Demo" --assistants antigravity,claude,cursor --e2e-cmd "npx playwright test" --apply` devuelve exit code `0`, imprime `COMPASS_ONBOARDING_APPLIED`, crea todos los archivos y symlinks en `.agents/skills/`, `.claude/skills/` y `.cursor/skills/`, e inyecta `npx playwright test` en `docs/brain/architecture.md`.
    2. Verificar por CLI que re-ejecutar `compass init --path <tmp_path> --apply` sin `--force` respeta archivos modificados y con `--apply --force` los sobrescribe.
    Ejecutar `pytest` y verificar que toda la suite de tests del repositorio pasa en verde.
  - **GREEN**: Ajustar cualquier detalle necesario en `src/compass_harness/cli.py` o `installer.py` y registrar la Prueba Observada tanto de `pytest` como de una ejecución real del binario `compass init --help`.
  - **Prueba Observada**:
    - **Paso a verde (GREEN)**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/pytest /home/carlos/compass-harness/tests
      collected 27 items

      ../../../compass-harness/tests/test_agent_onboarding.py ........         [ 29%]
      ../../../compass-harness/tests/test_cli_skeleton.py ...                  [ 40%]
      ../../../compass-harness/tests/test_project_inspector.py ......          [ 62%]
      ../../../compass-harness/tests/test_templates_and_skills.py ..........   [100%]

      ============================== 27 passed in 0.24s ==============================
      ```
    - **Ejecucion real de ayuda CLI**:
      ```text
      $ /home/carlos/compass-harness/.venv/bin/compass init --help
      Usage: compass init [OPTIONS]

      Inicializa Compass Meta-Harness en el proyecto objetivo siguiendo el protocolo
      de 3 fases.

      Options:
        --path                  <path>  Directorio del proyecto objetivo. [default: .]
        --name                  <str>   Nombre del proyecto.
        --goal                  <str>   Objetivo del proyecto.
        --stack                 <str>   Stack tecnologico principal.
        --domain                <str>   Dominio tecnico y educativo.
        --arch                  <str>   Estilo arquitectonico (hexagonal, layered, mvc, script).
        --model-strategy        <str>   Estrategia de modelos (subagent-fast, subagent-inherit, single).
        --assistants            <str>   Asistentes objetivo separados por coma (antigravity,claude,cursor,codex).
        --test-cmd              <str>   Comando para tests unitarios e integracion.
        --lint-cmd              <str>   Comando para linter y chequeo estatico.
        --e2e-cmd               <str>   Comando para tests E2E / Playwright opcional.
        --preview                       Fase 2: Muestra el plan de instalacion sin escribir en disco.
        --apply                         Fase 3: Escribe los archivos y crea los symlinks en disco.
        --force                         Sobrescribe archivos existentes al usar --apply.
        --help                          Show this message and exit.
      ```
