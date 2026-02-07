"""메인 모니터링 스크립트 - rules + notifier 조합."""

import sys
from pathlib import Path

import yaml

from rules import evaluate_folder
from notifier import send_notification

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run() -> None:
    config = load_config()

    for folder_cfg in config["folders"]:
        report = evaluate_folder(
            folder_path=folder_cfg["path"],
            max_files=folder_cfg.get("max_files", 20),
            max_extensions=folder_cfg.get("max_extensions", 8),
            max_stale_files=folder_cfg.get("max_stale_files", 10),
            stale_days=folder_cfg.get("stale_days", 7),
        )

        if report.level != "clean":
            print(
                f"[{report.level.upper()}] {report.path}: "
                f"score={report.score}, files={report.total_files}"
            )
            for reason in report.reasons:
                print(f"  - {reason}")
            send_notification(report)
        else:
            print(f"[CLEAN] {report.path}: files={report.total_files}")


if __name__ == "__main__":
    run()
