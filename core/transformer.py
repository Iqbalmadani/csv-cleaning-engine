import logging
import re
import pandas as pd
from .canonical_model import CanonicalTable

logger = logging.getLogger(__name__)


def smart_title(text):
    """
    Title case that preserves acronyms (all-caps words stay as-is).
    E.g., "MDNA" stays "MDNA", "taylor swift" becomes "Taylor Swift"
    """
    if not isinstance(text, str):
        return text
    words = text.split()
    titled = []
    for word in words:
        if word.isupper() and len(word) > 1:
            titled.append(word)  # Protect acronym
        else:
            titled.append(word.title())
    return ' '.join(titled)


def deep_clean_text(text):
    """
    Remove citations [1], [a], etc., symbols (†‡*), and normalize dashes.
    """
    if not isinstance(text, str):
        return text
    text = re.sub(r'\[.*?\]', '', text)  # Remove [1], [a], [b], etc.
    text = re.sub(r'[†‡*]', '', text)    # Remove symbols †‡*
    text = text.replace('–', '-').replace('—', '-')  # Normalize en-dash, em-dash to hyphen
    return text.strip()


def convert_currency(val):
    """
    Convert currency strings to numeric (float/int).
    Handles $, commas, citations [b], [e], etc.
    E.g., "$780,000,000" → 780000000, "$123.45" → 123.45
    """
    if pd.isna(val):
        return val
    s = str(val).strip()
    s = re.sub(r'\[.*?\]', '', s)  # Remove citations [b], [e]
    s = re.sub(r'[$]', '', s)      # Remove $ safely
    s = s.replace(',', '')          # Remove comma thousands separator
    try:
        # Return float if decimal, else int
        return float(s) if '.' in s else int(s)
    except ValueError:
        logger.warning(f"Could not convert currency value: {val}")
        return val


def transform(canonical_table: CanonicalTable, schema: dict) -> CanonicalTable:
    """
    Apply transformations to CanonicalTable based on schema.
    
    Schema Rules:
    - type = "text" → strip whitespace, optional deep_clean and case
    - type = "email" → lowercase
    - type = "currency" → convert to numeric
    - type = "date" → parse with coerce, normalize_dash optional
    - type = "ignore" → drop column
    - standardize_headers (top-level) → lowercase headers with underscores
    
    If no schema: minimal whitespace strip only (no heuristics).
    """
    if not schema:
        # Minimal fallback: strip whitespace from all text
        df = canonical_table.to_dataframe()
        df = df.apply(
            lambda column: column.map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
        )
        return CanonicalTable.from_dataframe(df)

    df = canonical_table.to_dataframe()

    # Process each column based on schema FIRST (before standardizing headers)
    for schema_column_name, column_schema in schema.items():
        # Skip top-level schema keys that aren't column specs
        if schema_column_name == "standardize_headers" or not isinstance(column_schema, dict):
            continue

        column_name = next(
            (
                column
                for column in df.columns
                if str(column).casefold() == schema_column_name.casefold()
            ),
            None,
        )
        if column_name is None:
            continue

        col_type = column_schema.get("type")

        if col_type == "text":
            df[column_name] = df[column_name].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
            
            # Optional: deep clean (remove citations, symbols, normalize dashes)
            if column_schema.get("deep_clean", False):
                df[column_name] = df[column_name].apply(deep_clean_text)
                logger.info(f"Deep cleaned text column: {column_name}")
            
            # Optional: proper case (preserves acronyms)
            if column_schema.get("case") == "proper":
                df[column_name] = df[column_name].apply(smart_title)
                logger.info(f"Applied proper case to: {column_name}")

        elif col_type == "email":
            df[column_name] = df[column_name].map(
                lambda value: value.lower() if isinstance(value, str) else value
            )

        elif col_type == "currency":
            # Convert to numeric
            df[column_name] = df[column_name].apply(convert_currency)
            logger.info(f"Converted currency column: {column_name}")

        elif col_type == "date":
            # Optional: normalize dashes before parsing
            if column_schema.get("normalize_dash", False):
                df[column_name] = df[column_name].map(
                    lambda value: (
                        value.replace('–', '-').replace('—', '-')
                        if isinstance(value, str)
                        else value
                    )
                )
            
            # Parse dates with coerce to detect failures
            original_col = df[column_name].copy()
            converted = pd.to_datetime(df[column_name], errors="coerce")
            
            # Count NaT values (conversion failures)
            failed_values = original_col.notna() & converted.isna()
            failed_count = int(failed_values.sum())
            if failed_count > 0:
                logger.warning(
                    f"Date column '{column_name}': {failed_count} values failed to parse. "
                    f"Keeping original values for failed rows."
                )
            df[column_name] = converted.where(converted.notna(), original_col)

        elif col_type == "ignore":
            # Drop column
            df = df.drop(column_name, axis=1, errors='ignore')
            logger.info(f"Dropped column: {column_name}")

    # Process standardize_headers LAST (applies to all columns after transformations)
    if schema.get("standardize_headers", False):
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(r'\s+', '_', regex=True)
            .str.replace(r'[()]', '', regex=True)
        )
        logger.info("Headers standardized to lowercase with underscores")

    return CanonicalTable.from_dataframe(df)
