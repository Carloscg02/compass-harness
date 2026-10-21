"""Tests para el motor de instalacion y onboarding de compass-harness."""

from pathlib import Path
import pytest

from compass_harness.core.installer import (
    InstallationPlan,
    InstallationResult,
    SymlinkSpec,
    apply_installation,
    plan_installation,
)
from compass_harness.core.renderer import ProjectConfig


def test_plan_installation_structure_and_conflicts(tmp_path: Path) -> None:
    config = ProjectConfig(
        project_name="demo-project",
        project_goal="Demo goal",
        tech_stack="python",
        target_assistants=("antigravity",),
    )

    plan = plan_installation(tmp_path, config)

    assert isinstance(plan, InstallationPlan)
    assert len(list(tmp_path.iterdir())) == 0
    assert len(plan.files_to_create) == 13
    assert "AGENTS.md" in plan.files_to_create
    assert "CLAUDE.md" not in plan.files_to_create
    assert plan.existing_conflicts == ()
    assert len(plan.symlinks_to_create) == 5
    for symlink in plan.symlinks_to_create:
        assert symlink.link_path.startswith(".agents/skills/")
        assert symlink.target_path.startswith(".compass/skills/")

    config_claude = ProjectConfig(
        project_name="demo-project",
        project_goal="Demo goal",
        tech_stack="python",
        target_assistants=("antigravity", "claude"),
    )
    plan_claude = plan_installation(tmp_path, config_claude)
    assert len(plan_claude.files_to_create) == 14
    assert "CLAUDE.md" in plan_claude.files_to_create
    assert len(plan_claude.symlinks_to_create) == 10
    link_paths = {s.link_path for s in plan_claude.symlinks_to_create}
    assert ".agents/skills/tdd" in link_paths
    assert ".claude/skills/tdd" in link_paths

    existing_agents = tmp_path / "AGENTS.md"
    existing_agents.write_text("# Existing Agents\n", encoding="utf-8")

    plan_with_conflict = plan_installation(tmp_path, config)
    assert "AGENTS.md" in plan_with_conflict.existing_conflicts
    assert "AGENTS.md" not in plan_with_conflict.files_to_create


def test_apply_installation_writes_bundle_and_creates_symlinks(tmp_path: Path) -> None:
    config = ProjectConfig(
        project_name="demo-project",
        project_goal="Demo goal",
        tech_stack="python",
        target_assistants=("antigravity", "claude"),
    )

    result = apply_installation(tmp_path, config)

    assert isinstance(result, InstallationResult)
    assert len(result.written_files) == 14
    assert "AGENTS.md" in result.written_files
    assert "CLAUDE.md" in result.written_files
    assert len(result.skipped_files) == 0

    assert (tmp_path / "docs/brain/modules").is_dir()
    assert (tmp_path / "specs").is_dir()
    assert (tmp_path / "guides").is_dir()

    skills = ("tdd", "project-architect", "sdd-workflow", "mentor-guide", "ui-design")
    for assistant_dir in (".agents/skills", ".claude/skills"):
        for skill in skills:
            skill_link = tmp_path / assistant_dir / skill
            assert skill_link.is_symlink()
            target = tmp_path / ".compass/skills" / skill
            assert skill_link.resolve() == target.resolve()

    tdd_skill_content = (tmp_path / ".agents/skills/tdd/SKILL.md").read_text(encoding="utf-8")
    assert "name: tdd" in tdd_skill_content
    claude_tdd_skill_content = (tmp_path / ".claude/skills/tdd/SKILL.md").read_text(encoding="utf-8")
    assert "name: tdd" in claude_tdd_skill_content


def test_apply_installation_overwrite_protection_and_force(tmp_path: Path) -> None:
    agents_file = tmp_path / "AGENTS.md"
    custom_content = "# Custom AGENTS content\n"
    agents_file.write_text(custom_content, encoding="utf-8")

    config = ProjectConfig(
        project_name="demo-project",
        project_goal="Demo goal",
        tech_stack="python",
        target_assistants=("antigravity",),
    )

    result_no_force = apply_installation(tmp_path, config, force=False)
    assert "AGENTS.md" in result_no_force.skipped_files
    assert "AGENTS.md" not in result_no_force.written_files
    assert agents_file.read_text(encoding="utf-8") == custom_content

    result_force = apply_installation(tmp_path, config, force=True)
    assert "AGENTS.md" in result_force.written_files
    assert "AGENTS.md" not in result_force.skipped_files
    assert agents_file.read_text(encoding="utf-8") != custom_content
    assert "demo-project" in agents_file.read_text(encoding="utf-8")


