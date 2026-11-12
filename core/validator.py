import logging
from .canonical_model import CanonicalTable

logger = logging.getLogger(__name__)


def validate_columns(
    canonical_table: CanonicalTable,
    schema: dict,
    strict: bool = True
) -> None:
    """
    Validate that all schema keys exist in CanonicalTable columns.
    Case-insensitive column matching.
    
    Args:
        canonical_table: The table to validate
        schema: Schema dict with keys as column names
        strict: If True, raise ValueError on missing columns.
                If False, log warning instead.
    
    Raises:
        ValueError: If strict=True and schema columns missing in table
    """
    if not schema:
        # No schema to validate against
        return

    # Filter schema to only column specs (skip top-level config keys like standardize_headers)
    schema_columns = {k: v for k, v in schema.items() if isinstance(v, dict)}
    
    # Case-insensitive comparison
    table_columns_lower = {col.lower(): col for col in canonical_table.columns}
    
    # Find missing columns (case-insensitive)
    missing_in_table = []
    for schema_col in schema_columns.keys():
        if schema_col.lower() not in table_columns_lower:
            missing_in_table.append(schema_col)
    
    if missing_in_table:
        error_msg = f"Schema columns missing in table: {sorted(missing_in_table)}"
        if strict:
            raise ValueError(error_msg)
        else:
            logger.warning(error_msg)
