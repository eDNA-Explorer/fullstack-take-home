import random
import string

from dagster import asset


def generate_sample_id() -> str:
    """Generate a random sample ID like 'SAMPLE_A1B2C3'."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SAMPLE_{suffix}"


@asset
def sample_list() -> dict[str, list[str]]:
    """
    Returns a dictionary mapping sample IDs to their forward and reverse read files.

    Returns:
        dict mapping sample_id to [forward_file, reverse_file]

    Example output:
        {
            "SAMPLE_A1B2C3": ["/path/to/SAMPLE_A1B2C3_R1.fastq.gz", "/path/to/SAMPLE_A1B2C3_R2.fastq.gz"],
            "SAMPLE_D4E5F6": ["/path/to/SAMPLE_D4E5F6_R1.fastq.gz", "/path/to/SAMPLE_D4E5F6_R2.fastq.gz"],
        }
    """
    # TODO: Implement this to scan the samples directory for fastq.gz files
    # and group them by sample ID based on paired-end naming conventions.
    #
    # Expected file patterns:
    # - sample_R1.fastq.gz / sample_R2.fastq.gz
    # - sample_1.fastq.gz / sample_2.fastq.gz

    # Mock implementation - generates random sample data
    num_samples = random.randint(3, 20)
    result: dict[str, list[str]] = {}

    for _ in range(num_samples):
        sample_id = generate_sample_id()
        result[sample_id] = [
            f"/samples/{sample_id}_R1.fastq.gz",
            f"/samples/{sample_id}_R2.fastq.gz",
        ]

    return result
