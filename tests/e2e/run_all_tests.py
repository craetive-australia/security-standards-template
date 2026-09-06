"""
Master E2E Test Suite Runner
Runs Tiers 1-4 compliance-as-code test suites for security-standards-template,
formats unified summary reports, and controls exit codes.
"""

import argparse
import subprocess
import sys
import time
import unittest
from pathlib import Path

# Add tests/e2e directory to sys.path so modules can be imported
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(CURRENT_DIR))

try:
    import yaml  # noqa: F401
except ModuleNotFoundError:
    candidate_venvs = [
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / ".venv" / "bin" / "python",
    ]
    for venv_py in candidate_venvs:
        if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
            sys.exit(subprocess.call([str(venv_py), *sys.argv]))
    raise

import test_tier1_static
import test_tier2_mkdocs_build
import test_tier3_automation
import test_tier4_governance_audit

TIERS = {
    1: {
        "name": "Tier 1: Static Checks, Syntax & Structure",
        "module": test_tier1_static,
        "test_class": test_tier1_static.TestTier1Static,
    },
    2: {
        "name": "Tier 2: MkDocs Strict Build & Navigation Parity",
        "module": test_tier2_mkdocs_build,
        "test_class": test_tier2_mkdocs_build.TestTier2MkDocsBuild,
    },
    3: {
        "name": "Tier 3: Automation Tooling Validation",
        "module": test_tier3_automation,
        "test_class": test_tier3_automation.TestTier3Automation,
    },
    4: {
        "name": "Tier 4: Governance, Auditing & Harmonization",
        "module": test_tier4_governance_audit,
        "test_class": test_tier4_governance_audit.TestTier4GovernanceAudit,
    },
}


def run_tier(tier_num: int, verbosity: int = 1) -> dict:
    """Runs a specific test tier and returns execution metrics."""
    tier_info = TIERS[tier_num]
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(tier_info["test_class"])

    print(f"\n{'='*70}")
    print(f"RUNNING: {tier_info['name']}")
    print(f"{'='*70}")

    runner = unittest.TextTestRunner(verbosity=verbosity)
    start_time = time.time()
    result = runner.run(suite)
    duration = time.time() - start_time

    return {
        "tier": tier_num,
        "name": tier_info["name"],
        "total": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
        "duration": duration,
        "success": result.wasSuccessful(),
    }


def main():
    parser = argparse.ArgumentParser(description="Master E2E Test Suite Runner")
    parser.add_argument(
        "--tier",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Specific test tier to run (default: all)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose test execution output",
    )
    args = parser.parse_args()

    verbosity = 2 if args.verbose else 1

    selected_tiers = [1, 2, 3, 4] if args.tier == "all" else [int(args.tier)]
    tier_results = []
    overall_success = True

    print("\n" + "=" * 70)
    print("STARTING SECURITY-STANDARDS-TEMPLATE E2E TEST RUNNER")
    print(f"Target Repository Root: {REPO_ROOT}")
    print(f"Tiers Selected: {selected_tiers}")
    print("=" * 70)

    for tier_num in selected_tiers:
        res = run_tier(tier_num, verbosity=verbosity)
        tier_results.append(res)
        if not res["success"]:
            overall_success = False

    # Summary Report
    print("\n" + "=" * 70)
    print("E2E TEST SUITE SUMMARY REPORT")
    print("=" * 70)
    print(f"{'Tier':<6} | {'Status':<8} | {'Pass':<5} | {'Fail':<5} | {'Err':<5} | {'Time':<7} | Tier Name")
    print("-" * 70)

    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_time = 0.0

    for r in tier_results:
        status_str = "PASS" if r["success"] else "FAIL"
        print(
            f"Tier {r['tier']:<1} | {status_str:<8} | {r['passed']:<5} | {r['failures']:<5} | "
            f"{r['errors']:<5} | {r['duration']:<6.2f}s | {r['name']}"
        )
        total_tests += r["total"]
        total_passed += r["passed"]
        total_failed += r["failures"]
        total_errors += r["errors"]
        total_time += r["duration"]

    print("-" * 70)
    print(
        f"TOTAL  | {'PASS' if overall_success else 'FAIL':<8} | {total_passed:<5} | {total_failed:<5} | "
        f"{total_errors:<5} | {total_time:<6.2f}s"
    )
    print("=" * 70)

    if overall_success:
        print("\nSUCCESS: All executed test tiers passed cleanly!")
        sys.exit(0)
    else:
        print("\nFAILURE: One or more test tiers experienced failures or errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
