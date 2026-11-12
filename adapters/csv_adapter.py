import pandas as pd
from pathlib import Path
from core.canonical_model import CanonicalTable



def detect_separator(file_path: str) -> str:
    """
    Detect CSV separator by checking first line for common delimiters.
    Returns detected separator or defaults to comma.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
    except Exception:
        return ','

    # Check for common separators
    separators = [',', ';', '\t', '|']
    separator_counts = {sep: first_line.count(sep) for sep in separators}

    # Return separator with highest count (likely the actual separator)
    return max(separator_counts, key=separator_counts.get)


def read_csv_to_canonical(file_path: str) -> CanonicalTable:
    """
    Read CSV file and return as CanonicalTable.
    Auto-detects separator and normalizes column names (converts non-breaking spaces to regular spaces).
    """
    separator = detect_separator(file_path)
    df = pd.read_csv(file_path, sep=separator)
    
    # Normalize column names: convert non-breaking spaces and other whitespace to regular spaces
    df.columns = df.columns.str.replace('\xa0', ' ', regex=False)
    
    return CanonicalTable.from_dataframe(df)


def write_canonical_to_csv(canonical_table: CanonicalTable, output_path: str) -> None:
    """
    Write CanonicalTable to CSV file.
    """
    df = canonical_table.to_dataframe()
    df.to_csv(output_path, index=False)
