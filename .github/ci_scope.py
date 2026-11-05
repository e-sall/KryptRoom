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
# Policy/classifier changes are shared and fail closed. They are not documentation.
M9_WORKFLOW = ".github/workflows/control-api-foundation.yml"
M9_WORKFLOW_HASHES = {
    # Exact c99d8f5 PR1 recipe, and the separately reviewed explicit-scope follow-up.
    "9588eac2e7b840c09a3c6500df51369fb18694e98ca3050143182277eea6deef",
    "88e12beb2ddcdce0fd56de63f00c46b8f8644e4080a698efea7f4f6ec86d267d",
}
M9_FILES = {
    "services/control-api/.gitkeep", "services/control-api/.dockerignore",
    "services/control-api/.gitattributes", "services/control-api/.gitignore",
    "services/control-api/.python-version", "services/control-api/Dockerfile",
    "services/control-api/README.md", "services/control-api/alembic.ini",
    "services/control-api/compose.yml", "services/control-api/pyproject.toml",
    "services/control-api/uv.lock", "services/control-api/requirements.lock",
    "services/control-api/requirements-dev.lock",
}
M9_PREFIXES = (
    "services/control-api/src/kryptroom_control/", "services/control-api/migrations/",
    "services/control-api/scripts/", "services/control-api/tests/", "docs/m9/",
)
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


def same_events_and_execution(before, after):
    def events(text):
        found = re.search(r"^on:\n(?:[ \t].*\n|\n|#.*\n)*", text.replace("\r\n", "\n"), re.M)
        return found.group(0) if found else None
    return (before and after and events(before) == events(after) and
            workflow_execution(before) == workflow_execution(after))


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

# One downstream synthetic-vector refresh, not historical proof/chain evidence.
M7_MIGRATION_FILES = {
    "tests/chain_anchor/fixtures/state-proof.json": (
        "55ec723b51ea52defa59688a180da6feea07e4815161cd673401ac62ba7304d4",
        "425fbe7b5424b7bcb6737f18853c44ed1d014afa009faa37db101a0c4bd2e5d1",
    ),
    "tests/chain_anchor/fixtures/vectors.json": (
        "95fa998eb32fb4ee7edced2daa865162fae9b839d7812039fcd8289957ac77b8",
        "a4bde7cf4c96d05fd92f3f84b05f3d99da0591c25abff93fe9d77d0242b31039",
    ),
}


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

def exact_m7_fixture_migration(paths, read_before, read_after):
    if set(paths) & set(M7_MIGRATION_FILES) != set(M7_MIGRATION_FILES):
        return False
    for path, (old, new) in M7_MIGRATION_FILES.items():
        if content_hash(read_before(path)) != old or content_hash(read_after(path)) != new:
            return False
    # Full PR: the complete, previously authorized M5 migration must match.
    if set(paths) & set(MIGRATION_FILES):
        return exact_fixture_migration(paths, read_before, read_after)
    # Follow-up push: all M5 files must already be the exact migrated bytes.
    for path, (_, expected) in MIGRATION_FILES.items():
        if content_hash(read_before(path)) != expected or content_hash(read_after(path)) != expected:
            return False
    for path, expected in MIGRATION_S1.items():
        if content_hash(read_before(path)) != expected or content_hash(read_after(path)) != expected:
            return False
    return all(content_hash(read(MIGRATION_WORKFLOW)) == MIGRATION_NEW_WORKFLOW
               for read in (read_before, read_after))


def requires_core(paths, read_before, read_after):
    if not paths:
        return True
    migration = exact_fixture_migration(paths, read_before, read_after)
    m7_migration = exact_m7_fixture_migration(paths, read_before, read_after)
    for path in paths:
        if migration and path in MIGRATION_FILES:
            continue
        if migration and path == MIGRATION_WORKFLOW:
            continue  # exact old/new hashes were already verified with the complete migration
        if m7_migration and path in M7_MIGRATION_FILES:
            continue
        if path.startswith(("apps/web/", "docs/m8/")) or path in DOCS:
            continue
        if m9_path(path) or exact_m9_workflow(path, read_before, read_after):
            continue
        if path == M9_WORKFLOW:
            return True  # no generic trigger-only exemption for an unrecognized M9 recipe
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")):
            before, after = read_before(path), read_after(path)
            if same_events_and_execution(before, after):
                continue
        return True
    return False


def m9_path(path):
    return path in M9_FILES or path.startswith(M9_PREFIXES)


def exact_m9_workflow(path, read_before, read_after):
    if path != M9_WORKFLOW:
        return False
    before, after = read_before(path), read_after(path)
    return (content_hash(after) in M9_WORKFLOW_HASHES and
            (before is None or content_hash(before) in M9_WORKFLOW_HASHES))


def core_only_path(path):
    # Shared manifests, CI/security policy and unknown paths intentionally are NOT here.
    return (path.startswith(("engines/", "nodes/", "tests/", "chain/")) or
            path in {"package.json", "package-lock.json"} or path.startswith("compose."))


def classify_paths(paths, read_before, read_after):
    if not paths:
        return {"core": True, "web": True, "m9": True}
    core = requires_core(paths, read_before, read_after)
    web = m9 = False
    metadata_only = all(path in DOCS for path in paths)
    migration = exact_fixture_migration(paths, read_before, read_after)
    m7_migration = exact_m7_fixture_migration(paths, read_before, read_after)
    for path in paths:
        if path in DOCS:
            continue  # contextual changelog entries do not turn M9 into a frontend change
        if path.startswith(("apps/web/", "docs/m8/")):
            web = True
        elif m9_path(path) or exact_m9_workflow(path, read_before, read_after):
            m9 = True
        elif path == M9_WORKFLOW:
            web = m9 = True
        elif ((migration and path in MIGRATION_FILES) or
              (m7_migration and path in M7_MIGRATION_FILES) or core_only_path(path)):
            continue
        elif path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")):
            before, after = read_before(path), read_after(path)
            if not same_events_and_execution(before, after):
                web = m9 = True
        else:
            web = m9 = True  # shared contracts/security/CI/unknown: all relevant consumers
    return {"core": core, "web": web or metadata_only, "m9": m9 or metadata_only}


def event_diff(event_name, event, read_git=git):
    if event_name not in ("pull_request", "push"):
        return None  # workflow_dispatch and any future event retain full execution
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

    return paths, lambda p: at(base, p), lambda p: at(head, p)


def classify_event(event_name, event, read_git=git):
    diff = event_diff(event_name, event, read_git)
    return True if diff is None else requires_core(*diff)


def classify_scopes_event(event_name, event, read_git=git):
    diff = event_diff(event_name, event, read_git)
    return {"core": True, "web": True, "m9": True} if diff is None else classify_paths(*diff)


if __name__ == "__main__":
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    scopes = classify_scopes_event(os.environ["GITHUB_EVENT_NAME"], event)
    print(json.dumps(scopes, sort_keys=True))
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        for name, enabled in scopes.items():
            output.write(f"{name}={str(enabled).lower()}\n")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write("CI applicability: " + json.dumps(scopes, sort_keys=True) + "\n")
