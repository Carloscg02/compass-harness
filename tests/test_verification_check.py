"""Tests para el motor de auditoria y verificacion de compass-harness."""

from pathlib import Path
import shutil
import pytest
from typer.testing import CliRunner

from compass_harness.cli import app
from compass_harness.core.installer import apply_installation
from compass_harness.core.renderer import ProjectConfig
from compass_harness.core.verifier import (
    CheckIssue,
    HarnessReport,
    SpecProgress,
    verify_harness,
)


@pytest.fixture
def initialized_project(tmp_path: Path) -> Path:
    """Fixture que crea un proyecto inicializado de forma valida."""
    config = ProjectConfig(
        project_name="demo-harness",
        project_goal="Probar motor de verificacion",
        tech_stack="python",
        target_assistants=("antigravity",),
    )
    apply_installation(tmp_path, config)
    return tmp_path


def test_verify_harness_passes_on_healthy_initialized_project(initialized_project: Path) -> None:
    """Un proyecto recien inicializado debe superar todas las comprobaciones."""
    report = verify_harness(initialized_project)

    assert isinstance(report, HarnessReport)
    assert report.is_installed is True
    assert report.passed is True
    assert report.issues == ()
    assert len(report.present_brain_files) == 5
    assert report.missing_brain_files == ()
    assert "tdd" in report.installed_skills
    assert ".agents/skills/tdd" in report.active_symlinks
    assert report.broken_symlinks == ()


def test_verify_harness_fails_on_empty_uninitialized_directory(tmp_path: Path) -> None:
    """Un directorio vacio debe detectarse como no instalado y listar archivos del cerebro faltantes."""
    report = verify_harness(tmp_path)

    assert report.is_installed is False
    assert report.passed is False
    assert len(report.missing_brain_files) == 5
    missing_codes = [issue.code for issue in report.issues]
    assert all(code == "MISSING_BRAIN_FILE" for code in missing_codes)
    assert len(report.issues) == 5


def test_verify_harness_detects_context_budget_exceeded(initialized_project: Path) -> None:
    """Detecta archivos que sobrepasan el presupuesto maximo de lineas."""
    agents_file = initialized_project / "AGENTS.md"
    agents_file.write_text("\n".join([f"line {i}" for i in range(105)]) + "\n", encoding="utf-8")

    handoff_file = initialized_project / "docs/brain/handoff.md"
    handoff_file.write_text("\n".join([f"line {i}" for i in range(35)]) + "\n", encoding="utf-8")

    report = verify_harness(initialized_project)

    assert report.passed is False
    budget_issues = [issue for issue in report.issues if issue.code == "BUDGET_EXCEEDED"]
    assert len(budget_issues) == 2
    paths = {issue.path for issue in budget_issues}
    assert "AGENTS.md" in paths
    assert "docs/brain/handoff.md" in paths


def test_verify_harness_detects_adr_index_bloat(initialized_project: Path) -> None:
    """Detecta inflacion en docs/brain/index.md si lista multiples decisiones individuales."""
    index_file = initialized_project / "docs/brain/index.md"
    bloated_content = (
        "# Cerebro\n\n"
        "- [decisions/index.md](decisions/index.md)\n"
        "- [decisions/0001-first.md](decisions/0001-first.md)\n"
        "- [decisions/0002-second.md](decisions/0002-second.md)\n"
    )
    index_file.write_text(bloated_content, encoding="utf-8")

    report = verify_harness(initialized_project)

    assert report.passed is False
    adr_issues = [issue for issue in report.issues if issue.code == "ADR_INDEX_BLOAT"]
    assert len(adr_issues) == 1
    assert adr_issues[0].path == "docs/brain/index.md"


def test_verify_harness_detects_broken_symlinks(initialized_project: Path) -> None:
    """Detecta enlaces simbolicos rotos si el destino de la skill desaparece."""
    skill_target = initialized_project / ".compass/skills/tdd"
    shutil.rmtree(skill_target)

    report = verify_harness(initialized_project)

    assert report.passed is False
    assert ".agents/skills/tdd" in report.broken_symlinks
    symlink_issues = [issue for issue in report.issues if issue.code == "BROKEN_SYMLINK"]
    assert len(symlink_issues) == 1
    assert symlink_issues[0].path == ".agents/skills/tdd"


def test_verify_harness_detects_missing_observed_proof_in_completed_tasks(
    initialized_project: Path,
) -> None:
    """Detecta tareas marcadas [x] que carecen de prueba observada o mantienen *(Pendiente)*."""
    spec_dir = initialized_project / "specs" / "01-demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")

    tasks_content = (
        "# Tasks\n\n"
        "- [x] **Tarea 1: Demo completada sin prueba**\n"
        "  - Detalle previo.\n"
        "  - **Prueba Observada**: *(Pendiente)*\n\n"
        "- [ ] **Tarea 2: Demo pendiente**\n"
        "  - Detalle pendiente.\n"
        "  - **Prueba Observada**: *(Pendiente)*\n"
    )
    (spec_dir / "tasks.md").write_text(tasks_content, encoding="utf-8")

    report = verify_harness(initialized_project)

    assert report.passed is False
    assert len(report.specs_progress) == 1
    progress = report.specs_progress[0]
    assert progress.spec_id == "01-demo"
    assert progress.has_spec_md is True
    assert progress.has_plan_md is True
    assert progress.has_tasks_md is True
    assert progress.total_tasks == 2
    assert progress.completed_tasks == 1
    assert len(progress.tasks_missing_proof) == 1
    assert "Tarea 1" in progress.tasks_missing_proof[0]

    proof_issues = [issue for issue in report.issues if issue.code == "MISSING_OBSERVED_PROOF"]
    assert len(proof_issues) == 1
    assert proof_issues[0].path == "specs/01-demo/tasks.md"


