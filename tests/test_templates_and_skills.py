"""Tests para el motor de plantillas y skills de compass-harness."""

from compass_harness.core.renderer import ProjectConfig, render_project_bundle

EXPECTED_BUNDLE_PATHS = {
    "AGENTS.md",
    "docs/brain/index.md",
    "docs/brain/architecture.md",
    "docs/brain/handoff.md",
    "docs/brain/decisions/index.md",
    "docs/brain/decisions/0001-initial-architecture.md",
    ".compass/skills/tdd/SKILL.md",
    ".compass/skills/tdd/tests.md",
    ".compass/skills/tdd/mocking.md",
    ".compass/skills/project-architect/SKILL.md",
    ".compass/skills/sdd-workflow/SKILL.md",
    ".compass/skills/mentor-guide/SKILL.md",
    ".compass/skills/ui-design/SKILL.md",
}


def test_render_project_bundle_contains_all_13_paths() -> None:
    config = ProjectConfig(
        project_name="demo-project",
        project_goal="Construir una herramienta CLI robusta",
        tech_stack="python",
    )
    bundle = render_project_bundle(config)

    assert set(bundle.keys()) == EXPECTED_BUNDLE_PATHS
    assert len(bundle) == 13


def test_tdd_skill_assets_fidelity() -> None:
    config = ProjectConfig(
        project_name="demo-project",
        project_goal="Construir una herramienta CLI robusta",
        tech_stack="python",
    )
    bundle = render_project_bundle(config)

    skill_md = bundle[".compass/skills/tdd/SKILL.md"]
    assert "name: tdd" in skill_md
    assert "## What a good test is" in skill_md
    assert "## Seams: where tests go" in skill_md
    assert "## Anti-patterns" in skill_md
    assert "Horizontal slicing" in skill_md
    assert "## Rules of the loop" in skill_md

    tests_md = bundle[".compass/skills/tdd/tests.md"]
    assert "Good and Bad Tests" in tests_md
    assert "Integration-style" in tests_md
    assert "Tautological tests" in tests_md

    mocking_md = bundle[".compass/skills/tdd/mocking.md"]
    assert "When to Mock" in mocking_md
    assert "system boundaries" in mocking_md
    assert "Designing for Mockability" in mocking_md


def test_agents_md_structure_and_model_strategies() -> None:
    cfg_fast = ProjectConfig(
        project_name="my-service",
        project_goal="High throughput processing",
        tech_stack="rust",
        model_strategy="subagent-fast",
    )
    bundle_fast = render_project_bundle(cfg_fast)
    agents_fast = bundle_fast["AGENTS.md"]
    assert len(agents_fast.splitlines()) < 100
    assert "`ANSWER`" in agents_fast
    assert "`FTD`" in agents_fast
    assert "`SDD`" in agents_fast
    assert "docs/brain/index.md" in agents_fast
    assert ".compass/skills/project-architect" in agents_fast
    assert ".compass/skills/sdd-workflow" in agents_fast
    assert ".compass/skills/tdd" in agents_fast
    assert ".compass/skills/mentor-guide" in agents_fast
    assert "subagente" in agents_fast.lower() or "subagent" in agents_fast.lower()
    assert "fast" in agents_fast.lower() or "flash" in agents_fast.lower()
    assert "builder" in agents_fast.lower()
    assert "auditor" in agents_fast.lower()
    assert "audit" in agents_fast.lower()

    cfg_single = ProjectConfig(
        project_name="my-service",
        project_goal="High throughput processing",
        tech_stack="rust",
        model_strategy="single",
    )
    bundle_single = render_project_bundle(cfg_single)
    agents_single = bundle_single["AGENTS.md"]
    assert len(agents_single.splitlines()) < 100
    assert "single" in agents_single.lower() or "monolitico" in agents_single.lower() or "sin subagentes" in agents_single.lower()

    cfg_inherit = ProjectConfig(
        project_name="my-service",
        project_goal="High throughput processing",
        tech_stack="rust",
        model_strategy="subagent-inherit",
    )
    bundle_inherit = render_project_bundle(cfg_inherit)
    agents_inherit = bundle_inherit["AGENTS.md"]
    assert len(agents_inherit.splitlines()) < 100
    assert "inherit" in agents_inherit.lower()


def test_brain_index_md_contents_and_o1_adr_link() -> None:
    config = ProjectConfig(
        project_name="telecom-dsp",
        project_goal="Procesador SDR de senales",
        tech_stack="python + numpy",
        domain="Telecomunicaciones y Procesamiento de Senal (RF/DSP)",
    )
    bundle = render_project_bundle(config)
    index_md = bundle["docs/brain/index.md"]

    assert config.project_name in index_md
    assert config.project_goal in index_md
    assert config.tech_stack in index_md
    assert config.domain in index_md
    assert "architecture.md" in index_md
    assert "handoff.md" in index_md
    assert "modules/" in index_md

    adr_lines = [line for line in index_md.splitlines() if "decisions" in line]
    assert len(adr_lines) == 1
    assert "decisions/index.md" in adr_lines[0]
    assert "0001-initial-architecture" not in index_md


