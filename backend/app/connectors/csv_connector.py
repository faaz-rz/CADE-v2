"""
CSV Connector — Stub wrapping existing ingestion logic.

In a full implementation, this would handle CSV-specific transformations.
Currently delegates to the existing IngestionService for backward compatibility.
"""

from typing import List
from app.connectors.base import BaseConnector
from app.models.canonical import CanonicalFinancialRecord


class CsvConnector(BaseConnector):
    """
    Connector for CSV file data sources.
    Stub: full implementation would accept file path or stream.
    """

    def __init__(self, file_content: bytes = b"", filename: str = "input.csv"):
        self.file_content = file_content
        self.filename = filename

    def fetch_records(self) -> List[CanonicalFinancialRecord]:
        """
        Parse CSV content into canonical records.
        Stub: raises NotImplementedError until wired to ingestion pipeline.
        """
        raise NotImplementedError(
            "CsvConnector.fetch_records() — use IngestionService.process_file() for now"
        )
