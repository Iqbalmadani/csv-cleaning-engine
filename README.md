# CSV Cleaning Engine

Schema-driven command-line tool for cleaning CSV files. It runs locally and
does not send your data to a service.

## Requirements

- Python 3.10 or newer
- pandas

Install the dependency:

```bash
python -m pip install -r requirements.txt
```

## Quick start

From this directory, run:

```bash
python cli/main.py --input "examples/sample.csv" --output "cleaned.csv" --schema "examples/schema.json"
```

The output path is overwritten if it already exists. Without `--schema`, the
input is copied to CSV output without schema-based transformations.
The example input contains synthetic data only.

To run the tests:

```bash
python -m unittest discover -s tests -v
```

## Schema

The schema is a JSON object. Each column name maps to a transformation:

```json
{
  "standardize_headers": true,
  "Customer Name": { "type": "text", "case": "proper" },
  "Email Address": { "type": "email" },
  "Order Total": { "type": "currency" },
  "Order Date": { "type": "date" },
  "Notes": { "type": "text", "deep_clean": true }
}
```

Supported column types:

- `text`: trim surrounding whitespace. Set `deep_clean` to remove bracketed
  citations and footnote symbols; set `case` to `proper` to title-case text
  while preserving all-uppercase words.
- `email`: convert values to lowercase.
- `currency`: convert simple dollar amounts with commas or citations to numbers.
- `date`: parse dates and preserve values that cannot be parsed. Set
  `normalize_dash` to normalize en/em dashes before parsing.
- `ignore`: remove the column from the output.

Set `standardize_headers` to `true` to lowercase headers and replace spaces
with underscores. Schema column matching is case-insensitive.

## Current scope

- CSV input and output are supported; Excel adapter support is not implemented.
- Delimiters are detected from comma, semicolon, tab, and pipe characters in
  the header line.
- This is an early-stage project. Validate output before using it in a
  production workflow, especially for ambiguous dates and unusual currency
  formats.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
