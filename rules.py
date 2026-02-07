"""더러움 판단 규칙 엔진."""

import os
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FolderReport:
    path: str
    total_files: int = 0
    extension_count: int = 0
    stale_file_count: int = 0
    score: int = 0
    reasons: list[str] = field(default_factory=list)

    @property
    def level(self) -> str:
        if self.score >= 3:
            return "critical"
        elif self.score >= 2:
            return "warning"
        elif self.score >= 1:
            return "caution"
        return "clean"


def evaluate_folder(
    folder_path: str,
    max_files: int = 20,
    max_extensions: int = 8,
    max_stale_files: int = 10,
    stale_days: int = 7,
) -> FolderReport:
    """폴더 상태를 평가하고 더러움 점수를 산출한다."""
    report = FolderReport(path=folder_path)
    path = Path(folder_path)

    if not path.exists():
        return report

    files = [f for f in path.iterdir() if f.is_file()]
    report.total_files = len(files)

    # 규칙 1: 파일 개수 초과
    if report.total_files > max_files:
        report.score += 1
        report.reasons.append(f"파일 {report.total_files}개 (기준: {max_files}개)")

    # 규칙 2: 확장자 종류 혼재
    extensions = {f.suffix.lower() for f in files if f.suffix}
    report.extension_count = len(extensions)
    if report.extension_count > max_extensions:
        report.score += 1
        report.reasons.append(
            f"확장자 {report.extension_count}종류 (기준: {max_extensions}종류)"
        )

    # 규칙 3: 오래된 파일
    now = time.time()
    stale_threshold = now - (stale_days * 86400)
    stale_files = [f for f in files if f.stat().st_mtime < stale_threshold]
    report.stale_file_count = len(stale_files)
    if report.stale_file_count > max_stale_files:
        report.score += 1
        report.reasons.append(
            f"{stale_days}일 이상 방치 파일 {report.stale_file_count}개 "
            f"(기준: {max_stale_files}개)"
        )

    return report
