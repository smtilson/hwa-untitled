import csv
import sys
from pathlib import Path


def csv_to_tsv(csv_file, tsv_file=None):
    """Convert a CSV file to a TSV file.
    
    Args:
        csv_file: Path to the input CSV file
        tsv_file: Path to the output TSV file (optional, defaults to same name with .tsv extension)
    """
    csv_path = Path(csv_file)
    
    if not csv_path.exists():
        print(f"Error: File '{csv_file}' not found.")
        return False
    
    if tsv_file is None:
        tsv_path = csv_path.with_suffix('.tsv')
    else:
        tsv_path = Path(tsv_file)
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csv_input:
            with open(tsv_path, 'w', encoding='utf-8', newline='') as tsv_output:
                reader = csv.reader(csv_input)
                writer = csv.writer(tsv_output, delimiter='\t')
                writer.writerows(reader)
        
        print(f"✓ Successfully converted '{csv_file}' to '{tsv_path}'")
        return True
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python csv_to_tsv.py <input_csv> [output_tsv]")
        print("  If output_tsv is not specified, it will use the same name with .tsv extension")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_tsv = sys.argv[2] if len(sys.argv) > 2 else None
    
    csv_to_tsv(input_csv, output_tsv)
