export interface RejectionReason {
    row: number;
    reason: string;
    raw: string;
}

export interface IngestResult {
    status: string;
    filename: string;
    rows_total: number;
    rows_accepted: number;
    rows_rejected: number;
    sheets_processed: string[];
    mapping_method: "yaml" | "fuzzy" | "llm" | "hybrid" | "none";
    confidence_score: number;
    column_mapping: Record<string, string>;
    rejections_summary: RejectionReason[];
    decisions_generated: number;
    warnings: string[];
}
