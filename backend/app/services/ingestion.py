import pandas as pd
import io
import json
from typing import List, Dict
from app.models.data import FinancialRecord

class IngestionService:
    @staticmethod
    def process_file(file_content: bytes, filename: str, mapping_config: dict = None) -> Dict[str, int]:
        """
        Universal Ingestion Adapter.
        Transforms ANY dataset into CanonicalFinancialRecord using a schema mapping.
        """
        try:
            # 1. Load Data
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise ValueError("Unsupported file type")
            
            # 2. Schema Mapping Detection
            from app.core.mappings import SchemaMapping
            import yaml
            import os
            
            mapping_data = None
            
            # If explicit config provided, use it
            if mapping_config:
                 mapping_data = mapping_config
            else:
                # Auto-detect from config directory
                config_dir = "config"
                for filename in os.listdir(config_dir):
                    if filename.endswith(".yaml") or filename.endswith(".yml"):
                        try:
                            with open(os.path.join(config_dir, filename), "r", encoding='utf-8') as f:
                                candidate = yaml.safe_load(f)
                                # Check if required source columns exist in DF
                                if not candidate.get("column_mapping"): continue
                                
                                required_cols = [
                                    col for field, col in candidate["column_mapping"].items()
                                    if field in ["entity", "amount"] # Minimal requirements
                                ]
                                
                                if all(col in df.columns for col in required_cols):
                                    mapping_data = candidate
                                    print(f"Detected mapping: {filename}")
                                    break
                        except Exception as e:
                            print(f"Error loading config {filename}: {e}")
                            continue
            
            # 3. Heuristic Fallback (SAFE MODE)
            if not mapping_data:
                from app.core.heuristics import HeuristicMapper
                analysis = HeuristicMapper.analyze_columns(df.columns.tolist())
                
                if analysis.is_valid and analysis.confidence_score >= HeuristicMapper.CONFIDENCE_THRESHOLD:
                    mapping = analysis.mapping
                    print(f"SAFE HEURISTIC APPLIED (Score: {analysis.confidence_score:.2f})")
                    print(f"Mapped: {mapping.column_mapping}")
                else:
                    # FAILED SAFETY GATE
                    error_msg = "Ambiguous Dataset Structure. "
                    if analysis.missing_required:
                        error_msg += f"Could not confidently map required fields: {analysis.missing_required}. \n"
                    else:
                        error_msg += f"Confidence score ({analysis.confidence_score:.2f}) below threshold ({HeuristicMapper.CONFIDENCE_THRESHOLD}). \n"
                    
                    error_msg += "System Refused to Guess. Please provide an explicit mapping configuration."
                    raise ValueError(error_msg)
            else:
                 mapping = SchemaMapping(**mapping_data)

            # 3. Normalization & Transformation
            canonical_data = []
            
            for _, row in df.iterrows():
                record_data = {}
                
                # Map fields
                for canonical_field, source_col in mapping.column_mapping.items():
                    if source_col in df.columns:
                        val = row[source_col]
                        # Handle NaN
                        if pd.isna(val) and canonical_field in mapping.defaults:
                             val = mapping.defaults[canonical_field]
                        
                        # Apply Multipliers (e.g. for K units)
                        if canonical_field in mapping.multipliers:
                            try:
                                val = float(val) * mapping.multipliers[canonical_field]
                            except (ValueError, TypeError):
                                pass # Keep original if conversion fails
                        
                        record_data[canonical_field] = val
                
                # Apply static defaults
                for default_field, default_val in mapping.defaults.items():
                    if default_field not in record_data or pd.isna(record_data.get(default_field)):
                        record_data[default_field] = default_val


                # Add metadata
                record_data['source_file'] = filename

                # 4. Canonical Model Validation
                from app.models.canonical import CanonicalFinancialRecord
                try:
                    record = CanonicalFinancialRecord(**record_data)
                    canonical_data.append(record)
                except Exception as e:
                    # Log error but maybe continue? For strict mode, we fail.
                    print(f"Skipping invalid row: {e}")
                    continue

            if not canonical_data:
                raise ValueError("No valid records found after ingestion.")

            # PERSISTENCE (v1): Save to JSON for analysis
            import os
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            # Serialize
            output_data = [r.model_dump(mode='json') for r in canonical_data]
            with open(os.path.join(data_dir, "transactions.json"), "w") as f:
                json.dump(output_data, f, indent=2)

            return {
                "total_rows_read": len(df),
                "processed_canonical": len(canonical_data),
                "errors": len(df) - len(canonical_data)
            }
            
        except Exception as e:
            raise ValueError(f"Universal Adapter Failed: {str(e)}")
