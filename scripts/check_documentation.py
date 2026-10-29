"""
OpenAPI Documentation & Route Consistency Checker.
Automation tool that verifies whether implemented API routes match documented specifications.
Fails with exit code 1 if required endpoints are missing, returning 0 if compliant.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, Set, Tuple

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Required inventory of REST endpoints for Capstone 48
EXPECTED_ENDPOINTS = {
    ("GET", "/health"): "Service health check probe",
    ("GET", "/api/v1/books"): "List books with pagination and search",
    ("GET", "/api/v1/books/{book_id}"): "Retrieve single book by ID",
    ("POST", "/api/v1/books"): "Create new book in inventory",
    ("PUT", "/api/v1/books/{book_id}"): "Complete replacement update of book",
    ("PATCH", "/api/v1/books/{book_id}"): "Partial update of book",
    ("DELETE", "/api/v1/books/{book_id}"): "Delete book when permitted",
    ("POST", "/api/v1/books/{book_id}/borrow"): "Borrow an available book",
    ("POST", "/api/v1/books/{book_id}/return"): "Return a borrowed book",
    ("GET", "/api/v1/borrowings"): "List borrowing records with pagination",
}


def load_openapi_spec(url: str, file_path: str) -> Tuple[Dict[str, Any], str]:
    """Attempt to load OpenAPI spec from live URL, fallback to local file, or direct FastAPI app."""
    # 1. Try live HTTP server if requests is available
    try:
        import requests
        resp = requests.get(f"{url.rstrip('/')}/openapi.json", timeout=2.0)
        if resp.status_code == 200:
            return resp.json(), f"Live HTTP Server ({url})"
    except Exception:
        pass

    # 2. Try saved openapi.json file
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data, f"Local Spec File ({file_path})"
        except Exception as exc:
            print(f"[!] Warning: Could not read {file_path}: {exc}")

    # 3. Fallback: extract directly from FastAPI application object
    try:
        from app.main import app
        schema = app.openapi()
        return schema, "Direct FastAPI Application Object"
    except Exception as exc:
        print(f"[!] Critical Error: Unable to inspect FastAPI application: {exc}", file=sys.stderr)
        sys.exit(1)


def normalize_path(path: str) -> str:
    """Standardize path parameter notation."""
    return path.rstrip("/") if path != "/" else "/"


def run_checks(spec: Dict[str, Any], source_desc: str) -> int:
    """Compare OpenAPI spec paths and methods against expected inventory."""
    print("=" * 70)
    print("  CAPSTONE 48: REST API DOCUMENTATION CONSISTENCY VERIFIER")
    print("=" * 70)
    print(f"[*] Spec Source: {source_desc}")
    print(f"[*] Spec Title:  {spec.get('info', {}).get('title', 'Unknown')}")
    print(f"[*] Version:     {spec.get('info', {}).get('version', 'Unknown')}")
    print("-" * 70)

    documented_endpoints: Set[Tuple[str, str]] = set()
    paths = spec.get("paths", {})

    for path, operations in paths.items():
        for method, details in operations.items():
            if method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}:
                documented_endpoints.add((method.upper(), path))

    missing_endpoints = []
    for (expected_method, expected_path), desc in EXPECTED_ENDPOINTS.items():
        if (expected_method, expected_path) not in documented_endpoints:
            missing_endpoints.append((expected_method, expected_path, desc))

    # Print Inventory Status
    print(f"\n[+] Verified Documented Endpoints ({len(documented_endpoints)} total found):")
    for (method, path) in sorted(documented_endpoints):
        is_required = (method, path) in EXPECTED_ENDPOINTS
        flag = "[REQUIRED]" if is_required else "[EXTRA/DOC]"
        print(f"  {flag:<12} {method:<6} {path}")

    # Evaluate results
    print("\n" + "-" * 70)
    print("VERIFICATION SUMMARY:")
    if missing_endpoints:
        print(f"[FAILED] {len(missing_endpoints)} required endpoints are MISSING from OpenAPI documentation:\n")
        for method, path, desc in missing_endpoints:
            print(f"  [X] {method:<6} {path:<32} -> {desc}")
        print("\nResult: Non-compliant with capstone specification (Exit code: 1).")
        return 1
    else:
        print(f"[PASSED] All {len(EXPECTED_ENDPOINTS)} required endpoints are correctly documented!")
        print(f"[PASSED] OpenAPI schema complies with REST API Design Kit requirements.")
        print("\nResult: Fully compliant with capstone specification (Exit code: 0).")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Verify REST API route and OpenAPI documentation consistency.")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base URL of running FastAPI server.")
    parser.add_argument("--file", default="openapi/openapi.json", help="Path to static openapi.json file.")
    args = parser.parse_args()

    spec, source_desc = load_openapi_spec(args.url, args.file)
    exit_code = run_checks(spec, source_desc)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
