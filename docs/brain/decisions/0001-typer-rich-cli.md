# 0001. Elección de `Typer` + `Rich` frente a `argparse` para la CLI

- **Estado**: accepted
- **Fecha**: 2026-10-18

## Contexto y Problema
Necesitamos construir el ejecutable de consola `compass` en Python. Existían dos opciones: usar `argparse` (librería estándar) o `Typer` + `Rich` (estándar moderno en la comunidad Python).

## Decisión
Elegimos `Typer` + `Rich`.

## Consecuencias y Razonamiento
1. **Aprendizaje de Python Moderno**: `Typer` utiliza *Type Hints* nativos (`str`, `Path`, `bool`) para generar argumentos y ayuda `--help`, compartiendo filosofía con `FastAPI`.
2. **Legibilidad**: Un subcomando es una función estándar decorada con `@app.command()`.
3. **Testing integrado**: `CliRunner` permite probar ejecuciones de consola en memoria con `pytest` en milisegundos.
