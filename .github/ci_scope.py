"""Only decide CI scope; never import or execute KryptRoom runtime code."""

import json
import os
from pathlib import Path
import re
import subprocess


DOCS = {
    "ARCHITECTURE.md", "PROJECT_CONTEXT.md", "CHANGELOG.md", "TODO.md",
    "docs/DECISIONS.md",
}
FILTER_FILES = {
    ".github/ci_scope.py", ".github/test_ci_scope.py",
    ".github/workflows/web-foundation.yml",
}
GATE = "  change-scope:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    outputs:\n      core: ${{ steps.scope.outputs.core }}\n    steps:\n      - uses: actions/checkout@v7\n        with:\n          fetch-depth: 0\n          persist-credentials: false\n      - id: scope\n        run: python3 .github/ci_scope.py\n\n"
CONDITION = "    needs: change-scope\n    if: ${{ needs.change-scope.outputs.core == 'true' }}\n"


def git(*args):
    return subprocess.check_output(["git", *args]).decode("utf-8")


def workflow_execution(text):
    # Only event filters and our exact scope plumbing may be ignored. Any change
    # to commands, images, dependencies, permissions, env, runners, or other job
    # conditions remains core-sensitive. Unknown/new workflows also remain core.
    text = text.replace("\r\n", "\n")
    text = re.sub(r"^on:\n(?:[ \t].*\n|\n|#.*\n)*", "", text, flags=re.M)
    return text.replace(GATE, "").replace(CONDITION, "")


def requires_core(paths, read_before, read_after):
    if not paths:
        return True
    for path in paths:
        if path.startswith(("apps/web/", "docs/m8/")) or path in DOCS | FILTER_FILES:
            continue
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")):
            before, after = read_before(path), read_after(path)
            if before and after and workflow_execution(before) == workflow_execution(after):
                continue
        return True
    return False


def classify_event(event_name, event, read_git=git):
    if event_name not in ("pull_request", "push"):
        return True  # workflow_dispatch and any future event retain full execution
    if event_name == "pull_request":
        base = event["pull_request"]["base"]["sha"]
        head = event["pull_request"]["head"]["sha"]
        base = read_git("merge-base", base, head).strip()
    else:
        base, head = event["before"], event["after"]
        if not base or set(base) == {"0"}:
            # New feature branch: compare the complete branch against dev, not
            # HEAD^ (which would miss core changes in earlier feature commits).
            base = read_git("merge-base", "origin/dev", head).strip()
    for sha in (base, head):
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("Invalid event commit")
    # No GitHub 300-file path limit or REST pagination. --no-renames includes
    # both sides of a move, preventing core -> frontend rename bypasses.
    paths = read_git("diff", "--no-renames", "--name-only", "-z", base, head).split("\0")
    paths = [path for path in paths if path]

    def at(revision, path):
        try:
            return read_git("show", f"{revision}:{path}")
        except subprocess.CalledProcessError:
            return None

    return requires_core(paths, lambda p: at(base, p), lambda p: at(head, p))


if __name__ == "__main__":
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    core = classify_event(os.environ["GITHUB_EVENT_NAME"], event)
    value = str(core).lower()
    print(f"Core integration required: {value}")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"core={value}\n")
