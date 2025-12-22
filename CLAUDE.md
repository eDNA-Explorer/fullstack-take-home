# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A monorepo with two components: a Dagster data pipeline that processes FASTQ genomic sequencing files, and a Next.js dashboard that displays the results via tRPC.

## Commands

### Data Pipeline (data-pipeline/)
```bash
docker-compose up          # Run pipeline via Docker (http://localhost:3000)
uv sync                    # Install Python dependencies
.venv/bin/dg dev           # Run Dagster dev server directly
```

### Dashboard (dashboard/)
```bash
bun install                # Install dependencies
bun dev                    # Run dev server (http://localhost:3001)
bun run build              # Build for production
bun run lint               # Run ESLint
```

## Architecture

### Data Flow
```
samples/*.fastq.gz → Dagster Pipeline → output/*.parquet → tRPC API → Dashboard
```

### Data Pipeline (Dagster)
- Uses `dg` CLI tooling with `@definitions` decorator pattern
- Assets in `src/data_pipeline/defs/` (one asset per file):
  - `sample_list.py` - Discovers FASTQ pairs in samples/ directory
  - `sequence_counts.py` - Counts unique sequences per sample → `output/sequence_counts.parquet`
  - `sample_stats.py` - Computes quality metrics (Q20, Q30, read counts) → `output/sample_stats.parquet`
- Libraries: Polars + PyArrow for DataFrames, seqkit CLI for FASTQ quality stats

### Dashboard (Next.js)
- **Framework**: Next.js 16 with App Router, React 19, TypeScript
- **Data Layer**: tRPC with React Query
  - Server: `server/routers/` - tRPC routers
  - Client: `lib/trpc.ts` - React Query hooks via `createTRPCReact`
  - API routes: `app/api/trpc/[trpc]/route.ts`
- **UI**: shadcn/ui components (Radix primitives), Tailwind CSS v4, Recharts
- **Parquet Reading**: Uses `parquetjs-lite` (limited encoding support - requires `use_dictionary=False` and `version="1.0"`)

### Key Integration Point
The dashboard reads Parquet files from `../data-pipeline/output/` relative to the dashboard directory. Docker syncs pipeline output via volume mount.

## FASTQ Format Reference
```
@read_id          <- Header
ATCGATCG...       <- Sequence (A, T, C, G, N)
+                 <- Separator
IIIIII...         <- Quality scores (ASCII Phred: quality = ord(char) - 33)
```
Quality thresholds: Q30 = 99.9% accuracy, Q20 = 99% accuracy
