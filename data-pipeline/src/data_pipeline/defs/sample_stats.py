import random
from pathlib import Path

import polars as pl
from dagster import asset

from .sample_list import sample_list


@asset(deps=[sample_list])
def sample_stats(sample_list: dict[str, list[str]]) -> None:
    """
    Generate quality statistics for each sample and write to Parquet.

    Outputs a Parquet file with columns: sample_id, q30, q20, num_seqs,
    min_len, avg_len, max_len.
    """
    # Output to data-pipeline/output directory (synced via Docker volume)
    output_dir = Path(__file__).parents[3] / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "sample_stats.parquet"

    # TODO: Implement this to compute actual quality metrics from FASTQ files.
    #
    # For each sample in sample_list:
    # 1. Read sequences from both forward and reverse FASTQ files
    # 2. Calculate quality score distributions (Q20, Q30 percentages)
    # 3. Calculate sequence length statistics (min, avg, max)
    # 4. Count total number of sequences

    # Mock implementation - generates random quality metrics
    records: list[dict] = []

    for sample_id in sample_list.keys():
        # Generate realistic FASTQ quality metrics
        q30 = round(75 + random.random() * 20, 1)  # 75-95%
        q20 = round(85 + random.random() * 12, 1)  # 85-97%
        num_seqs = random.randint(500, 2500)
        min_len = random.randint(50, 100)
        avg_len = random.randint(120, 200)
        max_len = max(random.randint(200, 300), avg_len + 20)

        records.append({
            "sample_id": sample_id,
            "q30": q30,
            "q20": q20,
            "num_seqs": num_seqs,
            "min_len": min_len,
            "avg_len": avg_len,
            "max_len": max_len,
        })

    # Write to parquet using polars
    df = pl.DataFrame(records)
    df = df.sort("sample_id")
    df.write_parquet(
        output_path,
        compression="snappy",
        use_pyarrow=True,
        pyarrow_options={
            "use_dictionary": False,
            "version": "1.0",
        },
    )
