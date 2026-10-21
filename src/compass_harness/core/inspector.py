"""Inspector determinista de contexto de proyecto (Greenfield vs Brownfield)."""

from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path

MANIFEST_TO_STACK: dict[str, str] = {
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "setup.py": "python",
    "package.json": "node",
    "Cargo.toml": "rust",
    "go.mod": "go",
}

UI_SIGNAL_FILES: dict[str, str] = {
    "tailwind.config.js": "tailwind",
    "tailwind.config.ts": "tailwind",
    "tailwind.config.mjs": "tailwind",
    "postcss.config.js": "postcss",
    "components.json": "shadcn-ui",
    "next.config.js": "nextjs",
    "next.config.ts": "nextjs",
    "next.config.mjs": "nextjs",
    "vite.config.ts": "vite",
    "vite.config.js": "vite",
    "astro.config.mjs": "astro",
    "svelte.config.js": "svelte",
}

UI_EXTENSIONS: set[str] = {".tsx", ".jsx", ".vue", ".svelte", ".css"}

DESIGN_CONTRACT_FILES: tuple[str, ...] = ("DESIGN.md", "docs/brain/design.md")

EXTENSION_TO_STACK: dict[str, str] = {
    ".py": "python",
    ".ts": "node",
    ".js": "node",
    ".rs": "rust",
    ".go": "go",
    ".c": "c/cpp",
    ".cpp": "c/cpp",
    ".h": "c/cpp",
    ".m": "matlab",
}

IGNORED_DIRS: set[str] = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".compass",
    ".agents",
    ".claude",
}

TRACKED_DIRS: tuple[str, ...] = ("src", "tests", "docs", "specs", "guides")

HARNESS_MARKERS: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    ".compass",
    ".agents",
    ".claude",
    "docs/brain",
)


class ProjectState(str, Enum):
    """Estado base del proyecto evaluado."""

    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"


@dataclass(frozen=True)
class ProjectInspection:
    """Resultado inmutable de la inspeccion determinista de un proyecto."""

    root_path: Path
    state: ProjectState
    detected_stacks: tuple[str, ...]
    existing_dirs: tuple[str, ...]
    has_git: bool
    existing_harness_files: tuple[str, ...]
    detected_ui_signals: tuple[str, ...] = ()
    existing_design_files: tuple[str, ...] = ()


def inspect_project(target_dir: Path) -> ProjectInspection:
    """Inspecciona un directorio objetivo y determina su estado y caracteristicas."""
    if not target_dir.exists():
        raise FileNotFoundError(f"Path does not exist: {target_dir}")

    if not target_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {target_dir}")

    root = target_dir.resolve()
    has_git = (root / ".git").exists()

    detected_stacks_dict: dict[str, None] = {}
    detected_ui_dict: dict[str, None] = {}

    for manifest, stack in MANIFEST_TO_STACK.items():
        if (root / manifest).is_file():
            detected_stacks_dict[stack] = None

    for signal_file, signal_name in UI_SIGNAL_FILES.items():
        if (root / signal_file).is_file():
            detected_ui_dict[signal_name] = None

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for filename in filenames:
            ext = Path(filename).suffix.lower()
            if ext in EXTENSION_TO_STACK:
                detected_stacks_dict[EXTENSION_TO_STACK[ext]] = None
            if filename in UI_SIGNAL_FILES:
                detected_ui_dict[UI_SIGNAL_FILES[filename]] = None
            if ext in UI_EXTENSIONS:
                detected_ui_dict["frontend-components"] = None

    detected_stacks = tuple(detected_stacks_dict.keys())
    detected_ui_signals = tuple(detected_ui_dict.keys())
    existing_dirs = tuple(d for d in TRACKED_DIRS if (root / d).is_dir())
    existing_harness_files = tuple(marker for marker in HARNESS_MARKERS if (root / marker).exists())
    existing_design_files = tuple(marker for marker in DESIGN_CONTRACT_FILES if (root / marker).is_file())

    state = ProjectState.BROWNFIELD if detected_stacks else ProjectState.GREENFIELD

    return ProjectInspection(
        root_path=root,
        state=state,
        detected_stacks=detected_stacks,
        existing_dirs=existing_dirs,
        has_git=has_git,
        existing_harness_files=existing_harness_files,
        detected_ui_signals=detected_ui_signals,
        existing_design_files=existing_design_files,
    )
