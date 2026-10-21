# 0005. Estructura del Cerebro en Niveles y Sub-Índice Aislado para ADRs

- **Estado**: accepted
- **Fecha**: 2026-10-19

## Contexto y Problema
En proyectos de larga duración (meses o años), un archivo único `decisions.md` o un `handoff.md` acumulativo crecerían indefinidamente, disparando el consumo de tokens al iniciar cada sesión.

## Decisión
Adoptar la jerarquía de memoria inspirada en `rsc-harness`:
1. **`docs/brain/index.md` (Lectura obligatoria en cada turno)**: Contiene solo enlaces cortos. La sección de decisiones ocupa **1 única línea** apuntando a `docs/brain/decisions/index.md`.
2. **`docs/brain/handoff.md` (Tamaño fijo, máx. 30 líneas)**: Se sobrescribe en cada turno con el estado presente; nunca acumula historial antiguo.
3. **`docs/brain/architecture.md` (Tamaño fijo, ~60-80 líneas)**: Contiene las reglas arquitectónicas vigentes (capas, estilo Hexagonal/DDD o el acordado) y se lee siempre al diseñar o modificar código (`FTD` / `SDD`).
4. **`docs/brain/decisions/index.md` + `NNNN-titulo.md` (Consulta bajo demanda)**: Cada ADR vive en un archivo individual numerado y se lista en `decisions/index.md`. No se leen en el flujo normal de tareas; solo se abren cuando una skill detecta una decisión irreversible nueva o un conflicto con una decisión existente.
