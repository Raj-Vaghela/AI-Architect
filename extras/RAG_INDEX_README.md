# HF RAG Index Builder - Instructions

## Overview

This system builds a deterministic, versioned RAG index from Hugging Face model cards with:
- ✅ Automatic exclusion of low-quality cards
- ✅ Deduplication by content hash (saves ~11% embedding costs)
- ✅ Section-based chunking with markdown awareness
- ✅ OpenAI embeddings (text-embedding-3-small)
- ✅ Resumable processing (idempotent operations)
- ✅ Comprehensive reporting

## Prerequisites

1. **Python 3.8+** with packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Supabase Database** with:
   - `hf.models` table (already exists)
   - `hf.model_cards` table (already exists with 30,403 cards)
   - New tables created by migrations (card_canon, model_to_card, card_chunks)

3. **OpenAI API Key** for embeddings

## Setup

### Step 1: Configure Environment

Copy the template and fill in your credentials:

```bash
cp env.local.template .env.local
```

Edit `.env.local`:

```bash
# Supabase Database Connection
SUPABASE_DB_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_EMBED_MODEL=text-embedding-3-small

# Chunking Configuration (defaults are good)
CHUNKER_VERSION=hf_chunker_v1
CHUNK_TARGET_TOKENS=900
CHUNK_OVERLAP_TOKENS=120

# Processing Limits
MAX_CANON_MODELS=0  # 0 = process all, use 50 for testing
BATCH_SIZE=100
```

### Step 2: Test Run (Recommended)

Test with 50 models first:

```bash
# Edit .env.local and set:
MAX_CANON_MODELS=50

# Run the script
python scripts/build_hf_rag_index.py --env-file .env.local
```

**Expected output:**
- Exclusions applied (~5-7% of cards)
- Canonical mapping created
- ~125-150 chunks generated
- Embeddings generated (takes ~2-3 minutes)
- Report generated at `docs/hf_rag_index_report.md`

### Step 3: Review Test Report

Check `docs/hf_rag_index_report.md` for:
- ✅ Exclusion counts look reasonable
- ✅ Deduplication stats (should see ~10% duplicates)
- ✅ Chunk counts per card (median should be ~2-3)
- ✅ No major failures

### Step 4: Full Run

Once test looks good:

```bash
# Edit .env.local and set:
MAX_CANON_MODELS=0  # Process all ~27k unique cards

# Run full pipeline
python scripts/build_hf_rag_index.py --env-file .env.local
```

**Full run estimates:**
- **Chunking:** ~5-10 minutes
- **Embeddings:** ~2-3 hours for ~65k chunks
- **Total cost:** ~$8-12 (OpenAI embeddings)

## What the Script Does

### Step A: Exclusion Rules

Marks cards as `excluded_from_rag=true`:
1. "No model card found." (1,045 cards)
2. Token count < 50 (minimal/empty cards)
3. Token count > 100,000 (likely non-textual data)

### Step B: Canonical Mapping (Deduplication)

- Groups cards by `card_hash` (SHA256 of content)
- Picks canonical model per group (highest downloads → likes → model_id)
- Creates `hf.card_canon` table
- Maps all models to canonical cards in `hf.model_to_card`

**Result:** ~27k unique cards instead of 30k (saves ~11% embedding costs)

### Step C: Deterministic Chunking

