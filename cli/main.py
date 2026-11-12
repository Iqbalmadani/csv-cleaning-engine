import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.csv_adapter import read_csv_to_canonical, write_canonical_to_csv
from core.schema_engine import load_schema
from core.validator import validate_columns
from core.transformer import transform


def setup_logging():
    """Configure basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )


def main():
    """
    Main CLI entry point.
    
    Flow:
    1. Load schema (optional)
    2. Read CSV file
    3. Validate columns
    4. Transform data
    5. Write output
    """
    parser = argparse.ArgumentParser(
        description="CSV Cleaning Engine - Transform and validate CSV files"
    )
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    parser.add_argument('--schema', default=None, help='Schema JSON file path (optional)')

    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load schema
        logger.info(f"Loading schema from: {args.schema if args.schema else 'NONE'}")
        schema = load_schema(args.schema)

        # Read CSV
        logger.info(f"Reading CSV from: {args.input}")
        canonical_table = read_csv_to_canonical(args.input)
        logger.info(f"Loaded {len(canonical_table.rows)} rows with {len(canonical_table.columns)} columns")

        # Validate columns
        if schema:
            logger.info("Validating columns against schema")
            validate_columns(canonical_table, schema)
            logger.info("Column validation passed")

        # Transform data
        if schema:
            logger.info("Transforming data according to schema")
            canonical_table = transform(canonical_table, schema)
            logger.info("Transformation complete")

        # Write output
        logger.info(f"Writing output to: {args.output}")
        write_canonical_to_csv(canonical_table, args.output)
        logger.info("Pipeline complete - CSV cleaned and saved successfully")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
