import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from colorama import Fore, Style, init

from evidence_manager import EvidenceManager
from exporter import ReportExporter
from utils import normalize_tags
from file_hasher import SUPPORTED_ALGORITHMS


def print_title():
    print(Fore.CYAN + "\nDigital Evidence Organizer (Cyber Forensics Tool)" + Style.RESET_ALL)
    print(Fore.CYAN + "======================================" + Style.RESET_ALL)


def print_menu():
    print(Fore.GREEN + "\nSelect an action:" + Style.RESET_ALL)
    print("1. Create case")
    print("2. Add evidence to case")
    print("3. Verify evidence integrity")
    print("4. Search evidence")
    print("5. Export case report")
    print("6. List cases")
    print("7. Exit")


def prompt(text):
    return input(Fore.BLUE + text + Style.RESET_ALL).strip()


def show_error(message):
    print(Fore.RED + "ERROR: " + str(message) + Style.RESET_ALL)


def show_success(message):
    print(Fore.GREEN + str(message) + Style.RESET_ALL)


def show_info(message):
    print(Fore.YELLOW + str(message) + Style.RESET_ALL)


def display_case(case):
    print(Fore.MAGENTA + f"\nCase: {case['case_name']} ({case['case_id']})" + Style.RESET_ALL)
    print(f"  Description: {case.get('description', '')}")
    print(f"  Created At : {case.get('created_at')}")
    print(f"  Evidence count: {len(case.get('evidence', []))}")


def display_evidence(evidence):
    print(Fore.WHITE + f"\nEvidence ID: {evidence['evidence_id']}" + Style.RESET_ALL)
    print(f"  Name: {evidence['original_name']}")
    print(f"  Stored File: {evidence['stored_name']}")
    alg = (evidence.get('hash_algorithm') or ('sha256' if evidence.get('sha256') else 'sha256')).upper()
    hashv = evidence.get('hash') or evidence.get('sha256') or ''
    print(f"  Hash ({alg}): {hashv}")
    print(f"  Status: {evidence.get('status')}")
    print(f"  Tags: {', '.join(evidence.get('tags', []))}")
    if evidence.get("duplicate_hash_warning"):
        print(Fore.YELLOW + "  Warning: " + "; ".join(evidence.get("duplicate_hash_warning")) + Style.RESET_ALL)


def main():
    init(autoreset=True)
    root_dir = Path(__file__).resolve().parent
    manager = EvidenceManager(root_dir)
    exporter = ReportExporter(root_dir)

    print_title()
    while True:
        print_menu()
        choice = prompt("Enter choice (1-7): ")

        try:
            if choice == "1":
                case_name = prompt("Case name: ")
                description = prompt("Description (optional): ")
                created_by = prompt("Investigator name: ") or "Investigator"
                case = manager.create_case(case_name, description, created_by)
                show_success(f"Created case {case['case_id']}")

            elif choice == "2":
                case_id = prompt("Case ID: ")
                file_path = prompt("Evidence file path: ")
                tags = normalize_tags(prompt("Tags (comma-separated): "))
                added_by = prompt("Investigator name: ") or "Investigator"
                alg_input = prompt(f"Hash algorithm [{', '.join(sorted(SUPPORTED_ALGORITHMS))}] (default sha256): ")
                algorithm = alg_input.strip().lower() or "sha256"
                if algorithm not in SUPPORTED_ALGORITHMS:
                    show_info(f"Unsupported algorithm '{algorithm}', falling back to sha256.")
                    algorithm = "sha256"
                evidence = manager.add_evidence(case_id, file_path, tags, added_by, algorithm=algorithm)
                show_success(f"Added evidence {evidence['evidence_id']}")
                if evidence.get("duplicate_hash_warning"):
                    show_info("Duplicate hash detected: " + "; ".join(evidence["duplicate_hash_warning"]))

            elif choice == "3":
                case_id = prompt("Case ID: ")
                evidence_id = prompt("Evidence ID: ")
                verified_by = prompt("Investigator name: ") or "Investigator"
                status = manager.verify_evidence(case_id, evidence_id, verified_by)
                if status == "SAFE":
                    show_success("Evidence integrity verified: SAFE")
                else:
                    show_error("Evidence integrity failure: TAMPERED")

            elif choice == "4":
                query = prompt("Search filename or case substring (optional): ")
                tags = prompt("Search tags (comma-separated, optional): ")
                case_id = prompt("Case ID filter (optional): ")
                results = manager.search_evidence(query=query, tags=tags, case_id=case_id or None)
                if not results:
                    show_info("No matching evidence found.")
                for item in results:
                    display_evidence(item)
                    print(f"  Case: {item['case_name']} ({item['case_id']})")

            elif choice == "5":
                case_id = prompt("Case ID: ")
                case = manager.get_case(case_id)
                logs = manager.get_case_logs(case_id)
                json_path = exporter.export_json(case, logs)
                csv_path = exporter.export_csv(case, logs)
                txt_path = exporter.export_text(case, logs)
                show_success(f"Exported report to:\n  {json_path}\n  {csv_path}\n  {txt_path}")

            elif choice == "6":
                cases = manager.list_cases()
                if not cases:
                    show_info("No cases registered yet.")
                for case in cases:
                    display_case(case)

            elif choice == "7":
                show_success("Exiting Digital Evidence Organizer.")
                break
            else:
                show_error("Invalid selection. Choose a number from 1 to 7.")
        except Exception as exc:
            show_error(exc)


if __name__ == "__main__":
    main()