For each canonical card:
1. **Normalize text** (consistent line endings, collapse blank lines)
2. **Extract key sections** for large cards (10k-100k tokens)
3. **Chunk by markdown headings** (## and ###)
4. **Fall back to sliding window** if no headings
5. **Target 900 tokens per chunk** with 120-token overlap
6. **Compute chunk_hash** (SHA256) for deduplication

**Result:** ~65-70k chunks stored in `hf.card_chunks`

### Step D: OpenAI Embeddings

- Generates embeddings only for chunks where `embedding IS NULL`
- Uses `text-embedding-3-small` (1536 dimensions)
- Rate-limited with exponential backoff
- Resumable (safe to rerun if interrupted)

**Result:** All chunks get vector embeddings for similarity search

## Output Files

### 1. `docs/hf_rag_index_report.md`

Comprehensive report with:
- Configuration used
- Exclusion counts by reason
- Deduplication statistics
- Chunk counts and token distributions
- Top 20 largest cards and how they were handled
- Any failures encountered

### 2. `hf_rag_index.log`

Detailed execution log with timestamps

## Database Tables Created

### `hf.card_canon`
Canonical card mapping (deduplicated)
- `card_hash` (PK)
- `canonical_model_id`
- `duplicate_count`

### `hf.model_to_card`
Maps all models to their canonical card
- `model_id` (PK, FK to hf.models)
- `card_hash` (FK to hf.card_canon)

### `hf.card_chunks`
Chunked text with embeddings
- `id` (PK)
- `chunk_hash` (deterministic ID)
- `card_hash` (FK to hf.card_canon)
- `chunk_index` (order within card)
- `chunk_text`
- `token_count`
- `embedding` (vector[1536])
- `embedding_model_name`
- `chunker_version`
- **Unique constraint:** (chunker_version, embedding_model_name, chunk_hash)

## Resumability

The script is fully resumable:

1. **Exclusions:** Updates only non-excluded cards
2. **Canonical mapping:** Uses `ON CONFLICT DO UPDATE`
3. **Chunking:** Uses unique constraint on (chunker_version, embedding_model_name, chunk_hash)
4. **Embeddings:** Only processes chunks where `embedding IS NULL`

**Safe to rerun** without duplicating work or data!

## Validation Queries

After running, verify with these SQL queries:

```sql
-- Check exclusion counts
SELECT exclusion_reason, COUNT(*) 
FROM hf.model_cards 
WHERE excluded_from_rag = TRUE 
GROUP BY exclusion_reason;

-- Check canonical mapping
SELECT COUNT(*) as unique_cards FROM hf.card_canon;
SELECT COUNT(*) as total_mappings FROM hf.model_to_card;

-- Check chunks
SELECT COUNT(*) as total_chunks FROM hf.card_chunks;
SELECT COUNT(*) as chunks_with_embeddings 
FROM hf.card_chunks 
WHERE embedding IS NOT NULL;

-- Verify no excluded cards were chunked
SELECT COUNT(*) 
FROM hf.card_chunks cc
JOIN hf.card_canon canon ON cc.card_hash = canon.card_hash
JOIN hf.model_cards mc ON canon.canonical_model_id = mc.model_id
WHERE mc.excluded_from_rag = TRUE;
-- Should return 0

-- Check chunk uniqueness
SELECT chunk_hash, COUNT(*) 
FROM hf.card_chunks 
GROUP BY chunk_hash 
HAVING COUNT(*) > 1;
-- Should return 0 rows (all unique)
```

## Cost Estimates

### OpenAI Embeddings

**text-embedding-3-small:**
- $0.02 per 1M tokens
- ~65k chunks × ~800 avg tokens = ~52M tokens
- **Cost:** ~$1.04

**Actual cost will be higher due to:**
- API overhead
- Retry attempts
- **Estimated total:** $8-12

### Supabase Storage

**Vector storage:**
- 65k chunks × 1536 dimensions × 4 bytes = ~400 MB
- Well within free tier limits

## Troubleshooting

### "SUPABASE_DB_URL not set"
- Check `.env.local` exists and has correct variable name
- Verify no typos in the connection string

### "OpenAI rate limit errors"
- Script has automatic retry with exponential backoff
- Will slow down automatically, just wait
- Check your OpenAI account has available quota

### "Chunks not getting embeddings"
- Check `WHERE embedding IS NULL` in database
- Verify OpenAI API key is valid
- Check `hf_rag_index.log` for specific errors

### "Out of memory during chunking"
- Reduce `MAX_CANON_MODELS` to process in smaller batches
- Run multiple times, script will skip already-chunked cards

## Next Steps After Building Index

1. **Test vector search:**
   ```sql
   SELECT model_id, chunk_text, 
          embedding <=> '[your_query_embedding]' as distance
   FROM hf.card_chunks cc
   JOIN hf.card_canon canon ON cc.card_hash = canon.card_hash
   ORDER BY distance
   LIMIT 10;
   ```

2. **Build RAG query interface**
3. **Add metadata filtering** (task, license, downloads)
4. **Implement reranking** for better precision

## Support

For issues or questions:
1. Check `hf_rag_index.log` for detailed errors
2. Review `docs/hf_rag_index_report.md` for statistics
3. Run validation SQL queries above

---

**Built with:** Python, PostgreSQL, pgvector, OpenAI, tiktoken

