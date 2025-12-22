import { publicProcedure, router } from "../trpc";
import path from "path";
import { ParquetReader } from "parquetjs-lite";

// Seeded random number generator for consistent values per sample
function seededRandom(seed: string): () => number {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    const char = seed.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return () => {
    hash = Math.sin(hash) * 10000;
    return hash - Math.floor(hash);
  };
}

function generateSampleMetrics(sampleId: string) {
  const random = seededRandom(sampleId);

  // Generate realistic FASTQ quality metrics
  const q30 = 75 + random() * 20; // 75-95%
  const q20 = 85 + random() * 12; // 85-97%
  const numSeqs = Math.floor(500 + random() * 2000); // 500-2500 sequences
  const minLen = Math.floor(50 + random() * 50); // 50-100 bp
  const avgLen = Math.floor(120 + random() * 80); // 120-200 bp
  const maxLen = Math.floor(200 + random() * 100); // 200-300 bp

  return {
    q30: Number(q30.toFixed(1)),
    q20: Number(q20.toFixed(1)),
    num_seqs: numSeqs,
    min_len: minLen,
    avg_len: avgLen,
    max_len: Math.max(maxLen, avgLen + 20), // Ensure max > avg
  };
}

export const samplesRouter = router({
  getSampleIds: publicProcedure.query(async () => {
    const parquetPath = path.join(
      process.cwd(),
      "..",
      "data-pipeline",
      "output",
      "sequence_counts.parquet"
    );

    const reader = await ParquetReader.openFile(parquetPath);
    const cursor = reader.getCursor();

    const sampleIds = new Set<string>();

    let record: Record<string, unknown> | null = null;
    while ((record = await cursor.next())) {
      if (typeof record.sample_id === "string") {
        sampleIds.add(record.sample_id);
      }
    }

    await reader.close();

    return Array.from(sampleIds).sort();
  }),

  getSampleMetrics: publicProcedure.query(async () => {
    const parquetPath = path.join(
      process.cwd(),
      "..",
      "data-pipeline",
      "output",
      "sequence_counts.parquet"
    );

    const reader = await ParquetReader.openFile(parquetPath);
    const cursor = reader.getCursor();

    const sampleIds = new Set<string>();

    let record: Record<string, unknown> | null = null;
    while ((record = await cursor.next())) {
      if (typeof record.sample_id === "string") {
        sampleIds.add(record.sample_id);
      }
    }

    await reader.close();

    // Generate metrics for each sample
    const samples = Array.from(sampleIds)
      .sort()
      .map((sampleId, index) => ({
        id: index + 1,
        sample_id: sampleId,
        ...generateSampleMetrics(sampleId),
      }));

    return samples;
  }),
});
