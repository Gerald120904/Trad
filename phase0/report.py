import json
import os
import tempfile
from pathlib import Path

from .config import GateConfig

ITEMS = (
    "Todos los archivos diarios existen y sus SHA-256 coinciden.",
    "Todos los CSV cargan estrictamente.",
    "No hay IDs inválidos, repetidos, desordenados o discontinuos.",
    "No hay retrocesos temporales ni filas duplicadas.",
    "Precios, cantidades y fechas son válidos.",
    "Las vistas DuckDB existen y son consultables.",
    "El reporte automático tiene estado PASS.",
)


def atomic(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=path.name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write(config: GateConfig, report: dict):
    rows = "\n".join(
        f"| `{t['name']}` | {'PASS' if t['passed'] else 'FAIL'} | "
        f"`{t['observed']}` | `{t['expected']}` |" for t in report["tests"])
    markdown = (f"# Auditoría de datos - Fase 0\n\n**Estado:** `{report['status']}`\n\n"
                f"- Mercado: `spot`\n- Símbolo: `{config.symbol}`\n"
                f"- Periodo: `{config.start_date}` a `{config.end_date}` UTC\n"
                f"- Filas: `{report['total_rows']}`\n\n"
                "## Pruebas\n\n| Prueba | Estado | Observado | Esperado |\n"
                "|---|---|---:|---:|\n" + rows + "\n")
    atomic(config.report_dir / "data_audit.json",
           json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    atomic(config.report_dir / "data_audit.md", markdown)
    mark = "x" if report["status"] == "PASS" else " "
    checklist = "# Checklist - Compuerta 0\n\nEstado automático: **" + report["status"] + \
        "**\n\n> Generado automáticamente; no editar manualmente.\n\n" + \
        "\n".join(f"- [{mark}] {item}" for item in ITEMS) + "\n"
    atomic(config.project_root / "docs" / "PHASE_0_CHECKLIST.md", checklist)
