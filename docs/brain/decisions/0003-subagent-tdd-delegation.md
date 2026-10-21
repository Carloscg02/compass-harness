# 0003. Delegación en Subagentes y Flexibilidad de Modelos

- **Estado**: accepted
- **Fecha**: 2026-10-18

## Contexto y Problema
Queremos máxima autonomía (no tener que cambiar manualmente de modelo a mitad de una feature), aprovechar modelos rápidos (como Flash) para el bucle mecánico de TDD, permitir que un usuario con plan ilimitado use siempre su modelo por defecto (`inherit`), y permitir que si se agota la cuota de modelos pesados se pueda hacer el ciclo entero con un modelo rápido sin reconfigurar el proyecto.

## Decisión
Separar el trabajo en dos roles:
1. **Agente Principal (Hilo de chat activo)**: Ejecuta siempre las fases de diálogo, diseño (`spec.md`, `plan.md`, `tasks.md`), revisión y mentoría (`GUIDE.md`) usando el modelo que el usuario tenga activo en su ventana.
2. **Subagente Constructor (Ventana de contexto aislada)**: Al aprobarse `tasks.md`, el Agente Principal lanza un subagente para ejecutar el bucle TDD (`RED -> GREEN -> REFACTOR`) con el tier configurado (`flash` o `inherit`), manteniendo el chat principal limpio de trazas de consola.
