# Especificación (Spec): `04-agent-onboarding`

- **ID de Feature**: `04-agent-onboarding`
- **Estado**: Borrador (Pendiente de aprobación humana)
- **Objetivo**: Implementar el motor de instalación y el subcomando `compass init` siguiendo el **Protocolo de Onboarding Conducido por el Agente en 3 Fases** ([ADR-0004](../../docs/brain/decisions/0004-agent-driven-onboarding.md)) y el **Diseño de Meta-Harness Agnóstico mediante enlaces simbólicos** ([ADR-0002](../../docs/brain/decisions/0002-agnostic-symlinks.md)).

---

## 1. Contexto y Problema

Cuando un usuario le dice a su agente de IA en el chat *"Instala compass en este proyecto"*, el CLI `compass init` no debe lanzar un cuestionario `input()` bloqueante en la terminal (porque los agentes se quedan colgados esperando `stdin` o inventan banderas a ciegas), ni tampoco escribir archivos directamente sin consensuar antes la arquitectura y la configuración con el usuario.

Inspirándonos en el protocolo de onboarding de `rsc-harness`, `compass init` funcionará como una máquina de estados determinista en **3 Fases** que guía al agente paso a paso mediante salidas estructuradas por consola (`COMPASS_ONBOARDING_REQUIRED`, `COMPASS_ONBOARDING_PLAN`, `COMPASS_ONBOARDING_APPLIED`).

---

## 2. Alcance Funcional (Qué vamos a construir)

### 2.1 Mapa Agnóstico de Asistentes y Symlinks (`src/compass_harness/core/installer.py`)
Una única fuente de verdad se instala siempre en `.compass/skills/<skill_name>/` y `AGENTS.md` + `docs/brain/`. Según los asistentes seleccionados en `target_assistants` (separados por coma en CLI, ej. `--assistants antigravity,claude`), el instalador crea enlaces simbólicos relativos (o copia de respaldo si el sistema operativo rechaza symlinks) hacia cada skill (`tdd`, `project-architect`, `sdd-workflow`, `mentor-guide`):

| Asistente (`target_assistants`) | Directorio de Skills (Symlinks a `.compass/skills/<skill>`) | Puntero adicional opcional |
| :--- | :--- | :--- |
| **`antigravity`** | `.agents/skills/<skill>` | Lee `AGENTS.md` de forma nativa |
| **`claude`** | `.claude/skills/<skill>` | Crea `CLAUDE.md` enlazando/apuntando a `AGENTS.md` (si no existe) |
| **`cursor`** | `.cursor/skills/<skill>` | Lee `AGENTS.md` de forma nativa |
| **`codex`** | `.agents/skills/<skill>` | Lee `AGENTS.md` de forma nativa |

### 2.2 Las 3 Fases del Comando `compass init` (`src/compass_harness/cli.py` + `core/installer.py`)

El comando `compass init` acepta las siguientes opciones en la CLI:
- `--path`: Ruta del directorio del proyecto (por defecto `.`).
- `--name`: Nombre del proyecto (por defecto el nombre de la carpeta si no se especifica).
- `--goal`: Objetivo del proyecto.
- `--stack`: Stack tecnológico (si se omite, usa los `detected_stacks` de `inspect_project` o `"python"`).
- `--domain`: Dominio técnico/educativo para el Modo Mentor (por defecto `"General Software Engineering"`).
- `--arch`: Estilo arquitectónico (`"hexagonal"`, `"layered"`, `"mvc"`, `"script"`, por defecto `"hexagonal"`).
- `--model-strategy`: Estrategia de delegación (`"subagent-fast"`, `"subagent-inherit"`, `"single"`, por defecto `"subagent-fast"`).
- `--assistants`: Lista separada por comas de asistentes objetivo (por defecto `"antigravity"`).
- `--test-cmd`: Comando de tests unitarios/integración (por defecto `"pytest"`).
- `--lint-cmd`: Comando de linter/tipado (por defecto `"ruff check"`).
- `--e2e-cmd`: Comando E2E/Playwright opcional (por defecto `"N/A"`).
- `--preview`: Bandera booleana para ejecutar la Fase 2 (Vista Previa).
- `--apply`: Bandera booleana para ejecutar la Fase 3 (Escritura real en disco y creación de symlinks).
- `--force`: Bandera booleana para permitir sobrescribir archivos existentes del harness cuando se combina con `--apply`.

#### Comportamiento exacto por Fase:

1. **Fase 1 — Inspección y Guía para el Agente (`compass init` sin `--preview` ni `--apply`)**:
   - Ejecuta `inspect_project(path)` sin modificar ningún archivo en disco.
   - Imprime el bloque estructurado con cabecera **`COMPASS_ONBOARDING_REQUIRED`**:
     - `project_state`: `GREENFIELD` o `BROWNFIELD`.
     - `detected_stacks`: Stacks detectados.
     - `existing_Tracked_dirs` y `existing_harness_files`.
     - **Instrucciones para el Agente**:
       - Si es `GREENFIELD`: Qué acordar con el humano en el chat (objetivo `--goal`, stack `--stack`, dominio educativo `--domain`, confirmar si arquitectura `hexagonal` o más simple, comandos de test/E2E y asistentes `--assistants`).
       - Si es `BROWNFIELD`: Además de lo anterior, instruye al agente a inspeccionar los directorios existentes (`existing_tracked_dirs`) para proponer cómo documentar los módulos actuales en `docs/brain/modules/` tras la instalación.
     - Ejemplo exacto del comando del **Paso 2 (`compass init --preview ...`)** que el agente debe ejecutar a continuación.
   - Termina con código de salida `0`.

