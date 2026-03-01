"""
helpers.py

Miscellaneous helper utilities for Smart Attendance System.

This module contains:
- File helpers
- Date / time helpers
- CSV export helpers
- Safe string utilities

No database or authentication logic should live here.
"""

import os
import csv
import uuid
from datetime import datetime, date
from typing import List, Dict, Any


# ==============================
# FILE & PATH HELPERS
# ==============================

def ensure_directory(path: str) -> None:
    """
    Ensure a directory exists.
    Creates it if missing.
    """
    os.makedirs(path, exist_ok=True)


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename while preserving extension.
    Used for profile images, uploads, etc.
    """
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4().hex}{ext}"


# ==============================
# DATE & TIME HELPERS
# ==============================

def today_date() -> date:
    """Return today's date (UTC-safe)."""
    return date.today()


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.utcnow()


def format_date(value: date | datetime) -> str:
    """
    Format date or datetime consistently for responses / exports.
    """
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return ""


# ==============================
# CSV EXPORT HELPERS
# ==============================

def export_to_csv(
    filename: str,
    headers: List[str],
    rows: List[Dict[str, Any]],
    directory: str = "exports"
) -> str:
    """
    Export rows of dicts to CSV file.

    Returns the file path.
    """
    ensure_directory(directory)

    filepath = os.path.join(directory, filename)

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return filepath


# ==============================
# STRING & DATA HELPERS
# ==============================

def normalize_email(email: str) -> str:
    """Normalize email for comparisons."""
    return email.strip().lower()


def safe_str(value: Any) -> str:
    """
    Convert value to string safely.
    Avoids None -> 'None'
    """
    return "" if value is None else str(value)


# ==============================
# PAGINATION HELPER (OPTIONAL)
# ==============================

def paginate(items: List[Any], page: int = 1, size: int = 20) -> Dict[str, Any]:
    """
    Simple in-memory pagination helper.
    Useful for admin views.
    """
    start = (page - 1) * size
    end = start + size

    return {
        "page": page,
        "size": size,
        "total": len(items),
        "items": items[start:end],
    }
