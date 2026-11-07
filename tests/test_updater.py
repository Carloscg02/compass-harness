"""Tests para el motor de sincronizacion y actualizacion (updater) de compass-harness."""

import json
from pathlib import Path
import pytest

from compass_harness.core.installer import apply_installation
from compass_harness.core.renderer import ProjectConfig
from compass_harness.core.updater import (
    UpdatePlan,
    UpdateResult,
    apply_update,
    extract_project_config,
    plan_update,
    save_project_config,
)
from typer.testing import CliRunner
from compass_harness.cli import app


@pytest.fixture
def existing_project_without_config_json(tmp_path: Path) -> Path:
    """Crea un proyecto inicializado con Compass pero sin archivo .compass/config.json."""
    config = ProjectConfig(
        project_name="legacy-project",
        project_goal="Sistema de pagos legacy",
        tech_stack="python, fast-api",
        domain="Fintech & Payments",
        architecture_style="hexagonal",
        model_strategy="subagent-fast",
        target_assistants=("antigravity", "claude"),
        test_command="pytest -v",
        lint_command="ruff check .",
        e2e_command="playwright test",
    )
    apply_installation(tmp_path, config)
    # Verificamos que no existe .compass/config.json
    assert not (tmp_path / ".compass" / "config.json").exists()
    return tmp_path


def test_extract_project_config_from_existing_brain(
    existing_project_without_config_json: Path,
) -> None:
    """Debe reconstruir la configuracion inspeccionando docs/brain y symlinks."""
    config = extract_project_config(existing_project_without_config_json)

    assert isinstance(config, ProjectConfig)
    assert config.project_name == "legacy-project"
    assert config.project_goal == "Sistema de pagos legacy"
    assert "python" in config.tech_stack
    assert config.domain == "Fintech & Payments"
    assert config.architecture_style == "hexagonal"
    assert config.model_strategy == "subagent-fast"
    assert "antigravity" in config.target_assistants
    assert "claude" in config.target_assistants
    assert config.test_command == "pytest -v"
    assert config.lint_command == "ruff check ."
    assert config.e2e_command == "playwright test"


def test_extract_project_config_from_config_json(tmp_path: Path) -> None:
    """Si existe .compass/config.json, debe leerlo directamente."""
    compass_dir = tmp_path / ".compass"
    compass_dir.mkdir(parents=True, exist_ok=True)
    config_file = compass_dir / "config.json"
    data = {
        "project_name": "json-project",
        "project_goal": "Proyecto configurado con JSON",
        "tech_stack": "typescript, react",
        "domain": "E-commerce",
        "architecture_style": "layered",
        "model_strategy": "single",
        "target_assistants": ["antigravity", "cursor"],
        "test_command": "npm test",
        "lint_command": "npm run lint",
        "e2e_command": "npm run e2e",
    }
    config_file.write_text(json.dumps(data), encoding="utf-8")

    # Requiere AGENTS.md y docs/brain/index.md para confirmar que esta inicializado
    (tmp_path / "AGENTS.md").write_text("# Agents", encoding="utf-8")
    (tmp_path / "docs" / "brain").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "brain" / "index.md").write_text("# Cerebro", encoding="utf-8")

    config = extract_project_config(tmp_path)

    assert config.project_name == "json-project"
    assert config.project_goal == "Proyecto configurado con JSON"
    assert config.tech_stack == "typescript, react"
    assert config.domain == "E-commerce"
    assert config.architecture_style == "layered"
    assert config.model_strategy == "single"
    assert config.target_assistants == ("antigravity", "cursor")
    assert config.test_command == "npm test"
    assert config.lint_command == "npm run lint"
    assert config.e2e_command == "npm run e2e"


def test_extract_project_config_uninitialized_raises(tmp_path: Path) -> None:
    """Un directorio sin inicializar debe lanzar FileNotFoundError."""
    with pytest.raises(FileNotFoundError) as exc_info:
        extract_project_config(tmp_path)
    assert "no esta inicializado" in str(exc_info.value).lower()


def test_save_project_config(tmp_path: Path) -> None:
    """save_project_config debe persistir la configuracion en .compass/config.json."""
    config = ProjectConfig(
        project_name="saved-project",
        project_goal="Probar guardado",
        tech_stack="python",
        domain="Core",
        target_assistants=("antigravity",),
    )
    saved_path = save_project_config(tmp_path, config)

    assert saved_path == tmp_path / ".compass" / "config.json"
    assert saved_path.is_file()

    content = json.loads(saved_path.read_text(encoding="utf-8"))
    assert content["project_name"] == "saved-project"
    assert content["target_assistants"] == ["antigravity"]


