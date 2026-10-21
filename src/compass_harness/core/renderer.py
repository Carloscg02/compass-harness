"""Motor de renderizado de plantillas y skills de compass-harness."""

from dataclasses import dataclass

from compass_harness.templates.brain_assets import (
    render_agents_md,
    render_architecture_md,
    render_brain_index_md,
    render_decisions_index_md,
    render_handoff_md,
    render_initial_adr_md,
)
from compass_harness.templates.compass_skills_assets import (
    render_mentor_guide_skill,
    render_project_architect_skill,
    render_sdd_workflow_skill,
    render_ui_design_skill,
)
from compass_harness.templates.tdd_skill_assets import (
    TDD_MOCKING_MD,
    TDD_SKILL_MD,
    TDD_TESTS_MD,
)


@dataclass(frozen=True)
class ProjectConfig:
    """Configuracion inmutable para el renderizado del bundle del proyecto."""

    project_name: str
    project_goal: str
    tech_stack: str
    domain: str = "General Software Engineering"
    architecture_style: str = "hexagonal"
    model_strategy: str = "subagent-fast"
    target_assistants: tuple[str, ...] = ("antigravity",)
    test_command: str = "pytest"
    lint_command: str = "ruff check"
    e2e_command: str = "N/A"


def render_project_bundle(config: ProjectConfig) -> dict[str, str]:
    """Genera el diccionario de archivos y contenidos en memoria para el proyecto."""
    bundle: dict[str, str] = {
        "AGENTS.md": render_agents_md(config),
        "docs/brain/index.md": render_brain_index_md(config),
        "docs/brain/architecture.md": render_architecture_md(config),
        "docs/brain/handoff.md": render_handoff_md(config),
        "docs/brain/decisions/index.md": render_decisions_index_md(config),
        "docs/brain/decisions/0001-initial-architecture.md": render_initial_adr_md(config),
        ".compass/skills/tdd/SKILL.md": TDD_SKILL_MD,
        ".compass/skills/tdd/tests.md": TDD_TESTS_MD,
        ".compass/skills/tdd/mocking.md": TDD_MOCKING_MD,
        ".compass/skills/project-architect/SKILL.md": render_project_architect_skill(config),
        ".compass/skills/sdd-workflow/SKILL.md": render_sdd_workflow_skill(config),
        ".compass/skills/mentor-guide/SKILL.md": render_mentor_guide_skill(config),
        ".compass/skills/ui-design/SKILL.md": render_ui_design_skill(config),
    }
    return bundle