def test_cli_init_phase_1_greenfield_and_brownfield(tmp_path: Path) -> None:
    from typer.testing import CliRunner
    from compass_harness.cli import app

    runner = CliRunner()

    greenfield_dir = tmp_path / "gf"
    greenfield_dir.mkdir()
    result_gf = runner.invoke(app, ["init", "--path", str(greenfield_dir)])
    assert result_gf.exit_code == 0
    assert len(list(greenfield_dir.iterdir())) == 0
    assert "COMPASS_ONBOARDING_REQUIRED" in result_gf.stdout
    assert "GREENFIELD" in result_gf.stdout.upper()
    assert "--preview" in result_gf.stdout

    brownfield_dir = tmp_path / "bf"
    brownfield_dir.mkdir()
    (brownfield_dir / "app.py").write_text("print('hello')\n", encoding="utf-8")
    result_bf = runner.invoke(app, ["init", "--path", str(brownfield_dir)])
    assert result_bf.exit_code == 0
    assert "COMPASS_ONBOARDING_REQUIRED" in result_bf.stdout
    assert "BROWNFIELD" in result_bf.stdout.upper()
    assert "--preview" in result_bf.stdout


def test_cli_init_phase_2_preview_mode(tmp_path: Path) -> None:
    from typer.testing import CliRunner
    from compass_harness.cli import app

    runner = CliRunner()
    preview_dir = tmp_path / "preview"
    preview_dir.mkdir()

    result = runner.invoke(
        app,
        [
            "init",
            "--path",
            str(preview_dir),
            "--name",
            "demo",
            "--goal",
            "Demo",
            "--assistants",
            "antigravity,claude",
            "--preview",
        ],
    )
    assert result.exit_code == 0
    assert len(list(preview_dir.iterdir())) == 0
    assert "COMPASS_ONBOARDING_PLAN" in result.stdout
    assert ".agents/skills/tdd" in result.stdout
    assert ".claude/skills/tdd" in result.stdout
    assert "--apply" in result.stdout


def test_cli_init_mutual_exclusion_preview_and_apply(tmp_path: Path) -> None:
    from typer.testing import CliRunner
    from compass_harness.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["init", "--path", str(tmp_path), "--preview", "--apply"])
    assert result.exit_code != 0


def test_cli_init_phase_3_apply_end_to_end(tmp_path: Path) -> None:
    from typer.testing import CliRunner
    from compass_harness.cli import app

    runner = CliRunner()
    target_dir = tmp_path / "applied"
    target_dir.mkdir()

    result = runner.invoke(
        app,
        [
            "init",
            "--path",
            str(target_dir),
            "--name",
            "demo",
            "--goal",
            "Demo",
            "--assistants",
            "antigravity,claude,cursor",
            "--e2e-cmd",
            "npx playwright test",
            "--apply",
        ],
    )
    assert result.exit_code == 0
    assert "COMPASS_ONBOARDING_APPLIED" in result.stdout
    assert (target_dir / "AGENTS.md").is_file()
    assert (target_dir / "CLAUDE.md").is_file()
    assert (target_dir / "docs/brain/architecture.md").is_file()

    arch_content = (target_dir / "docs/brain/architecture.md").read_text(encoding="utf-8")
    assert "npx playwright test" in arch_content

    for assistant_dir in (".agents/skills", ".claude/skills", ".cursor/skills"):
        for skill in ("tdd", "project-architect", "sdd-workflow", "mentor-guide", "ui-design"):
            skill_path = target_dir / assistant_dir / skill
            assert skill_path.is_symlink()
            assert (skill_path / "SKILL.md").is_file()


def test_cli_init_phase_3_overwrite_protection_and_force(tmp_path: Path) -> None:
    from typer.testing import CliRunner
    from compass_harness.cli import app

    runner = CliRunner()
    target_dir = tmp_path / "overwrite_test"
    target_dir.mkdir()

    result_initial = runner.invoke(
        app,
        [
            "init",
            "--path",
            str(target_dir),
            "--name",
            "demo",
            "--goal",
            "Demo",
            "--apply",
        ],
    )
    assert result_initial.exit_code == 0

    custom_text = "# Custom modifications preserved\n"
    agents_file = target_dir / "AGENTS.md"
    agents_file.write_text(custom_text, encoding="utf-8")

    result_no_force = runner.invoke(
        app,
        [
            "init",
            "--path",
            str(target_dir),
            "--name",
            "demo",
            "--goal",
            "Demo",
            "--apply",
        ],
    )
    assert result_no_force.exit_code == 0
    assert agents_file.read_text(encoding="utf-8") == custom_text
    assert "[SKIPPED] AGENTS.md" in result_no_force.stdout

    result_force = runner.invoke(
        app,
        [
            "init",
            "--path",
            str(target_dir),
            "--name",
            "demo",
            "--goal",
            "Demo",
            "--apply",
            "--force",
        ],
    )
    assert result_force.exit_code == 0
    assert agents_file.read_text(encoding="utf-8") != custom_text
    assert "[WRITTEN] AGENTS.md" in result_force.stdout
