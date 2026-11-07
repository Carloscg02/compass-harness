# Módulo: `harness-updater` (Sincronización Determinista del Arnés)

> **Corte Vertical de Dominio**: Mantenimiento evolutivo del arnés en proyectos existentes, reconstrucción de configuración e inmutabilidad garantizada de la memoria viva.

---

## 1. Responsabilidad y Propósito
Este módulo implementa la capacidad de sincronizar y actualizar la infraestructura de Compass Harness en proyectos que ya fueron inicializados:
- Extrae y reconstruye la configuración (`ProjectConfig`) de forma determinista leyendo `.compass/config.json` o analizando `docs/brain/index.md`, `architecture.md` y directorios de asistentes.
- Actualiza atómicamente los activos de infraestructura (*Stateless*: `.compass/skills/*`, router `AGENTS.md`, `CLAUDE.md` y symlinks).
- **Garantiza la inmutabilidad absoluta** de los archivos de memoria viva (*Stateful*: `docs/brain/modules/*.md`, `handoff.md`, `decisions/`, `architecture.md`, `specs/`, etc.).
- Proporciona el comando de consola `compass update` con modos `--preview`, `--apply` y `--force`.

---

## 2. Entidades y Modelos de Dominio
- **`UpdatePlan`**: Modelo inmutable (`@dataclass(frozen=True)`) que clasifica los archivos a actualizar, los archivos protegidos y los enlaces simbólicos a verificar.
- **`UpdateResult`**: Resultado consolidado de la aplicación en disco, detallando archivos actualizados, omitidos, enlaces reparados y estado de serialización de configuración.
- **`extract_project_config(root)`**: Extractor determinista con fallback seguro ante ausencia o corrupción de `.compass/config.json`.
- **`apply_update(root, config, force)`**: Ejecutor atómico de actualización que solo escribe en los ficheros del plan marcados como *Stateless*.

---

## 3. Adaptadores y Puntos de Entrada
- `src/compass_harness/core/updater.py`: Lógica de dominio pura sin dependencias de consola.
- `src/compass_harness/cli.py`: Subcomando `compass update` con gestión de estados (`COMPASS_NOT_INITIALIZED`, `COMPASS_UPDATE_REQUIRED`, `COMPASS_UPDATE_PLAN`, `COMPASS_UPDATE_APPLIED`) y auto-verificación con `verify_harness`.
- `.compass/config.json`: Formato ligero de persistencia de configuración del proyecto.

---

## 4. Tests y Seams de Verificación
- `tests/test_updater.py`:
  - Pruebas unitarias de parsing con y sin `config.json`.
  - Pruebas de inmutabilidad estricta de memoria viva frente a `apply_update`.
  - Pruebas de integración de CLI con `CliRunner` cubriendo combinaciones de banderas y códigos de salida.
- `compass check`:
  - Audita que las 3 tareas de `specs/08-compass-update/tasks.md` cuentan con Prueba Observada válida.
