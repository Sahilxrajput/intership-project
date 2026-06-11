from pathlib import Path
from datetime import datetime, timedelta
import shutil
import time

from app.utils.logger import get_logger

logger = get_logger(__name__)

WORKSPACE_ROOT = Path("workspaces")


def cleanup_old_workspaces(max_age_hours: int = 24):
    if not WORKSPACE_ROOT.exists():
        return

    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

    for workspace in WORKSPACE_ROOT.iterdir():

        if not workspace.is_dir():
            continue

        try:
            modified_time = datetime.fromtimestamp(workspace.stat().st_mtime)

            if modified_time < cutoff_time:
                shutil.rmtree(workspace)

                logger.info(f"Deleted workspace: {workspace.name}")

        except Exception as e:
            logger.error(f"Failed deleting {workspace}: {e}")


def cleanup_worker():
    while True:

        cleanup_old_workspaces(max_age_hours=24)

        time.sleep(3600)  # every hour
