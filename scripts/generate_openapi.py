"""
Generate openapi.json directly from the live FastAPI application definition.
Ensures the specification matches the running code with zero manual drift.
"""

import sys
import os
import json

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


def export_openapi(output_path: str = "openapi/openapi.json") -> int:
    """Generate and write the OpenAPI schema."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    schema = app.openapi()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"[+] Successfully exported OpenAPI specification to: {output_path}")
    print(f"    Title: {schema.get('info', {}).get('title')}")
    print(f"    Version: {schema.get('info', {}).get('version')}")
    print(f"    Total Paths Documented: {len(schema.get('paths', {}))}")
    return 0


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "openapi/openapi.json"
    sys.exit(export_openapi(out_file))
