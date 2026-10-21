# Guía de Auditoría de Harness Engineering (Basada en `learn-harness-engineering`, OpenAI Codex, Anthropic y `rsc-harness`)

> **Propósito**: Marco de referencia neutral y lista de control para auditar cualquier harness de agentes de codificación, basado fielmente en la teoría y el temario de [`walkinglabs/learn-harness-engineering`](https://github.com/walkinglabs/learn-harness-engineering), los papers fundacionales de **Anthropic** (*Effective Harnesses for Long-Running Agents*) y **OpenAI** (*Harness Engineering*), y las buenas prácticas de **`rsc-harness`**.

---

## 1. Definición Base: ¿Qué es el Harness y por qué fallan los modelos potentes? (Lección 1)

En *Harness Engineering*, **el Harness es todo lo que está fuera de los pesos del modelo**: instrucciones, herramientas, entorno de ejecución, gestión de estado y bucles de retroalimentación/verificación.

Cuando un modelo de frontera falla en un proyecto real, rara vez es por falta de inteligencia del modelo; suele ser un **Fallo Inducido por el Harness (*Harness-Induced Failure*)**. Al auditar un harness existente, lo primero es comprobar si resuelve los **5 modos de fallo clásicos identificados en la Lección 1**:

1. **Requisitos vagos (*Vague requirements*)**: Si el sistema permite pasar de una petición ambigua directamente a escribir código, el agente adivina.
2. **Convenciones implícitas no escritas (*Implicit conventions*)**: Las reglas de arquitectura, versiones de librerías o patrones que solo existen en la cabeza del desarrollador nunca se cumplen de forma consistente.
3. **Configuración de entorno incompleta (*Incomplete environment setup*)**: El agente quema su ventana de contexto peleando con errores de entorno, dependencias o rutas en lugar de resolver la tarea.
4. **Brecha de verificación y Ansiedad de Contexto (*Verification Gap & Context Anxiety*)**:
   * **Verification Gap**: La distancia entre *"el agente cree que ha terminado"* y *"el sistema realmente funciona"*.
   * **Context Anxiety (Anthropic)**: Cuando el agente nota que su ventana de contexto se está llenando, se precipita para terminar rápido, se salta comprobaciones y elige parches simples en lugar de soluciones correctas.
5. **Pérdida de estado entre sesiones (*Cross-session state loss*)**: Cada nueva sesión empieza desde cero o repite trabajo ya hecho si el progreso y los resultados de verificación no quedan registrados en archivos versionados.

---

## 2. El Marco de los 5 Subsistemas (Lecciones 2 a 12 + Análisis de Claude Code, Codex, Pi y DeepSeek)

Todo harness de producción se evalúa auditando sus **5 subsistemas**.

### Subsistema 1: Instrucciones (*Instructions*) — Lecciones 2 a 4
* **Principio 1 — "AGENTS.md es una página de directorio, no una enciclopedia" (OpenAI Codex / Lección 4)**:
  * Un archivo único gigante de instrucciones falla inevitablemente: es imposible de mantener actualizado, provoca contradicciones y el modelo ignora las reglas de la mitad del archivo.
  * **Criterio de auditoría**: `AGENTS.md` / `CLAUDE.md` debe mantenerse alrededor de **~100 líneas**, actuando como un mapa/índice que apunta a documentación estructurada en el repositorio (`docs/`) o a *skills* que el agente lee bajo demanda.
* **Principio 2 — "Imponer invariantes, no microgestionar la implementación" (Lección 2 / Codex)**:
  * `AGENTS.md` debe definir las **restricciones inviolables** (límites de arquitectura, qué no tocar, qué comandos de verificación son obligatorios) y dejar los detalles de implementación al modelo o a documentos específicos de tarea.
* **Principio 3 — Jerarquía y Carga Bajo Demanda (Claude Code Breakdown)**:
  * Las instrucciones deben dividirse por alcance (global, proyecto, subdirectorio o *skills* con *Progressive Disclosure*) para que los tokens entren en la ventana de contexto solo cuando aplican a la tarea actual.

### Subsistema 2: Contexto y Estado (*Context & State*) — Lecciones 5 y 6
Se audita mediante las **4 estrategias de Ingeniería de Contexto (*Write - Select - Compress - Isolate*)**:
1. **Write (Escribir fuera de la ventana)**: El repositorio es el sistema de registro (*System of Record*). Las decisiones, el estado de las funcionalidades (`feature_list.json` o equivalente) y el progreso (`progress.md`) deben persistirse en disco, nunca quedarse solo en la conversación.
2. **Select (Seleccionar bajo demanda)**: El agente debe poder localizar qué módulo o documento leer a través de un índice sin tener que escanear todo el código fuente ni cargar archivos históricos que crecen infinitamente.
3. **Compress (Compactar con seguridad)**: El sistema debe soportar compactación o resumen estructurado antes de que aparezca la *ansiedad de contexto*, sin perder las reglas ni el estado de qué tareas están ya hechas.
4. **Isolate (Aislar contextos)**: Separar tareas pesadas o ruidosas en subagentes o sesiones limpias para que los logs de herramientas no contaminen el contexto principal.

### Subsistema 3: Alcance (*Scope*) — Lecciones 7 y 8
* **Una funcionalidad a la vez (*One feature at a time, no overreach*)**:
  * El fallo más caro documentado por Anthropic es dejar que el agente intente construir varias funcionalidades a la vez (*one-shotting*).
  * **Criterio de auditoría**: El harness debe desglosar el trabajo en unidades atómicas con dependencias explícitas y criterios de cierre claros, prohibiendo modificar código fuera del alcance de la tarea activa.
* **Fricción proporcional (`rsc-harness`)**:
  * Debe distinguir entre consultas de solo lectura, cambios pequeños y funcionalidades complejas, para no imponer burocracia pesada en tareas triviales ni permitir cambios complejos sin especificación previa.

### Subsistema 4: Entorno y Retroalimentación de Verificación (*Environment & Verification Feedback*) — Lecciones 10 y 11
* **Arranque determinista (`init.sh` o equivalente)**:
  * Debe existir una forma documentada y reproducible de levantar y comprobar el entorno al inicio.
* **Puertas de verificación objetivas (*Verification Gates*)**:
  * El agente **solo puede detenerse cuando la verificación pasa** (tests unitarios/integración, linter, chequeo de tipos, pruebas de humo).
  * La verificación debe basarse en **evidencia observada** (salida real de la ejecución de los comandos), nunca en la autoevaluación subjetiva del modelo.

### Subsistema 5: Ciclo de Vida y Continuidad (*Lifecycle & Handoff*) — Lecciones 9 y 12
* **Rutina de Inicio y Cierre de Sesión**:
  * Al iniciar sesión: leer el estado actual, el registro de progreso y el historial reciente de Git para reconstruir el contexto sin repetir tareas ya completadas.
  * Al cerrar sesión (*Session Handoff*): dejar el árbol de trabajo en un estado limpio y compilable, con los tests pasando y una nota de relevo (`session-handoff.md` / `progress.md`) que indique qué se completó, qué se verificó y cuál es el siguiente paso exacto.

---

## 3. Auditoría de Nivel Avanzado: Loop Engineering y Graph Engineering (Lecciones 13 y 14)

Si el harness que estás auditando busca autonomía avanzada (más allá de que el humano escriba cada prompt paso a paso), el curso define **la pila de 4 capas (`Prompt -> Context -> Loop -> Graph`)**:

### A. Los 3 Elementos de un Loop Autónomo (Lección 13)
Para que un humano pase de estar *"dentro del loop"* (empujando cada paso) a *"fuera del loop"* (diseñando el sistema), todo bucle necesita tres piezas:
1. **Un objetivo claro (*Goal*)**: Qué aspecto tiene el estado final deseado.
2. **Un método de verificación independiente (*Verification Method*)**.
3. **Una condición de parada verificable (*Stopping Condition*)**.

### B. Separación Generador / Evaluador (*Generator / Evaluator Split — Maker-Checker*)
* **Regla fundamental (Lección 13 y Anthropic)**: *"La persona (o agente) que escribe el código no puede corregir su propio examen"*.
* Un agente evaluando su propio trabajo en la misma sesión sufre de sesgo de confirmación. Un harness robusto separa el **Maker (Generador)** del **Checker (Evaluador)** mediante scripts deterministas de test/auditoría y/o un subagente revisor independiente con contexto limpio.

### C. Los 6 Primitivos de Loop Engineering (Addy Osmani / Lección 13)
Un sistema de bucle completo combina:
1. **External State (La columna vertebral)**: Memoria en disco que sobrevive entre iteraciones.
2. **Skills**: Conocimiento procedimental del proyecto codificado y reutilizable.
3. **Sub-agents**: Para aislar el contexto y separar *Maker* de *Checker*.
4. **Worktrees**: Aislamiento físico en ramas/directorios de Git independientes cuando hay ejecución paralela para evitar colisiones de archivos.
5. **Connectors**: Acceso controlado y probado a herramientas externas (MCPs, APIs, CLI).
6. **Automations**: Disparadores por objetivo (`/goal`), por tiempo (`/loop`) o por eventos (CI/Webhooks).

### D. Los 4 Costes Silenciosos y los 3 Fallos a Escala (Qué vigilar en una auditoría)
En las Lecciones 13 y 14 se advierte que un mal harness autónomo acelera cuatro costes ocultos y tres fallos estructurales:
* **Los 4 Costes Silenciosos**:
  1. *Verification Debt* (Deuda de verificación): Se genera código más rápido de lo que se prueba de verdad.
  2. *Comprehension Rot* (Degradación de comprensión): El código crece pero ni el humano ni los nuevos agentes entienden cómo encaja la arquitectura global.
  3. *Cognitive Surrender* (Rendición cognitiva): El desarrollador aprueba cambios sin entender qué hacen ni por qué.
  4. *Token Blowout* (Explosión de tokens): Relecturas masivas de contexto o bucles infinitos sin condición de parada clara.
* **Los 3 Fallos Estructurales (Lección 14)**:
  1. *Ley de Goodhart*: El agente modifica o debilita los tests (`skip`, relajar `assert`) para que la métrica dé verde sin arreglar el problema real.
  2. *Ceguera hacia arriba (Blindness upward)*: Un agente ejecutando una subtarea toma una decisión local que rompe la arquitectura global porque no comprueba las invariantes del proyecto.
  3. *Impuesto de Orquestación (Orchestration Tax)*: Montar un grafo complejo de múltiples agentes paralelos cuando una secuencia simple con buenos *checkpoints* habría resuelto el problema con una fracción del coste.

---

## 4. Rúbrica Práctica de Auditoría (12 Preguntas Basadas en `harness-creator`)

Para auditar el harness en tu otra cuenta, evalúa estos 12 puntos directamente extraídos de [`skills/harness-creator/SKILL.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/skills/harness-creator/SKILL.md) y las lecciones del curso:

| # | Subsistema | Pregunta de Auditoría | Cumple (Sí / Parcial / No) |
| :--- | :--- | :--- | :--- |
| **1** | **Instructions** | ¿Es `AGENTS.md` / `CLAUDE.md` una página de directorio concisa (~100 líneas) en lugar de una enciclopedia gigante? | |
| **2** | **Instructions** | ¿Define invariantes claras (arquitectura, prohibiciones, definición de hecho) en vez de microgestionar o duplicar reglas? | |
| **3** | **Context** | ¿Aplica *Progressive Disclosure* (cargando *skills* y documentos de `docs/` solo bajo demanda para no saturar la ventana)? | |
| **4** | **State** | ¿Es el repositorio el *System of Record* (guardando el estado de features, decisiones y arquitectura en archivos versionados fuera del chat)? | |
| **5** | **State** | ¿Evita la degradación de contexto (*Context Rot*) impidiendo que los archivos que se leen al arrancar crezcan sin límite con el tiempo? | |
| **6** | **Scope** | ¿Obliga a trabajar una funcionalidad/tarea a la vez con límites de alcance explícitos (evitando el *one-shotting*)? | |
| **7** | **Scope** | ¿Proporciona fricción adaptada al riesgo (evitando que el usuario apague el harness por exceso de ceremonia en cambios simples)? | |
| **8** | **Verification** | ¿Tiene puertas de verificación objetivas (tests, lint, scripts) que el agente **debe** ejecutar y demostrar con evidencia antes de declarar "hecho"? | |
| **9** | **Verification** | ¿Protege contra la *Ley de Goodhart* (prohibiendo explícitamente borrar o debilitar tests para forzar el verde)? | |
| **10** | **Lifecycle** | ¿Tiene un protocolo de *Session Handoff* limpio que permita cerrar la sesión hoy y que otra sesión mañana retome sin repetir tareas hechas? | |
| **11** | **Isolation** | ¿Aísla las tareas de ejecución ruidosa (subagentes / separación *Maker-Checker*) para que quien escribe el código no sea el único juez en un contexto sucio? | |
| **12** | **Simplicidad** | ¿Cumple la regla de oro de `harness-creator` (*"Keep the harness small enough that agents actually follow it"*) sin caer en un *Frankenstein Harness*? | |
