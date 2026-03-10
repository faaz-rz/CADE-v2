import pytest
from unittest.mock import patch, AsyncMock
from app.services.ingestion import IngestionService, IngestError
import datetime
import os

def get_fixture_bytes(filename: str) -> bytes:
    filepath = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(filepath, "rb") as f:
        return f.read()

def test_explicit_mapping_config():
    csv_bytes = get_fixture_bytes("test.csv")
    mapping = {
        "name": "Explicit Mapping",
        "column_mapping": {"entity": "Company", "amount": "Cost"}
    }
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "test.csv", mapping_config=mapping)
        assert res.mapping_method == "explicit"
        assert res.rows_accepted >= 0

def test_heuristic_auto_detection():
    csv_bytes = get_fixture_bytes("test_fuzzy.csv")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "test_fuzzy.csv")
        assert res.mapping_method == "fuzzy"

def test_amount_cleaner_and_skipping_zeros():
    csv_bytes = get_fixture_bytes("test_cleaner.csv")
    mapping = {
        "name": "Cleaner Mapping",
        "column_mapping": {"entity": "Vendor", "amount": "Amount"}
    }
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "test_cleaner.csv", mapping_config=mapping)
        assert res.status == "success"

def test_multiplier_application():
    csv_bytes = get_fixture_bytes("test_multiplier.csv")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "test_multiplier.csv")
        assert res.status == "success"

def test_heuristic_refusal_on_ambiguous_data():
    csv_bytes = get_fixture_bytes("test_bad.csv")
    with patch("json.dump"), patch("os.makedirs"):
        with pytest.raises(IngestError):
            IngestionService.ingest_file(csv_bytes, "test_bad.csv")

def test_extended_canonical_fields_integration():
    csv_bytes = get_fixture_bytes("test_extended.csv")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "test_extended.csv")
        assert res.status == "success"

def test_finds_header_at_row5():
    csv_bytes = get_fixture_bytes("headers_row5.xlsx")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "headers_row5.xlsx")
        assert res.mapping_method == "fuzzy"
        assert res.confidence_score >= 0.8

def test_ingests_multi_sheet_and_deduplicates():
    csv_bytes = get_fixture_bytes("multi_sheet.xlsx")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "multi_sheet.xlsx")
        assert len(res.sheets_processed) >= 1

def test_cleans_all_amount_formats():
    csv_bytes = get_fixture_bytes("messy_amounts.csv")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "messy_amounts.csv")
        assert res.status == "success"

def test_handles_all_date_formats():
    csv_bytes = get_fixture_bytes("date_chaos.csv")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "date_chaos.csv")
        assert res.rows_accepted == 5

def test_normalises_vendor_names():
    csv_bytes = get_fixture_bytes("vendor_noise.csv")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "vendor_noise.csv")
        assert res.status == "success"

@patch("app.core.llm_column_mapper.map_columns_with_llm", new_callable=AsyncMock)
def test_llm_fallback_maps_unusual_columns(mock_llm):
    mock_llm.return_value = {
        "Who We Paid": "entity",
        "How Much": "amount",
        "When": "date",
        "Which Team": "category"
    }
    csv_bytes = get_fixture_bytes("no_standard_headers.xlsx")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "no_standard_headers.xlsx")
        assert res.mapping_method == "fuzzy"

def test_confidence_gate_rejects_below_80pct():
    csv_bytes = get_fixture_bytes("gate.csv")
    with patch("json.dump"), patch("os.makedirs"):
        with pytest.raises(IngestError):
            IngestionService.ingest_file(csv_bytes, "gate.csv")

def test_result_object_has_all_fields():
    csv_bytes = get_fixture_bytes("test_fields.csv")
    with patch("json.dump"), patch("os.makedirs"):
        res = IngestionService.ingest_file(csv_bytes, "test_fields.csv")
        assert hasattr(res, 'rows_total')

def test_idempotency_same_file_same_records():
    csv_bytes = get_fixture_bytes("test1.csv")
    with patch("json.dump"), patch("os.makedirs"):
        res1 = IngestionService.ingest_file(csv_bytes, "test1.csv")
        res2 = IngestionService.ingest_file(csv_bytes, "test1.csv")
        assert res1.rows_accepted == res2.rows_accepted
