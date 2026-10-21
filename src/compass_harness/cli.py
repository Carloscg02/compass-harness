"""Punto de entrada de la interfaz de linea de comandos para compass-harness."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from compass_harness import __version__
from compass_harness.core.inspector import ProjectState, inspect_project
from compass_harness.core.installer import apply_installation, plan_installation
from compass_harness.core.renderer import ProjectConfig
from compass_harness.core.verifier import REQUIRED_BRAIN_FILES, verify_harness

app = typer.Typer(
    name="compass",
    help="Compass: Meta-Harness agnostico y educativo para desarrollo con agentes.",
    no_args_is_help=True,
)

__all__ = ["app", "check", "init", "main", "status", "version_callback"]

console = Console()


def version_callback(value: bool) -> None:
    """Muestra la version actual del paquete y finaliza la ejecucion."""
    if value:
        console.print(f"compass-harness v{__version__}")
        raise typer.Exit(code=0)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Muestra la version de compass-harness y termina.",
    ),
) -> None:
    """Punto de entrada principal para la aplicacion compass."""
    pass


@app.command("init")
def init(
    path: Path = typer.Option(Path("."), "--path", help="Directorio del proyecto objetivo."),
    name: Optional[str] = typer.Option(None, "--name", help="Nombre del proyecto."),
    goal: str = typer.Option("Desarrollo asistido por agentes con Compass", "--goal", help="Objetivo del proyecto."),
    stack: Optional[str] = typer.Option(None, "--stack", help="Stack tecnologico principal."),
    domain: str = typer.Option("General Software Engineering", "--domain", help="Dominio tecnico y educativo."),
    arch: str = typer.Option("hexagonal", "--arch", help="Estilo arquitectonico (hexagonal, layered, mvc, script)."),
    model_strategy: str = typer.Option("subagent-fast", "--model-strategy", help="Estrategia de modelos (subagent-fast, subagent-inherit, single)."),
    assistants: str = typer.Option("antigravity", "--assistants", help="Asistentes objetivo separados por coma (antigravity,claude,cursor,codex)."),
    test_cmd: str = typer.Option("pytest", "--test-cmd", help="Comando para tests unitarios e integracion."),
    lint_cmd: str = typer.Option("ruff check", "--lint-cmd", help="Comando para linter y chequeo estatico."),
    e2e_cmd: str = typer.Option("N/A", "--e2e-cmd", help="Comando para tests E2E / Playwright opcional."),
    preview: bool = typer.Option(False, "--preview", help="Fase 2: Muestra el plan de instalacion sin escribir en disco."),
    apply: bool = typer.Option(False, "--apply", help="Fase 3: Escribe los archivos y crea los symlinks en disco."),
    force: bool = typer.Option(False, "--force", help="Sobrescribe archivos existentes al usar --apply."),
) -> None:
    """Inicializa Compass Meta-Harness en el proyecto objetivo siguiendo el protocolo de 3 fases."""
    if preview and apply:
        console.print("Error: No se pueden especificar --preview y --apply simultaneamente.")
        raise typer.Exit(code=1)

    root = path.resolve()
    if not root.exists():
        console.print(f"Error: El directorio especificado no existe: {root}")
        raise typer.Exit(code=1)
    if not root.is_dir():
        console.print(f"Error: La ruta especificada no es un directorio: {root}")
        raise typer.Exit(code=1)

    inspection = inspect_project(root)

    project_name = name or root.name
    project_stack = stack or (", ".join(inspection.detected_stacks) if inspection.detected_stacks else "python")
    assistants_tuple = tuple(a.strip().lower() for a in assistants.split(",") if a.strip())

    config = ProjectConfig(
        project_name=project_name,
        project_goal=goal,
        tech_stack=project_stack,
        domain=domain,
        architecture_style=arch,
        model_strategy=model_strategy,
        target_assistants=assistants_tuple,
        test_command=test_cmd,
        lint_command=lint_cmd,
        e2e_command=e2e_cmd,
    )

    # Fase 1: Inspeccion y Guia para el Agente
    if not preview and not apply:
        console.print("=== COMPASS_ONBOARDING_REQUIRED ===")
        console.print(f"Estado del proyecto: {inspection.state.value.upper()}")
        console.print(f"Stacks detectados: {', '.join(inspection.detected_stacks) if inspection.detected_stacks else 'Ninguno'}")
        console.print(f"Directorios tracked detectados: {', '.join(inspection.existing_dirs) if inspection.existing_dirs else 'Ninguno'}")
        console.print(f"Archivos de harness previos: {', '.join(inspection.existing_harness_files) if inspection.existing_harness_files else 'Ninguno'}")
        if inspection.detected_ui_signals:
            console.print(f"Senales UI detectadas: {', '.join(inspection.detected_ui_signals)}")
        if inspection.existing_design_files:
            console.print(f"Contratos de diseno previos: {', '.join(inspection.existing_design_files)}")
        console.print("")
        console.print("Instrucciones para el Agente:")
        if inspection.state == ProjectState.GREENFIELD:
            console.print("Proyecto Greenfield detectado. Acuerda con el usuario en el chat:")
            console.print("1. Objetivo del proyecto (--goal)")
            console.print("2. Stack tecnologico (--stack)")
            console.print("3. Dominio tecnico/educativo (--domain)")
            console.print("4. Estilo arquitectonico (--arch: hexagonal, layered, mvc, script)")
            console.print("5. Comandos de verificacion (--test-cmd, --lint-cmd, --e2e-cmd)")
            console.print("6. Asistentes objetivo (--assistants: antigravity, claude, cursor, codex)")
        else:
            console.print("Proyecto Brownfield detectado. Acuerda con el usuario en el chat:")
            console.print("1. Objetivo del proyecto (--goal)")
            console.print("2. Stack tecnologico (--stack)")
            console.print("3. Dominio tecnico/educativo (--domain)")
            console.print("4. Estilo arquitectonico (--arch: hexagonal, layered, mvc, script)")
            console.print("5. Comandos de verificacion (--test-cmd, --lint-cmd, --e2e-cmd)")
            console.print("6. Asistentes objetivo (--assistants: antigravity, claude, cursor, codex)")
            console.print(
                f"7. Inspecciona el codigo existente ({', '.join(inspection.existing_dirs)}) y documenta `docs/brain/modules/` "
                "por SUBSISTEMAS FUNCIONALES / CAPACIDADES DE NEGOCIO (ej. auth, billing, extraction, valuation), "
                "NUNCA por capas tecnicas horizontales (prohibido crear domain.md, adapters.md o application.md)."
            )
            if "DESIGN.md" in inspection.existing_design_files:
                console.print(
                    "8. Se detecto DESIGN.md previo: tras --apply, sintetiza sus Design Tokens y Typography en `docs/brain/design.md` (<= 80 lineas)."
                )
            if any(m in inspection.existing_harness_files for m in ("agents.md", "SDD-WoW.md", ".agent")):
                console.print(
                    "9. Se detectaron archivos de un arnes previo (ej. agents.md en minusculas o SDD-WoW.md): propon consolidarlos o eliminar duplicados para evitar conflicto con AGENTS.md."
                )
        console.print("")
        console.print("Siguiente paso sugerido:")
        console.print(f'compass init --path "{root}" --name "{project_name}" --preview')
        raise typer.Exit(code=0)

    # Fase 2: Plan de Onboarding y Vista Previa
    if preview:
        plan = plan_installation(root, config)
        console.print("=== COMPASS_ONBOARDING_PLAN ===")
        console.print("Configuracion acordada:")
        console.print(f"  Nombre: {config.project_name}")
        console.print(f"  Objetivo: {config.project_goal}")
        console.print(f"  Stack: {config.tech_stack}")
        console.print(f"  Dominio: {config.domain}")
        console.print(f"  Arquitectura: {config.architecture_style}")
        console.print(f"  Estrategia de modelos: {config.model_strategy}")
        console.print(f"  Asistentes: {', '.join(config.target_assistants)}")
        console.print(f"  Comandos: test={config.test_command}, lint={config.lint_command}, e2e={config.e2e_command}")
        console.print("")
        console.print("Archivos del bundle:")
        for f in plan.files_to_create:
            console.print(f"  [CREATE] {f}")
        for f in plan.existing_conflicts:
            console.print(f"  [CONFLICT] {f} (se omitira salvo --force)")
        console.print("")
        console.print("Enlaces simbolicos:")
        for s in plan.symlinks_to_create:
            console.print(f"  [SYMLINK] {s.link_path} -> {s.target_path}")
        console.print("")
        console.print("Siguiente paso sugerido:")
        console.print(f'compass init --path "{root}" --name "{config.project_name}" --apply')
        raise typer.Exit(code=0)

    # Fase 3: Aplicacion en Disco y Creacion de Symlinks
    if apply:
        result = apply_installation(root, config, force=force)
        console.print("=== COMPASS_ONBOARDING_APPLIED ===")
        console.print(f"Proyecto inicializado en: {root}")
        console.print("Archivos escritos:")
        for f in result.written_files:
            console.print(f"  [WRITTEN] {f}")
        if result.skipped_files:
            console.print("Archivos omitidos por existir previamente:")
            for f in result.skipped_files:
                console.print(f"  [SKIPPED] {f}")
        console.print("Enlaces simbolicos creados:")
        for s in result.created_symlinks:
            console.print(f"  [SYMLINK] {s}")
        console.print("Directorios asegurados:")
        for d in result.ensured_directories:
            console.print(f"  [DIR] {d}")
        raise typer.Exit(code=0)


@app.command("status")
def status(
    path: Path = typer.Option(Path("."), "--path", help="Directorio del proyecto objetivo."),
) -> None:
    """Muestra el estado actual del arnes Compass en el proyecto objetivo."""
    root = path.resolve()
    if not root.exists():
        console.print(f"Error: El directorio especificado no existe: {root}")
        raise typer.Exit(code=1)
    if not root.is_dir():
        console.print(f"Error: La ruta especificada no es un directorio: {root}")
        raise typer.Exit(code=1)

    report = verify_harness(root)
    console.print("=== COMPASS_STATUS ===")
    if not report.is_installed:
        console.print("Estado general: NOT_INITIALIZED")
    elif report.passed:
        console.print("Estado general: HEALTHY")
    else:
        console.print("Estado general: ISSUES_FOUND")

    console.print(f"Archivos del Cerebro: {len(report.present_brain_files)}/{len(REQUIRED_BRAIN_FILES)} presentes")
    if report.missing_brain_files:
        console.print(f"  Faltantes: {', '.join(report.missing_brain_files)}")

    skills_str = ", ".join(report.installed_skills) if report.installed_skills else "Ninguna"
    console.print(f"Skills instaladas: {skills_str}")

    contract_status = "Activo" if report.has_design_contract else "No requerido / Inactivo"
    console.print(f"Contrato UI (design.md): {contract_status}")
    if report.has_design_contract and not report.has_agent_eyes:
        console.print("  Aviso UI: Contrato UI activo pero E2E / Agent Eyes esta en N/A. Usa la skill ui-design para auto-configurar Playwright + ariaSnapshot.")

    console.print(f"Enlaces simbolicos: {len(report.active_symlinks)} activos, {len(report.broken_symlinks)} rotos")
    if report.broken_symlinks:
        console.print(f"  Rotos: {', '.join(report.broken_symlinks)}")

    if report.specs_progress:
        console.print("Progreso de Specs:")
        for spec in report.specs_progress:
            console.print(f"  - {spec.spec_id}: {spec.completed_tasks}/{spec.total_tasks} tareas completadas")
    else:
        console.print("Progreso de Specs: Ninguna spec encontrada")

    raise typer.Exit(code=0)


@app.command("check")
def check(
    path: Path = typer.Option(Path("."), "--path", help="Directorio del proyecto objetivo."),
) -> None:
    """Ejecuta la puerta de calidad determinista sobre las invariantes del arnes Compass."""
    root = path.resolve()
    if not root.exists():
        console.print(f"Error: El directorio especificado no existe: {root}")
        raise typer.Exit(code=1)
    if not root.is_dir():
        console.print(f"Error: La ruta especificada no es un directorio: {root}")
        raise typer.Exit(code=1)

    report = verify_harness(root)
    if report.passed:
        console.print("=== COMPASS_CHECK_PASSED ===")
        console.print(f"Proyecto verificado correctamente en: {root}")
        console.print(f"- Archivos del Cerebro: {len(report.present_brain_files)}/{len(REQUIRED_BRAIN_FILES)} presentes")
        console.print("- Presupuestos de contexto respetados (AGENTS.md y handoff.md)")
        console.print("- Aislamiento O(1) de decisiones tecnicas respetado")
        console.print(f"- Enlaces simbolicos: {len(report.active_symlinks)} activos, 0 rotos")
        console.print(f"- Tareas con Prueba Observada auditadas: {sum(s.completed_tasks for s in report.specs_progress)} completadas validas")
        raise typer.Exit(code=0)
    else:
        console.print("=== COMPASS_CHECK_FAILED ===")
        console.print(f"Se encontraron {len(report.issues)} problemas en el proyecto:")
        for issue in report.issues:
            console.print(f"[{issue.code}] {issue.path}: {issue.message}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
