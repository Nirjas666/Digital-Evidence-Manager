import shutil
import uuid
from pathlib import Path

from file_hasher import compute_sha256, verify_file
from logger import EvidenceLogger
from utils import ensure_dir, load_json, save_json, normalize_tags


class EvidenceManager:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.case_root = ensure_dir(self.root_dir / "data" / "cases")
        self.logger = EvidenceLogger(root_dir)

    def create_case(self, case_name, description=None, created_by="System"):
        case_id = str(uuid.uuid4())
        case_dir = self.case_root / case_id
        ensure_dir(case_dir)

        metadata = {
            "case_id": case_id,
            "case_name": case_name,
            "description": description or "",
            "created_by": created_by,
            "created_at": None,
            "evidence": [],
        }
        metadata["created_at"] = self._current_timestamp()
        save_json(case_dir / "metadata.json", metadata)
        self.logger.log("CREATE_CASE", case_id=case_id, user=created_by, details={"case_name": case_name})
        return metadata

    def list_cases(self):
        cases = []
        for case_dir in self.case_root.iterdir():
            if case_dir.is_dir():
                metadata_path = case_dir / "metadata.json"
                if metadata_path.exists():
                    cases.append(load_json(metadata_path, {}))
        return sorted(cases, key=lambda item: item.get("created_at", ""))

    def get_case(self, case_id):
        metadata_path = self.case_root / case_id / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Case metadata not found for case_id={case_id}")
        return load_json(metadata_path, {})

    def add_evidence(self, case_id, source_path, tags, added_by="Investigator"):
        case_dir = self.case_root / case_id
        if not case_dir.exists():
            raise FileNotFoundError(f"Case not found: {case_id}")

        source_path = Path(source_path)
        if not source_path.exists() or not source_path.is_file():
            raise FileNotFoundError(f"Evidence file not found: {source_path}")

        evidence_id = str(uuid.uuid4())
        file_hash = compute_sha256(source_path)
        tags = normalize_tags(tags)

        duplicate_case, duplicate_evidence = self._find_duplicate_hash(file_hash)
        warnings = []
        if duplicate_evidence:
            warnings.append(
                f"Duplicate hash detected in case {duplicate_case}, evidence {duplicate_evidence['evidence_id']}"
            )

        stored_file_name = f"{evidence_id}_{source_path.name}"
        stored_file_path = case_dir / stored_file_name
        shutil.copy2(source_path, stored_file_path)

        evidence_data = {
            "evidence_id": evidence_id,
            "original_name": source_path.name,
            "stored_name": stored_file_name,
            "stored_path": str(stored_file_path.resolve()),
            "sha256": file_hash,
            "tags": tags,
            "added_by": added_by,
            "added_at": self._current_timestamp(),
            "status": "UNVERIFIED",
            "duplicate_hash_warning": warnings,
        }

        metadata = self.get_case(case_id)
        metadata["evidence"].append(evidence_data)
        save_json(case_dir / "metadata.json", metadata)
        self.logger.log(
            "ADD_EVIDENCE",
            case_id=case_id,
            evidence_id=evidence_id,
            file_name=source_path.name,
            user=added_by,
            details={"tags": tags, "warnings": warnings},
        )
        return evidence_data

    def verify_evidence(self, case_id, evidence_id, verified_by="Investigator"):
        metadata = self.get_case(case_id)
        evidence = next((item for item in metadata["evidence"] if item["evidence_id"] == evidence_id), None)
        if evidence is None:
            raise ValueError(f"Evidence not found: {evidence_id}")

        stored_path = Path(evidence["stored_path"])
        if not stored_path.exists():
            raise FileNotFoundError(f"Stored evidence missing: {stored_path}")

        is_safe, current_hash = verify_file(stored_path, evidence["sha256"])
        evidence["last_verified_at"] = self._current_timestamp()
        evidence["last_verified_by"] = verified_by
        evidence["current_hash"] = current_hash
        evidence["status"] = "SAFE" if is_safe else "TAMPERED"
        save_json(self.case_root / case_id / "metadata.json", metadata)

        self.logger.log(
            "VERIFY_EVIDENCE",
            case_id=case_id,
            evidence_id=evidence_id,
            file_name=evidence["original_name"],
            user=verified_by,
            details={"result": evidence["status"]},
        )
        return evidence["status"]

    def search_evidence(self, query=None, tags=None, case_id=None):
        query = (query or "").lower()
        tags = normalize_tags(tags)
        found = []
        for case in self.list_cases():
            if case_id and case["case_id"] != case_id:
                continue
            for ev in case["evidence"]:
                name_match = query in ev["original_name"].lower() or query in ev["stored_name"].lower()
                tag_match = not tags or any(tag in ev["tags"] for tag in tags)
                if query and not name_match:
                    continue
                if not tag_match:
                    continue
                entry = {**ev, "case_name": case["case_name"], "case_id": case["case_id"]}
                found.append(entry)
        return found

    def get_case_logs(self, case_id):
        return self.logger.load_logs(case_id=case_id)

    def _find_duplicate_hash(self, file_hash):
        for case in self.list_cases():
            for evidence in case.get("evidence", []):
                if evidence.get("sha256") == file_hash:
                    return case["case_id"], evidence
        return None, None

    def _current_timestamp(self):
        from datetime import datetime

        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
