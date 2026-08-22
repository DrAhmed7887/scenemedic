"""Print current billing + credit state before any paid API call.

Rule of thumb before running anything expensive:
  python -m tools.cost_check
If "Billing linked: NO" — we're safe (can't charge anything).
If "Billing linked: YES" — check the credits URL to confirm the GenAI
App Builder trial is still Available and being consumed.

Usage:
  python -m tools.cost_check
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

BILLING_ACCOUNT = os.getenv("BILLING_ACCOUNT_ID", "01C037-D624BF-1F8009")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0491760285")
LOG_PATH = Path(__file__).resolve().parents[1] / "outputs" / "cost_log.jsonl"


def log_cost(step: str, model: str, endpoint: str, expected_usd: float,
              credit_expected: str, status: str = "ok", note: str = "") -> None:
    """Append a per-step cost expectation to the session log.

    `credit_expected` should be the name of the credit we believe covers this SKU
    ("GenAI App Builder trial" | "Always Free" | "GDP monthly" | "NONE — CARD").
    Reconcile against the Credits page at end of session or 24-48h later.
    """
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "model": model,
        "endpoint": endpoint,
        "expected_usd": expected_usd,
        "credit_expected": credit_expected,
        "status": status,
        "note": note,
    }
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(row) + "\n")


def print_log() -> None:
    """Show the running session cost log."""
    if not LOG_PATH.exists():
        print("(no cost log yet)")
        return
    total = 0.0
    print(f"\n{'ts':<20} {'step':<24} {'model':<32} {'usd':>6}  credit")
    print("-" * 100)
    for line in LOG_PATH.read_text().splitlines():
        r = json.loads(line)
        print(f"{r['ts'][:19]:<20} {r['step'][:24]:<24} "
              f"{r['model'][:32]:<32} {r['expected_usd']:6.4f}  {r['credit_expected']}")
        total += r["expected_usd"]
    print("-" * 100)
    print(f"{'TOTAL EXPECTED':<77} {total:6.4f} USD  (reconcile vs Credits page in 24-48h)")


def _gcloud(*args: str) -> str:
    return subprocess.check_output(
        ["gcloud", *args, "--format=json"], text=True
    )


def project_billing_status() -> dict:
    return json.loads(_gcloud("billing", "projects", "describe", PROJECT_ID))


def list_budgets() -> list[dict]:
    out = _gcloud("billing", "budgets", "list",
                  f"--billing-account={BILLING_ACCOUNT}")
    return json.loads(out) if out.strip() else []


def print_state() -> int:
    print("=" * 60)
    print(f"COST CHECK — {date.today()}")
    print("=" * 60)

    b = project_billing_status()
    linked = bool(b.get("billingAccountName"))
    enabled = b.get("billingEnabled", False)

    print(f"\nProject:             {PROJECT_ID}")
    if not linked or not enabled:
        print("Billing linked:      NO — SAFE (no charges possible)")
        return 0
    print(f"Billing linked:      YES → {b.get('billingAccountName')}")
    print(f"Billing enabled:     True")

    print("\nBudgets on billing account:")
    budgets = list_budgets()
    if not budgets:
        print("  (none — set one before spending)")
    for bud in budgets:
        amount = bud.get("amount", {}).get("specifiedAmount", {})
        treat = bud["budgetFilter"].get("creditTypesTreatment", "?")
        print(
            f"  - {bud['displayName']:35s} cap "
            f"{amount.get('units','?')} {amount.get('currencyCode','?'):3s}  "
            f"credits: {treat}"
        )

    print("\nCredit balance + spend (browser — no public API):")
    print(f"  Credits:  https://console.cloud.google.com/billing/{BILLING_ACCOUNT}/credits")
    print(f"  Reports:  https://console.cloud.google.com/billing/{BILLING_ACCOUNT}/reports"
          f"?project={PROJECT_ID}")
    print()
    print("Safety rules:")
    print("  1. Confirm 'Trial credit for GenAI App Builder' shows > $0 on Credits page.")
    print("  2. On Reports, filter by SKU — every row must show credit applied.")
    print("  3. If any row shows uncredited spend, STOP and investigate.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(print_state())
