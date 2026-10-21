# Especificación (Spec): `01-cli-skeleton`

- **ID de Feature**: `01-cli-skeleton`
- **Estado**: Aprobado
- **Objetivo**: Configurar el paquete Python instalable (`compass-harness`), su estructura base con layout `src/`, y el punto de entrada del ejecutable CLI (`compass`) capaz de informar su versión y mostrar la ayuda general, verificado mediante `pytest`.

---

## 1. Alcance Funcional (Qué vamos a construir)

1. **Empaquetado estándar (`pyproject.toml`)**:
   - Definir los metadatos del paquete `compass-harness` (versión inicial `0.1.0`, requerimiento de Python `>=3.10`).
   - Declarar las dependencias de ejecución (`typer`, `rich`) y de desarrollo (`pytest`).
   - Configurar el *entry point* de consola para que el comando `compass` invoque a `compass_harness.cli:app`.
   - Configurar el sistema de construcción para utilizar el directorio `src/compass_harness/`.

2. **Módulo Base y Versión (`src/compass_harness/__init__.py`)**:
   - Exponer la constante `__version__ = "0.1.0"` como fuente única de verdad para la versión del paquete.

3. **Interfaz CLI Inicial (`src/compass_harness/cli.py`)**:
   - Crear la aplicación principal `Typer` (`app`) con descripción clara del propósito de `compass`.
   - Soportar la opción global `--version` / `-v` que imprima `compass-harness v0.1.0` y termine con código de salida `0`.
   - Soportar `--help` mostrando la descripción de la herramienta sin errores.

---

## 2. Fuera de Alcance (Qué NO entra en este paso)

- Inspección de archivos del proyecto (`02-project-inspector`).
- Plantillas y Skills (`03-templates-and-skills`).
- Comandos `compass init`, `compass status` o `compass check` completos (se añadirán en los Pasos 4 y 5).

---

## 3. Criterios de Aceptación (Requisitos para TDD)

Cada criterio se convertirá en un test automatizado en `tests/test_cli_skeleton.py`:

- **CA-1 (Versión del paquete)**: Al importar `compass_harness`, el atributo `__version__` debe existir y ser igual a `"0.1.0"`.
- **CA-2 (Flag `--version` y `-v` en CLI)**: Al ejecutar `compass --version` o `compass -v` mediante `CliRunner`, el código de salida debe ser `0` y la salida estándar debe contener `"compass-harness v0.1.0"`.
- **CA-3 (Ayuda `--help` en CLI)**: Al ejecutar `compass --help`, el código de salida debe ser `0` y la salida debe mostrar la descripción del meta-harness.
- **CA-4 (Ejecución real en consola)**: Tras instalar el paquete en modo editable en el entorno virtual del proyecto, ejecutar `compass --version` en la terminal devuelve `compass-harness v0.1.0`.
