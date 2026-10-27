"""Browser journey through the web UI against a running container (set BASE_URL)."""

import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("BASE_URL")
RECEIPT = Path(__file__).parents[2] / "docs" / "assets" / "demo-receipt.png"

pytestmark = pytest.mark.skipif(not BASE_URL, reason="BASE_URL not set")


def open_view(page: Page, view: str) -> None:
    page.locator(f'#nav button[data-view="{view}"]').click()
    expect(page.locator(f"#view-{view}")).to_be_visible()


def add_member(page: Page, name: str) -> None:
    page.fill("#member-name", name)
    page.locator("#member-form button.btn").click()
    expect(page.locator("#members")).to_contain_text(name)


@pytest.fixture
def household(page: Page) -> Page:
    page.goto(f"{BASE_URL}/ui/")
    page.click("#household-add")
    page.fill("#household-name", "UI Flat")
    page.locator("#household-form button.btn").click()
    expect(page.locator("#toast")).to_contain_text("UI Flat created")
    for name in ("Lea", "Noah"):
        add_member(page, name)
    return page


def test_quick_add_and_settle_up(household: Page) -> None:
    page = household
    open_view(page, "overview")
    page.select_option("#quick-payer", label="Lea")
    page.fill("#quick-text", "Groceries 45.50")
    page.locator("#quick-form button").click()
    expect(page.locator("#recent-expenses")).to_contain_text("Groceries")

    open_view(page, "settle")
    transfer = page.locator("#transfers li").first
    expect(transfer).to_contain_text("Noah → Lea")
    expect(transfer).to_contain_text("22.75")
    transfer.get_by_role("button", name="Paid").click()
    expect(page.locator("#transfers")).to_contain_text("All settled")
    expect(page.locator("#settlements")).to_contain_text("Noah → Lea")


def test_chores_are_planned_fairly(household: Page) -> None:
    page = household
    open_view(page, "chores")
    for name, effort in (("Bathroom", 4), ("Trash", 1)):
        page.fill("#chore-name", name)
        page.get_by_role("button", name=f"Effort {effort}").click()
        page.locator("#chore-form button.btn").click()
        expect(page.locator("#chores")).to_contain_text(name)
    page.click("#plan-week")
    expect(page.locator("#assignments li")).to_have_count(2)
    expect(page.locator("#assignments")).to_contain_text("Lea")
    expect(page.locator("#assignments")).to_contain_text("Noah")


def test_receipt_scan_reports_the_server_answer(household: Page) -> None:
    page = household
    open_view(page, "expenses")
    page.set_input_files("#receipt-file", RECEIPT)
    toast = page.locator("#toast")
    if os.getenv("RECEIPT_PARSER", "none") == "none":
        expect(toast).to_contain_text(re.compile("switched off", re.IGNORECASE))
    else:
        expect(toast).to_contain_text("Suggested")
        expect(page.locator("#expense-amount")).not_to_have_value("")
