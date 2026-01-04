# Hugging Face Model Ingestion Scripts

## Overview

This directory contains scripts for ingesting Hugging Face marketplace data into the Supabase database.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Copy `.env.template` to `.env` and fill in your credentials:
   ```bash
   cp .env.template .env
   ```

   Required variables:
   - `SUPABASE_DB_URL`: PostgreSQL connection string
   - `HF_TOKEN`: Hugging Face API token (optional but recommended)

## Scripts

### `hf_ingest_top_models.py`

Ingests top models from Hugging Face for each task type.

**Usage:**

```bash
# Dry run (2 tasks, 50 models per task)
python scripts/hf_ingest_top_models.py --max-tasks 2 --limit-per-task 50

# Full ingestion (all tasks, 1000 models per task)
python scripts/hf_ingest_top_models.py --limit-per-task 1000

# Custom limits
python scripts/hf_ingest_top_models.py --max-tasks 10 --limit-per-task 500
```

**Features:**
- ✅ Idempotent: Safe to rerun multiple times
- ✅ Rate limit handling: Automatic retry with exponential backoff
- ✅ Conservative concurrency: 500ms delay between requests
- ✅ Deduplication: Models appearing in multiple tasks stored once
- ✅ Logging: Outputs to console and `hf_ingestion.log`

**Arguments:**
- `--limit-per-task`: Number of models to fetch per task (default: 1000)
- `--max-tasks`: Limit number of tasks to process (for testing)

## Database Schema

The script populates three tables in the `hf` schema:

- `hf.models`: Unique models with metadata
- `hf.tasks`: HF task types
- `hf.model_tasks`: Many-to-many mapping with rankings

## Troubleshooting

**Rate Limits:**
- The script automatically retries with exponential backoff
- Set `HF_TOKEN` in `.env` for higher rate limits
- Adjust `request_delay` in the script if needed

**Connection Issues:**
- Verify `SUPABASE_DB_URL` is correct
- Check network connectivity to Supabase
- Ensure database has the `hf` schema created

**Logs:**
- Check `hf_ingestion.log` for detailed error messages
- Use `--max-tasks 1` to test with a single task

