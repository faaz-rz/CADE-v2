from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.exports.excel_exporter import generate_executive_report

router = APIRouter()


@router.get("/executive_report")
def export_executive_report():
    """
    Generate and download the Executive Report as an Excel file.
    Returns: .xlsx StreamingResponse
    """
    buffer = generate_executive_report()

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=executive_report.xlsx"
        },
    )
