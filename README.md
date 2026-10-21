# Compass Harness (`compass-harness`)

Meta-Harness agnóstico, ligero y educativo en Python para ingeniería de software asistida por agentes de IA (Antigravity, Claude Code, Cursor, Codex).

Proporciona memoria persistente jerárquica (`docs/brain/`), enrutamiento por carriles (`ANSWER`, `FTD`, `SDD`), TDD estricto en costuras públicas (*Seams* de Matt Pocock), gobernanza de UI/Frontend contra el *AI Slop* y generación de guías didácticas bajo demanda (`GUIDE.md`).

---

## Instrucciones para el Agente de IA (Agent Onboarding Protocol)

> **Si eres un Agente de IA** y el usuario te ha pedido instalar `compass-harness` (o has leído este repositorio desde `https://github.com/Carloscg02/compass-harness`), ejecuta estrictamente estos pasos sin saltarte ninguno:

### Paso 0: Verificar o Instalar el CLI `compass`
Comprueba primero si el binario `compass` ya está disponible en el `PATH`:

```bash
compass --version
```

Si no está instalado, instálalo globalmente con `uv` o `pipx` (o desde este repositorio de GitHub):

```bash
uv tool install git+https://github.com/Carloscg02/compass-harness.git
# Alternativa con pipx:
# pipx install git+https://github.com/Carloscg02/compass-harness.git
```

### Paso 1: Inspección Determinista (`COMPASS_ONBOARDING_REQUIRED`)
Sitúate en el directorio del proyecto objetivo (y asegúrate de cambiar antes a la rama de Git que te haya indicado el usuario si es un repositorio existente) y ejecuta **sin banderas**:

```bash
compass init --path .
```

Este comando **no escribe nada en disco**. Analizará el repositorio y devolverá un bloque `=== COMPASS_ONBOARDING_REQUIRED ===` indicando:
- Si el proyecto es **`GREENFIELD`** (desde cero) o **`BROWNFIELD`** (con código existente).
- Los stacks tecnológicos y señales de UI detectadas (`tailwind`, `shadcn-ui`, `nextjs`, etc.).
- Los directorios existentes (`src`, `tests`, `docs`, etc.).

### Paso 2: Conversación con el Usuario y Vista Previa (`--preview`)
**NO ejecutes `--apply` directamente**. Antes, habla con el usuario en el chat para consensuar:
1. **Objetivo del proyecto (`--goal`)** y **Dominio técnico/educativo (`--domain`)** para las guías del Modo Mentor.
2. **Estilo arquitectónico (`--arch`)**: `hexagonal` (por defecto), `layered`, `mvc` o `script`.
3. **Comandos de verificación reales del proyecto**:
   - `--test-cmd`: comando para tests unitarios y de integración (ej. `pytest`, `npm test`, `go test ./...`).
   - `--lint-cmd`: comando de linter/tipado (ej. `ruff check`, `npm run lint`).
   - `--e2e-cmd`: comando E2E/Playwright si el proyecto tiene interfaz y tests E2E (ej. `npx playwright test` o `N/A`).
4. **Asistentes objetivo (`--assistants`)**: separados por coma (`antigravity`, `claude`, `cursor`, `codex`).

Una vez hablados o deducidos del proyecto, ejecuta el modo vista previa:

```bash
compass init --path . \
  --name "<nombre-proyecto>" \
  --goal "<objetivo>" \
  --stack "<stack>" \
  --domain "<dominio>" \
  --arch "<hexagonal|layered|mvc|script>" \
  --assistants "antigravity" \
  --test-cmd "<comando-test>" \
  --lint-cmd "<comando-lint>" \
  --e2e-cmd "<comando-e2e-o-N/A>" \
  --preview
```

Presenta al usuario el resumen devuelto por `=== COMPASS_ONBOARDING_PLAN ===`.

### Paso 3: Instalación Real (`--apply`), Documentación Brownfield y Verificación (`compass check`)
Tras el visto bueno del usuario, cambia `--preview` por `--apply`:

```bash
compass init --path . \
  --name "<nombre-proyecto>" \
  --goal "<objetivo>" \
  --stack "<stack>" \
  --domain "<dominio>" \
  --arch "<hexagonal|layered|mvc|script>" \
  --assistants "antigravity" \
  --test-cmd "<comando-test>" \
  --lint-cmd "<comando-lint>" \
  --e2e-cmd "<comando-e2e-o-N/A>" \
  --apply
```

- **Si el proyecto es `BROWNFIELD` (proyecto ya en marcha)**:
  Inmediatamente después de ejecutar `compass init --apply`, inspecciona los módulos principales ya existentes en el repositorio, crea sus fichas de resumen en `docs/brain/modules/<modulo>.md` y enlázalas en la sección `## 3. Modulos del Sistema` de `docs/brain/index.md`.
