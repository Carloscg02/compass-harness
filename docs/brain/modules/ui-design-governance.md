# Ficha de Módulo: `ui-design-governance`

- **Ubicación**:
  - `src/compass_harness/core/inspector.py` (`detected_ui_signals`, `existing_design_files`)
  - `src/compass_harness/templates/compass_skills_assets.py` (`render_ui_design_skill`)
  - `src/compass_harness/templates/brain_assets.py` (UI / Frontend Gate en `AGENTS.md`)
  - `src/compass_harness/core/verifier.py` (`has_design_contract`, `DESIGN_MAX_LINES = 80`, `INCOMPLETE_DESIGN_CONTRACT`)
- **Spec asociada**: [`specs/06-ui-design-governance/spec.md`](../../../specs/06-ui-design-governance/spec.md)
- **Tests**: [`tests/test_ui_design_governance.py`](../../../tests/test_ui_design_governance.py) (`11 passed`, suite total `51 passed`)

---

## 1. Responsabilidad
Gobernar la creación y modificación de interfaces visuales (UI/Frontend) para evitar el *AI Slop* y la *Zombie UI* sin añadir peso de contexto a proyectos puramente backend:
1. Detectar señales de UI (`tailwind`, `shadcn-ui`, `nextjs`, `vite`, `.tsx`, etc.) y contratos previos (`DESIGN.md` / `docs/brain/design.md`) durante la inspección.
2. Instalar la 5.ª skill oficial (`.compass/skills/ui-design/SKILL.md`) con el protocolo de coherencia Brownfield, la entrevista de diseño desde cero para desarrolladores backend (apoyada en `https://ancient-prompt-design-flow.base44.app/` y 4 arquetipos con personalidad) y las 5 Leyes Duras Anti-Slop.
3. Activar de forma perezosa (*Just-In-Time UI Gate*) el contrato `docs/brain/design.md` solo cuando una tarea toque interfaz visual, y auditar su presupuesto (`<= 80` líneas) y completitud en `compass check` y `compass status`.
