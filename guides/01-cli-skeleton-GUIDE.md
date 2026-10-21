# Guía de Mentoría #01: Disección del Esqueleto CLI y TDD con `CliRunner` (`01-cli-skeleton`)

> **Modo Mentor (`compass`)** · **Nivel**: Fundamentos de Ingeniería de Software y Testing en Python  
> **Objetivo**: Entender línea por línea el código real que se acaba de escribir en `pyproject.toml`, `src/compass_harness/cli.py` y `tests/test_cli_skeleton.py`, y por qué funciona el flujo TDD con subagentes.

---

## 1. Qué acabamos de lograr a nivel de Arquitectura Agéntica

Acabas de ver en acción el patrón **Maker-Checker (Arquitecto + Subagente Constructor)** que diseñamos:
1. En el hilo principal definimos el contrato (`spec.md`, `plan.md`, `tasks.md`).
2. El subagente en modo `flash` ejecutó en una sesión aislada la instalación del entorno virtual `.venv`, el ciclo `RED -> GREEN -> REFACTOR` y las pruebas de consola, sin ensuciar nuestra conversación con decenas de líneas de logs de `pip` y `pytest`.
3. La evidencia quedó grabada en [`specs/01-cli-skeleton/tasks.md`](../specs/01-cli-skeleton/tasks.md).

Ahora vamos a destripar las tres piezas técnicas nuevas que existen en tu repositorio.

---

## 2. Disección de [`src/compass_harness/cli.py`](../src/compass_harness/cli.py)

En este archivo hay tres conceptos de `Typer` que todo desarrollador de Python debe conocer cuando construye una herramienta de consola:

### A. `no_args_is_help=True`
```python
app = typer.Typer(
    name="compass",
    help="Compass: Meta-Harness agnostico y educativo para desarrollo con agentes.",
    no_args_is_help=True,
)
```
* **Qué hace**: Si un usuario escribe simplemente `compass` en la terminal sin ningún subcomando ni bandera, en lugar de dar un error feo o quedarse en blanco, `Typer` muestra automáticamente la pantalla de ayuda (`--help`).

### B. ¿Qué diferencia hay entre `@app.command()` y `@app.callback()`?
En `cli.py` verás que la función `main` tiene el decorador `@app.callback()`:
```python
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Muestra la version de compass-harness y termina.",
    ),
) -> None:
```
* **`@app.command()`**: Se usa para definir **subcomandos** (como `compass init` o `compass check`).
* **`@app.callback()`**: Se ejecuta en **el nivel raíz** del programa (antes de cualquier subcomando). Es el lugar donde se colocan las opciones globales que aplican a toda la herramienta, como `--version` o `--verbose`.

### C. El patrón `callback=version_callback` + `is_eager=True`
¿Por qué `version` tiene `is_eager=True` y llama a la función `version_callback`?
```python
def version_callback(value: bool) -> None:
    if value:
        console.print(f"compass-harness v{__version__}")
        raise typer.Exit(code=0)
```
* En una CLI, si el usuario escribe `compass --version`, no quiere que el programa valide otros argumentos obligatorios ni ejecute nada más: quiere ver la versión e irse inmediatamente.
* **`is_eager=True`** ("ansioso/prioritario") le dice a `Typer`: *"Procesa esta bandera antes que cualquier otra cosa"*.
* **`raise typer.Exit(code=0)`**: Es la forma limpia en `Typer` de terminar el programa devolviendo al sistema operativo Linux el código `0` (en Linux/Unix, el código de salida `0` significa "ejecución exitosa sin errores", mientras que cualquier número distinto de `0` indica error).

---

## 3. Disección de los Tests en [`tests/test_cli_skeleton.py`](../tests/test_cli_skeleton.py)

Mira cómo probamos la interfaz de consola sin tener que abrir una terminal real a mano cada vez:

```python
from typer.testing import CliRunner

runner = CliRunner()

def test_cli_version_flag() -> None:
    from compass_harness.cli import app

    result_long = runner.invoke(app, ["--version"])
    assert result_long.exit_code == 0
    assert "compass-harness v0.1.0" in result_long.stdout
```

### ¿Cómo funciona `CliRunner` por dentro?
1. `runner.invoke(app, ["--version"])` simula en memoria que un usuario ejecutó `compass --version`.
2. Captura dos cosas fundamentales en el objeto `result_long`:
   * **`exit_code`**: El código de retorno del proceso (comprobamos que sea `0`).
   * **`stdout`** (*Standard Output*): Todo el texto que el programa imprimió por pantalla (comprobamos que contenga `"compass-harness v0.1.0"`).
3. Gracias a esto, ejecutar los 3 tests tarda apenas **0.12 segundos**, pero nos garantiza matemáticamente que el contrato del CLI se cumple.

---

## 4. Cómo probarlo tú mismo en tu terminal WSL

El entorno virtual de tu proyecto ya está creado en `/home/carlos/compass-harness/.venv` con el paquete instalado en modo editable. Si abres una terminal dentro de `/home/carlos/compass-harness`, puedes activar el entorno y usar tu comando:

```bash
source .venv/bin/activate
compass --version
compass --help
pytest
```
*(O si quieres que `compass` esté disponible globalmente en cualquier terminal de tu usuario sin activar el `.venv`, basta con crear un enlace simbólico en `~/.local/bin/compass` apuntando a `/home/carlos/compass-harness/.venv/bin/compass`).*