2. **Fase 2 — Plan de Onboarding y Vista Previa (`compass init --preview ...`)**:
   - Construye `ProjectConfig` y ejecuta `plan_installation(root, config)` sin escribir nada en disco.
   - Imprime el bloque estructurado con cabecera **`COMPASS_ONBOARDING_PLAN`**:
     - Resumen de la configuración acordada (`name`, `goal`, `stack`, `domain`, `arch`, `model_strategy`, `assistants`, `test_cmd`, `lint_cmd`, `e2e_cmd`).
     - Lista de archivos que se crearán (`CREATE`) o que ya existen en el directorio (`CONFLICT` / `SKIP unless --force`).
     - Lista de enlaces simbólicos (`SYMLINK`) que se crearán para los asistentes seleccionados (ej. `.agents/skills/tdd -> ../../.compass/skills/tdd`).
     - Ejemplo exacto del comando del **Paso 3 (`compass init --apply ...`)** tras recibir la confirmación del usuario.
   - Termina con código de salida `0`.

3. **Fase 3 — Aplicación en Disco y Creación de Symlinks (`compass init --apply ...`)**:
   - Ejecuta `apply_installation(root, config, force=force)`:
     - Crea los directorios necesarios (`docs/brain/decisions`, `docs/brain/modules`, `specs`, `guides`, `.compass/skills/...`).
     - Escribe los 12 archivos generados por `render_project_bundle(config)` (respetando archivos existentes salvo que `force=True`, para no destruir nunca un `AGENTS.md` o `docs/brain/` previo por accidente en un proyecto *Brownfield*).
     - Crea los enlaces simbólicos de las 4 skills en los directorios de los asistentes seleccionados (`.agents/skills/<skill>`, `.claude/skills/<skill>`, `.cursor/skills/<skill>`) apuntando a `.compass/skills/<skill>`. Si se incluye `claude` en `--assistants` y no existe `CLAUDE.md`, crea `CLAUDE.md` referenciando `AGENTS.md`.
   - Imprime el bloque **`COMPASS_ONBOARDING_APPLIED`** con el resumen de archivos escritos y symlinks creados.
   - Termina con código de salida `0`.

---

## 3. Criterios de Aceptación (Requisitos para TDD)

Archivo de pruebas: `tests/test_agent_onboarding.py`:

- **CA-1 (Fase 1 — `compass init` sin banderas de acción)**: En un directorio `tmp_path` (tanto *Greenfield* como *Brownfield*), ejecutar `compass init --path <tmp_path>` no crea ningún archivo en disco, devuelve exit code `0` e imprime `COMPASS_ONBOARDING_REQUIRED`, el estado (`GREENFIELD` o `BROWNFIELD`) y la instrucción hacia `--preview`.
- **CA-2 (Fase 2 — `compass init --preview`)**: Ejecutar `compass init --path <tmp_path> --name demo --goal "Test" --assistants antigravity,claude --preview` no escribe ningún archivo en `<tmp_path>`, devuelve exit code `0` e imprime `COMPASS_ONBOARDING_PLAN` listando los 12 archivos del bundle y los symlinks de `.agents/skills/` y `.claude/skills/`.
- **CA-3 (Fase 3 — `compass init --apply` y Symlinks Agnósticos)**: Ejecutar `compass init --path <tmp_path> --name demo --goal "Test" --assistants antigravity,claude --apply` devuelve exit code `0`, imprime `COMPASS_ONBOARDING_APPLIED`, escribe en disco los 12 archivos del bundle (más los directorios `docs/brain/modules/`, `specs/`, `guides/` y `CLAUDE.md`), y crea enlaces simbólicos funcionales en `.agents/skills/{tdd,project-architect,sdd-workflow,mentor-guide}` y `.claude/skills/{tdd,project-architect,sdd-workflow,mentor-guide}` que resuelven a `.compass/skills/<skill>` (de modo que `.agents/skills/tdd/SKILL.md` existe y es legible).
- **CA-4 (Protección contra sobrescritura accidental y flag `--force`)**: Si `AGENTS.md` ya existe en `<tmp_path>` con contenido personalizado, ejecutar `compass init --path <tmp_path> --apply` (sin `--force`) conserva intacto el `AGENTS.md` previo e instala el resto de archivos que falten; si se ejecuta con `--apply --force`, sobrescribe `AGENTS.md` con la plantilla de Compass.
- **CA-5 (Exclusión mutua `--preview` y `--apply`)**: Si se pasan simultáneamente `--preview` y `--apply`, el comando devuelve código de salida distinto de cero informando del conflicto.
