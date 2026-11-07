"""Motor de sincronizacion y actualizacion determinista del arnes Compass."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil

from compass_harness.core.installer import (
    SymlinkSpec,
    _compute_symlinks,
    _get_bundle_files,
)
from compass_harness.core.renderer import ProjectConfig


@dataclass(frozen=True)
class UpdatePlan:
    """Plan determinista de actualizacion sin efectos secundarios."""

    config: ProjectConfig
    files_to_update: tuple[str, ...]
    preserved_files: tuple[str, ...]
    symlinks_to_repair: tuple[SymlinkSpec, ...]


@dataclass(frozen=True)
class UpdateResult:
    """Resultado tras la aplicacion de la actualizacion en disco."""

    updated_files: tuple[str, ...]
    skipped_files: tuple[str, ...]
    repaired_symlinks: tuple[str, ...]
    preserved_files: tuple[str, ...]
    config_saved: bool = False


def extract_project_config(root: Path) -> ProjectConfig:
    """Extrae o reconstruye la configuracion del proyecto analizando disco o config.json."""
    target_root = root.resolve()

    agents_file = target_root / "AGENTS.md"
    brain_index_file = target_root / "docs" / "brain" / "index.md"
    config_json_file = target_root / ".compass" / "config.json"

    if not agents_file.is_file() or not brain_index_file.is_file():
        raise FileNotFoundError(
            f"El directorio '{target_root}' no esta inicializado con Compass "
            "(falta AGENTS.md o docs/brain/index.md)."
        )

    # 1. Si existe .compass/config.json, lo leemos directamente
    if config_json_file.is_file():
        try:
            data = json.loads(config_json_file.read_text(encoding="utf-8"))
            return ProjectConfig(
                project_name=data["project_name"],
                project_goal=data["project_goal"],
                tech_stack=data["tech_stack"],
                domain=data.get("domain", "General Software Engineering"),
                architecture_style=data.get("architecture_style", "hexagonal"),
                model_strategy=data.get("model_strategy", "subagent-fast"),
                target_assistants=tuple(data.get("target_assistants", ["antigravity"])),
                test_command=data.get("test_command", "pytest"),
                lint_command=data.get("lint_command", "ruff check"),
                e2e_command=data.get("e2e_command", "N/A"),
            )
        except (json.JSONDecodeError, KeyError):
            pass  # Fallback a reconstruccion desde docs/brain si el JSON esta corrupto

    # 2. Reconstruccion desde docs/brain/index.md
    brain_index_text = brain_index_file.read_text(encoding="utf-8")

    # Nombre del proyecto
    name_match = re.search(r"-\s+\*\*Nombre(?: del Paquete / Repo)?\*\*:\s*`?([^`\n]+)`?", brain_index_text)
    if not name_match:
        name_match = re.search(r"#\s+Cerebro del Proyecto:\s*`?([^`\n]+)`?", brain_index_text)
    project_name = name_match.group(1).strip() if name_match else target_root.name

    # Objetivo
    goal_match = re.search(r"-\s+\*\*(?:Objetivo|Qué es|Que es)\*\*:\s*(.+)", brain_index_text)
    project_goal = (
        goal_match.group(1).strip()
        if goal_match
        else "Desarrollo asistido por agentes con Compass"
    )

    # Stack tecnologico
    stack_match = re.search(r"-\s+\*\*Stack(?: Tecnologico)?\*\*:\s*`?([^`\n]+)`?", brain_index_text)
    tech_stack = stack_match.group(1).strip() if stack_match else "python"

    # Dominio
    domain_match = re.search(r"-\s+\*\*Dominio\*\*:\s*(.+)", brain_index_text)
    domain = domain_match.group(1).strip() if domain_match else "General Software Engineering"

    # 3. Reconstruccion desde docs/brain/architecture.md
    architecture_file = target_root / "docs" / "brain" / "architecture.md"
    arch_style = "hexagonal"
    test_cmd = "pytest"
    lint_cmd = "ruff check"
    e2e_cmd = "N/A"

    if architecture_file.is_file():
        arch_text = architecture_file.read_text(encoding="utf-8")
        arch_lower = arch_text.lower()
        if "hexagonal" in arch_lower:
            arch_style = "hexagonal"
        elif "layered" in arch_lower or "en capas" in arch_lower:
            arch_style = "layered"
        elif "mvc" in arch_lower:
            arch_style = "mvc"
        elif "script" in arch_lower:
            arch_style = "script"

        test_match = re.search(r"-\s+\*\*Unit & Integration Tests.*?\*\*:\s*`?([^`\n]+)`?", arch_text)
        if test_match:
            test_cmd = test_match.group(1).strip()

        lint_match = re.search(r"-\s+\*\*Static / Lint Gate.*?\*\*:\s*`?([^`\n]+)`?", arch_text)
        if lint_match:
            lint_cmd = lint_match.group(1).strip()

        e2e_match = re.search(r"-\s+\*\*E2E / Browser UI Tests.*?\*\*:\s*`?([^`\n]+)`?", arch_text)
        if e2e_match:
            e2e_cmd = e2e_match.group(1).strip()

    # 4. Estrategia de modelos desde AGENTS.md
    agents_text = agents_file.read_text(encoding="utf-8")
    if "subagent-fast" in agents_text:
        model_strategy = "subagent-fast"
    elif "subagent-inherit" in agents_text:
        model_strategy = "subagent-inherit"
    elif "single" in agents_text:
        model_strategy = "single"
    else:
        model_strategy = "subagent-fast"

    # 5. Deteccion de asistentes desde directorios y archivos activos
    detected_assistants: list[str] = []
    if (target_root / ".agents").exists():
        detected_assistants.append("antigravity")
    if (target_root / ".claude").exists() or (target_root / "CLAUDE.md").exists():
        detected_assistants.append("claude")
    if (target_root / ".cursor").exists():
        detected_assistants.append("cursor")

    if not detected_assistants:
        detected_assistants = ["antigravity"]

    return ProjectConfig(
        project_name=project_name,
        project_goal=project_goal,
        tech_stack=tech_stack,
        domain=domain,
        architecture_style=arch_style,
        model_strategy=model_strategy,
        target_assistants=tuple(detected_assistants),
        test_command=test_cmd,
        lint_command=lint_cmd,
        e2e_command=e2e_cmd,
    )


def save_project_config(root: Path, config: ProjectConfig) -> Path:
    """Guarda la configuracion actual del proyecto en .compass/config.json."""
    target_root = root.resolve()
    compass_dir = target_root / ".compass"
    compass_dir.mkdir(parents=True, exist_ok=True)
    config_file = compass_dir / "config.json"

    data = {
        "project_name": config.project_name,
        "project_goal": config.project_goal,
        "tech_stack": config.tech_stack,
        "domain": config.domain,
        "architecture_style": config.architecture_style,
        "model_strategy": config.model_strategy,
        "target_assistants": list(config.target_assistants),
        "test_command": config.test_command,
        "lint_command": config.lint_command,
        "e2e_command": config.e2e_command,
    }

    config_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return config_file


def plan_update(root: Path, config: ProjectConfig) -> UpdatePlan:
    """Calcula el plan determinista de actualizacion sin efectos secundarios."""
    target_root = root.resolve()
    bundle = _get_bundle_files(config)

    # Archivos a actualizar: activos stateless (skills, AGENTS.md, CLAUDE.md)
    files_to_update: list[str] = []
    preserved_set: set[str] = set()

    for rel_path in bundle:
        if rel_path.startswith(".compass/skills/") or rel_path in ("AGENTS.md", "CLAUDE.md"):
            files_to_update.append(rel_path)
        else:
            preserved_set.add(rel_path)

    # Identificar y registrar archivos de memoria viva existentes en disco
    for folder in ("docs/brain/modules", "docs/brain/decisions", "specs", "guides"):
        folder_path = target_root / folder
        if folder_path.is_dir():
            for item in folder_path.rglob("*"):
                if item.is_file():
                    preserved_set.add(item.relative_to(target_root).as_posix())

    if (target_root / "docs" / "brain" / "design.md").is_file():
        preserved_set.add("docs/brain/design.md")

    symlinks = _compute_symlinks(config.target_assistants)

    return UpdatePlan(
        config=config,
        files_to_update=tuple(sorted(files_to_update)),
        preserved_files=tuple(sorted(preserved_set)),
        symlinks_to_repair=symlinks,
    )


def apply_update(
    root: Path, config: ProjectConfig, force: bool = False
) -> UpdateResult:
    """Aplica la actualizacion del arnes en disco garantizando la inmutabilidad de la memoria viva."""
    target_root = root.resolve()
    plan = plan_update(target_root, config)
    bundle = _get_bundle_files(config)

    updated_files: list[str] = []
    skipped_files: list[str] = []

    # Actualizar unicamente archivos de infraestructura stateless
    for rel_path in plan.files_to_update:
        file_path = target_root / rel_path
        new_content = bundle[rel_path]

        if file_path.exists() and not force:
            existing_content = file_path.read_text(encoding="utf-8")
            if existing_content == new_content:
                skipped_files.append(rel_path)
                continue

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(new_content, encoding="utf-8")
        updated_files.append(rel_path)

    # Reparar / asegurar enlaces simbolicos
    repaired_symlinks: list[str] = []
    for symlink in plan.symlinks_to_repair:
        link_abs = target_root / symlink.link_path
        target_abs = target_root / symlink.target_path

        link_abs.parent.mkdir(parents=True, exist_ok=True)
        relative_target = os.path.relpath(target_abs, link_abs.parent)

        if link_abs.is_symlink():
            link_abs.unlink()
        elif link_abs.exists():
            if force:
                if link_abs.is_dir():
                    shutil.rmtree(link_abs)
                else:
                    link_abs.unlink()
            else:
                continue

        try:
            link_abs.symlink_to(relative_target, target_is_directory=True)
            repaired_symlinks.append(symlink.link_path)
        except OSError:
            if target_abs.is_dir():
                shutil.copytree(target_abs, link_abs, dirs_exist_ok=True)
            repaired_symlinks.append(symlink.link_path)

    # Persistir configuracion en .compass/config.json
    save_project_config(target_root, config)

    return UpdateResult(
        updated_files=tuple(updated_files),
        skipped_files=tuple(skipped_files),
        repaired_symlinks=tuple(repaired_symlinks),
        preserved_files=plan.preserved_files,
        config_saved=True,
    )
