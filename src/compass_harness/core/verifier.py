"""Motor de auditoria y verificacion del arnes de ingenieria (Compass Verifier)."""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional

REQUIRED_BRAIN_FILES: tuple[str, ...] = (
    "AGENTS.md",
    "docs/brain/index.md",
    "docs/brain/architecture.md",
    "docs/brain/handoff.md",
    "docs/brain/decisions/index.md",
)
AGENTS_MAX_LINES = 99
HANDOFF_MAX_LINES = 30
DESIGN_MAX_LINES = 80
ASSISTANT_SKILL_DIRS: tuple[str, ...] = (
    ".agents/skills",
    ".claude/skills",
    ".cursor/skills",
)
TASK_HEADER_PATTERN = re.compile(r"^-\s*\[([ xX])\]\s*(.*)$")
OBSERVED_PROOF_HEADER_PATTERN = re.compile(
    r"^\s*(?:-\s*)?(?:\*{0,2}|#{1,6}\s*)(?:Prueba Observada|Observed Proof)\*{0,2}\s*:",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SpecProgress:
    """Progreso de implementacion de una feature segun su spec y tasks.md."""

    spec_id: str
    has_spec_md: bool = False
    has_plan_md: bool = False
    has_tasks_md: bool = False
    total_tasks: int = 0
    completed_tasks: int = 0
    tasks_missing_proof: tuple[str, ...] = ()


@dataclass(frozen=True)
class CheckIssue:
    """Problema o incumplimiento detectado durante la auditoria."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class HarnessReport:
    """Resultado consolidado de la auditoria del arnes."""

    is_installed: bool
    present_brain_files: tuple[str, ...] = ()
    missing_brain_files: tuple[str, ...] = ()
    installed_skills: tuple[str, ...] = ()
    active_symlinks: tuple[str, ...] = ()
    broken_symlinks: tuple[str, ...] = ()
    specs_progress: tuple[SpecProgress, ...] = ()
    issues: tuple[CheckIssue, ...] = ()
    has_design_contract: bool = False
    has_agent_eyes: bool = False

    @property
    def passed(self) -> bool:
        """Indica si el arnes esta completamente instalado y sin incidencias."""
        return self.is_installed and len(self.issues) == 0


def _parse_tasks_file(content: str) -> list[tuple[bool, str, list[str]]]:
    """Parsea el contenido de tasks.md retornando lista de (completada, titulo, lineas_cuerpo)."""
    tasks: list[tuple[bool, str, list[str]]] = []
    current_task: Optional[tuple[bool, str, list[str]]] = None

    for line in content.splitlines():
        match = TASK_HEADER_PATTERN.match(line.strip())
        if match:
            if current_task is not None:
                tasks.append(current_task)
            is_done = match.group(1).lower() == "x"
            title = match.group(2).strip()
            current_task = (is_done, title, [])
        elif current_task is not None:
            current_task[2].append(line)

    if current_task is not None:
        tasks.append(current_task)

    return tasks


def _has_valid_observed_proof(body_lines: list[str]) -> bool:
    """Determina si las lineas del cuerpo de una tarea contienen evidencia de prueba observada valida."""
    found_idx = -1
    for i, line in enumerate(body_lines):
        if OBSERVED_PROOF_HEADER_PATTERN.match(line):
            found_idx = i
            break

    if found_idx == -1:
        return False

    proof_lines = body_lines[found_idx:]
    first_line_rest = proof_lines[0].split(":", 1)[1] if ":" in proof_lines[0] else ""
    all_content = "\n".join([first_line_rest] + proof_lines[1:])
    cleaned = all_content.strip(" \t\r\n*:_")

    if not cleaned:
        return False

    if (
        "*(pendiente)*" in all_content.lower()
        or "*(pending)*" in all_content.lower()
        or "(pendiente)" in cleaned.lower()
        or "(pending)" in cleaned.lower()
    ):
        return False

    return True


def verify_harness(root: Path) -> HarnessReport:
    """Audita de forma determinista el estado e invariantes del arnes en el proyecto."""
    root_path = Path(root).resolve()
    issues: list[CheckIssue] = []

    # 1. Inspeccion de archivos del Cerebro
    present_brain: list[str] = []
    missing_brain: list[str] = []
    for file_rel in REQUIRED_BRAIN_FILES:
        target = root_path / file_rel
        if target.is_file():
            present_brain.append(file_rel)
        else:
            missing_brain.append(file_rel)
            issues.append(
                CheckIssue(
                    code="MISSING_BRAIN_FILE",
                    path=file_rel,
                    message=f"Archivo obligatorio del cerebro ausente: {file_rel}",
                )
            )

    is_installed = (root_path / "AGENTS.md").is_file() or (root_path / "docs/brain/index.md").is_file()

    # 2. Presupuesto de contexto
    agents_file = root_path / "AGENTS.md"
    if agents_file.is_file():
        agents_lines = agents_file.read_text(encoding="utf-8").splitlines()
        if len(agents_lines) > AGENTS_MAX_LINES:
            issues.append(
                CheckIssue(
                    code="BUDGET_EXCEEDED",
                    path="AGENTS.md",
                    message=f"AGENTS.md excede el presupuesto maximo de {AGENTS_MAX_LINES} lineas ({len(agents_lines)} lineas).",
                )
            )

    handoff_file = root_path / "docs/brain/handoff.md"
    if handoff_file.is_file():
        handoff_lines = handoff_file.read_text(encoding="utf-8").splitlines()
        if len(handoff_lines) > HANDOFF_MAX_LINES:
            issues.append(
                CheckIssue(
                    code="BUDGET_EXCEEDED",
                    path="docs/brain/handoff.md",
                    message=f"docs/brain/handoff.md excede el presupuesto maximo de {HANDOFF_MAX_LINES} lineas ({len(handoff_lines)} lineas).",
                )
            )

    # 2.1 Presupuesto y validez del contrato de diseno UI (docs/brain/design.md) y Agent Eyes
    design_file = root_path / "docs/brain/design.md"
    has_design_contract = False
    if design_file.is_file():
        has_design_contract = True
        design_lines = design_file.read_text(encoding="utf-8").splitlines()
        if len(design_lines) > DESIGN_MAX_LINES:
            issues.append(
                CheckIssue(
                    code="BUDGET_EXCEEDED",
                    path="docs/brain/design.md",
                    message=f"docs/brain/design.md excede el presupuesto maximo de {DESIGN_MAX_LINES} lineas ({len(design_lines)} lineas).",
                )
            )
        content_lower = "\n".join(design_lines).lower()
        has_tokens = "token" in content_lower or "paleta" in content_lower
        has_typography = "typograph" in content_lower or "tipograf" in content_lower
        if not (has_tokens and has_typography):
            issues.append(
                CheckIssue(
                    code="INCOMPLETE_DESIGN_CONTRACT",
                    path="docs/brain/design.md",
                    message="docs/brain/design.md esta incompleto: debe incluir secciones de Design Tokens y Typography.",
                )
            )

    arch_file = root_path / "docs/brain/architecture.md"
    has_agent_eyes = False
    if arch_file.is_file():
        arch_text = arch_file.read_text(encoding="utf-8")
        for line in arch_text.splitlines():
            if "E2E / Browser UI Tests" in line and ":" in line:
                cmd_val = line.split(":", 1)[1].strip(" `\t")
                if cmd_val and cmd_val.upper() != "N/A":
                    has_agent_eyes = True
                break

    # 3. Aislamiento O(1) de decisiones tecnicas en docs/brain/index.md
    index_file = root_path / "docs/brain/index.md"
    if index_file.is_file():
        index_content = index_file.read_text(encoding="utf-8")
        index_lines = index_content.splitlines()
        decision_lines = [line for line in index_lines if "decisions/" in line]
        if "decisions/index.md" not in index_content:
            issues.append(
                CheckIssue(
                    code="ADR_INDEX_BLOAT",
                    path="docs/brain/index.md",
                    message="docs/brain/index.md debe enlazar al sub-indice decisions/index.md.",
                )
            )
        elif len(decision_lines) > 1:
            issues.append(
                CheckIssue(
                    code="ADR_INDEX_BLOAT",
                    path="docs/brain/index.md",
                    message=(
                        f"docs/brain/index.md contiene {len(decision_lines)} referencias a decisions/; "
                        "debe mantener aislamiento O(1) enlazando unicamente a decisions/index.md."
                    ),
                )
            )

    # 4. Inspeccion de Skills y Enlaces Simbolicos
    installed_skills: list[str] = []
    compass_skills_dir = root_path / ".compass" / "skills"
    if compass_skills_dir.is_dir():
        for item in sorted(compass_skills_dir.iterdir()):
            if item.is_dir() and (item / "SKILL.md").is_file():
                installed_skills.append(item.name)

    active_symlinks: list[str] = []
    broken_symlinks: list[str] = []
    for assistant_rel in ASSISTANT_SKILL_DIRS:
        assistant_dir = root_path / assistant_rel
        if assistant_dir.is_dir():
            for entry in sorted(assistant_dir.iterdir()):
                if entry.is_symlink():
                    rel_path = f"{assistant_rel}/{entry.name}"
                    if not entry.exists():
                        broken_symlinks.append(rel_path)
                        issues.append(
                            CheckIssue(
                                code="BROKEN_SYMLINK",
                                path=rel_path,
                                message=f"Enlace simbolico roto: {rel_path} apunta a un destino inexistente.",
                            )
                        )
                    else:
                        active_symlinks.append(rel_path)

    # 5. Auditoria de specs/*/tasks.md
    specs_progress: list[SpecProgress] = []
    specs_dir = root_path / "specs"
    if specs_dir.is_dir():
        for spec_dir in sorted(specs_dir.iterdir()):
            if spec_dir.is_dir():
                spec_id = spec_dir.name
                has_spec_md = (spec_dir / "spec.md").is_file()
                has_plan_md = (spec_dir / "plan.md").is_file()
                tasks_file = spec_dir / "tasks.md"
                has_tasks_md = tasks_file.is_file()

                total_tasks = 0
                completed_tasks = 0
                tasks_missing_proof: list[str] = []

                if has_tasks_md:
                    tasks_content = tasks_file.read_text(encoding="utf-8")
                    parsed_tasks = _parse_tasks_file(tasks_content)
                    total_tasks = len(parsed_tasks)

                    for is_done, title, body_lines in parsed_tasks:
                        if is_done:
                            completed_tasks += 1
                            if not _has_valid_observed_proof(body_lines):
                                tasks_missing_proof.append(title)
                                issues.append(
                                    CheckIssue(
                                        code="MISSING_OBSERVED_PROOF",
                                        path=f"specs/{spec_id}/tasks.md",
                                        message=f"Tarea completada sin evidencia de Prueba Observada: {title}",
                                    )
                                )

                specs_progress.append(
                    SpecProgress(
                        spec_id=spec_id,
                        has_spec_md=has_spec_md,
                        has_plan_md=has_plan_md,
                        has_tasks_md=has_tasks_md,
                        total_tasks=total_tasks,
                        completed_tasks=completed_tasks,
                        tasks_missing_proof=tuple(tasks_missing_proof),
                    )
                )

    return HarnessReport(
        is_installed=is_installed,
        present_brain_files=tuple(present_brain),
        missing_brain_files=tuple(missing_brain),
        installed_skills=tuple(installed_skills),
        active_symlinks=tuple(active_symlinks),
        broken_symlinks=tuple(broken_symlinks),
        specs_progress=tuple(specs_progress),
        issues=tuple(issues),
        has_design_contract=has_design_contract,
        has_agent_eyes=has_agent_eyes,
    )
