"""Plantillas del Router (AGENTS.md) y del Cerebro (docs/brain/...)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compass_harness.core.renderer import ProjectConfig


def render_agents_md(config: "ProjectConfig") -> str:
    """Genera AGENTS.md garantizando menos de 100 lineas y enrutamiento agnostico."""
    if config.model_strategy == "subagent-fast":
        strategy_desc = (
            "Delegacion en Subagentes Ligeros (`subagent-fast`) - Triada de roles:\n"
            "  1. Main Agent (Orquestador / Arquitecto / Mentor): Contexto principal y coordinacion.\n"
            "  2. Builder Subagent (Constructor TDD): Modelo rapido (`flash` / fast tier) para el ciclo RED-GREEN-REFACTOR.\n"
            "  3. Auditor Subagent (Auditor Adversarial): Modelo rapido (`flash`) con contexto limpio para la puerta de auditoria."
        )
    elif config.model_strategy == "subagent-inherit":
        strategy_desc = (
            "Delegacion en Subagentes (`subagent-inherit`): Delega tareas de construccion (Builder) "
            "y auditoria (Auditor) en subagentes con modelo heredado (`inherit`)."
        )
    else:
        strategy_desc = (
            "Agente Monolitico (`single`): Ejecucion directa en un unico agente sin "
            "delegacion en subagentes."
        )

    return f"""# AGENTS.md - Router y Politicas de Agente para `{config.project_name}`

> Enrutador principal de contexto. Lee este archivo al inicio de cada sesion.

---

## 1. Memoria Central del Proyecto
- Consulta siempre [`docs/brain/index.md`](docs/brain/index.md) para el mapa de arquitectura y estado vivo.
- Consulta [`docs/brain/handoff.md`](docs/brain/handoff.md) para retomar el trabajo donde se quedo.

---

## 2. Decisor de Carriles de Ejecucion
- Carril 1: `ANSWER` - Preguntas de orientacion, explicaciones y diseno conceptual sin edicion de ficheros.
- Carril 2: `FTD` (Fix-The-Docs) - Correcciones directas en documentacion, arquitectura o handoff sin codigo de produccion.
- Carril 3: `SDD` (Spec-Driven Development) - Flujo formal en 6 pasos: `spec.md` -> `plan.md` -> `tasks.md` -> `TDD Implementation` (Builder) -> `Independent Audit Gate` (Auditor) -> `Brain Consolidation & Guide` (Main).

---

## 3. Estrategia de Modelos y Delegacion
- {strategy_desc}

---

## 4. Catalogo de Skills Instaladas
- [project-architect](.compass/skills/project-architect/SKILL.md): Negociacion de arquitectura y diagnostico de proyecto.
- [sdd-workflow](.compass/skills/sdd-workflow/SKILL.md): Flujo formal de especificacion, Seams y verificacion proporcional.
- [tdd](.compass/skills/tdd/SKILL.md): Ciclo estricto red-green-refactor y testing en seams publicos.
- [mentor-guide](.compass/skills/mentor-guide/SKILL.md): Generacion de guias educativas bajo demanda.
- [ui-design](.compass/skills/ui-design/SKILL.md): Gobernanza de diseno UI/Frontend, entrevista guiada y reglas Anti-Slop.

---

## 5. UI / Frontend Gate (Just-In-Time Design & Agent Eyes)
- Cuando una tarea (`FTD` o `SDD`) vaya a crear o modificar interfaz visual (HTML, CSS, Tailwind, React, Vue, Svelte), detenerse antes de escribir codigo: abrir `.compass/skills/ui-design/SKILL.md`, verificar o consensuar `docs/brain/design.md` y asegurar que el agente tiene configurada la verificacion semantica de DOM / navegador (`Agent Eyes`, cambiando `e2e_command` en `docs/brain/architecture.md` si sigue en `N/A`).
"""


def render_brain_index_md(config: "ProjectConfig") -> str:
    """Genera docs/brain/index.md con identificacion del proyecto y enlace O(1) a ADRs."""
    return f"""# Cerebro del Proyecto: `{config.project_name}`

> Mapa central de contexto del proyecto (Nivel 1). Consulta los documentos de Nivel 2 segun necesidad.

---

## 1. Identidad del Proyecto
- **Nombre**: `{config.project_name}`
- **Objetivo**: {config.project_goal}
- **Stack Tecnologico**: `{config.tech_stack}`
- **Dominio**: {config.domain}

---

