"""Local immutable PostgreSQL privilege-helper acceptance; no database mutation."""

import argparse
import json
import re
import shutil
import subprocess
import time
from uuid import uuid4


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", args.image):
        raise ValueError("An immutable local image ID is required")
    executable = shutil.which("docker")
    if executable is None:
        raise RuntimeError("Docker required")

    def docker(*command: str, checked: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(  # noqa: S603 — fixed executable/flags and validated image ID
            [executable, *command],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if checked and result.returncode:
            raise RuntimeError("Disposable image acceptance operation failed")
        return result

    common = [
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--cap-add",
        "SETUID",
        "--cap-add",
        "SETGID",
        "--security-opt",
        "no-new-privileges:true",
    ]
    version = docker("run", *common, args.image, "gosu", "--version").stdout.strip()
    if "1.20 (go1.27.4 " not in version:
        raise RuntimeError("Unexpected privilege helper build")
    results: dict[str, object] = {"image_id": args.image, "gosu": version}
    for user, uid in (("nobody", "65534"), ("postgres", "999"), ("10001:10001", "10001")):
        actual = docker("run", *common, args.image, "gosu", user, "id", "-u").stdout.strip()
        groups = docker("run", *common, args.image, "gosu", user, "id", "-G").stdout.split()
        if actual != uid or "0" in groups:
            raise RuntimeError("Privilege drop or supplementary-group isolation failed")
        results[user] = {"uid": actual, "groups": groups}
    invalid = docker(
        "run", *common, args.image, "gosu", "kr_nonexistent_user", "true", checked=False
    )
    elevate = docker(
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--user",
        "10001:10001",
        "--security-opt",
        "no-new-privileges:true",
        args.image,
        "gosu",
        "root",
        "sh",
        "-c",
        "echo FORBIDDEN",
        checked=False,
    )
    if invalid.returncode == 0 or elevate.returncode == 0 or "FORBIDDEN" in elevate.stdout:
        raise RuntimeError("Forbidden helper invocation succeeded")
    results["invalid_user_refused"] = True
    results["nonroot_elevation_refused"] = True
    name = "kr-m9-pr7-signal-" + uuid4().hex
    try:
        docker(
            "run",
            "-d",
            "--name",
            name,
            *common[1:],
            args.image,
            "gosu",
            "nobody",
            "sh",
            "-c",
            "trap 'exit 0' TERM; echo READY; while :; do sleep 0.2; done",
        )
        for _ in range(30):
            if "READY" in docker("logs", name).stdout:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("Signal fixture did not start")
        status = docker("exec", name, "cat", "/proc/1/status").stdout
        if not re.search(r"^Uid:\s+65534\s+65534\s+65534\s+65534$", status, re.MULTILINE):
            raise RuntimeError("Helper did not exec unprivileged PID1")
        # PostgreSQL declares STOPSIGNAL SIGINT; request TERM explicitly for this
        # helper test instead of assuming docker stop always delivers SIGTERM.
        results["image_stop_signal"] = docker(
            "inspect", "--format", "{{.Config.StopSignal}}", name
        ).stdout.strip()
        docker("kill", "--signal", "TERM", name)
        docker("wait", name)
        if docker("inspect", "--format", "{{.State.ExitCode}}", name).stdout.strip() != "0":
            raise RuntimeError("Graceful signal forwarding failed")
        results["unprivileged_pid1_and_graceful_sigterm"] = True
    finally:
        docker("rm", "--force", name, checked=False)
    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
