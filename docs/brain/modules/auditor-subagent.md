# Módulo: `auditor-subagent` (Puerta de Auditoría Independiente)

> **Corte Vertical de Dominio**: Gobernanza del ciclo SDD, mitigación del *Builder Blindness* y verificación adversarial automatizada con contexto limpio y modelo rápido.

---

## 1. Responsabilidad y Propósito
Este módulo formaliza la transición de la díada de desarrollo (Orquestador + Builder) a la **Tríada de Roles** (Orquestador + Builder + Auditor):
- Provee al agente orquestador un protocolo estandarizado de auditoría independiente tras la fase TDD.
- Evita la "ceguera de taller" (*Builder Blindness*) evaluando el código generado desde una ventana de contexto limpia con modelo ligero (`flash`).
- Emite un veredicto binario estructurado (`VERDICT: APPROVED` o `VERDICT: REJECTED`) apoyado en una **Rúbrica de 4 Puntos**.

---

## 2. Entidades y Contratos Clave
- **Rol Auditor Subagent**: Subagente efímero estrictamente de solo lectura (`read-only`) con modelo rápido (`flash` / fast tier).
- **Rúbrica de 4 Puntos**:
  1. *Traza de Criterios de Aceptación*: Correspondencia 1:1 entre cada `CA-X` de `spec.md` y aserciones de prueba en código.
  2. *Ejecución Determinista*: Ejecución sin fallos de `test_command`, `lint_command` y `compass check`.
  3. *Inspección de Anti-Patrones de IA*: Detección de tests tautológicos, mocks sobre el SUT, asserts vacíos, `except: pass` y prints de debug.
  4. *Veredicto Binario*: Formato estandarizado con lista procesable de discrepancias si es rechazado.
- **Feedback Loop**: En caso de `REJECTED`, el Auditor no repara el código; devuelve el informe al Orquestador para que delegue tareas puntuales al Builder Subagent.

---

## 3. Adaptadores y Plantillas Involucradas
- `src/compass_harness/templates/brain_assets.py`:
  - `render_agents_md`: Genera el enrutador con la definición de la tríada para `subagent-fast` y la secuencia SDD en 6 pasos, manteniendo el presupuesto `< 99` líneas.
- `src/compass_harness/templates/compass_skills_assets.py`:
  - `render_sdd_workflow_skill`: Genera `.compass/skills/sdd-workflow/SKILL.md` incluyendo la sección `## 2. Puerta de Auditoria Independiente (Auditor Subagent)`.
- `AGENTS.md` (raíz):
  - Enrutador vivo del repositorio que aplica esta gobernanza por *dogfooding*.

---

## 4. Tests y Seams de Verificación
- `tests/test_templates_and_skills.py`:
  - `test_agents_md_structure_and_model_strategies`: Comprueba que `render_agents_md` documenta los roles `builder` y `auditor` bajo la estrategia `subagent-fast`.
  - `test_sdd_workflow_skill_includes_auditor_gate_and_rubric`: Comprueba que `render_sdd_workflow_skill` contiene la sección del auditor, la rúbrica de 4 puntos y el feedback loop.
- `compass check`:
  - Valida que todas las tareas en `specs/07-auditor-subagent/tasks.md` cuentan con Prueba Observada válida y que los presupuestos de líneas se cumplen.
