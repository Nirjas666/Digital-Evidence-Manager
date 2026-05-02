# Digital Evidence Organizer (Cyber Forensics Tool)

A Python-based digital forensics simulator that supports chain-of-custody workflows, evidence hashing, case management, tagging, integrity verification, and report export.

## Features

- SHA256 evidence hashing and tamper detection
- Evidence tagging and metadata storage
- Chain-of-custody logging with append-only audit records
- Multiple case management with directory-based storage
- Automatic UUID generation for all evidence items
- Case export to JSON, CSV, and plain text
- Search evidence by filename, tags, or case ID
- Interactive CLI menu with colorized terminal output
- Duplicate evidence hash detection and warning
- Robust error handling for missing files and invalid inputs

## Project Structure

```text
digital_evidence_organizer/
│── main.py
│── evidence_manager.py
│── file_hasher.py
│── logger.py
│── exporter.py
│── utils.py
│── __init__.py
│── requirements.txt
│── README.md
│── data/
│    ├── cases/
│    ├── logs/
```

## Installation

1. Clone or download the repository.
2. Navigate to the project folder:

```bash
cd "d:\cybersecurity\Digital Evidence Manager\digital_evidence_organizer"
```

3. Install required dependencies:

```bash
python -m pip install -r requirements.txt
```

## How to Run

Run the interactive CLI:

```bash
python main.py
```

Follow the on-screen menu to create cases, add evidence, verify integrity, search items, and export reports.

## Example Workflow

1. Create a new case with a case name and investigator name.
2. Add an evidence file by path and supply tags such as `critical`, `suspicious`, or `benign`.
3. Verify evidence integrity to compare the stored SHA256 hash with the current file.
4. Export case reports into JSON, CSV, and text files in `data/reports/`.
5. Review the append-only audit log at `data/logs/audit.log.jsonl`.

## Notes

- All case metadata is saved under `data/cases/<case_id>/metadata.json`.
- Evidence files are copied into their associated case folder to maintain a case-based evidence store.
- The audit log is written as newline-delimited JSON for easy review and parsing.

## License

This project is provided as example code for digital evidence management and chain-of-custody simulation.
