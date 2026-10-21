"""Tests para la gobernanza de diseno UI y contratos de diseno en compass-harness."""

from pathlib import Path
import pytest

from compass_harness.core.inspector import (
    ProjectInspection,
    ProjectState,
    inspect_project,
)


def test_inspect_project_backend_pure_has_empty_ui_signals_and_design_files(tmp_path: Path) -> None:
    """Verifica que un proyecto backend puro retorne tuplas vacias para senales UI y diseno."""
    backend_dir = tmp_path / "backend_pure"
    backend_dir.mkdir()
    (backend_dir / "pyproject.toml").write_text('[project]\nname = "backend"\n', encoding="utf-8")
    src_dir = backend_dir / "src"
    src_dir.mkdir()
    (src_dir / "server.py").write_text("print('server')\n", encoding="utf-8")

    result = inspect_project(backend_dir)
    assert result.state == ProjectState.BROWNFIELD
    assert result.detected_stacks == ("python",)
    assert result.detected_ui_signals == ()
    assert result.existing_design_files == ()


def test_inspect_project_detects_ui_signals_from_manifests_and_components(tmp_path: Path) -> None:
    """Verifica la deteccion de senales UI como tailwind, shadcn y componentes frontend."""
    frontend_dir = tmp_path / "frontend_proj"
    frontend_dir.mkdir()
    (frontend_dir / "tailwind.config.js").write_text("module.exports = {};\n", encoding="utf-8")
    (frontend_dir / "components.json").write_text('{"style": "default"}\n', encoding="utf-8")
    src_dir = frontend_dir / "src"
    src_dir.mkdir()
    (src_dir / "Button.tsx").write_text("export const Button = () => <button />;\n", encoding="utf-8")

    result = inspect_project(frontend_dir)
    assert "tailwind" in result.detected_ui_signals
    assert "shadcn-ui" in result.detected_ui_signals
    assert "frontend-components" in result.detected_ui_signals


def test_inspect_project_detects_existing_design_files(tmp_path: Path) -> None:
    """Verifica la deteccion de DESIGN.md y docs/brain/design.md como contratos previos."""
    design_dir = tmp_path / "design_proj"
    design_dir.mkdir()
    (design_dir / "DESIGN.md").write_text("# Design System\n", encoding="utf-8")
    brain_dir = design_dir / "docs" / "brain"
    brain_dir.mkdir(parents=True)
    (brain_dir / "design.md").write_text("# Brain Design\n", encoding="utf-8")

    result = inspect_project(design_dir)
    assert "DESIGN.md" in result.existing_design_files
    assert "docs/brain/design.md" in result.existing_design_files


def test_render_project_bundle_includes_ui_design_skill_with_frontmatter() -> None:
    """Verifica que el bundle incluya .compass/skills/ui-design/SKILL.md con frontmatter valido (CA-2)."""
    from compass_harness.core.renderer import ProjectConfig, render_project_bundle

    config = ProjectConfig(
        project_name="ui-demo",
        project_goal="Probar gobernanza UI",
        tech_stack="typescript",
    )
    bundle = render_project_bundle(config)

    assert ".compass/skills/ui-design/SKILL.md" in bundle
    skill_content = bundle[".compass/skills/ui-design/SKILL.md"]
    lines = skill_content.strip().splitlines()
    assert lines[0] == "---"
    assert any(line.startswith("name: ui-design") for line in lines[:5])
    assert any(line.startswith("description:") for line in lines[:5])
    closing_indices = [i for i, line in enumerate(lines[1:], start=1) if line == "---"]
    assert len(closing_indices) >= 1


