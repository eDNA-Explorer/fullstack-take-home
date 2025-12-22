# FASTQ Quality Analysis Pipeline Challenge

## Overview

Build a Dagster data pipeline that analyzes FASTQ sequencing data quality and generates summary reports.

**Language**: Python 3.10+

**Framework**: Dagster

## Background

### What is FASTQ?

FASTQ is a text-based format for storing nucleotide sequences along with their quality scores. Each read consists of 4 lines:

```
@read_id                          <- Header (starts with @)
ATCGATCGATCG...                   <- Sequence (A, T, C, G, N)
+                                  <- Separator (+ optionally followed by ID)
IIIIIIIIIII...                    <- Quality scores (ASCII-encoded Phred scores)
```

### Quality Scores (Phred)

Quality scores indicate the probability that a base call is incorrect:

- **Q = -10 * log10(P_error)**
- Q30 = 1 in 1,000 error rate (99.9% accurate)
- Q20 = 1 in 100 error rate (99% accurate)
- Q10 = 1 in 10 error rate (90% accurate)

Quality scores are ASCII-encoded using: `quality_score = ord(character) - 33`

## The Dataset

You are provided with **8 paired-end FASTQ samples** in the `samples/` directory:

| Sample | Reads | Quality | Description |
|--------|-------|---------|-------------|
| sample_01 | 1,000 | High | High quality, low contamination |
| sample_02 | 1,500 | High | High quality, moderate contamination |
| sample_03 | 800 | Medium | Medium quality, low contamination |
| sample_04 | 2,000 | Medium | Medium quality, high contamination |
| sample_05 | 1,200 | Lower | Lower quality, moderate contamination |
| sample_06 | 500 | High | High quality, very low contamination (small sample) |
| sample_07 | 1,800 | Variable | Variable quality with quality decay |
| sample_08 | 1,000 | Medium | Medium quality, high adapter contamination |

Each sample has paired-end reads: `sample_XX_R1.fastq.gz` (forward) and `sample_XX_R2.fastq.gz` (reverse).

---

## Challenge Tasks

A `sample_list` asset has been provided that discovers all samples in the `samples/` directory and returns them in the format:

```python
{
    "sample_01": ["path/to/sample_01_R1.fastq.gz", "path/to/sample_01_R2.fastq.gz"],
    "sample_02": ["path/to/sample_02_R1.fastq.gz", "path/to/sample_02_R2.fastq.gz"],
    ...
}
```

### Task 1: Sample Quality Evaluation

Create a Dagster asset that evaluates the quality of each sample.

**Requirements:**
- Use any bioinformatics library you prefer (e.g., BioPython, seqkit, pyfastx, or others)
- For each sample, calculate quality metrics such as:
  - Mean quality score
  - Total reads
  - GC content
  - Read length statistics
- The asset should depend on `sample_list`

### Task 2: Reads Per Sequence Report

Create a Dagster asset that generates a report of total reads per unique sequence per sample.

**Requirements:**
- Count occurrences of each unique sequence in each sample
- Output the results as a **Parquet file**
- The Parquet file should include columns for:
  - `sample_id`: The sample identifier
  - `sequence`: The nucleotide sequence
  - `read_count`: Number of times this sequence appears
- Consider memory efficiency for large files

---

## Getting Started

### Installing Dependencies

**Option 1: uv**

