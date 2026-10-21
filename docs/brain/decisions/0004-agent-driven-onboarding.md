# 0004. Onboarding Conducido por el Agente y Soporte Greenfield/Brownfield

- **Estado**: accepted
- **Fecha**: 2026-10-18

## Contexto y Problema
El usuario no debe tener que teclear largos comandos con banderas manuales en la terminal para configurar un proyecto. La experiencia principal debe ser pedirle al agente en el chat: *"Instala compass en este proyecto"*, tanto en proyectos desde cero (*Greenfield*) como en proyectos ya empezados (*Brownfield*).

## Decisión
Protocolo en 3 pasos (Agente + CLI):
1. **Paso 1 — Inspección (`compass init` sin argumentos)**: El CLI inspecciona la raíz del directorio sin escribir nada, detecta si el proyecto es nuevo (*Greenfield*) o existente (*Brownfield*) y devuelve `COMPASS_ONBOARDING_REQUIRED` indicando al agente qué preguntas y qué análisis arquitectónico debe conversar con el usuario en el chat.
2. **Paso 2 — Conversación y Vista Previa (`--preview`)**: El agente debate en lenguaje natural con el usuario y ejecuta el CLI en modo vista previa (`COMPASS_ONBOARDING_PLAN`) mostrando qué archivos y enlaces simbólicos se van a crear.
3. **Paso 3 — Aplicación (`--apply`)**: Tras el visto bueno del usuario, el agente aplica la instalación y completa el Cerebro inicial.
