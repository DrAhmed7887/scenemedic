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
from datetime import date

BILLING_ACCOUNT = os.getenv("BILLING_ACCOUNT_ID", "01C037-D624BF-1F8009")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0491760285")


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
