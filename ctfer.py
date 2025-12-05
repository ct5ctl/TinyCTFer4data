import os
from pathlib import Path
import docker
from docker.models.containers import Container

SCRIPT_DIR = Path(__file__).resolve().parent

class Ctfer:
    def __init__(self, vnc_port, workspace):
        self.image = "l3yx/sandbox:latest"
        self.volumes = [
            f"{SCRIPT_DIR/'claude_code'}:/opt/claude_code:ro",
            f"{workspace}:/home/ubuntu/Workspace"
        ]
        self.environment = {
            "ANTHROPIC_BASE_URL": os.getenv("ANTHROPIC_BASE_URL"),
            "ANTHROPIC_AUTH_TOKEN": os.getenv("ANTHROPIC_AUTH_TOKEN"),
            "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL"),
            "NO_CODESERVER": "true"
        }
        self.ports = {
            f"{vnc_port}":"5901",
        }

        self.docker_client = docker.DockerClient()
        self.container:Container = self.docker_client.containers.run(
            image=self.image,
            volumes=self.volumes,
            environment=self.environment,
            ports=self.ports,
            detach=True,
            remove=True
        )

    def __del__(self):
        self.container.stop(timeout=5)