## 2. Documentos Centrales (Nivel 2)
- **[`architecture.md`](architecture.md)** - Diseno de capas, reglas de codigo y comandos de verificacion.
- **[`handoff.md`](handoff.md)** - Estado del turno actual y siguiente paso inmediato (maximo 30 lineas).
- **[`decisions/index.md`](decisions/index.md)** - Sub-indice de decisiones tecnicas irreversibles (ADRs). Consultar solo ante decisiones arquitectonicas.

---

## 3. Modulos del Sistema (`modules/`)
Registro de fichas tecnicas de cada modulo implementado en el proyecto.
"""


def render_architecture_md(config: "ProjectConfig") -> str:
    """Genera docs/brain/architecture.md segun el estilo y comandos de verificacion."""
    style_key = config.architecture_style.lower()
    if style_key == "hexagonal":
        arch_details = (
            "Arquitectura Hexagonal (Puertos y Adaptadores):\n"
            "- Dominio puro en el nucleo sin dependencias de I/O o librerias de infraestructura.\n"
            "- Puertos (interfaces y seams publicos) para conectar logica de negocio y el mundo exterior.\n"
            "- Adaptadores de entrada (CLI, API) y salida (persistencia, clientes externos)."
        )
    elif style_key == "layered":
        arch_details = (
            "Arquitectura en Capas (Layered Architecture):\n"
            "- Capa de Presentacion / Entrada.\n"
            "- Capa de Logica de Negocio / Dominio.\n"
            "- Capa de Acceso a Datos e Infraestructura."
        )
    elif style_key == "mvc":
        arch_details = (
            "Arquitectura MVC (Modelo-Vista-Controlador):\n"
            "- Modelos: Estructuras y logica de datos.\n"
            "- Vistas: Formato de representacion y respuesta.\n"
            "- Controladores: Coordinacion de entradas y flujo de aplicacion."
        )
    else:
        arch_details = (
            "Arquitectura Script / Modular Ligera:\n"
            "- Funciones modulares con responsabilidad unica y ejecucion determinista.\n"
            "- Enfoque directo sin sobreingenieria ni capas innecesarias."
        )

    return f"""# Arquitectura de `{config.project_name}`

## 1. Estilo Arquitectonico
{arch_details}

---

## 2. Verification Commands
Comandos oficiales de verificacion ejecutados por el subagente constructor en cada ciclo:

- **Unit & Integration Tests (In-Loop TDD)**: `{config.test_command}`
  Ejecutado en cada iteracion red-green-refactor sobre los seams publicos.
- **Static / Lint Gate**: `{config.lint_command}`
  Ejecutado como barrera de calidad estatica y tipado.
- **E2E / Browser UI Tests (Optional)**: `{config.e2e_command}`
  Ejecutado al completar features que toquen interfaz de usuario o flujos end-to-end completos.
"""


def render_handoff_md(config: "ProjectConfig") -> str:
    """Genera docs/brain/handoff.md garantizando menos de 30 lineas."""
    return f"""# Handoff del Proyecto: `{config.project_name}`

- **Estado Actual**: Proyecto inicializado con Compass Harness.
- **Ultima Tarea**: Estructuracion de cerebro, router y catalogo de skills.
- **Siguiente Paso**: Especificar el primer requerimiento en `specs/` usando el flujo SDD.
- **Bloqueos Activos**: Ninguno.
"""


def render_decisions_index_md(config: "ProjectConfig") -> str:
    """Genera docs/brain/decisions/index.md."""
    return f"""# Indice de Decisiones de Arquitectura (ADRs) - `{config.project_name}`

Registro de decisiones tecnicas irreversibles del proyecto.

| ADR | Titulo | Estado | Fecha |
|---|---|---|---|
| [0001](0001-initial-architecture.md) | Eleccion de arquitectura inicial ({config.architecture_style}) | Aceptado | Inicial |
"""


def render_initial_adr_md(config: "ProjectConfig") -> str:
    """Genera docs/brain/decisions/0001-initial-architecture.md."""
    return f"""# ADR 0001: Eleccion de arquitectura inicial

- **Estado**: Aceptado
- **Fecha**: Inicial
- **Estilo Acordado**: `{config.architecture_style}`

## 1. Contexto
Al inicializar `{config.project_name}` con el objetivo de `{config.project_goal}`, se requiere establecer las fronteras arquitectonicas base.

## 2. Decision
Se adopta el estilo `{config.architecture_style}` para estructurar el codigo y los seams de prueba.

## 3. Consecuencias
Todo nuevo componente o feature desarrollada en el proyecto debe respetar las directrices registradas en `docs/brain/architecture.md`.
"""
