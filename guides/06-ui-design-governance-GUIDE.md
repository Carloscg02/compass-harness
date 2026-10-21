# Guía de Ingeniería (Paso 6): Gobernanza de UI/Frontend para Desarrolladores Backend, Activación Perezosa (Just-In-Time) y Prevención de AI Slop

Esta guía explica cómo hemos estructurado el módulo **`06-ui-design-governance`** en `compass-harness` para que cualquier desarrollador con perfil backend o de sistemas pueda dirigir a un agente de IA hacia interfaces con personalidad de estudio, sin caer en *AI Slop* ni inflar el contexto en proyectos sin UI.

---

## 1. El Problema Técnico: Por qué los LLMs generan "AI Slop" y "Zombie UI"

Desde el punto de vista de la teoría de la información y el entrenamiento de modelos de lenguaje:
- Un LLM predice el siguiente token maximizando la verosimilitud sobre millones de repositorios públicos (tutoriales de Tailwind, plantillas de Bootstrap, dashboards de demostración).
- Si le pides *"Hazme un dashboard para mi API"*, el modelo cae en el **atractor estadístico medio**:
  1. **Cliché cromático**: Gradientes morados/índigo (`from-indigo-500 to-purple-600`) sobre blanco puro `#FFFFFF` o gris azulado `#0f172a`.
  2. **Cliché estructural**: Cabecera centrada con dos botones y debajo una fila de 3 tarjetas simétricas con un icono dentro de un círculo coloreado.
  3. **Dispersión de tokens (*Magic Values*)**: En lugar de definir variables semánticas (`--surface`, `--text-muted`), el modelo escribe `#3b82f6` en un componente, `#2563eb` en otro y `p-[13px]` en un tercero, haciendo imposible mantener la interfaz.
  4. **Zombie UI (Solo el Happy Path)**: El componente renderiza una tabla con datos falsos estáticos, pero carece de los otros tres estados del ciclo de vida de los datos: **`Loading`**, **`Empty`** y **`Error`**.

---

## 2. Arquitectura "Just-In-Time" (Lazy Contract) para evitar Context Rot

Un error de sobreingeniería habría sido obligar a todos los proyectos a tener un archivo `docs/brain/design.md` desde el minuto cero en `compass init`. Si estás programando un motor DSP en Python o un servicio gRPC en Go, tener un archivo de diseño visual en el Cerebro ensucia el repositorio.

En su lugar, hemos aplicado el patrón **Lazy Initialization + Gate**:
1. En `AGENTS.md` (Nivel 1), el **UI / Frontend Gate** ocupa exactamente **2 líneas**. Mientras trabajes en backend, el agente gasta **0 tokens** en reglas de diseño.
2. En el instante en que pides la primera pantalla o componente visual:
   - El Gate intercepta al agente antes de escribir código y le obliga a leer `.compass/skills/ui-design/SKILL.md`.
   - Si el proyecto ya tenía UI (*Brownfield*), extrae los tokens existentes a `docs/brain/design.md`.
   - Si empieza desde cero (*Greenfield*), te hace la entrevista de 3 preguntas, te ofrece consultar **`https://ancient-prompt-design-flow.base44.app/`** o elegir uno de los 4 arquetipos (`precision-dark/light`, `warm-editorial`, `telemetry-grid`, `neo-brutalist-craft`), y crea `docs/brain/design.md`.
3. A partir de ese momento, `compass status` detecta automáticamente `Contrato UI (design.md): Activo` y `compass check` audita en cada ejecución que `docs/brain/design.md` no supere las **80 líneas** y mantenga sus secciones de **Design Tokens** y **Typography**.

---

## 3. Las 4 Reglas de Oro que un Backend Dev debe exigir en `design.md`

Incluso sin saber diseño gráfico, estas 4 reglas objetivas y verificables en código transforman cualquier interfaz:

| Regla | Qué prohíbe (AI Slop) | Qué exige (Ingeniería de UI) |
| :--- | :--- | :--- |
| **1. Tokens Semánticos** | Colores hexadecimales sueltos (`#3b82f6`) en el HTML/JSX. | Variables por función: `surface`, `surface-elevated`, `text-primary`, `text-muted`, `border-subtle`, `accent-primary`. |
| **2. Pareja Tipográfica + `tabular-nums`** | Usar una sola fuente para todo y que los números bailen al cambiar de valor. | Fuente UI (`--font-sans`) + Fuente Técnica (`--font-mono`) con `font-variant-numeric: tabular-nums` en todas las tablas, métricas y contadores. |
| **3. Máquina de Estados Completa (4 Estados)** | Programar únicamente la vista cuando `data.length > 0`. | Implementar explícitamente `Loading` (skeletons con la geometría real), `Empty` (mensaje útil + acción), `Error` (causa + botón reintentar) y `Populated`. |
| **4. Superficies y Bordes (`1px`) en vez de Sombras Difusas** | Abusar de `shadow-xl` y fondos `#FFFFFF` puros que cansan la vista. | Jerarquía por capas de luminancia sutil (`#FAF8F5` en claro o `#0A0A0C -> #121216` en oscuro) separadas por bordes nítidos de `1px`. |
