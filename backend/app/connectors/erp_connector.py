"""
ERP Connector — Mock implementation.

In production, this would integrate with SAP/Oracle/NetSuite APIs,
fetch AP/GL records, and transform to canonical format.
"""

from typing import List
from app.connectors.base import BaseConnector
from app.models.canonical import CanonicalFinancialRecord


class ErpConnector(BaseConnector):
    """
    Mock connector for ERP system integration.
    Stub: returns empty list until API integration is implemented.
    """

    def __init__(self, erp_url: str = "", credentials: dict = None):
        self.erp_url = erp_url
        self.credentials = credentials or {}

    def fetch_records(self) -> List[CanonicalFinancialRecord]:
        """
        Fetch records from ERP system.
        Mock: returns empty list.
        """
        # TODO: Implement ERP API integration
        # 1. Authenticate with ERP instance
        # 2. Query AP/GL tables
        # 3. Transform to CanonicalFinancialRecord
        return []
