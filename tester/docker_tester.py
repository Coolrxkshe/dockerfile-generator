import subprocess
import tempfile
import os
import shutil
from pathlib import Path


def is_docker_running() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def test_dockerfile(dockerfile_content: str) -> dict:
    if not is_docker_running():
        return {
            "success": False,
            "error": "Docker is not running. Please start Docker Desktop.",
            "logs": [],
            "image_size": None,
            "build_time": None,
        }

    tmp_dir = tempfile.mkdtemp(prefix="dockertest_")
    image_tag = "dockergen-test:latest"

    try:
        # Write Dockerfile to temp dir
        dockerfile_path = os.path.join(tmp_dir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)

        # Run docker build
        import time
        start = time.time()

        result = subprocess.run(
            ["docker", "build", "-t", image_tag, "--no-cache", tmp_dir],
            capture_output=True,
            text=True,
            timeout=300
        )

        elapsed = round(time.time() - start, 1)
        logs = (result.stdout + result.stderr).strip().splitlines()

        if result.returncode == 0:
            # Get image size
            size_result = subprocess.run(
                ["docker", "image", "inspect", image_tag,
                 "--format", "{{.Size}}"],
                capture_output=True, text=True
            )
            size_bytes = 0
            if size_result.returncode == 0:
                try:
                    size_bytes = int(size_result.stdout.strip())
                except Exception:
                    pass

            size_mb = round(size_bytes / 1e6, 1)

            # Cleanup image
            subprocess.run(
                ["docker", "rmi", image_tag, "-f"],
                capture_output=True
            )

            return {
                "success":    True,
                "error":      None,
                "logs":       logs,
                "image_size": f"{size_mb} MB",
                "build_time": f"{elapsed}s",
            }
        else:
            # Find the error line
            error_line = ""
            for line in reversed(logs):
                if line.strip() and "ERROR" in line.upper():
                    error_line = line.strip()
                    break
            if not error_line and logs:
                error_line = logs[-1].strip()

            return {
                "success":    False,
                "error":      error_line,
                "logs":       logs,
                "image_size": None,
                "build_time": f"{elapsed}s",
            }

    except subprocess.TimeoutExpired:
        return {
            "success":    False,
            "error":      "Build timed out after 5 minutes.",
            "logs":       [],
            "image_size": None,
            "build_time": "timeout",
        }
    except Exception as e:
        return {
            "success":    False,
            "error":      str(e),
            "logs":       [],
            "image_size": None,
            "build_time": None,
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)