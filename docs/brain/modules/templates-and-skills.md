# Ficha de Módulo: `templates-and-skills`

- **Ubicación**:
  - `src/compass_harness/core/renderer.py`
  - `src/compass_harness/templates/tdd_skill_assets.py`
  - `src/compass_harness/templates/brain_assets.py`
  - `src/compass_harness/templates/compass_skills_assets.py`
- **Spec asociada**: [`specs/03-templates-and-skills/spec.md`](../../../specs/03-templates-and-skills/spec.md)
- **Tests**: [`tests/test_templates_and_skills.py`](../../../tests/test_templates_and_skills.py) (`10 passed`)

---

## 1. Responsabilidad
Generar en memoria de forma pura y determinista (`dict[str, str]`, sin tocar el sistema de archivos) el paquete completo de documentos que `compass init --apply` instalará en cualquier proyecto objetivo:
1. El Router de arranque (`AGENTS.md`, garantizando `< 100` líneas).
2. El Cerebro de 3 niveles (`docs/brain/index.md`, `architecture.md`, `handoff.md`, `decisions/index.md`, `decisions/0001-initial-architecture.md`).
3. Las 4 Skills instaladas en `.compass/skills/`:
   - `tdd` (la skill oficial íntegra de Matt Pocock: `SKILL.md`, `tests.md`, `mocking.md`).
   - `project-architect` (negociación arquitectónica y diagnóstico Greenfield vs Brownfield).
   - `sdd-workflow` (flujo `spec -> plan -> tasks`, *Seams*, *ADR Gate*, *Observed Proof* y verificación proporcional con subagente ligero y soporte E2E/Playwright opcional).
   - `mentor-guide` (generador bajo demanda de `guides/<slug>-GUIDE.md` con doble lente).

---

## 2. API Pública (Seam)
- `ProjectConfig` (`@dataclass(frozen=True)`):
  - Parámetros: `project_name`, `project_goal`, `tech_stack`, `domain`, `architecture_style`, `model_strategy`, `target_assistants`, `test_command`, `lint_command`, `e2e_command`.
- `render_project_bundle(config: ProjectConfig) -> dict[str, str]`:
  - Devuelve el diccionario con las 12 rutas relativas listas para previsualizar (`--preview`) o persistir (`--apply`).
