# Especificación: 07-auditor-subagent (Puerta de Auditoría Independiente en Flujo SDD)

## 1. Contexto y Justificación
En el flujo Spec-Driven Development (SDD) con delegación de subagentes, el subagente implementador (`Builder Subagent`) ejecuta el ciclo TDD (`RED -> GREEN -> REFACTOR`). Sin embargo, sufre de **ceguera de taller** (*Builder Blindness*): tiende a crear tests tautológicos, mocks complacientes o a olvidar sutilmente Criterios de Aceptación (CA) de la especificación tras acumular ruido de ejecución y reintentos en su contexto.

Para cerrar esta brecha sin consumir cuota del modelo de razonamiento principal ni exigir que el usuario revise manualmente cada diff, se introduce la figura del **Subagente Auditor** (`Auditor Subagent`): un subagente efímero que nace con contexto limpio, utiliza un modelo rápido (`flash` / fast tier), evalúa el trabajo con una **Rúbrica de 4 Puntos** y emite un veredicto binario (`APPROVED` o `REJECTED`).

---

## 2. Requerimientos Funcionales y Criterios de Aceptación (CA)

### CA-1: Evolución de `AGENTS.md` hacia la Tríada de Roles
- El enrutador `AGENTS.md` (y su plantilla generadora `render_agents_md` en `brain_assets.py`) debe documentar explícitamente tres roles cuando la estrategia es `subagent-fast`:
  1. **Main Agent (Orquestador / Arquitecto / Mentor)**.
  2. **Builder Subagent (Constructor TDD efímero)**.
  3. **Auditor Subagent (Revisor Adversarial con contexto limpio)**.
- El flujo `[LANE: SDD]` debe incorporar explícitamente el paso de auditoría independiente entre la implementación TDD y la consolidación del Cerebro.
- El presupuesto máximo de líneas (`AGENTS_MAX_LINES <= 99`) debe mantenerse estrictamente.

### CA-2: Protocolo y Rúbrica de Auditoría en `sdd-workflow/SKILL.md`
- La plantilla `render_sdd_workflow_skill` en `compass_skills_assets.py` debe definir el protocolo de invocación del Auditor Subagent con una **Rúbrica de 4 Puntos**:
  1. **Trazabilidad de Criterios de Aceptación**: Mapeo explícito de cada `CA-X` de `spec.md` con su aserción real en tests y código.
  2. **Ejecución Determinista**: Ejecución obligatoria de los comandos declarados (`test_command`, `lint_command`, `compass check`).
  3. **Inspección de Anti-Patrones de IA**: Búsqueda activa de mocks sobre el sistema bajo prueba, tests tautológicos, asserts vacíos, prints de depuración o ramas de error no manejadas (`except: pass`).
  4. **Veredicto Binario Estructurado**: Respuesta normalizada `VERDICT: APPROVED` o `VERDICT: REJECTED` con lista procesable de discrepancias.

### CA-3: Bucle de Retroalimentación (*Feedback Loop*)
- `sdd-workflow/SKILL.md` debe estipular que el Auditor **no edita código**. Si emite `REJECTED`, reporta los hallazgos al Main Agent, quien despacha tareas correctivas puntuales al Builder Subagent antes de volver a auditar.

### CA-4: Consistencia y *Dogfooding* en el Repositorio de Compass
- El archivo raíz [`AGENTS.md`](../../AGENTS.md) del repositorio `compass-harness` debe actualizarse con este protocolo.
- `compass check` debe verificar que todas las invariantes de arnés siguen cumpliéndose con éxito (`COMPASS_CHECK_PASSED`).

### CA-5: Cobertura de Tests Automatizados
- La suite de tests en `tests/test_templates_and_skills.py` debe ampliarse para verificar:
  - Presencia del rol del Auditor y del paso de auditoría en `AGENTS.md`.
  - Presencia de la Rúbrica de 4 Puntos y el veredicto estructurado en `sdd-workflow/SKILL.md`.
  - Que la generación completa del bundle (`render_project_bundle`) sigue produciendo los 13 archivos válidos sin romper contratos existentes.

---

## 3. Costuras Públicas de Prueba (*Seams*)
- `compass_harness.templates.brain_assets.render_agents_md(config)`: Retorna texto de `AGENTS.md` con la tríada de agentes y presupuesto < 100 líneas.
- `compass_harness.templates.compass_skills_assets.render_sdd_workflow_skill(config)`: Retorna `SKILL.md` con la sección de Auditor Subagent y la rúbrica de 4 puntos.
- CLI `compass check`: Debe seguir ejecutándose con exit code 0 contra el repositorio propio.
