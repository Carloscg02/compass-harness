# Ficha de Módulo: `verification-check`

- **Ubicación**:
  - `src/compass_harness/core/verifier.py`
  - `src/compass_harness/cli.py` (`@app.command("status")`, `@app.command("check")`)
- **Spec asociada**: [`specs/05-verification-check/spec.md`](../../../specs/05-verification-check/spec.md)
- **Tests**: [`tests/test_verification_check.py`](../../../tests/test_verification_check.py) (`13 passed`, suite total `40 passed`)

---

## 1. Responsabilidad
Auditar de manera determinista las invariantes del Meta-Harness Compass sobre cualquier proyecto objetivo para prevenir el deterioro de contexto (*Context Rot*) y los falsos cierres de tareas (*False Completion*):
1. Existencia de los 5 archivos núcleo del Cerebro (`MISSING_BRAIN_FILE`).
2. Presupuesto de líneas en `AGENTS.md` (`< 100` líneas) y `docs/brain/handoff.md` (`<= 30` líneas) (`BUDGET_EXCEEDED`).
3. Aislamiento $O(1)$ del índice de ADRs en `docs/brain/index.md` (`ADR_INDEX_BLOAT`).
4. Salud de enlaces simbólicos en `.agents/skills`, `.claude/skills`, `.cursor/skills` (`BROKEN_SYMLINK`).
5. Evidencia real de **Prueba Observada** en toda tarea marcada como `[x]` dentro de `specs/*/tasks.md` (`MISSING_OBSERVED_PROOF`).

---

## 2. API Pública (Seams)
- **Nivel Core (`compass_harness.core.verifier`)**:
  - `SpecProgress`, `CheckIssue`, `HarnessReport`
  - `verify_harness(root: Path) -> HarnessReport`
- **Nivel CLI**:
  - `compass status [--path <dir>]` (`COMPASS_STATUS`, código de salida `0`).
  - `compass check [--path <dir>]` (`COMPASS_CHECK_PASSED` con código `0`, o `COMPASS_CHECK_FAILED` con código `1`).
