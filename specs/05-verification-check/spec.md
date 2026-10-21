# Especificación (Spec): `05-verification-check`

- **ID de Feature**: `05-verification-check`
- **Estado**: Borrador (Pendiente de aprobación humana)
- **Objetivo**: Implementar el motor de auditoría determinista (`src/compass_harness/core/verifier.py`) y los subcomandos CLI `compass status` y `compass check` (`src/compass_harness/cli.py`) para verificar la salud del Cerebro, los presupuestos de contexto (`AGENTS.md < 100` líneas, `handoff.md <= 30` líneas), la integridad de los enlaces simbólicos de skills y el cumplimiento de la **Prueba Observada** en las tareas marcadas como completadas (`[x]`) en `specs/*/tasks.md`.

---

## 1. Contexto y Problema

Un arnés de ingeniería para agentes de IA se degrada con el tiempo (*Context Rot* y *False Completion*) si no existe una herramienta determinista fuera del LLM que audite sus invariantes:
1. Los agentes tienden a inflar `AGENTS.md` o convertir `docs/brain/handoff.md` en un diario infinito (*append-only*), rompiendo el presupuesto de tokens de arranque.
2. En el flujo SDD, un agente puede caer en la tentación de marcar una tarea como `- [x] **Tarea N...**` en `specs/<feature>/tasks.md` dejando `- **Prueba Observada**: *(Pendiente)*` o sin registrar evidencia real.
3. Si alguien mueve o borra una carpeta de skills, los enlaces simbólicos en `.agents/skills/`, `.claude/skills/` o `.cursor/skills/` pueden quedar rotos (*dangling symlinks*).

Para cerrar la v1.0 de `compass-harness`, necesitamos dos comandos:
- **`compass status`**: Muestra una radiografía rápida del estado del arnés en el proyecto (archivos del cerebro presentes, skills instaladas, symlinks activos y resumen de specs/tareas `completadas / totales`).
- **`compass check`**: Ejecuta la puerta de calidad (*Quality Gate*) determinista sobre las invariantes del arnés. Devuelve código de salida `0` (`COMPASS_CHECK_PASSED`) si todas las reglas se cumplen, o código de salida `1` (`COMPASS_CHECK_FAILED`) detallando exactamente qué regla ha fallado.

---

## 2. Alcance Funcional (Qué vamos a construir)

### 2.1 Motor de Verificación (`src/compass_harness/core/verifier.py`)

Modelos inmutables de dominio:
- `@dataclass(frozen=True) class SpecProgress`:
  - `spec_id: str` (ej. `"01-cli-skeleton"`)
  - `has_spec_md: bool`
  - `has_plan_md: bool`
  - `has_tasks_md: bool`
  - `total_tasks: int`
  - `completed_tasks: int`
  - `tasks_missing_proof: tuple[str, ...]` (nombres/líneas de tareas marcadas `[x]` que no tienen evidencia en su bloque `Prueba Observada` / `Observed Proof`)
- `@dataclass(frozen=True) class CheckIssue`:
  - `code: str` (ej. `"MISSING_BRAIN_FILE"`, `"BUDGET_EXCEEDED"`, `"ADR_INDEX_BLOAT"`, `"BROKEN_SYMLINK"`, `"MISSING_OBSERVED_PROOF"`)
  - `path: str`
  - `message: str`
- `@dataclass(frozen=True) class HarnessReport`:
  - `is_installed: bool`
  - `present_brain_files: tuple[str, ...]`
  - `missing_brain_files: tuple[str, ...]`
  - `installed_skills: tuple[str, ...]`
  - `active_symlinks: tuple[str, ...]`
  - `broken_symlinks: tuple[str, ...]`
  - `specs_progress: tuple[SpecProgress, ...]`
  - `issues: tuple[CheckIssue, ...]`
  - `@property def passed(self) -> bool`: devuelve `True` si `is_installed` es `True` y `len(self.issues) == 0`.

### 2.2 Reglas auditadas por `verify_harness(root: Path) -> HarnessReport`

1. **Existencia de archivos núcleo del Cerebro (`MISSING_BRAIN_FILE`)**:
   - Verifica la presencia de `AGENTS.md`, `docs/brain/index.md`, `docs/brain/architecture.md`, `docs/brain/handoff.md` y `docs/brain/decisions/index.md`.
2. **Presupuesto de líneas (*Context Budget* — `BUDGET_EXCEEDED`)**:
   - `AGENTS.md` debe tener **menos de 100 líneas** (`< 100`).
   - `docs/brain/handoff.md` debe tener **como máximo 30 líneas** (`<= 30`).