def test_architecture_md_style_and_verification_commands() -> None:
    cfg_hex = ProjectConfig(
        project_name="banking-api",
        project_goal="Gestion de cuentas",
        tech_stack="go",
        architecture_style="hexagonal",
        test_command="go test ./...",
        lint_command="golangci-lint run",
        e2e_command="npx playwright test",
    )
    bundle_hex = render_project_bundle(cfg_hex)
    arch_hex = bundle_hex["docs/brain/architecture.md"]

    assert "Hexagonal" in arch_hex or "Puertos y Adaptadores" in arch_hex
    assert "go test ./..." in arch_hex
    assert "golangci-lint run" in arch_hex
    assert "npx playwright test" in arch_hex

    cfg_script = ProjectConfig(
        project_name="data-migrator",
        project_goal="Scripts de migracion",
        tech_stack="python",
        architecture_style="script",
    )
    bundle_script = render_project_bundle(cfg_script)
    arch_script = bundle_script["docs/brain/architecture.md"]

    assert "Script" in arch_script or "script" in arch_script
    assert "pytest" in arch_script
    assert "ruff check" in arch_script
    assert "N/A" in arch_script


def test_handoff_and_decisions_assets() -> None:
    config = ProjectConfig(
        project_name="demo-service",
        project_goal="Servicio de prueba",
        tech_stack="typescript",
    )
    bundle = render_project_bundle(config)

    handoff_md = bundle["docs/brain/handoff.md"]
    assert len(handoff_md.splitlines()) < 30
    assert "Handoff" in handoff_md or "Estado" in handoff_md

    adr_index_md = bundle["docs/brain/decisions/index.md"]
    assert "0001-initial-architecture.md" in adr_index_md

    initial_adr_md = bundle["docs/brain/decisions/0001-initial-architecture.md"]
    assert "0001" in initial_adr_md
    assert config.architecture_style in initial_adr_md.lower()


def test_all_skills_have_valid_yaml_frontmatter() -> None:
    config = ProjectConfig(
        project_name="skill-demo",
        project_goal="Validar skills",
        tech_stack="python",
    )
    bundle = render_project_bundle(config)

    skill_paths = [
        ".compass/skills/tdd/SKILL.md",
        ".compass/skills/project-architect/SKILL.md",
        ".compass/skills/sdd-workflow/SKILL.md",
        ".compass/skills/mentor-guide/SKILL.md",
        ".compass/skills/ui-design/SKILL.md",
    ]

    for path in skill_paths:
        content = bundle[path]
        lines = content.strip().splitlines()
        assert lines[0] == "---", f"{path} no comienza con ---"
        assert any(line.startswith("name: ") for line in lines[:10]), f"{path} no define name:"
        assert any(line.startswith("description: ") for line in lines[:10]), f"{path} no define description:"
        closing_dashes = [i for i, line in enumerate(lines[1:], start=1) if line == "---"]
        assert len(closing_dashes) >= 1, f"{path} no cierra frontmatter YAML con ---"


def test_sdd_workflow_skill_content() -> None:
    config = ProjectConfig(
        project_name="skill-demo",
        project_goal="Validar flujo SDD",
        tech_stack="python",
    )
    bundle = render_project_bundle(config)
    sdd_md = bundle[".compass/skills/sdd-workflow/SKILL.md"]

    assert "name: sdd-workflow" in sdd_md
    assert "spec.md" in sdd_md
    assert "plan.md" in sdd_md
    assert "tasks.md" in sdd_md
    assert "Seams" in sdd_md or "seams" in sdd_md
    assert "tdd" in sdd_md
    assert "decisions/index.md" in sdd_md or "ADR Gate" in sdd_md
    assert "Observed Proof" in sdd_md or "Prueba Observada" in sdd_md
    assert "Playwright" in sdd_md or "E2E" in sdd_md
    assert "flash" in sdd_md or "fast tier" in sdd_md


def test_sdd_workflow_skill_includes_auditor_gate_and_rubric() -> None:
    config = ProjectConfig(
        project_name="audit-demo",
        project_goal="Validar puerta de auditoria",
        tech_stack="python",
        test_command="pytest",
        lint_command="ruff check",
    )
    bundle = render_project_bundle(config)
    sdd_md = bundle[".compass/skills/sdd-workflow/SKILL.md"]

    # Puerta de Auditoria y Rol
    assert "Auditor Subagent" in sdd_md
    assert "contexto limpio" in sdd_md.lower() or "clean context" in sdd_md.lower()

    # Rubrica de 4 Puntos
    assert "Rubrica de 4 Puntos" in sdd_md or "4-point" in sdd_md.lower()
    assert "Criterios de Aceptacion" in sdd_md or "CA-" in sdd_md
    assert "Ejecucion Determinista" in sdd_md or config.test_command in sdd_md
    assert "Anti-Patrones" in sdd_md or "anti-patrones" in sdd_md.lower()
    assert "VERDICT: APPROVED" in sdd_md
    assert "VERDICT: REJECTED" in sdd_md

    # Feedback loop: el auditor no edita codigo
    assert "no edita codigo" in sdd_md.lower() or "no modifica codigo" in sdd_md.lower()



def test_mentor_guide_skill_injects_domain() -> None:
    custom_domain = "Sistemas Distribuidos y Procesamiento Concurrente"
    config = ProjectConfig(
        project_name="skill-demo",
        project_goal="Validar mentor guide",
        tech_stack="go",
        domain=custom_domain,
    )
    bundle = render_project_bundle(config)
    mentor_md = bundle[".compass/skills/mentor-guide/SKILL.md"]

    assert "name: mentor-guide" in mentor_md
    assert custom_domain in mentor_md
    assert "guides/" in mentor_md
    assert "Ingenieria de Software" in mentor_md or "Software Engineering" in mentor_md


def test_core_package_reexports_renderer_symbols() -> None:
    from compass_harness.core import (
        ProjectConfig as CoreProjectConfig,
        render_project_bundle as core_render_project_bundle,
    )

    assert CoreProjectConfig is ProjectConfig
    assert core_render_project_bundle is render_project_bundle


