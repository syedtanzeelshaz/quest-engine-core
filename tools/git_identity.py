import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class GitIdentity:
    name: str
    email: str


def get_git_identity() -> GitIdentity:
    """
    Returns the Git user's configured name and email.
    Git resolves these from the repository/global Git configuration.
    """
    try:
        name = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        email = subprocess.run(
            ["git", "config", "--get", "user.email"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        return GitIdentity(
            name=name or "Unknown",
            email=email or "Unknown",
        )
    except (subprocess.CalledProcessError, OSError):
        return GitIdentity(
            name="Unknown",
            email="Unknown",
        )