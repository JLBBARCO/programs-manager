"""Bump the version number stored in .github/version-compiler.txt and write
the result into the root version.txt, so the new version is available
before the application is compiled.

Usage:
    python .github/scripts/bump_version.py <branch>

<branch> should be "develop" (bumps "Pre-release") or anything else
(bumps "Latest release"). Prints the new version number to stdout.
"""

import re
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: bump_version.py <branch>", file=sys.stderr)
        return 1

    branch = sys.argv[1].strip().lower()
    key = "Pre-release" if branch == "develop" else "Latest release"
    version_compiler_path = ".github/version-compiler.txt"
    version_txt_path = "version.txt"

    with open(version_compiler_path, "r", newline="") as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped.startswith("<<<<<<< ") or stripped == "=======" or stripped.startswith(">>>>>>> "):
            print(
                f"{version_compiler_path} has unresolved git merge conflict markers. "
                "Resolve the conflict and commit before running this workflow again.",
                file=sys.stderr,
            )
            return 1

    current = None
    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped.startswith(key + "="):
            current = stripped.split("=", 1)[1].strip()
            break

    if current is None or not re.match(r"^\d+\.\d+\.\d+$", current):
        print(f"Invalid current version for {key!r}: {current!r}", file=sys.stderr)
        return 1

    major, minor, patch = current.split(".")
    new_version = f"{major}.{minor}.{int(patch) + 1}"

    with open(version_compiler_path, "w", newline="") as f:
        for line in lines:
            stripped = line.rstrip("\r\n")
            ending = line[len(stripped):] or "\r\n"
            if stripped.startswith(key + "="):
                f.write(f"{key}={new_version}{ending}")
            else:
                f.write(line)

    with open(version_txt_path, "w", newline="") as f:
        f.write(f"system_version={new_version}")

    print(new_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
