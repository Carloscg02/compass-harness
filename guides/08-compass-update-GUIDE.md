# Guía de Ingeniería (Paso 8): Sincronización Determinista de Arneses, Segregación Stateless/Stateful y Preservación de Memoria Viva

Esta guía didáctica explica las decisiones de arquitectura e ingeniería aplicadas en la implementación de `compass update` dentro de [`updater.py`](../src/compass_harness/core/updater.py) y [`cli.py`](../src/compass_harness/cli.py).

---

## 1. Lente de Ingeniería de Software: Segregación Stateless vs. Stateful en Herramientas de Desarrollo

### 1.1. El problema del *In-Place Upgrade* en herramientas de infraestructura
Cuando una herramienta de software crea una estructura inicial en un proyecto del usuario (como `create-react-app`, `cargo init` o `compass init`), se enfrenta a un dilema clásico en versiones posteriores: **¿cómo actualizar la infraestructura sin destruir el trabajo del usuario?**

Si la herramienta trata todos los archivos por igual:
- Si sobreescribe con `--force`, destruye el código o la memoria personalizada.
- Si no sobreescribe nada, el proyecto queda desfasado e incapaz de aprovechar correcciones de seguridad, nuevas skills o mejoras metodológicas.

### 1.2. El Patrón de Segregación de Estado
En [`updater.py`](../src/compass_harness/core/updater.py) resolvemos este problema mediante una clasificación estricta de los activos del repositorio:

```mermaid
flowchart TD
    subgraph Repo["Repositorio del Proyecto"]
        subgraph Stateless["Activos de Infraestructura (Stateless)"]
            S1[".compass/skills/* (tdd, sdd-workflow, etc.)"]
            S2["AGENTS.md (Router y Constitución)"]
            S3["Symlinks (.agents/skills, .claude/skills)"]
        end
        subgraph Stateful["Memoria Viva del Usuario (Stateful - INMUTABLE)"]
            M1["docs/brain/modules/*.md"]
            M2["docs/brain/handoff.md"]
            M3["docs/brain/decisions/*.md"]
            M4["docs/brain/architecture.md & design.md"]
            M5["specs/* y guides/*"]
        end
    end

    CLI["compass update --apply"] -->|Sobreescribe y regenera| Stateless
    CLI -.->|PROHIBIDO TOCAR (Garantía de Inmutabilidad)| Stateful
```

1. **Activos Stateless (Actualizables)**: Son plantillas puras parametrizadas por la configuración del proyecto. Al ejecutar `compass update`, se regeneran con la última versión del paquete manteniendo los comandos propios del proyecto (`{config.test_command}`).
2. **Activos Stateful (Inmutables)**: Contienen la memoria viva, el contexto acumulado y las decisiones irreversibles del usuario. El código de `apply_update` itera **únicamente** sobre la lista `files_to_update`, garantizando que la memoria de negocio jamás sea alterada.

---

## 2. Lente de Ingeniería de Arneses: Por qué la Sincronización no debe dejarse al LLM

### 2.1. El Atajo del "Vibe Update"
Pedirle a un agente de IA *"actualiza el arnés de este proyecto mirando el último commit del repositorio de Compass"* introduce riesgos severos:
1. **Pérdida de Configuración**: El modelo tiende a copiar el texto literal del template, pudiendo inyectar comandos de Python (`pytest`) en un proyecto de Go o TypeScript.
2. **Contaminación de Memoria**: El agente puede mezclar las notas de handoff o módulos de un proyecto con el del arnés maestro.
3. **Consumo de Tokens y Latencia**: Analizar árboles remotos de Git, parsear diffs y aplicar parches manuales con herramientas de edición consume miles de tokens y múltiples llamadas de ida y vuelta.

### 2.2. Determinismo en un solo comando: `compass update`
Al encapsular la sincronización en una función pura de Python:
- La extracción de configuración es instantánea y resistente a fallos (lee `.compass/config.json` o recurre a expresiones regulares tolerantes en `docs/brain/index.md` y `architecture.md`).
- La aplicación es atómica y reporta exactamente qué archivos se modificaron y cuáles quedaron protegidos.
- Se ejecuta automáticamente `verify_harness` al finalizar, certificando que el arnés queda 100% sano y listo para el siguiente turno de desarrollo.
