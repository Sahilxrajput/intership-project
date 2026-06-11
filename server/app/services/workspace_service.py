from pathlib import Path
import uuid
import shutil


class WorkspaceService:

    ROOT = Path("workspaces")

    @classmethod
    def create_workspace(cls) -> Path:
        cls.ROOT.mkdir(exist_ok=True)

        workspace_id = str(uuid.uuid4())

        workspace = cls.ROOT / workspace_id

        workspace.mkdir(parents=True)

        return workspace

    @classmethod
    def cleanup_workspace(cls, workspace_id: str):
        path = cls.ROOT / workspace_id

        if path.exists():
            shutil.rmtree(path)
