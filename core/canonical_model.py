import pandas as pd


class CanonicalTable:
    """
    Internal neutral representation of a table.
    Uses pandas DataFrame internally but exposes simplified interface.
    """

    def __init__(self, columns: list[str], rows: list[dict]):
        """
        Args:
            columns: List of column names
            rows: List of dictionaries where each dict represents a row
        """
        self.columns = columns
        self.rows = rows

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert CanonicalTable to pandas DataFrame.
        """
        if not self.rows:
            return pd.DataFrame(columns=self.columns)
        return pd.DataFrame(self.rows)

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> "CanonicalTable":
        """
        Create CanonicalTable from pandas DataFrame.
        """
        columns = df.columns.tolist()
        rows = df.to_dict(orient="records")
        return CanonicalTable(columns=columns, rows=rows)