def test_plan_update_identifies_stateless_and_preserves_stateful(
    existing_project_without_config_json: Path,
) -> None:
    """plan_update debe marcar skills y AGENTS para actualizar y preservar modulos y handoff."""
    root = existing_project_without_config_json

    # Crear memoria viva personalizada en el proyecto
    custom_module = root / "docs" / "brain" / "modules" / "billing.md"
    custom_module.write_text("# Modulo Billing\nLogica viva.", encoding="utf-8")

    custom_decision = root / "docs" / "brain" / "decisions" / "0002-custom.md"
    custom_decision.write_text("# ADR 0002\nPersonalizado.", encoding="utf-8")

    custom_handoff = root / "docs" / "brain" / "handoff.md"
    custom_handoff.write_text("# Handoff vivo\nNo sobreescribir.", encoding="utf-8")

    config = extract_project_config(root)
    plan = plan_update(root, config)

    assert isinstance(plan, UpdatePlan)
    # Archivos a actualizar: stateless (skills, AGENTS.md, CLAUDE.md)
    assert "AGENTS.md" in plan.files_to_update
    assert "CLAUDE.md" in plan.files_to_update
    assert ".compass/skills/tdd/SKILL.md" in plan.files_to_update
    assert ".compass/skills/sdd-workflow/SKILL.md" in plan.files_to_update

    # Inmutabilidad de archivos de memoria viva
    assert "docs/brain/modules/billing.md" in plan.preserved_files
    assert "docs/brain/decisions/0002-custom.md" in plan.preserved_files
    assert "docs/brain/handoff.md" in plan.preserved_files
    assert "docs/brain/index.md" in plan.preserved_files
    assert "docs/brain/architecture.md" in plan.preserved_files

    # Ningun archivo protegido debe figurar en files_to_update
    for protected in plan.preserved_files:
        assert protected not in plan.files_to_update

    # Symlinks planificados
    assert len(plan.symlinks_to_repair) > 0
    symlink_links = {s.link_path for s in plan.symlinks_to_repair}
    assert ".agents/skills/tdd" in symlink_links
    assert ".claude/skills/tdd" in symlink_links


def test_apply_update_updates_skills_and_agents_and_preserves_living_memory(
    existing_project_without_config_json: Path,
) -> None:
    """apply_update actualiza skills y AGENTS.md pero no toca ningun archivo de memoria viva."""
    root = existing_project_without_config_json

    # Modificar skills y AGENTS para simular versiones obsoletas
    agents_file = root / "AGENTS.md"
    agents_file.write_text("# Old AGENTS router obsolete\n", encoding="utf-8")

    tdd_skill_file = root / ".compass" / "skills" / "tdd" / "SKILL.md"
    tdd_skill_file.write_text("# Old TDD skill version 0.1\n", encoding="utf-8")

    # Modificar o añadir fichas de memoria viva
    custom_module = root / "docs" / "brain" / "modules" / "billing.md"
    custom_module.write_text("# Modulo Billing Vivo\nLogica intacta.", encoding="utf-8")

    custom_decision = root / "docs" / "brain" / "decisions" / "0003-billing-db.md"
    custom_decision.write_text("# ADR 0003: Postgres para billing\nIntacto.", encoding="utf-8")

    handoff_file = root / "docs" / "brain" / "handoff.md"
    handoff_content = "# Handoff Vivo\nTurno 15 en progreso.\n"
    handoff_file.write_text(handoff_content, encoding="utf-8")

    config = extract_project_config(root)
    result = apply_update(root, config)

    assert isinstance(result, UpdateResult)
    assert result.config_saved is True
    assert (root / ".compass" / "config.json").is_file()

    # Archivos actualizados efectivamente
    assert "AGENTS.md" in result.updated_files
    assert ".compass/skills/tdd/SKILL.md" in result.updated_files
    assert "# Old AGENTS router obsolete" not in agents_file.read_text(encoding="utf-8")
    assert "# Old TDD skill version 0.1" not in tdd_skill_file.read_text(encoding="utf-8")

    # Inmutabilidad estricta de la memoria viva
    assert custom_module.read_text(encoding="utf-8") == "# Modulo Billing Vivo\nLogica intacta."
    assert custom_decision.read_text(encoding="utf-8") == "# ADR 0003: Postgres para billing\nIntacto."
    assert handoff_file.read_text(encoding="utf-8") == handoff_content

    # Ningun archivo de memoria viva figura en updated_files
    for updated in result.updated_files:
        assert not updated.startswith("docs/brain/modules/")
        assert not updated.startswith("docs/brain/decisions/")
        assert updated != "docs/brain/handoff.md"
        assert updated != "docs/brain/index.md"
        assert updated != "docs/brain/architecture.md"

    # Los archivos de memoria viva figuran en preserved_files
    assert "docs/brain/modules/billing.md" in result.preserved_files
    assert "docs/brain/decisions/0003-billing-db.md" in result.preserved_files
    assert "docs/brain/handoff.md" in result.preserved_files