Ensure [`uv`](https://docs.astral.sh/uv/) is installed following their [official documentation](https://docs.astral.sh/uv/getting-started/installation/).

Create a virtual environment and install dependencies:

```bash
uv sync
```

Then activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS | `source .venv/bin/activate` |
| Windows | `.venv\Scripts\activate` |

**Option 2: pip**

```bash
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### Running Dagster

Start the Dagster UI web server:

```bash
dg dev
```

Open http://localhost:3000 in your browser to see the project.

---

## Evaluation Criteria

### Correctness
- Assets execute successfully and produce expected outputs
- Quality metrics are accurate
- Parquet file is properly formatted and readable

### Code Quality
- Clean, readable code with type hints
- Proper error handling
- Follows Python best practices (PEP 8)

### Dagster Best Practices
- Proper asset dependencies
- Appropriate use of Dagster features (IO managers, metadata, etc.)
- Assets are well-documented

---

## Recommended Tools

You may use any bioinformatics library or tool you prefer. Below are some recommended options with examples.

### SeqKit (Command-Line Tool)

[SeqKit](https://bioinf.shenwei.me/seqkit/) is a fast, cross-platform toolkit for FASTA/FASTQ manipulation. It's pre-installed in the Docker container.

**Installation:**
```bash
# macOS
brew install seqkit

# conda
conda install -c bioconda seqkit

# Or use the provided Docker container
```

**Example Usage:**
```bash
# Basic stats for a FASTQ file
seqkit stats samples/sample_01_R1.fastq.gz

# Detailed stats with quality info
seqkit stats -a samples/sample_01_R1.fastq.gz

# Output as TSV for parsing
seqkit stats -T samples/*.fastq.gz > stats.tsv

# Count unique sequences
seqkit rmdup -s samples/sample_01_R1.fastq.gz -D duplicates.txt
```

**Calling from Python:**
```python
import subprocess
import json

def get_seqkit_stats(fastq_path: str) -> dict:
    result = subprocess.run(
        ["seqkit", "stats", "-a", "-T", fastq_path],
        capture_output=True,
        text=True
    )
    lines = result.stdout.strip().split("\n")
    headers = lines[0].split("\t")
    values = lines[1].split("\t")
    return dict(zip(headers, values))
```

**Documentation:** https://bioinf.shenwei.me/seqkit/

---

### BioPython

[BioPython](https://biopython.org/) is a comprehensive Python library for biological computation with excellent FASTQ support.

**Installation:**
```bash
uv add biopython
# or
pip install biopython
```

**Example Usage:**
```python
import gzip
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction

def analyze_fastq(fastq_path: str) -> dict:
    total_reads = 0
    total_quality = 0
    total_gc = 0
    total_length = 0

    with gzip.open(fastq_path, "rt") as handle:
        for record in SeqIO.parse(handle, "fastq"):
            total_reads += 1
            total_length += len(record.seq)
            total_gc += gc_fraction(record.seq)
            # Quality scores are in record.letter_annotations["phred_quality"]
            qualities = record.letter_annotations["phred_quality"]
            total_quality += sum(qualities) / len(qualities)

    return {
        "total_reads": total_reads,
        "mean_quality": total_quality / total_reads if total_reads else 0,
        "mean_gc_content": total_gc / total_reads if total_reads else 0,
        "mean_length": total_length / total_reads if total_reads else 0,
    }
```

**Documentation:** https://biopython.org/wiki/SeqIO

---

### pyfastx

[pyfastx](https://github.com/lmdu/pyfastx) is a fast Python library for random access to FASTA/FASTQ files with built-in quality analysis.

**Installation:**
```bash
uv add pyfastx
# or
pip install pyfastx
```

**Example Usage:**
```python
import pyfastx

def analyze_with_pyfastx(fastq_path: str) -> dict:
    fq = pyfastx.Fastq(fastq_path, build_index=False)

    total_reads = 0
    total_quality = 0
    sequences = {}

    for read in fq:
        total_reads += 1
        total_quality += sum(read.quali) / len(read.quali)

        # Count sequence occurrences
        seq = str(read.seq)
        sequences[seq] = sequences.get(seq, 0) + 1

    return {
        "total_reads": total_reads,
        "mean_quality": total_quality / total_reads if total_reads else 0,
        "unique_sequences": len(sequences),
        "sequence_counts": sequences,
    }
```

**Documentation:** https://pyfastx.readthedocs.io/

---

### Other Alternatives

| Tool | Type | Best For | Installation |
|------|------|----------|--------------|
| [fastp](https://github.com/OpenGene/fastp) | CLI | Fast all-in-one preprocessing | `conda install -c bioconda fastp` |
| [scikit-bio](http://scikit-bio.org/) | Python | Scientific analysis, diversity metrics | `pip install scikit-bio` |
| [HTSeq](https://htseq.readthedocs.io/) | Python | High-throughput sequencing analysis | `pip install HTSeq` |
| [Biotite](https://www.biotite-python.org/) | Python | Modern, fast sequence analysis | `pip install biotite` |

---

## Docker

A Dockerfile is provided with seqkit pre-installed:

```bash
# Build the container
docker build -t data-pipeline .

# Run Dagster webserver
docker run -p 3000:3000 data-pipeline

# Run interactively to test tools
docker run -it data-pipeline bash
```

---

## Writing Parquet Output

[Polars](https://pola.rs/) is pre-installed in this project for fast DataFrame operations and Parquet output:

```python
import polars as pl

def write_sequence_counts(data: list[dict], output_path: str):
    df = pl.DataFrame(data)
    # Expected columns: sample_id, sequence, read_count
    df.write_parquet(output_path)

# Or build from columns directly
df = pl.DataFrame({
    "sample_id": ["sample_01", "sample_01", "sample_02"],
    "sequence": ["ATCGATCG", "GCTAGCTA", "ATCGATCG"],
    "read_count": [150, 42, 89],
})
df.write_parquet("output/sequence_counts.parquet")
```

**Reading Parquet:**
```python
df = pl.read_parquet("output/sequence_counts.parquet")
print(df)
```

---

## Learn More

- [Dagster Documentation](https://docs.dagster.io/)
- [SeqKit Documentation](https://bioinf.shenwei.me/seqkit/)
- [BioPython SeqIO](https://biopython.org/wiki/SeqIO)
- [pyfastx Documentation](https://pyfastx.readthedocs.io/)
- [Polars User Guide](https://docs.pola.rs/)
