# Guía de Mentoría #00: ¿Cómo funciona una CLI profesional en Python?

> **Modo Mentor (`compass`)** · **Nivel**: Fundamentos de Ingeniería de Software  
> **Objetivo**: Entender desde cero qué ocurre bajo el capó cuando escribes un comando en tu terminal de Linux/WSL, por qué hemos elegido `Typer` + `Rich`, y cómo se organiza un paquete de Python profesional antes de escribir la primera línea de código.

---

## 1. El Misterio de la Terminal: ¿Cómo sabe Linux qué es `compass`?

Cuando trabajas haciendo scripts sueltos en Python, normalmente ejecutas algo así:
```bash
python mi_script.py
```
El problema de eso es que si estás en otra carpeta (por ejemplo, creando un nuevo proyecto de Telecomunicaciones en `/home/carlos/radio-sim`), no tienes `mi_script.py` ahí. Nosotros queremos poder estar en **cualquier carpeta del ordenador** y escribir simplemente:
```bash
compass init
```

### ¿Cómo funciona ese mecanismo en Linux y Python?
1. **La variable `$PATH` de Linux**: Cuando escribes una palabra como `git`, `ls` o `compass`, Linux busca un archivo ejecutable con ese nombre dentro de una lista de carpetas especiales (como `/usr/bin` o `.venv/bin`).
2. **El archivo `pyproject.toml` y los *Entry Points***: En un paquete de Python moderno, no creamos ese ejecutable a mano. En la raíz del proyecto ponemos un archivo de configuración estándar llamado `pyproject.toml` con estas líneas:
   ```toml
   [project.scripts]
   compass = "compass_harness.cli:app"
   ```
   **Traducción**: *"Cuando se instale este paquete, genera un comando ejecutable llamado `compass` que importe el módulo `compass_harness.cli` y ejecute el objeto `app`"*.
3. **La Instalación Editable (`pip install -e .` o `uv pip install -e .`)**:
   La bandera `-e` significa **Editable**. En lugar de copiar tu código a una carpeta oculta del sistema, crea un enlace vivo hacia tu carpeta `/home/carlos/compass-harness/src`. Así, cada vez que cambies una línea en tu código, el comando `compass` refleja el cambio al instante sin reinstalar nada.

---

## 2. Por qué elegimos la Opción A (`Typer` + `Rich`) en lugar de `argparse`

Entre `argparse` (Opción B, librería estándar) y `Typer` + `Rich` (Opción A), hemos elegido la **Opción A** por tres razones técnicas y formativas:

### Comparativa en código
Imagina que queremos crear el subcomando `compass init --force`:

* **Con `argparse` (Estilo imperativo clásico)**:
  Obliga a configurar manualmente analizadores, sub-analizadores, tipos y textos de ayuda. A medida que crecen los subcomandos, el código de configuración oculta la lógica real.
* **Con `Typer` (Estilo declarativo moderno basado en *Type Hints*)**:
  ```python
  import typer

  app = typer.Typer()

  @app.command()
  def init(force: bool = False) -> None:
      """Inicializa el harness Compass en el proyecto actual."""
      ...
  ```
  `Typer` inspecciona tres elementos estándar de Python:
  1. El **nombre de la función** (`def init`) se convierte en el subcomando `compass init`.
  2. El **tipo y valor por defecto del parámetro** (`force: bool = False`) se convierte automáticamente en la opción `--force` en la terminal.
  3. El **Docstring** (`"""Inicializa..."""`) se convierte automáticamente en la documentación de `compass init --help`.

> **Nota formativa**: `Typer` fue creado por el mismo autor de **FastAPI**. Ambos utilizan *Type Hints* y decoradores (`@app...`) con la misma estructura. Aprender `Typer` te da la base directa para trabajar con `FastAPI`.

---

## 3. Nuestra Arquitectura: Separación de Interfaz y Dominio

En nuestro documento de arquitectura (`docs/brain/architecture.md`) aplicamos la primera regla de `compass`: **no sobrecomplicar, pero mantener fronteras limpias**.

Un error común al construir una CLI es meter toda la lógica dentro de la función del comando: abrir archivos, evaluar condiciones y mostrar texto en consola todo mezclado en la misma función.

### Analogía de Telecomunicaciones (DSP vs. Pantalla)
Imagina un receptor de radio donde el **procesador digital de señal (DSP)** estuviera soldado de forma inseparable a la **pantalla** que muestra los decibelios. Si quisieras verificar en laboratorio si el DSP calcula bien la relación señal-ruido (SNR) de forma automatizada sin mirar la pantalla, no podrías.

En software ocurre lo mismo. Por eso dividimos `compass-harness` en **3 capas**:

1. **`cli.py` (Adaptador de Entrada / Interfaz de Consola)**:
   * Recoge los argumentos que el usuario escribió en la terminal (`compass init`), invoca a `core/` y formatea la salida en pantalla usando `Rich`.
2. **`core/` (Dominio Determinista)**:
   * Código Python puro que recibe rutas (`Path`) y configuraciones, crea carpetas/enlaces simbólicos o audita archivos, y devuelve estructuras de datos con el resultado.
   * **Regla de diseño**: `core/` no sabe que existe una terminal ni imprime directamente por pantalla.
3. **`templates/` (Plantillas Maestras)**:
   * Los archivos Markdown parametrizables (`AGENTS.md`, `SKILL.md`, documentos base del cerebro) que `core/` renderiza e instala cuando ejecutas `compass init` en cualquier proyecto nuevo.

---

## 4. ¿Por qué existe la carpeta `src/`? (El *src-layout*)

La estructura definida en `architecture.md` es:
```text
compass-harness/
├── pyproject.toml
├── src/
│   └── compass_harness/
└── tests/
```
Muchos ejemplos básicos colocan la carpeta `compass_harness/` directamente en la raíz (sin `src/`). En proyectos profesionales se utiliza el **layout `src/`** por una razón crítica de pruebas:
* Al ejecutar `pytest`, Python añade automáticamente el directorio actual a su ruta de búsqueda. Si el paquete está en la raíz, los tests pueden importar los archivos locales por accidente aunque `pyproject.toml` esté mal configurado.
* Al aislar el código dentro de `src/`, obligamos a que `pytest` utilice el paquete instalado en modo editable, garantizando que el empaquetado real funciona.

---

## Resumen de Conceptos Clave
1. **`pyproject.toml` + `[project.scripts]`**: Conecta una función de Python con un comando ejecutable en la terminal (`compass`).
2. **Type Hints + Decoradores (`@app.command()`)**: Mecanismo declarativo de `Typer` para definir comandos y argumentos de consola.
3. **Desacoplamiento `CLI` vs `Core`**: Separar la interfaz de terminal de la lógica de archivos para facilitar el **TDD**.
4. **Layout `src/`**: Estándar de empaquetado en Python para asegurar que los tests validan el paquete instalado.
