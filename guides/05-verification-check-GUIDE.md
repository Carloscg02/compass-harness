# Guía de Ingeniería (Paso 5): Puertas de Calidad Deterministas, Parsing con Expresiones Regulares y Dogfooding

Esta guía explica las decisiones de ingeniería de software aplicadas en el último paso del Roadmap v1.0 (**`05-verification-check`**) dentro de [`verifier.py`](../src/compass_harness/core/verifier.py) y [`cli.py`](../src/compass_harness/cli.py).

---

## 1. Por qué un Harness necesita un Verificador Determinista fuera del LLM

En la literatura de ingeniería de arneses (tanto en Anthropic como en `rsc-harness` y `learn-harness-engineering`), existe una ley fundamental:

> **"No confíes únicamente en un prompt para vigilar que el LLM ha seguido las reglas de un prompt."**

Si le pides a un agente en `AGENTS.md` *"Mantén `handoff.md` por debajo de 30 líneas"* y *"Nunca marques una tarea como `[x]` sin pegar la Prueba Observada"*, el agente lo cumplirá el 90% de las veces. Pero en sesiones largas o bajo presión de contexto, puede olvidar borrar líneas antiguas en `handoff.md` o marcar `[x]` dejando `*(Pendiente)*`.

Al construir `compass check` en Python puro:
- Convertimos reglas escritas en prosa en **invariantes ejecutables** con código de salida (`0` o `1`).
- Puedes añadir `compass check` a un hook de Git (`pre-commit`), a GitHub Actions o al cierre de cada turno del agente, garantizando matemáticamente que el repositorio jamás entre en *Context Rot*.

---

## 2. Diseño del Parser de Tareas (`_parse_tasks_file` y Expresiones Regulares Compiladas)

En [`verifier.py`](../src/compass_harness/core/verifier.py), necesitamos auditar archivos Markdown (`specs/*/tasks.md`) sin añadir un parser externo pesado de AST Markdown. Observa cómo lo hemos resuelto con dos expresiones regulares precompiladas a nivel de módulo:

```python
TASK_HEADER_PATTERN = re.compile(r"^-\s*\[([ xX])\]\s*(.*)$")
OBSERVED_PROOF_HEADER_PATTERN = re.compile(
    r"^\s*(?:-\s*)?(?:\*{0,2}|#{1,6}\s*)(?:Prueba Observada|Observed Proof)\*{0,2}\s*:",
    re.IGNORECASE,
)
```

### Detalles clave de esta implementación:
1. **`re.compile` en el ámbito global del módulo**:
   En Python, si llamas a `re.match(patron, linea)` dentro de un bucle `for`, el intérprete consulta su caché interna en cada iteración. Al compilar la expresión regular una sola vez al importar el módulo (`re.compile(...)`), la máquina de estados del autómata finito queda lista en memoria.
2. **Grupos de captura vs. Grupos sin captura `(?:...)`**:
   - En `TASK_HEADER_PATTERN`, usamos paréntesis normales `([ xX])` y `(.*)` porque queremos extraer esos dos datos con `match.group(1)` (si está marcada con `x` o vacía) y `match.group(2)` (el título de la tarea).
   - En `OBSERVED_PROOF_HEADER_PATTERN`, usamos `(?:...)` (*non-capturing groups*) porque solo queremos comprobar si la línea coincide con cualquiera de las variantes (`- **Prueba Observada**:`, `### Observed Proof:`, etc.) sin desperdiciar memoria creando grupos de captura que no vamos a leer.
3. **Agrupación por bloques (*Chunking State Machine*)**:
   En `_parse_tasks_file(content)`, recorremos las líneas una sola vez ($O(N)$): cada vez que aparece una cabecera `- [ ]` o `- [x]`, abrimos un cubo nuevo `(is_done, title, [])` y todas las líneas siguientes caen en ese cubo hasta que empieza la siguiente tarea. Después, `_has_valid_observed_proof` examina únicamente el cubo de las tareas que tienen `is_done == True`.

---

## 3. Diferencia Semántica en CLI: `status` (Exit 0) vs `check` (Exit 0 / 1)

Fíjate en por qué hemos separado `compass status` y `compass check`:
- **`compass status`** es una herramienta de **observabilidad**: aunque el proyecto tenga tareas pendientes o aún no esté inicializado, el comando ha tenido éxito informándote del estado actual, por lo que devuelve siempre `exit_code = 0`.
- **`compass check`** es una **puerta de verificación (*Gate*)**: su contrato UNIX establece que `exit_code = 0` significa *"todas las invariantes se cumplen"* y `exit_code = 1` significa *"al menos una invariante se ha roto"*. Esto permite encadenarlo en scripts de automatización con el operador lógico `&&`:
  ```bash
  compass check && pytest
  ```

---

## 4. El Cierre del Círculo: *Dogfooding* Completo

En [`test_verification_check.py`](../tests/test_verification_check.py) hemos incluido el test `test_cli_dogfooding_on_compass_harness_repository()`, que ejecuta `compass check --path /home/carlos/compass-harness` contra nuestro propio repositorio real.

Esto significa que a partir de este momento, el propio código que hemos construido vigila en cada ejecución de `pytest` que:
- Nuestro `AGENTS.md` tiene menos de 100 líneas.
- Nuestro `docs/brain/handoff.md` tiene como máximo 30 líneas.
- Nuestro `docs/brain/index.md` mantiene aislamiento $O(1)$ hacia `decisions/index.md`.
- Las **16 tareas** repartidas en nuestras 5 especificaciones (`01` a `05`) tienen todas su bloque de **Prueba Observada** real documentado.