3. **Aislamiento $O(1)$ de ADRs en `docs/brain/index.md` (`ADR_INDEX_BLOAT`)**:
   - `docs/brain/index.md` debe enlazar a `decisions/index.md`, y no debe listar más de 1 línea con enlaces a ficheros dentro de `decisions/`.
4. **Integridad de Skills y Enlaces Simbólicos (`BROKEN_SYMLINK`)**:
   - Inspecciona `.compass/skills/` y los directorios de asistentes (`.agents/skills`, `.claude/skills`, `.cursor/skills`) comprobando que todo symlink existente apunte a un destino válido que exista en disco (`link.is_symlink() and not link.exists()` -> `BROKEN_SYMLINK`).
5. **Auditoría de Prueba Observada en `specs/*/tasks.md` (`MISSING_OBSERVED_PROOF`)**:
   - Escanea cada subdirectorio en `specs/<spec_id>/tasks.md`.
   - Parsea los bloques de tareas (`- [ ]` y `- [x]`).
   - Para cada tarea marcada como completada (`- [x]`), verifica el texto comprendido entre esa tarea y la siguiente tarea (o el final del archivo):
     - Debe mencionar `Prueba Observada` u `Observed Proof`.
     - No debe mantener el marcador de plantilla sin rellenar `*(Pendiente)*` ni `*(Pending)*`.
     - Si una tarea `[x]` sigue teniendo `*(Pendiente)*` o carece de sección de prueba observada, registra un `CheckIssue(code="MISSING_OBSERVED_PROOF", ...)`.

### 2.3 Subcomandos CLI en `src/compass_harness/cli.py`

1. **`compass status [--path <dir>]`**:
   - Ejecuta `verify_harness(root)`.
   - Imprime cabecera **`=== COMPASS_STATUS ===`**:
     - Estado general (`HEALTHY` si `report.passed`, `ISSUES_FOUND` si hay problemas, o `NOT_INITIALIZED` si falta el cerebro).
     - Archivos del Cerebro presentes/faltantes.
     - Skills y enlaces simbólicos detectados.
     - Lista de progreso de `specs/` (`<spec_id>: <completed>/<total> tareas completadas`).
   - Termina siempre con código de salida `0` (comando informativo de inspección).

2. **`compass check [--path <dir>]`**:
   - Ejecuta `verify_harness(root)`.
   - Si `report.passed` es `True`:
     - Imprime **`=== COMPASS_CHECK_PASSED ===`** con el resumen de invariantes verificadas y termina con código de salida `0`.
   - Si `report.passed` es `False`:
     - Imprime **`=== COMPASS_CHECK_FAILED ===`** listando cada `CheckIssue` (`[code] path: message`) y termina con código de salida `1`.

---

## 3. Criterios de Aceptación (Requisitos para TDD)

Archivo de pruebas: `tests/test_verification_check.py`:

- **CA-1 (Proyecto sano pasa `verify_harness` y `compass check`)**: Tras inicializar un proyecto con `apply_installation(tmp_path, config)`, `verify_harness(tmp_path).passed` es `True` y `compass check --path <tmp_path>` devuelve exit code `0` e imprime `COMPASS_CHECK_PASSED`.
- **CA-2 (Detección de exceso de presupuesto en `AGENTS.md` y `handoff.md`)**: Si `AGENTS.md` alcanza o supera las 100 líneas o `docs/brain/handoff.md` supera las 30 líneas, `verify_harness` registra `BUDGET_EXCEEDED` y `compass check` devuelve exit code `1` con `COMPASS_CHECK_FAILED`.
- **CA-3 (Detección de enlaces simbólicos rotos `BROKEN_SYMLINK`)**: Si existe un enlace simbólico roto en `.agents/skills/tdd`, `verify_harness` registra `BROKEN_SYMLINK` y `compass check` devuelve exit code `1`.
- **CA-4 (Auditoría de Prueba Observada en `specs/*/tasks.md`)**:
  - Si un archivo `specs/01-feature/tasks.md` tiene una tarea `- [x] **Tarea 1**` cuyo bloque sigue diciendo `- **Prueba Observada**: *(Pendiente)*` (o no tiene bloque de prueba observada), `verify_harness` registra `MISSING_OBSERVED_PROOF` y `compass check` devuelve exit code `1`.
  - Cuando el bloque de esa tarea contiene la evidencia real de ejecución (sin `*(Pendiente)*`), el check pasa con exit code `0`.
- **CA-5 (Comando informativo `compass status` y Dogfooding sobre el propio repositorio `/home/carlos/compass-harness`)**:
  - `compass status --path <tmp_path>` muestra `COMPASS_STATUS` y el conteo de tareas `completed/total` con exit code `0`.
  - Ejecutar `compass check --path /home/carlos/compass-harness` sobre nuestro propio repositorio real devuelve exit code `0` (`COMPASS_CHECK_PASSED`).
