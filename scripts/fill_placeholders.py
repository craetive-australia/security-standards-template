#!/usr/bin/env python3
"""
Automated placeholder population and discovery script for the ISMS repository.
Replaces standardized placeholders across Markdown documentation and MkDocs configuration.
"""

import argparse
import glob
import json
import os
import re
import sys
from typing import Dict, List, Tuple


def setup_console_encoding() -> None:
    """Ensure sys.stdout and sys.stderr handle UTF-8 and unicode safely across all platforms."""
    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def find_target_files(base_dir: str, docs_dir: str) -> List[str]:
    """Locate all markdown files in docs_dir and mkdocs.yml in base_dir."""
    # Resolve docs_path: check relative to base_dir, then relative to cwd, then absolute
    docs_path = docs_dir if os.path.isabs(docs_dir) else os.path.join(base_dir, docs_dir)
    if not os.path.isdir(docs_path) and os.path.isdir(docs_dir):
        docs_path = os.path.abspath(docs_dir)

    if not os.path.isdir(docs_path):
        print(f"Error: Documentation directory '{docs_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    md_files = glob.glob(os.path.join(docs_path, "**/*.md"), recursive=True)

    target_files = sorted(md_files)
    candidate_mkdocs = os.path.join(os.path.dirname(docs_path), "mkdocs.yml")
    if os.path.isfile(candidate_mkdocs):
        target_files.append(candidate_mkdocs)
    else:
        mkdocs_file = os.path.join(base_dir, "mkdocs.yml")
        if os.path.isfile(mkdocs_file):
            target_files.append(mkdocs_file)

    return target_files


def scan_remaining_placeholders(files: List[str]) -> List[Tuple[str, int, str]]:
    """Scan files for remaining unpopulated placeholder tags like [COMPANY_NAME], [CISO_NAME], etc."""
    # Pattern: [TAG] where TAG starts with uppercase letter and contains uppercase letters, numbers, underscores
    # Excludes Markdown links via negative lookahead on ( and [
    pattern = re.compile(r"\[([A-Z][A-Z0-9_]+)\](?![\[\(])")
    remaining = []
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    for match in pattern.finditer(line):
                        remaining.append((filepath, line_no, match.group(0)))
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
    return remaining


def process_replacements(
    files: List[str],
    replacements: Dict[str, str],
    dry_run: bool = False
) -> Tuple[int, int, Dict[str, int]]:
    """
    Perform replacements in target files.
    Returns (modified_files_count, total_replacements_count, replacements_by_key).
    """
    modified_files_count = 0
    total_replacements_count = 0
    replacement_counts: Dict[str, int] = {k: 0 for k in replacements}

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            file_replacements = 0
            new_content = content
            is_yaml = filepath.endswith((".yml", ".yaml"))
            for placeholder, value in replacements.items():
                count = new_content.count(placeholder)
                if count > 0:
                    target_val = value.replace("'", "''") if is_yaml else value
                    new_content = new_content.replace(placeholder, target_val)
                    replacement_counts[placeholder] += count
                    file_replacements += count

            if file_replacements > 0:
                modified_files_count += 1
                total_replacements_count += file_replacements
                if dry_run:
                    print(f"[DRY-RUN] Would update {filepath}: {file_replacements} placeholder(s) replaced")
                else:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated {filepath}: {file_replacements} placeholder(s) replaced")
        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)

    return modified_files_count, total_replacements_count, replacement_counts


def main():
    setup_console_encoding()
    parser = argparse.ArgumentParser(
        description="Replace placeholders in ISMS Markdown documents and mkdocs.yml."
    )
    parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Directory containing markdown files (default: docs)"
    )
    parser.add_argument(
        "--config",
        help="Optional YAML or JSON configuration file defining placeholder key-value pairs"
    )
    parser.add_argument("--company-name", help="Value for [COMPANY_NAME]")
    parser.add_argument("--ciso-name", help="Value for [CISO_NAME]")
    parser.add_argument("--author-name", help="Value for [AUTHOR_NAME]")
    parser.add_argument("--dpo-name", help="Value for [DPO_NAME]")
    parser.add_argument("--insert-date", help="Value for [INSERT_DATE]")
    parser.add_argument("--applicable-regulations", help="Value for [APPLICABLE_REGULATIONS]")
    parser.add_argument("--industry-sector", help="Value for [INDUSTRY_SECTOR]")
    parser.add_argument("--org-structure", help="Value for [ORG_STRUCTURE]")
    parser.add_argument("--isms-scope", help="Value for [ISMS_SCOPE]")
    parser.add_argument(
        "--min-password-length",
        type=int,
        default=14,
        help="Value for [MIN_PASSWORD_LENGTH] (default: 14)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate replacements without writing changes to disk"
    )
    parser.add_argument(
        "--list-remaining",
        action="store_true",
        help="Discover and display remaining unpopulated placeholders"
    )

    args = parser.parse_args()

    # Determine base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_files = find_target_files(base_dir, args.docs_dir)

    if not target_files:
        print(f"No target files found in {os.path.join(base_dir, args.docs_dir)} or {base_dir}.", file=sys.stderr)
        sys.exit(1)

    # Build replacements dictionary
    replacements = {}
    if args.config:
        if not os.path.isfile(args.config):
            print(f"Error: Configuration file '{args.config}' does not exist.", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.config, "r", encoding="utf-8") as cf:
                if args.config.lower().endswith(".json"):
                    cfg_data = json.load(cf)
                else:
                    import yaml
                    cfg_data = yaml.safe_load(cf)
            if isinstance(cfg_data, dict):
                for raw_key, raw_val in cfg_data.items():
                    if raw_val is not None and str(raw_val) != "":
                        norm_key = raw_key.upper().replace("-", "_")
                        if not norm_key.startswith("["):
                            norm_key = f"[{norm_key}]"
                        replacements[norm_key] = str(raw_val)
        except Exception as e:
            print(f"Error loading configuration file '{args.config}': {e}", file=sys.stderr)
            sys.exit(1)

    if args.company_name:
        replacements["[COMPANY_NAME]"] = args.company_name
    if args.ciso_name:
        replacements["[CISO_NAME]"] = args.ciso_name
    if args.author_name:
        replacements["[AUTHOR_NAME]"] = args.author_name
    if args.dpo_name:
        replacements["[DPO_NAME]"] = args.dpo_name
    if args.insert_date:
        replacements["[INSERT_DATE]"] = args.insert_date
    if args.applicable_regulations:
        replacements["[APPLICABLE_REGULATIONS]"] = args.applicable_regulations
    if args.industry_sector:
        replacements["[INDUSTRY_SECTOR]"] = args.industry_sector
    if args.org_structure:
        replacements["[ORG_STRUCTURE]"] = args.org_structure
    if args.isms_scope:
        replacements["[ISMS_SCOPE]"] = args.isms_scope
    if args.min_password_length is not None and (
        replacements or any(arg.startswith("--min-password-length") for arg in sys.argv)
    ):
        replacements["[MIN_PASSWORD_LENGTH]"] = str(args.min_password_length)

    # Check if any action was requested
    has_replacements = len(replacements) > 0
    if not has_replacements and not args.list_remaining:
        if args.dry_run:
            print("No placeholder arguments provided for dry-run. Exiting.")
            sys.exit(0)
        else:
            print("Error: No placeholder arguments provided. Specify at least one placeholder or --list-remaining.", file=sys.stderr)
            sys.exit(1)

    # Execute replacements if requested
    if has_replacements:
        mode_label = "DRY-RUN" if args.dry_run else "APPLY"
        print(f"--- Executing Placeholder Replacement ({mode_label}) ---")
        for k, v in replacements.items():
            print(f"  {k} => '{v}'")
        print()

        mod_files, total_reps, counts_by_key = process_replacements(
            target_files, replacements, dry_run=args.dry_run
        )

        print()
        print(f"Summary ({mode_label}):")
        print(f"  Files modified: {mod_files} / {len(target_files)}")
        print(f"  Total replacements: {total_reps}")
        for k, c in counts_by_key.items():
            print(f"    {k}: {c}")
        print()

    # Execute list-remaining if requested
    if args.list_remaining:
        print("--- Scanning for Remaining Placeholders ---")
        remaining = scan_remaining_placeholders(target_files)
        if remaining:
            print(f"Found {len(remaining)} unpopulated placeholder(s):")
            # Group by tag
            by_tag: Dict[str, List[Tuple[str, int]]] = {}
            for fpath, lno, tag in remaining:
                rel_path = os.path.relpath(fpath, base_dir)
                by_tag.setdefault(tag, []).append((rel_path, lno))

            for tag, occurrences in sorted(by_tag.items()):
                print(f"\nPlaceholder {tag} ({len(occurrences)} occurrences):")
                for rel_path, lno in occurrences:
                    print(f"  {rel_path}:{lno}")
        else:
            print("No unpopulated placeholders found.")
        print()

    sys.exit(0)


if __name__ == "__main__":
    main()