def test_verify_harness_fails_when_completed_task_has_no_observed_proof_keyword(
    initialized_project: Path,
) -> None:
    """Detecta tareas marcadas [x] que no incluyen la seccion de Prueba Observada."""
    spec_dir = initialized_project / "specs" / "01-demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "tasks.md").write_text(
        "# Tasks\n\n- [x] **Tarea 1: Sin seccion de prueba**\n  - Detalle.\n",
        encoding="utf-8",
    )

    report = verify_harness(initialized_project)

    assert report.passed is False
    proof_issues = [issue for issue in report.issues if issue.code == "MISSING_OBSERVED_PROOF"]
    assert len(proof_issues) == 1
    assert len(report.specs_progress[0].tasks_missing_proof) == 1


def test_verify_harness_passes_when_completed_tasks_have_real_observed_proof(
    initialized_project: Path,
) -> None:
    """Supera la comprobacion cuando todas las tareas [x] contienen salida real de prueba observada."""
    spec_dir = initialized_project / "specs" / "01-demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")

    valid_tasks = (
        "# Tasks\n\n"
        "- [x] **Tarea 1: Demo completada con prueba real**\n"
        "  - Detalle previo.\n"
        "  - **Prueba Observada**:\n"
        "    ```bash\n"
        "    pytest tests/test_demo.py\n"
        "    ```\n"
        "    Salida: 1 passed in 0.01s\n\n"
        "- [ ] **Tarea 2: Demo pendiente legitima**\n"
        "  - Detalle.\n"
        "  - **Prueba Observada**: *(Pendiente)*\n"
    )
    (spec_dir / "tasks.md").write_text(valid_tasks, encoding="utf-8")

    report = verify_harness(initialized_project)

    assert report.passed is True
    assert report.issues == ()
    assert len(report.specs_progress) == 1
    progress = report.specs_progress[0]
    assert progress.total_tasks == 2
    assert progress.completed_tasks == 1
    assert progress.tasks_missing_proof == ()


def test_core_reexports_verifier_symbols() -> None:
    """Verifica que compass_harness.core reexporte todos los simbolos publicos del verificador."""
    from compass_harness.core import (
        CheckIssue as CoreCheckIssue,
        HarnessReport as CoreHarnessReport,
        SpecProgress as CoreSpecProgress,
        verify_harness as core_verify_harness,
    )

    assert CoreCheckIssue is CheckIssue
    assert CoreHarnessReport is HarnessReport
    assert CoreSpecProgress is SpecProgress
    assert core_verify_harness is verify_harness


def test_cli_status_command_reports_healthy_and_specs_progress(
    initialized_project: Path,
) -> None:
    """Verifica el subcomando 'compass status' con progreso de specs en modo healthy."""
    spec_dir = initialized_project / "specs" / "01-demo"
    spec_dir.mkdir(parents=True)
    valid_tasks = (
        "# Tasks\n\n"
        "- [x] **Tarea 1: Demo completada**\n"
        "  - Detalle.\n"
        "  - **Prueba Observada**:\n"
        "    Salida: ok\n\n"
        "- [ ] **Tarea 2: Demo pendiente**\n"
        "  - Detalle.\n"
        "  - **Prueba Observada**: *(Pendiente)*\n"
    )
    (spec_dir / "tasks.md").write_text(valid_tasks, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["status", "--path", str(initialized_project)])

    assert result.exit_code == 0
    assert "=== COMPASS_STATUS ===" in result.output
    assert "HEALTHY" in result.output
    assert "01-demo: 1/2 tareas completadas" in result.output


def test_cli_check_command_passes_on_healthy_project(
    initialized_project: Path,
) -> None:
    """Verifica que 'compass check' devuelva codigo 0 cuando no hay incidencias."""
    runner = CliRunner()
    result = runner.invoke(app, ["check", "--path", str(initialized_project)])

    assert result.exit_code == 0
    assert "=== COMPASS_CHECK_PASSED ===" in result.output


def test_cli_check_command_fails_on_broken_project(
    initialized_project: Path,
) -> None:
    """Verifica que 'compass check' devuelva codigo 1 e imprima las incidencias detectadas."""
    handoff_file = initialized_project / "docs/brain/handoff.md"
    handoff_file.write_text("\n".join([f"line {i}" for i in range(35)]) + "\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["check", "--path", str(initialized_project)])

    assert result.exit_code == 1
    assert "=== COMPASS_CHECK_FAILED ===" in result.output
    assert "[BUDGET_EXCEEDED]" in result.output


def test_cli_dogfooding_on_compass_harness_repository() -> None:
    """Verifica que el propio repositorio de compass-harness supere la auditoria al 100%."""
    runner = CliRunner()
    check_result = runner.invoke(app, ["check", "--path", "/home/carlos/compass-harness"])

    assert check_result.exit_code == 0
    assert "=== COMPASS_CHECK_PASSED ===" in check_result.output

    status_result = runner.invoke(app, ["status", "--path", "/home/carlos/compass-harness"])
    assert status_result.exit_code == 0
    assert "=== COMPASS_STATUS ===" in status_result.output
    assert "HEALTHY" in status_result.output


