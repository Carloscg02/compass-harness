# Plan Técnico: 07-auditor-subagent (Puerta de Auditoría Independiente)

## 1. Alineación con la Arquitectura
El cambio se circunscribe a la capa de plantillas (`src/compass_harness/templates/`) y la gobernanza del repositorio ([`AGENTS.md`](../../AGENTS.md)), respetando el principio de diseño *Functional Core* del motor de renderizado (`render_project_bundle(config)`):
- No se añaden dependencias externas ni flags adicionales al CLI.
- Se mantiene el desacoplamiento: las plantillas siguen siendo funciones puras `ProjectConfig -> str`.
- Se respeta estrictamente el presupuesto de contexto de `AGENTS.md` (< 99 líneas) auditado por `compass_harness.core.verifier`.

---

## 2. Consulta de ADRs (ADR Gate)
- Consultamos [`docs/brain/decisions/index.md`](../../docs/brain/decisions/index.md) y [`docs/brain/decisions/0001-initial-architecture.md`](../../docs/brain/decisions/0001-initial-architecture.md).
- Decisión: No se contradice ningún ADR existente. La introducción de subagentes especializados consolida el principio de delegación en subagentes ligeros (`subagent-fast`) adoptado desde la fundación del arnés.

---

## 3. Diseño Detallado de Componentes

### 3.1. `src/compass_harness/templates/brain_assets.py` (`render_agents_md`)
- Actualizar `strategy_desc` para `subagent-fast` explicitando la tríada:
  - Delegación en subagentes ligeros (`flash` / fast tier) para el ciclo TDD (Builder) y para la auditoría independiente con contexto limpio (Auditor).
- Actualizar el carril `SDD`:
  1. `spec.md` (Aprobación humana).
  2. `plan.md` (Alineación técnica y Seams).
  3. `tasks.md` (Desglose TDD).
  4. `TDD Implementation` (Builder Subagent).
  5. `Independent Audit Gate` (Auditor Subagent).
  6. `Brain Consolidation & Guide` (Main Agent).
- Comprobar que el total de líneas de `render_agents_md` permanezca por debajo de 75 líneas (límite del verificador: 99).

### 3.2. `src/compass_harness/templates/compass_skills_assets.py` (`render_sdd_workflow_skill`)
- Añadir sección formal: `## 2. Puerta de Auditoría Independiente (Auditor Subagent)`:
  - Definición del rol: subagente con modelo rápido (`flash`) y contexto limpio.
  - Parámetros de entrada mínimos: `spec.md`, `plan.md`, `git diff`.
  - La **Rúbrica de 4 Puntos**:
    1. Trazabilidad de Criterios de Aceptación (CA-1, CA-2...).
    2. Ejecución determinista de comandos (`test_command`, `lint_command`, `compass check`).
    3. Detección de Anti-Patrones de IA (mocks en SUT, tests complacientes, `pass` silenciosos).
    4. Formato estricto de veredicto: `VERDICT: APPROVED` o `VERDICT: REJECTED`.
  - Protocolo del bucle de corrección (*Feedback Loop*): el Auditor no edita código; si rechaza, el Main Agent despacha al Builder.

### 3.3. Gobernanza del Repositorio (`/home/carlos/compass-harness/AGENTS.md`)
- Actualizar el router del proyecto actual para incorporar el rol `Auditor Subagent` en la sección 2 y la secuencia de 6 pasos en el carril `[LANE: SDD]`.

---

## 4. Plan de Pruebas (Test Plan)
- **Unit Testing**:
  - `tests/test_templates_and_skills.py`:
    - `test_agents_md_structure_and_model_strategies`: verificar que `AGENTS.md` incluye referencias a auditor/auditoría y se mantiene < 100 líneas.
    - `test_sdd_workflow_skill_includes_auditor_gate_and_rubric`: nuevo test unitario que verifique la presencia de la rúbrica de 4 puntos y el veredicto estructurado.
- **Auditoría de Invariantes**:
  - Ejecutar `compass check` para verificar que el repositorio propio pasa todas las validaciones sin romper presupuestos.
