"""Impostazioni lette dalle variabili d'ambiente (o dal file .env)."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    sorgente: str
    output_dir: Path


def carica_config() -> Config:
    return Config(
        sorgente=os.getenv("SAP_SORGENTE", "mock"),
        output_dir=Path(os.getenv("OUTPUT_DIR", "output")),
    )
