import sys
from pathlib import Path

import uvicorn
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    logger.level("INFO")
    logger.info("Starting KworkNotifications app...")
    uvicorn.run(
        "KworkNotifications.app:app",
        host="127.0.0.1",
        port=5000,
        log_level="info",
        access_log=False,
    )
    return


if __name__ == "__main__":
    main()
