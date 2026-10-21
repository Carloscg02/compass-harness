"""Tests para el esqueleto CLI y version del paquete compass-harness."""

from typer.testing import CliRunner

runner = CliRunner()


def test_package_version() -> None:
    """Verifica que el paquete exponga la version esperada 0.1.0 (CA-1)."""
    import compass_harness

    assert hasattr(compass_harness, "__version__")
    assert compass_harness.__version__ == "0.1.0"


def test_cli_version_flag() -> None:
    """Verifica que las opciones --version y -v retornen la version del paquete (CA-2)."""
    from compass_harness.cli import app

    result_long = runner.invoke(app, ["--version"])
    assert result_long.exit_code == 0
    assert "compass-harness v0.1.0" in result_long.stdout

    result_short = runner.invoke(app, ["-v"])
    assert result_short.exit_code == 0
    assert "compass-harness v0.1.0" in result_short.stdout


def test_cli_help_flag() -> None:
    """Verifica que la opcion --help muestre la ayuda y descripcion general (CA-3)."""
    from compass_harness.cli import app

    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Meta-Harness" in result.stdout
