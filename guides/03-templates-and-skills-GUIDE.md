# Guía de Ingeniería (Paso 3): Motor Puro de Plantillas, Separación Core/I-O y anatomía de la Skill `tdd` de Matt Pocock

Esta guía explica las decisiones de ingeniería de software aplicadas al construir la feature **`03-templates-and-skills`** (`src/compass_harness/core/renderer.py` y `src/compass_harness/templates/`).

---

## 1. El Patrón "Functional Core, Imperative Shell" en el Renderizador

Observa la firma de la función principal que hemos creado en [`renderer.py`](../src/compass_harness/core/renderer.py):

```python
def render_project_bundle(config: ProjectConfig) -> dict[str, str]:
```

Fíjate en lo que **NO** recibe esta función: no recibe un `Path` de destino, ni escribe carpetas en disco con `mkdir()`, ni crea enlaces simbólicos (`os.symlink`). Simplemente recibe un objeto inmutable `ProjectConfig` y devuelve un diccionario en memoria `{ruta_relativa: contenido_markdown}`.

### ¿Por qué es una decisión arquitectónica clave?
1. **Velocidad y Determinismo en los Tests**:
   En [`test_templates_and_skills.py`](../tests/test_templates_and_skills.py), hemos ejecutado **10 tests completos** verificando 12 archivos generados y múltiples combinaciones de arquitectura (`hexagonal` vs `script`) y estrategias de modelos (`subagent-fast`, `subagent-inherit`, `single`) en apenas **0.03 segundos**, sin tocar el disco duro ni una sola vez.
2. **Reutilización directa para `--preview` y `--apply`**:
   En el próximo Paso 4 (`04-agent-onboarding`), el comando `compass init` tendrá dos modos:
   - `--preview`: Mostrar al humano qué archivos se van a crear y con qué configuración, **sin escribir nada en el disco**.
   - `--apply`: Escribir esos archivos en disco y crear los symlinks.
   Gracias a que `render_project_bundle(config)` devuelve un `dict[str, str]` en memoria, tanto `--preview` como `--apply` llamarán exactamente a la misma función pura. No habrá riesgo de que el modo `--preview` muestre algo distinto de lo que luego escribe `--apply`.

---

## 2. Por qué usar Funciones Tipadas en Python en lugar de un Motor Pesado (Jinja2)

Cuando alguien construye un generador de plantillas en Python, el impulso habitual es añadir `Jinja2` como dependencia externa. Sin embargo, en `compass-harness` hemos usado funciones puras de Python con `f-strings` en [`brain_assets.py`](../src/compass_harness/templates/brain_assets.py) y [`compass_skills_assets.py`](../src/compass_harness/templates/compass_skills_assets.py).

- **Cero dependencias extra**: Nuestro CLI solo necesita `typer` y `rich`. Cuantas menos dependencias de terceros tenga un meta-harness que vas a instalar globalmente en tu máquina, menor es el riesgo de conflictos de versiones.
- **Chequeo estático y autocompletado**: Si te equivocas escribiendo `config.arch_style` en lugar de `config.architecture_style` dentro de un archivo `.j2` de Jinja2, no te enteras hasta que esa rama concreta se ejecuta en producción. En una función Python tipada con `ProjectConfig`, el IDE y el linter (`ruff` / `mypy`) detectan el error al instante.
- **Evitar referencias circulares con `TYPE_CHECKING`**:
  En `brain_assets.py` verás este patrón profesional de Python:
  ```python
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from compass_harness.core.renderer import ProjectConfig
  ```
  Como `renderer.py` importa las funciones de `brain_assets.py`, si `brain_assets.py` importara `ProjectConfig` en tiempo de ejecución tendríamos un **Import Circular** (`ImportError`). La constante `TYPE_CHECKING` vale `False` cuando el programa corre de verdad, pero vale `True` cuando tu editor o el verificador de tipos analiza el código. Así obtenemos tipado estricto sin ciclos de importación.

---

## 3. Disección de la Skill `tdd` de Matt Pocock

Al empaquetar los 3 archivos originales de Matt Pocock (`SKILL.md`, `tests.md`, `mocking.md`) en [`tdd_skill_assets.py`](../src/compass_harness/templates/tdd_skill_assets.py), merece la pena destacar los tres conceptos de ingeniería que introduce y cómo los hemos conectado con `sdd-workflow`:

1. **Seams (Costuras Públicas) vs. Detalles Internos**:
   Un error clásico al hacer TDD con agentes de IA es pedirles que testeen cada función privada o clase auxiliar. Eso congela la implementación interna: en la fase `REFACTOR`, si cambias una función auxiliar, se rompen los tests aunque el sistema siga funcionando igual. Un **Seam** es la interfaz pública de un módulo (como `inspect_project(root)` o `render_project_bundle(config)`). Al obligar en `sdd-workflow` a declarar los *Seams* en `plan.md` antes de escribir código, garantizamos que los tests cubran tanto lógica unitaria como la integración real entre módulos internos.
2. **Vertical Slices (Tracer Bullets) vs. Horizontal Slicing**:
   - *Horizontal Slicing (Mal patrón)*: "Tarea 1: Escribir los 10 tests de la feature. Tarea 2: Escribir todo el código de la feature". Cuando haces esto con un LLM, los 10 tests escritos a ciegas suelen ser tautológicos o estar mal planteados.
   - *Vertical Slicing (Buen patrón)*: "Tarea 1: Test RED del caso base -> Código GREEN del caso base. Tarea 2: Test RED de parametrización -> Código GREEN de parametrización". Cada tarea atraviesa todas las capas de principio a fin.
3. **Verificación Proporcional (In-Loop vs. E2E/Playwright)**:
   Como acordamos durante el diseño de la especificación, el bucle `RED -> GREEN -> REFACTOR` debe mantenerse en milisegundos ejecutando tests unitarios y de integración en memoria sobre los *Seams*. Si una aplicación web requiere pruebas en navegador real con **Playwright**, esa verificación se declara en `docs/brain/architecture.md` bajo `E2E / Browser UI Tests` y el subagente ligero (`flash`) la ejecuta como tarea de cierre de la feature cuando se tocan flujos de interfaz completos.
