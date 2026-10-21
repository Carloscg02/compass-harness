# Ficha de Módulo: `agent-onboarding`

- **Ubicación**:
  - `src/compass_harness/core/installer.py`
  - `src/compass_harness/cli.py` (`@app.command("init")`)
- **Spec asociada**: [`specs/04-agent-onboarding/spec.md`](../../../specs/04-agent-onboarding/spec.md)
- **Tests**: [`tests/test_agent_onboarding.py`](../../../tests/test_agent_onboarding.py) (`8 passed`, suite total `27 passed`)

---

## 1. Responsabilidad
Ejecutar el protocolo de onboarding e instalación conducido por el agente en 3 fases ([ADR-0004](../decisions/0004-agent-driven-onboarding.md)) y tender los enlaces simbólicos relativos desde los directorios nativos de cada asistente (`.agents/skills`, `.claude/skills`, `.cursor/skills`) hacia la fuente única de verdad en `.compass/skills/` ([ADR-0002](../decisions/0002-agnostic-symlinks.md)).

---

## 2. API Pública (Seams)
- **Nivel Core (`compass_harness.core.installer`)**:
  - `SymlinkSpec(link_path, target_path)`
  - `InstallationPlan(config, files_to_create, existing_conflicts, symlinks_to_create, directories_to_ensure)`
  - `InstallationResult(written_files, skipped_files, created_symlinks, ensured_directories)`
  - `plan_installation(root: Path, config: ProjectConfig) -> InstallationPlan`
  - `apply_installation(root: Path, config: ProjectConfig, force: bool = False) -> InstallationResult`
- **Nivel CLI (`compass init`)**:
  - Fase 1 (`compass init`): Diagnóstico sin escritura (`COMPASS_ONBOARDING_REQUIRED`).
  - Fase 2 (`compass init --preview ...`): Plan determinista sin escritura (`COMPASS_ONBOARDING_PLAN`).
  - Fase 3 (`compass init --apply [--force] ...`): Persistencia en disco y creación de symlinks (`COMPASS_ONBOARDING_APPLIED`).
