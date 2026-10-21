# Módulo: `cli-skeleton`

- **Feature origen**: [`specs/01-cli-skeleton/`](../../../specs/01-cli-skeleton/spec.md)
- **Archivos principales**:
  - [`pyproject.toml`](../../../pyproject.toml): Define el paquete `compass-harness` (`0.1.0`) y el entry point `compass = "compass_harness.cli:app"`.
  - [`src/compass_harness/__init__.py`](../../../src/compass_harness/__init__.py): Expone `__version__: str = "0.1.0"`.
  - [`src/compass_harness/cli.py`](../../../src/compass_harness/cli.py): Define `app = typer.Typer(name="compass", no_args_is_help=True)`, `console = Console()`, `version_callback(value: bool)` y `@app.callback() def main(...)`.
- **Tests**: [`tests/test_cli_skeleton.py`](../../../tests/test_cli_skeleton.py) (`test_package_version`, `test_cli_version_flag`, `test_cli_help_flag`).
- **Puntos de extensión**: Nuevos subcomandos (`init`, `status`, `check`) deben registrarse sobre `app` en `src/compass_harness/cli.py` delegando su lógica pura a módulos dentro de `src/compass_harness/core/`.