def test_apply_update_idempotency_and_force(
    existing_project_without_config_json: Path,
) -> None:
    """Una segunda ejecucion consecutiva de apply_update omite archivos identicos salvo con --force."""
    root = existing_project_without_config_json
    config = extract_project_config(root)

    # Primera ejecucion (actualiza lo que difiera)
    res1 = apply_update(root, config)
    assert isinstance(res1, UpdateResult)

    # Segunda ejecucion inmediata sin force: debe omitir los archivos ya actualizados
    res2 = apply_update(root, config, force=False)
    assert len(res2.updated_files) == 0
    assert len(res2.skipped_files) > 0
    assert "AGENTS.md" in res2.skipped_files
    assert ".compass/skills/tdd/SKILL.md" in res2.skipped_files

    # Tercera ejecucion con force=True: sobreescribe todos los stateless
    res3 = apply_update(root, config, force=True)
    assert len(res3.updated_files) > 0
    assert len(res3.skipped_files) == 0
    assert "AGENTS.md" in res3.updated_files


def test_apply_update_repairs_broken_symlinks(
    existing_project_without_config_json: Path,
) -> None:
    """apply_update repara enlaces simbolicos rotos o eliminados."""
    root = existing_project_without_config_json
    symlink_path = root / ".agents" / "skills" / "tdd"

    # Romper el symlink eliminandolo
    if symlink_path.is_symlink():
        symlink_path.unlink()

    assert not symlink_path.exists()

    config = extract_project_config(root)
    result = apply_update(root, config)

    assert symlink_path.is_symlink()
    assert symlink_path.resolve().exists()
    assert ".agents/skills/tdd" in result.repaired_symlinks


def test_cli_update_not_initialized(tmp_path: Path) -> None:
    """compass update sobre carpeta sin inicializar falla con COMPASS_NOT_INITIALIZED."""
    runner = CliRunner()
    result = runner.invoke(app, ["update", "--path", str(tmp_path)])

    assert result.exit_code == 1
    assert "=== COMPASS_NOT_INITIALIZED ===" in result.stdout
    assert "no esta" in result.stdout.lower()
    assert "inicializado" in result.stdout.lower()


def test_cli_update_both_preview_and_apply(
    existing_project_without_config_json: Path,
) -> None:
    """compass update con --preview y --apply simultaneos falla."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["update", "--path", str(existing_project_without_config_json), "--preview", "--apply"],
    )

    assert result.exit_code == 1
    assert "No se pueden especificar --preview y --apply simultaneamente" in result.stdout


def test_cli_update_required_info_screen(
    existing_project_without_config_json: Path,
) -> None:
    """compass update sin flags emite COMPASS_UPDATE_REQUIRED con estado y opciones."""
    runner = CliRunner()
    result = runner.invoke(app, ["update", "--path", str(existing_project_without_config_json)])

    assert result.exit_code == 0
    assert "=== COMPASS_UPDATE_REQUIRED ===" in result.stdout
    assert "--preview" in result.stdout
    assert "--apply" in result.stdout
    assert "legacy-project" in result.stdout


def test_cli_update_preview(
    existing_project_without_config_json: Path,
) -> None:
    """compass update --preview muestra el plan sin modificar disco."""
    root = existing_project_without_config_json
    runner = CliRunner()
    result = runner.invoke(app, ["update", "--path", str(root), "--preview"])

    assert result.exit_code == 0
    assert "=== COMPASS_UPDATE_PLAN ===" in result.stdout
    assert "[UPDATE]" in result.stdout
    assert "[PRESERVED]" in result.stdout
    assert "[SYMLINK]" in result.stdout
    assert "AGENTS.md" in result.stdout
    # El archivo config.json no se crea en modo preview
    assert not (root / ".compass" / "config.json").exists()


def test_cli_update_apply_and_health_summary(
    existing_project_without_config_json: Path,
) -> None:
    """compass update --apply actualiza y muestra el resumen de salud post-update."""
    root = existing_project_without_config_json
    # Modificamos AGENTS.md para simular que requiere actualizacion
    (root / "AGENTS.md").write_text("# Obsolete AGENTS router\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["update", "--path", str(root), "--apply"])

    assert result.exit_code == 0
    assert "=== COMPASS_UPDATE_APPLIED ===" in result.stdout
    assert "[UPDATED]" in result.stdout
    assert "[SYMLINK]" in result.stdout
    assert "Resumen de salud del arnes" in result.stdout
    assert "HEALTHY" in result.stdout
    assert (root / ".compass" / "config.json").is_file()


def test_cli_update_apply_force(
    existing_project_without_config_json: Path,
) -> None:
    """compass update --apply --force sobreescribe incluso si los archivos no cambiaron."""
    root = existing_project_without_config_json
    runner = CliRunner()

    # Primera aplicacion
    runner.invoke(app, ["update", "--path", str(root), "--apply"])

    # Segunda aplicacion con force
    result_force = runner.invoke(app, ["update", "--path", str(root), "--apply", "--force"])
    assert result_force.exit_code == 0
    assert "=== COMPASS_UPDATE_APPLIED ===" in result_force.stdout
    assert "[UPDATED] AGENTS.md" in result_force.stdout


