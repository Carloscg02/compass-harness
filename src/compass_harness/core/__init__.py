"""Modulo core para logica de dominio de compass-harness."""

from compass_harness.core.inspector import (
    ProjectInspection,
    ProjectState,
    inspect_project,
)
from compass_harness.core.installer import (
    InstallationPlan,
    InstallationResult,
    SymlinkSpec,
    apply_installation,
    plan_installation,
)
from compass_harness.core.renderer import (
    ProjectConfig,
    render_project_bundle,
)
from compass_harness.core.verifier import (
    CheckIssue,
    HarnessReport,
    SpecProgress,
    verify_harness,
)

__all__ = [
    "CheckIssue",
    "HarnessReport",
    "InstallationPlan",
    "InstallationResult",
    "ProjectConfig",
    "ProjectInspection",
    "ProjectState",
    "SpecProgress",
    "SymlinkSpec",
    "apply_installation",
    "inspect_project",
    "plan_installation",
    "render_project_bundle",
    "verify_harness",
]
