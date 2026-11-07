# Especificación: 08-compass-update (Sincronización Determinista del Arnés)

## 1. Contexto y Justificación
Cuando `compass-harness` evoluciona (nuevos guardarraíles para subagentes en `sdd-workflow`, mejoras en la constitución `AGENTS.md` o nuevas skills), los proyectos que ya fueron inicializados con `compass init` quedan desactualizados.

Actualmente, no existe un mecanismo formal para actualizar el arnés en un proyecto existente. Dejar que un LLM intente sincronizarse manualmente analizando commits remotos de Git es peligroso y antieconómico:
- Puede sobreescribir la memoria viva del proyecto (`docs/brain/modules/`, `handoff.md`, `architecture.md`).
- Puede perder la parametrización específica (`project_name`, comandos de test propios).
- Consume miles de tokens en llamadas a herramientas sin garantías de integridad.

El comando **`compass update`** proporciona una sincronización **atómica, determinista y segura**: actualiza los activos de infraestructura (*Stateless*: skills, router `AGENTS.md` y symlinks) garantizando la inmutabilidad absoluta de la memoria viva (*Stateful*).

---

## 2. Requerimientos Funcionales y Criterios de Aceptación (CA)

### CA-1: Reconstrucción Determinista de `ProjectConfig`
- El motor debe implementar una función que extraiga el `ProjectConfig` de un proyecto existente:
  1. Si existe `.compass/config.json`, lo lee directamente.
  2. Si no existe, lo reconstruye extrayendo campos de `docs/brain/index.md` (nombre, objetivo, stack, dominio), `docs/brain/architecture.md` (estilo arquitectónico y comandos de verificación) y detectando los symlinks activos en directorios de asistentes (`.agents`, `.claude`, `.cursor`).
- Si el proyecto no está inicializado con Compass (ausencia de `AGENTS.md` y `docs/brain/index.md`), debe fallar limpiamente con el código de error `COMPASS_NOT_INITIALIZED`.

### CA-2: Plan de Actualización (*Update Plan*)
- `plan_update(root: Path, config: ProjectConfig)` debe retornar un plan inmutable que clasifique:
  - **Archivos a actualizar / reescribir**: `.compass/skills/*`, `AGENTS.md` (y `CLAUDE.md` si aplica).
  - **Enlaces simbólicos a verificar / reparar**: Enlaces hacia `.agents/skills`, `.claude/skills`, etc.
  - **Archivos protegidos (Inmutabilidad estricta)**: `docs/brain/index.md`, `docs/brain/architecture.md`, `docs/brain/handoff.md`, `docs/brain/design.md`, `docs/brain/modules/*.md`, `docs/brain/decisions/*.md`, `specs/*` y `guides/*`. Ninguno de estos archivos debe figurar en la lista de escritura ni ser modificado.

### CA-3: Aplicación Segura de la Actualización (`apply_update`)
- `apply_update(root: Path, config: ProjectConfig, force: bool = False)`:
  - Escribe las nuevas versiones de las skills en `.compass/skills/` respetando `{config.test_command}`, `{config.lint_command}` y `{config.e2e_command}`.
  - Regenera `AGENTS.md` con las últimas reglas del arnés (tríada de subagentes, guardarraíles de solo lectura, bucle TDD).
  - Crea o repara los enlaces simbólicos relativos necesarios.
  - Guarda o actualiza `.compass/config.json` para facilitar futuras actualizaciones instantáneas.
  - Garantiza que ningún archivo de la memoria viva del usuario es alterado.

### CA-4: Subcomando CLI `compass update`
- Añadir el subcomando `compass update` a `cli.py` con las siguientes opciones:
  - `--path`: Directorio raíz del proyecto (por defecto `.`).
  - `--preview`: Muestra el plan detallado de actualización sin tocar disco (`=== COMPASS_UPDATE_PLAN ===`).
  - `--apply`: Aplica la actualización en disco (`=== COMPASS_UPDATE_APPLIED ===`).
  - `--force`: Fuerza la sobreescritura de skills modificadas localmente.
- Si no se pasa ni `--preview` ni `--apply`, emite un mensaje informativo con el estado actual y las opciones disponibles (`=== COMPASS_UPDATE_REQUIRED ===`).

### CA-5: Verificación Automática Post-Update
- Al finalizar `compass update --apply`, ejecuta automáticamente `verify_harness` sobre el proyecto y muestra un resumen del estado de salud del arnés.

### CA-6: Cobertura de Tests Automatizados
- La suite de pruebas debe incluir tests que verifiquen:
  1. Reconstrucción correcta de `ProjectConfig` desde proyectos existentes sin `config.json`.
  2. Preservación estricta de archivos de memoria (`modules/custom.md`, `handoff.md`) tras ejecutar `apply_update`.
  3. Actualización efectiva de las skills y `AGENTS.md` con las nuevas plantillas.
  4. Ejecución CLI de `compass update` en modos `--preview` y `--apply`.

---

## 3. Costuras Públicas de Prueba (*Seams*)
- `compass_harness.core.updater.extract_project_config(root: Path) -> ProjectConfig`
- `compass_harness.core.updater.plan_update(root: Path, config: ProjectConfig) -> UpdatePlan`
- `compass_harness.core.updater.apply_update(root: Path, config: ProjectConfig, force: bool = False) -> UpdateResult`
- CLI: `compass update --path <dir> [--preview | --apply]`
