# Setup Instructions for HF Model Ingestion

## Quick Start

### 1. Create `.env` file

Create a `.env` file in the project root with the following content:

```bash
# Supabase Database Connection
# Replace YOUR_PASSWORD with your actual Supabase database password
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@db.qzamfduqlcdwktobwarl.supabase.co:5432/postgres

# Hugging Face API Token (optional but recommended)
# Get your token from: https://huggingface.co/settings/tokens
HF_TOKEN=your_hf_token_here
```

**To find your Supabase password:**
1. Go to your Supabase project dashboard
2. Navigate to Settings → Database
3. Look for "Connection string" or "Database password"

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Dry Run Test

Test with 2 tasks and 50 models per task:

```bash
python scripts/hf_ingest_top_models.py --max-tasks 2 --limit-per-task 50
```

### 4. Check Results

After the dry run completes, check the ingestion report:

```bash
cat docs/hf_ingestion_report.md
```

### 5. Run Full Ingestion (Optional - NOT in this prompt)

Once the dry run is successful, you can run the full ingestion:

```bash
python scripts/hf_ingest_top_models.py --limit-per-task 1000
```

## Database Schema

The following schema and tables have been created:

- **Schema:** `hf`
- **Tables:**
  - `hf.models` - Unique models with metadata
  - `hf.tasks` - HF task types  
  - `hf.model_tasks` - Many-to-many mapping with rankings

## Troubleshooting

### Rate Limits
- Set `HF_TOKEN` in `.env` for higher rate limits
- The script automatically retries with exponential backoff

### Connection Issues
- Verify `SUPABASE_DB_URL` is correct
- Check that your IP is allowed in Supabase settings
- Ensure the database password is correct

### Logs
- Check `hf_ingestion.log` for detailed error messages
- Console output shows progress in real-time