def test_ui_design_skill_content_requirements() -> None:
    """Verifica que ui-design/SKILL.md contenga las secciones y reglas obligatorias (CA-3)."""
    from compass_harness.core.renderer import ProjectConfig, render_project_bundle

    config = ProjectConfig(
        project_name="ui-demo",
        project_goal="Probar gobernanza UI",
        tech_stack="typescript",
    )
    bundle = render_project_bundle(config)
    skill_content = bundle[".compass/skills/ui-design/SKILL.md"]

    assert "Brownfield" in skill_content or "brownfield" in skill_content.lower()
    assert "Greenfield" in skill_content or "greenfield" in skill_content.lower()
    assert "https://ancient-prompt-design-flow.base44.app/" in skill_content
    assert "precision-dark" in skill_content
    assert "warm-editorial" in skill_content
    assert "telemetry-grid" in skill_content
    assert "neo-brutalist-craft" in skill_content

    # Ley de los 4 estados
    assert "Loading" in skill_content
    assert "Empty" in skill_content
    assert "Error" in skill_content
    assert "Populated" in skill_content

    # Reglas Anti-Slop y Agent Eyes (Semantic DOM + Auto-Bootstrap)
    assert "Anti-Slop" in skill_content or "anti-slop" in skill_content.lower()
    assert "Tokens" in skill_content or "tokens" in skill_content.lower()
    assert "docs/brain/design.md" in skill_content
    assert "ariaSnapshot" in skill_content
    assert "scrollWidth" in skill_content and "clientWidth" in skill_content
    assert "Agent Eyes" in skill_content


def test_agents_md_and_sdd_workflow_contain_ui_gate() -> None:
    """Verifica que AGENTS.md y sdd-workflow/SKILL.md incluyan el UI / Frontend Gate (CA-4)."""
    from compass_harness.core.renderer import ProjectConfig, render_project_bundle

    config = ProjectConfig(
        project_name="ui-demo",
        project_goal="Probar gobernanza UI",
        tech_stack="typescript",
    )
    bundle = render_project_bundle(config)

    agents_content = bundle["AGENTS.md"]
    assert len(agents_content.splitlines()) < 100
    assert "ui-design" in agents_content
    assert "UI" in agents_content or "Frontend" in agents_content
    assert "docs/brain/design.md" in agents_content

    sdd_content = bundle[".compass/skills/sdd-workflow/SKILL.md"]
    assert "ui-design" in sdd_content
    assert "docs/brain/design.md" in sdd_content


def test_apply_installation_creates_ui_design_symlinks(tmp_path: Path) -> None:
    """Verifica que apply_installation cree el enlace simbolico de ui-design (CA-2)."""
    from compass_harness.core.installer import apply_installation
    from compass_harness.core.renderer import ProjectConfig

    config = ProjectConfig(
        project_name="symlink-demo",
        project_goal="Probar symlinks",
        tech_stack="typescript",
        target_assistants=("antigravity", "claude"),
    )
    apply_installation(tmp_path, config)

    ui_link_agents = tmp_path / ".agents/skills/ui-design"
    assert ui_link_agents.is_symlink()
    assert (ui_link_agents / "SKILL.md").is_file()

    ui_link_claude = tmp_path / ".claude/skills/ui-design"
    assert ui_link_claude.is_symlink()
    assert (ui_link_claude / "SKILL.md").is_file()


