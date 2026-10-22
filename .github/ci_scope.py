"""Only decide CI scope; never import or execute KryptRoom runtime code."""

import hashlib
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


# One owner-authorized migration, NOT a fixtures-directory exemption.
# These are SHA-256 of exact Git file bytes (no JSON normalization).
MIGRATION_PREFIX = "tests/state_proof/fixtures/"
MIGRATION_FILES = {
    MIGRATION_PREFIX + "S3_model.content.json": (
        "0995e7ecd45325e45f2e4de880d4cc8bf16e7a7d7aa2484595f0051ab6ff3e9d",
        "2bc12db60f5946e4e63596218fa577367ab476f48a5b1b8d2dd457e9ac0513d4",
    ),
    MIGRATION_PREFIX + "S3_model.json": (
        "984e4615612dd5f0339b5407b91400bb1c1b46a3fa7499335559d6c9689f048e",
        "8809ef3a666f73c58131f5678328687eb8d797ab0a53af63f97ed32631dff3c1",
    ),
    MIGRATION_PREFIX + "S4_eval.content.json": (
        "4783c68ffbae1b11475a009ccd421b15045287929143d0f975cb1842933d7a62",
        "bf73e16f59a924dcf4fff4c8bef8d32d656a2a80cdfbb153c2b61b3776338af1",
    ),
    MIGRATION_PREFIX + "S4_eval.json": (
        "e45cdbe4feb80505f9eafce07fa96f1afa2c2c629a5c08ec901506c732423df9",
        "314fec8325dac68bc58f8d6ae142cea9c5f4bba824e8f31ff5dc5658ce677699",
    ),
    MIGRATION_PREFIX + "receipt.json": (
        "1d5635f4b02ffd35c4978829eddf583106e712427cfdfcc90db3bfc0188dcbb1",
        "97498500cef2deac9d4ce59e44cefaf14254ad9b5d4f6c667c9cdfcf3049c27b",
    ),
    MIGRATION_PREFIX + "hashes.json": (
        "a0509064df3d753e685d1a6139f8e5187fddfa5032fdb0b504282b6eb1d9abea",
        "e31fcbec1ee15d0208620812aa41b17de27e4a5cd5dafaf40b7547846bb71c2f",
    ),
}
MIGRATION_S1 = {
    MIGRATION_PREFIX + "S1.json": "2ee643313bd23afb177aecc688c31052be6265e57763f4f8a95ddd28e2d1713b",
    MIGRATION_PREFIX + "S1.content.json": "cb23d577ab92e930d861c5bc3146be7539afe29f9ecc05001620d141daf87c7c",
}
MIGRATION_WORKFLOW = ".github/workflows/private-nn.yml"
MIGRATION_OLD_WORKFLOW = "d66c581c73dbe1953f73fc573d9377da3e792b350bc0f516475e57fef5ff5449"
MIGRATION_NEW_WORKFLOW = "490a46ad8295011b53f9399fc09de26b3f039d4a0c19958e7ef52951eee39c66"


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text is not None else None


def exact_fixture_migration(paths, read_before, read_after):
    if set(paths) & set(MIGRATION_FILES) != set(MIGRATION_FILES):
        return False  # no partial refresh, addition or deletion
    for path, (old, new) in MIGRATION_FILES.items():
        if content_hash(read_before(path)) != old or content_hash(read_after(path)) != new:
            return False
    for path, expected in MIGRATION_S1.items():
        if content_hash(read_before(path)) != expected or content_hash(read_after(path)) != expected:
            return False
    # A PR from dev includes the approved trigger change; a follow-up push starts
    # from its already-approved workflow bytes. Both end at the exact same bytes.
    before = content_hash(read_before(MIGRATION_WORKFLOW))
    after = content_hash(read_after(MIGRATION_WORKFLOW))
    return before in {MIGRATION_OLD_WORKFLOW, MIGRATION_NEW_WORKFLOW} and after == MIGRATION_NEW_WORKFLOW

def requires_core(paths, read_before, read_after):
    if not paths:
        return True
    migration = exact_fixture_migration(paths, read_before, read_after)
    for path in paths:
        if migration and path in MIGRATION_FILES:
            continue
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