- Por último, ejecuta la puerta de calidad para confirmar que el arnés ha quedado sano:
  ```bash
  compass check --path .
  compass status --path .
  ```

---

## Arquitectura del Meta-Harness

### 1. Cerebro de 3 Niveles (`docs/brain/`) — Coste de Arranque $O(1)$
- **Nivel 1 (Lectura en cada arranque)**:
  - `AGENTS.md` (< 100 líneas): Router de 3 carriles (`ANSWER`, `FTD`, `SDD`), estrategia de delegación en subagentes (`subagent-fast`, `subagent-inherit`, `single`), **UI / Frontend Gate** y enlaces a las 5 skills.
  - `docs/brain/index.md`: Mapa de identidad del proyecto, enlaces a Nivel 2, puntero de **1 única línea** a `decisions/index.md` y listado de módulos.
- **Nivel 2 (Lectura bajo demanda según el carril)**:
  - `docs/brain/architecture.md`: Leyes de capas y comandos oficiales de verificación (Unit/Integration In-Loop, Static/Lint y E2E/Playwright opcional).
  - `docs/brain/handoff.md`: Estado vivo del turno actual (máximo 30 líneas, sobrescribible, nunca *append-only*).
  - `docs/brain/design.md`: Contrato de diseño visual y tokens (creado de forma perezosa *Just-In-Time* solo cuando el proyecto toca UI/Frontend, máximo 80 líneas).
  - `docs/brain/modules/<modulo>.md`: Fichas técnicas por componente.
  - `docs/brain/decisions/index.md`: Tabla índice de ADRs.
- **Nivel 3 (Archivo histórico de decisiones)**:
  - `docs/brain/decisions/NNNN-titulo.md`: ADRs individuales (solo se abren cuando se evalúa cambiar una decisión previa).

### 2. Las 5 Skills Instaladas en `.compass/skills/` (con Symlinks Agnósticos)
`compass init --apply` instala la fuente única de verdad en `.compass/skills/` y crea enlaces simbólicos relativos en `.agents/skills/`, `.claude/skills/` o `.cursor/skills/`:
1. **`tdd` (Skill oficial de Matt Pocock)**: Incluye `SKILL.md`, `tests.md` y `mocking.md`. Enfocada en probar **Seams** (costuras públicas, cubriendo unitarios e integración entre módulos reales), *Vertical Slices* y hacer mock únicamente en *System Boundaries*.
2. **`project-architect`**: Negociación de estilo arquitectónico (Hexagonal por defecto pero adaptable) y diagnóstico *Greenfield* vs *Brownfield*.
3. **`sdd-workflow`**: Flujo formal `spec.md -> plan.md -> tasks.md`, con *Architecture Alignment*, *ADR Gate*, *UI Gate*, *Observed Proof* obligatorio por tarea y ejecución de tests delegada al subagente rápido (`flash` / fast tier).
4. **`ui-design`**: Gobernanza de UI/Frontend para evitar *AI Slop* y *Zombie UI*. Incluye modo de coherencia *Brownfield*, entrevista de 3 preguntas para *Greenfield* con referencia a `https://ancient-prompt-design-flow.base44.app/`, 4 arquetipos con personalidad (`precision-dark/light`, `warm-editorial`, `telemetry-grid`, `neo-brutalist-craft`) y las 5 leyes duras Anti-Slop (como la ley de los 4 estados: *Loading, Empty, Error, Populated*).
5. **`mentor-guide`**: Generador bajo demanda de guías educativas en `guides/<slug>-GUIDE.md` combinando la lente de Ingeniería de Software con el Dominio Técnico del proyecto.

---

## Comandos de la CLI

| Comando | Descripción |
| :--- | :--- |
| `compass --version` | Muestra la versión instalada de `compass-harness`. |
| `compass init [--path <dir>]` | Fase 1: Inspecciona el directorio sin tocar el disco (`COMPASS_ONBOARDING_REQUIRED`). |
| `compass init --preview ...` | Fase 2: Muestra el plan de archivos, conflictos y symlinks sin escribir en disco (`COMPASS_ONBOARDING_PLAN`). |
| `compass init --apply [--force] ...` | Fase 3: Instala el Cerebro, las 5 skills y los enlaces simbólicos (`COMPASS_ONBOARDING_APPLIED`). |
| `compass status [--path <dir>]` | Muestra el estado de salud del Cerebro, contrato UI, symlinks y progreso de tareas en `specs/`. |
| `compass check [--path <dir>]` | Puerta de calidad determinista (verifica presupuestos de líneas, aislamiento de ADRs, validez de symlinks y que toda tarea `[x]` en `specs/*/tasks.md` tenga su bloque de Prueba Observada). |

---

## Desarrollo Local y Tests

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
.venv/bin/compass check --path .
```
