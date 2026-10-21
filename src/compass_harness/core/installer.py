"""Motor de instalacion y onboarding de compass-harness."""

from dataclasses import dataclass
import os
from pathlib import Path
import shutil

from compass_harness.core.renderer import ProjectConfig, render_project_bundle

ASSISTANT_SKILL_DIRS: dict[str, str] = {
    "antigravity": ".agents/skills",
    "codex": ".agents/skills",
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
}

SKILL_NAMES: tuple[str, ...] = (
    "tdd",
    "project-architect",
    "sdd-workflow",
    "mentor-guide",
    "ui-design",
)

DIRECTORIES_TO_ENSURE: tuple[str, ...] = (
    "docs/brain/modules",
    "specs",
    "guides",
)


@dataclass(frozen=True)
class SymlinkSpec:
    """Especificacion de un enlace simbolico relativo para una skill."""

    link_path: str
    target_path: str


@dataclass(frozen=True)
class InstallationPlan:
    """Plan determinista de instalacion sin efectos secundarios."""

    config: ProjectConfig
    files_to_create: tuple[str, ...]
    existing_conflicts: tuple[str, ...]
    symlinks_to_create: tuple[SymlinkSpec, ...]
    directories_to_ensure: tuple[str, ...] = DIRECTORIES_TO_ENSURE


@dataclass(frozen=True)
class InstallationResult:
    """Resultado tras la aplicacion de la instalacion en disco."""

    written_files: tuple[str, ...]
    skipped_files: tuple[str, ...]
    created_symlinks: tuple[str, ...]
    ensured_directories: tuple[str, ...] = DIRECTORIES_TO_ENSURE


def render_claude_md(config: ProjectConfig) -> str:
    """Renderiza el archivo puente CLAUDE.md referenciando AGENTS.md."""
    return f"""# Claude Guide: {config.project_name}

Este proyecto utiliza el Meta-Harness Compass.
Para instrucciones de desarrollo, flujos de trabajo y memoria del proyecto, consulta:
- `AGENTS.md`
- `docs/brain/index.md`
"""


def _get_bundle_files(config: ProjectConfig) -> dict[str, str]:
    bundle = render_project_bundle(config)
    if "claude" in config.target_assistants:
        bundle["CLAUDE.md"] = render_claude_md(config)
    return bundle


def _compute_symlinks(target_assistants: tuple[str, ...]) -> tuple[SymlinkSpec, ...]:
    skill_dirs: list[str] = []
    for assistant in target_assistants:
        normalized = assistant.strip().lower()
        if normalized in ASSISTANT_SKILL_DIRS:
            directory = ASSISTANT_SKILL_DIRS[normalized]
            if directory not in skill_dirs:
                skill_dirs.append(directory)

    symlinks: list[SymlinkSpec] = []
    for directory in skill_dirs:
        for skill in SKILL_NAMES:
            symlinks.append(
                SymlinkSpec(
                    link_path=f"{directory}/{skill}",
                    target_path=f".compass/skills/{skill}",
                )
            )
    return tuple(symlinks)


def plan_installation(root: Path, config: ProjectConfig) -> InstallationPlan:
    """Calcula el plan de instalacion sin modificar el sistema de archivos."""
    target_root = root.resolve()
    bundle = _get_bundle_files(config)

    files_to_create: list[str] = []
    existing_conflicts: list[str] = []

    for rel_path in bundle:
        file_path = target_root / rel_path
        if file_path.exists():
            existing_conflicts.append(rel_path)
        else:
            files_to_create.append(rel_path)

    symlinks = _compute_symlinks(config.target_assistants)

    return InstallationPlan(
        config=config,
        files_to_create=tuple(files_to_create),
        existing_conflicts=tuple(existing_conflicts),
        symlinks_to_create=symlinks,
        directories_to_ensure=DIRECTORIES_TO_ENSURE,
    )


def apply_installation(
    root: Path, config: ProjectConfig, force: bool = False
) -> InstallationResult:
    """Aplica la instalacion en disco, creando archivos, directorios y symlinks."""
    target_root = root.resolve()
    plan = plan_installation(target_root, config)

    ensured_dirs: list[str] = []
    for directory in plan.directories_to_ensure:
        dir_path = target_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        ensured_dirs.append(directory)

    bundle = _get_bundle_files(config)
    written_files: list[str] = []
    skipped_files: list[str] = []

    for rel_path, content in bundle.items():
        file_path = target_root / rel_path
        if file_path.exists() and not force:
            skipped_files.append(rel_path)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            written_files.append(rel_path)

    created_symlinks: list[str] = []
    for symlink in plan.symlinks_to_create:
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
            created_symlinks.append(symlink.link_path)
        except OSError:
            if target_abs.is_dir():
                shutil.copytree(target_abs, link_abs, dirs_exist_ok=True)
            created_symlinks.append(symlink.link_path)

    return InstallationResult(
        written_files=tuple(written_files),
        skipped_files=tuple(skipped_files),
        created_symlinks=tuple(created_symlinks),
        ensured_directories=tuple(ensured_dirs),
    )
