"""
ServiceNow Connector — Mock implementation.

In production, this would authenticate with ServiceNow API,
fetch procurement/CMDB records, and transform to canonical format.
"""

from typing import List
from app.connectors.base import BaseConnector
from app.models.canonical import CanonicalFinancialRecord


class ServiceNowConnector(BaseConnector):
    """
    Mock connector for ServiceNow integration.
    Stub: returns empty list until API integration is implemented.
    """

    def __init__(self, instance_url: str = "", api_key: str = ""):
        self.instance_url = instance_url
        self.api_key = api_key

    def fetch_records(self) -> List[CanonicalFinancialRecord]:
        """
        Fetch records from ServiceNow.
        Mock: returns empty list.
        """
        # TODO: Implement ServiceNow API integration
        # 1. Authenticate with instance
        # 2. Query procurement/CMDB tables
        # 3. Transform to CanonicalFinancialRecord
        return []
