import json
from pathlib import Path
from datetime import datetime

from utils import ensure_dir, format_timestamp


class EvidenceLogger:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.log_dir = ensure_dir(self.root_dir / "data" / "logs")
        self.log_path = self.log_dir / "audit.log.jsonl"
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        if not self.log_path.exists():
            self.log_path.write_text("", encoding="utf-8")

    def _append(self, record):
        self._ensure_log_exists()
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    def log(self, action, case_id=None, evidence_id=None, file_name=None, user=None, details=None):
        record = {
            "timestamp": format_timestamp(datetime.utcnow()),
            "action": action,
            "case_id": case_id,
            "evidence_id": evidence_id,
            "file_name": file_name,
            "user": user,
            "details": details,
        }
        self._append(record)
        return record

    def load_logs(self, case_id=None):
        self._ensure_log_exists()
        logs = []
        with self.log_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if case_id and entry.get("case_id") != case_id:
                    continue
                logs.append(entry)
        return logs
