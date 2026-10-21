"""Tests para el inspector determinista de proyectos (Project Inspector)."""

from pathlib import Path
import pytest

from compass_harness.core.inspector import (
    ProjectInspection,
    ProjectState,
    inspect_project,
)


def test_inspect_empty_and_boilerplate_dir_is_greenfield(tmp_path: Path) -> None:
    """Verifica la deteccion de proyectos GREENFIELD en carpetas vacias o con boilerplate basico (CA-1)."""
    # Caso 1: Directorio completamente vacio
    empty_dir = tmp_path / "empty_proj"
    empty_dir.mkdir()

    result_empty = inspect_project(empty_dir)
    assert result_empty.root_path == empty_dir.resolve()
    assert result_empty.state == ProjectState.GREENFIELD
    assert result_empty.detected_stacks == ()
    assert result_empty.existing_dirs == ()
    assert result_empty.has_git is False
    assert result_empty.existing_harness_files == ()

    # Caso 2: Directorio con Git, README, .gitignore, LICENSE y .venv (con archivos internos ignorados)
    bp_dir = tmp_path / "bp_proj"
    bp_dir.mkdir()
    (bp_dir / ".git").mkdir()
    (bp_dir / "README.md").write_text("# Demo Project\n", encoding="utf-8")
    (bp_dir / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    (bp_dir / "LICENSE").write_text("MIT", encoding="utf-8")
    venv_lib = bp_dir / ".venv" / "lib"
    venv_lib.mkdir(parents=True)
    (venv_lib / "site.py").write_text("# virtualenv python file", encoding="utf-8")

    result_bp = inspect_project(bp_dir)
    assert result_bp.root_path == bp_dir.resolve()
    assert result_bp.state == ProjectState.GREENFIELD
    assert result_bp.detected_stacks == ()
    assert result_bp.existing_dirs == ()
    assert result_bp.has_git is True
    assert result_bp.existing_harness_files == ()


def test_inspect_raises_on_invalid_paths(tmp_path: Path) -> None:
    """Verifica que se lancen excepciones adecuadas ante rutas inexistentes o no directorios (CA-5)."""
    # Caso 1: Ruta inexistente debe lanzar FileNotFoundError
    non_existent = tmp_path / "not_found_dir"
    with pytest.raises(FileNotFoundError):
        inspect_project(non_existent)

    # Caso 2: Ruta a un archivo debe lanzar NotADirectoryError
    regular_file = tmp_path / "regular_file.txt"
    regular_file.write_text("content", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        inspect_project(regular_file)


def test_inspect_detects_manifest_as_brownfield(tmp_path: Path) -> None:
    """Verifica que la presencia de manifiestos clasifique como BROWNFIELD y detecte el stack (CA-2)."""
    # Proyecto Python con pyproject.toml
    py_proj = tmp_path / "py_project"
    py_proj.mkdir()
    (py_proj / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")

    result_py = inspect_project(py_proj)
    assert result_py.state == ProjectState.BROWNFIELD
    assert result_py.detected_stacks == ("python",)

    # Proyecto Node con package.json
    node_proj = tmp_path / "node_project"
    node_proj.mkdir()
    (node_proj / "package.json").write_text('{"name": "demo"}\n', encoding="utf-8")

    result_node = inspect_project(node_proj)
    assert result_node.state == ProjectState.BROWNFIELD
    assert result_node.detected_stacks == ("node",)


def test_inspect_detects_source_files_and_existing_dirs_without_manifest(tmp_path: Path) -> None:
    """Verifica la deteccion de stacks por extensiones y carpetas existentes sin manifiesto (CA-3)."""
    rf_proj = tmp_path / "rf_project"
    rf_proj.mkdir()
    (rf_proj / "src").mkdir()
    (rf_proj / "src" / "simulador_rf.py").write_text("def simular(): pass\n", encoding="utf-8")
    (rf_proj / "tests").mkdir()

    result_rf = inspect_project(rf_proj)
    assert result_rf.state == ProjectState.BROWNFIELD
    assert result_rf.detected_stacks == ("python",)
    assert result_rf.existing_dirs == ("src", "tests")


def test_inspect_detects_existing_harness_files(tmp_path: Path) -> None:
    """Verifica la deteccion de artefactos de harness preexistentes (CA-4)."""
    harness_proj = tmp_path / "harness_project"
    harness_proj.mkdir()
    (harness_proj / "AGENTS.md").write_text("# Agents configuration\n", encoding="utf-8")
    (harness_proj / "agents.md").write_text("# Legacy agents\n", encoding="utf-8")
    (harness_proj / ".agents").mkdir()
    (harness_proj / ".compass").mkdir()
    (harness_proj / "docs" / "brain").mkdir(parents=True)
    (harness_proj / "backend").mkdir()
    (harness_proj / "frontend").mkdir()

    result = inspect_project(harness_proj)
    assert result.existing_harness_files == ("AGENTS.md", "agents.md", ".compass", ".agents", "docs/brain")
    assert "backend" in result.existing_dirs
    assert "frontend" in result.existing_dirs


def test_core_module_exports() -> None:
    """Verifica que el paquete compass_harness.core exporte los simbolos publicos del inspector."""
    import compass_harness.core as core

    assert hasattr(core, "ProjectState")
    assert hasattr(core, "ProjectInspection")
    assert hasattr(core, "inspect_project")
    assert core.ProjectState is ProjectState
    assert core.ProjectInspection is ProjectInspection
    assert core.inspect_project is inspect_project



