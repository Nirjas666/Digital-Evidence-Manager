import csv
import json
from pathlib import Path

from utils import ensure_dir, format_timestamp


class ReportExporter:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.report_dir = ensure_dir(self.root_dir / "data" / "reports")

    def export_json(self, case_metadata, logs, output_path=None):
        output_path = self._get_output_path(output_path, suffix="json")
        report = {
            "generated_at": format_timestamp(),
            "case": case_metadata,
            "audit_logs": logs,
        }
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
        return output_path

    def export_csv(self, case_metadata, logs, output_path=None):
        output_path = self._get_output_path(output_path, suffix="csv")
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Case ID", case_metadata["case_id"]])
            writer.writerow(["Case Name", case_metadata["case_name"]])
            writer.writerow(["Description", case_metadata.get("description", "")])
            writer.writerow(["Created At", case_metadata.get("created_at", "")])
            writer.writerow([])
            writer.writerow(["Evidence ID", "Original Name", "Stored Name", "SHA256", "Tags", "Status", "Added At", "Added By"])
            for evidence in case_metadata.get("evidence", []):
                writer.writerow([
                    evidence.get("evidence_id"),
                    evidence.get("original_name"),
                    evidence.get("stored_name"),
                    evidence.get("sha256"),
                    ";".join(evidence.get("tags", [])),
                    evidence.get("status"),
                    evidence.get("added_at"),
                    evidence.get("added_by"),
                ])
            writer.writerow([])
            writer.writerow(["Audit Log Entries"])
            writer.writerow(["Timestamp", "Action", "Case ID", "Evidence ID", "File Name", "User", "Details"])
            for log in logs:
                writer.writerow([
                    log.get("timestamp"),
                    log.get("action"),
                    log.get("case_id"),
                    log.get("evidence_id"),
                    log.get("file_name"),
                    log.get("user"),
                    json.dumps(log.get("details", {}), ensure_ascii=False),
                ])
        return output_path

    def export_text(self, case_metadata, logs, output_path=None):
        output_path = self._get_output_path(output_path, suffix="txt")
        lines = [
            f"Case Report: {case_metadata['case_name']}",
            f"Case ID: {case_metadata['case_id']}",
            f"Created At: {case_metadata.get('created_at')}",
            f"Description: {case_metadata.get('description', '')}",
            "",
            "Evidence Summary:",
        ]
        for evidence in case_metadata.get("evidence", []):
            lines.extend([
                f"  - Evidence ID: {evidence.get('evidence_id')}",
                f"    Original Name: {evidence.get('original_name')}",
                f"    Stored Name: {evidence.get('stored_name')}",
                f"    SHA256: {evidence.get('sha256')}",
                f"    Status: {evidence.get('status')}",
                f"    Tags: {', '.join(evidence.get('tags', []))}",
                f"    Added At: {evidence.get('added_at')}",
                f"    Added By: {evidence.get('added_by')}",
                "",
            ])
        lines.append("Audit Log Summary:")
        for log in logs:
            lines.append(
                f"  [{log.get('timestamp')}] {log.get('action')} by {log.get('user')} - file={log.get('file_name')} details={json.dumps(log.get('details', {}), ensure_ascii=False)}"
            )
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def _get_output_path(self, output_path, suffix):
        if output_path is None:
            output_path = self.report_dir / f"report_{format_timestamp().replace(' ', '_').replace(':', '-')}.{suffix}"
        else:
            output_path = Path(output_path)
            ensure_dir(output_path.parent)
        return output_path