def test_verify_harness_without_design_contract_passes(tmp_path: Path) -> None:
    """Verifica que un proyecto sin docs/brain/design.md pase con has_design_contract=False (CA-5)."""
    from typer.testing import CliRunner
    from compass_harness.cli import app
    from compass_harness.core.installer import apply_installation
    from compass_harness.core.renderer import ProjectConfig
    from compass_harness.core.verifier import verify_harness

    config = ProjectConfig(
        project_name="backend-service",
        project_goal="API backend",
        tech_stack="python",
    )
    apply_installation(tmp_path, config)

    report = verify_harness(tmp_path)
    assert report.is_installed is True
    assert report.has_design_contract is False
    assert report.passed is True

    runner = CliRunner()
    result = runner.invoke(app, ["status", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "Contrato UI (design.md): No requerido / Inactivo" in result.stdout


def test_verify_harness_with_valid_design_contract(tmp_path: Path) -> None:
    """Verifica que un docs/brain/design.md valido active el contrato y pase la verificacion (CA-5)."""
    from typer.testing import CliRunner
    from compass_harness.cli import app
    from compass_harness.core.installer import apply_installation
    from compass_harness.core.renderer import ProjectConfig
    from compass_harness.core.verifier import verify_harness

    config = ProjectConfig(
        project_name="frontend-app",
        project_goal="App web",
        tech_stack="typescript",
    )
    apply_installation(tmp_path, config)

    design_content = """# Design Contract: frontend-app

## 1. Aesthetic Direction
Precision dark theme with clean surfaces.

## 2. Design Tokens
- surface: #121212
- text-primary: #FFFFFF
- border-subtle: #2A2A2A

## 3. Typography & Spacing
- Font sans: Inter
- Tabular figures for telemetry

## 4. Component & Anti-Slop Rules
- 4 states mandatory: Loading, Empty, Error, Populated
"""
    (tmp_path / "docs/brain/design.md").write_text(design_content, encoding="utf-8")

    report = verify_harness(tmp_path)
    assert report.has_design_contract is True
    assert report.has_agent_eyes is False
    assert report.passed is True

    runner = CliRunner()
    result = runner.invoke(app, ["status", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "Contrato UI (design.md): Activo" in result.stdout
    assert "Aviso UI: Contrato UI activo pero E2E / Agent Eyes esta en N/A" in result.stdout


def test_verify_harness_design_contract_budget_exceeded(tmp_path: Path) -> None:
    """Verifica que docs/brain/design.md con mas de 80 lineas falle con BUDGET_EXCEEDED (CA-5)."""
    from typer.testing import CliRunner
    from compass_harness.cli import app
    from compass_harness.core.installer import apply_installation
    from compass_harness.core.renderer import ProjectConfig
    from compass_harness.core.verifier import verify_harness

    config = ProjectConfig(
        project_name="bloated-design",
        project_goal="App con exceso de diseno",
        tech_stack="typescript",
    )
    apply_installation(tmp_path, config)

    # Generar 85 lineas incluyendo tokens y typography
    lines = [
        "# Design Contract",
        "## 1. Aesthetic Direction",
        "## 2. Design Tokens",
        "Tokens list:",
    ]
    lines.extend([f"- token-{i}: value-{i}" for i in range(80)])
    lines.extend([
        "## 3. Typography & Spacing",
        "Font settings",
        "## 4. Component Rules",
    ])
    assert len(lines) > 80

    (tmp_path / "docs/brain/design.md").write_text("\n".join(lines), encoding="utf-8")

    report = verify_harness(tmp_path)
    assert report.has_design_contract is True
    assert report.passed is False
    assert any(i.code == "BUDGET_EXCEEDED" and i.path == "docs/brain/design.md" for i in report.issues)

    runner = CliRunner()
    result = runner.invoke(app, ["check", "--path", str(tmp_path)])
    assert result.exit_code == 1
    assert "BUDGET_EXCEEDED" in result.stdout


def test_verify_harness_design_contract_incomplete(tmp_path: Path) -> None:
    """Verifica que docs/brain/design.md sin tokens o typography falle con INCOMPLETE_DESIGN_CONTRACT (CA-5)."""
    from typer.testing import CliRunner
    from compass_harness.cli import app
    from compass_harness.core.installer import apply_installation
    from compass_harness.core.renderer import ProjectConfig
    from compass_harness.core.verifier import verify_harness

    config = ProjectConfig(
        project_name="incomplete-design",
        project_goal="App con diseno incompleto",
        tech_stack="typescript",
    )
    apply_installation(tmp_path, config)

    incomplete_content = """# Design Contract

## 1. Aesthetic Direction
Solo direccion estetica basica sin secciones requeridas.
"""
    (tmp_path / "docs/brain/design.md").write_text(incomplete_content, encoding="utf-8")

    report = verify_harness(tmp_path)
    assert report.has_design_contract is True
    assert report.passed is False
    assert any(i.code == "INCOMPLETE_DESIGN_CONTRACT" and i.path == "docs/brain/design.md" for i in report.issues)

    runner = CliRunner()
    result = runner.invoke(app, ["check", "--path", str(tmp_path)])
    assert result.exit_code == 1
    assert "INCOMPLETE_DESIGN_CONTRACT" in result.stdout
