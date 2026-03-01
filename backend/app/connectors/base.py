"""
Connector Architecture — Interface stubs.

BaseConnector defines the contract: all connectors return List[CanonicalFinancialRecord].
Engine never binds to a specific connector implementation.
"""

from abc import ABC, abstractmethod
from typing import List
from app.models.canonical import CanonicalFinancialRecord


class BaseConnector(ABC):
    """
    Abstract base for all data connectors.
    Every connector must normalize its output to CanonicalFinancialRecord.
    """

    @abstractmethod
    def fetch_records(self) -> List[CanonicalFinancialRecord]:
        """
        Fetch and transform records from the data source.
        Must return canonical records — never raw/source-specific formats.
        """
        raise NotImplementedError
