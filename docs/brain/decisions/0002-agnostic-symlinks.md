# 0002. Diseño de Meta-Harness Agnóstico mediante Symlinks

- **Estado**: accepted
- **Fecha**: 2026-10-18

## Contexto y Problema
Queremos que `compass` funcione en Antigravity, Claude Code, Codex o Cursor sin depender de un asistente único ni duplicar archivos.

## Decisión
Al ejecutar `compass init` en cualquier proyecto, `compass` instalará una fuente única de verdad en `.compass/skills/` y `docs/brain/`, generará un `AGENTS.md` ligero como Router en la raíz y creará enlaces simbólicos (*symlinks*) hacia las carpetas específicas de los asistentes elegidos (ej. `.agents/skills/` para Antigravity, `.claude/skills/` para Claude Code).

## Consecuencias
Cero duplicación de archivos, ahorro de tokens por *Progressive Disclosure* y compatibilidad multi-herramienta.
