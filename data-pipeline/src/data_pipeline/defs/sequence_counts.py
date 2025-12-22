import random
from pathlib import Path

import polars as pl
from dagster import asset

from .sample_list import sample_list

DNA_BASES = "ACGT"


def generate_random_sequence(length: int = 50) -> str:
    """Generate a random DNA sequence."""
    return "".join(random.choices(DNA_BASES, k=length))


@asset(deps=[sample_list])
def sequence_counts(sample_list: dict[str, list[str]]) -> None:
    """
    Count occurrences of each unique sequence per sample and write to Parquet.

    Reads all FASTQ files from sample_list, counts unique sequences,
    and outputs a Parquet file with columns: sample_id, sequence, read_count.
    """
    # Output to data-pipeline/output directory (synced via Docker volume)
    output_dir = Path(__file__).parents[3] / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "sequence_counts.parquet"

    # TODO: Implement this to read FASTQ files and count unique sequences.
    #
    # For each sample in sample_list:
    # 1. Read sequences from both forward and reverse FASTQ files
    # 2. Count occurrences of each unique sequence
    # 3. Add records with sample_id, sequence, and read_count

    # Mock implementation - generates random sequence data
    records: list[dict] = []

    for sample_id in sample_list.keys():
        # Generate random number of unique sequences per sample
        num_sequences = random.randint(10, 25)

        for _ in range(num_sequences):
            records.append({
                "sample_id": sample_id,
                "sequence": generate_random_sequence(random.randint(30, 100)),
                "read_count": random.randint(1, 500),
            })

    # Write to parquet using polars
    df = pl.DataFrame(records)
    df = df.sort(["sample_id", "read_count"], descending=[False, True])
    df.write_parquet(
        output_path,
        compression="snappy",
        use_pyarrow=True,
        pyarrow_options={
            "use_dictionary": False,
            "version": "1.0",
        },
    )
