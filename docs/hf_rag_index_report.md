# HF RAG Index Build Report

**Generated:** 2025-12-28T11:10:14.283769  
**Chunker Version:** hf_chunker_v1  
**Embedding Model:** text-embedding-3-small  
**Tokenizer:** tiktoken cl100k_base  

## Configuration

| Parameter | Value |
|-----------|-------|
| Chunk Target Tokens | 900 |
| Chunk Overlap Tokens | 120 |
| Max Canon Models | 0 (0 = no limit) |
| Batch Size | 100 |

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Models** | 30,403 |
| **Total Model Cards** | 30,403 |
| **Excluded Cards** | 2,079 |
| - No content | 1,045 |
| - Too short (<50 tokens) | 990 |
| - Too long (>100k tokens) | 44 |
| **Unique Card Hashes (Canon)** | 26,346 |
| **Total Model Mappings** | 28,324 |
| **Duplicate Models** | 1,978 |
| **Total Chunks Generated** | 156,935 |
| **Chunks Inserted** | 95,596 |
| **Chunks with Embeddings** | 95,596 |
| **Chunks Pending Embeddings** | 0 |

## Chunk Statistics

### Chunks per Card

| Metric | Value |
|--------|-------|
| Minimum | 1 |
| Median | 1 |
| Maximum | 69 |

### Chunk Token Distribution

| Metric | Tokens |
|--------|--------|
| Minimum | 0 |
| Median | 226 |
| p95 | 900 |
| Maximum | 901 |

## Top 20 Largest Cards

| Model ID | Token Count | Excluded | Reason |
|----------|-------------|----------|--------|
| s3nh/SegFormer-b4-person-segmentation | 278,027 | ✅ | Too long (>100k tokens, likely non-textual) |
| s3nh/SegFormer-b0-person-segmentation | 277,999 | ✅ | Too long (>100k tokens, likely non-textual) |
| jinaai/jina-embeddings-v3 | 276,167 | ✅ | Too long (>100k tokens, likely non-textual) |
| LightDestory/segformer-b0-finetuned-segments-food-oct-24v2 | 261,544 | ✅ | Too long (>100k tokens, likely non-textual) |
| dwang-LI/segformer-b0-finetuned-segments-sidewalk-2 | 252,683 | ✅ | Too long (>100k tokens, likely non-textual) |
| mlx-community/nomicai-modernbert-embed-base-4bit | 241,973 | ✅ | Too long (>100k tokens, likely non-textual) |
| mlx-community/nomicai-modernbert-embed-base-bf16 | 241,970 | ✅ | Too long (>100k tokens, likely non-textual) |
| ibm-granite/granite-embedding-107m-multilingual | 236,917 | ✅ | Too long (>100k tokens, likely non-textual) |
| gety-ai/granite-embedding-107m-multilingual-onnx | 236,902 | ✅ | Too long (>100k tokens, likely non-textual) |
| ibm-granite/granite-embedding-278m-multilingual | 236,723 | ✅ | Too long (>100k tokens, likely non-textual) |
| HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1 | 227,570 | ✅ | Too long (>100k tokens, likely non-textual) |
| HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1.5 | 227,546 | ✅ | Too long (>100k tokens, likely non-textual) |
| HIT-TMG/KaLM-embedding-multilingual-mini-v1 | 227,415 | ✅ | Too long (>100k tokens, likely non-textual) |
| EMBO/ModernBERT-neg-sampling-PubMed | 224,454 | ✅ | Too long (>100k tokens, likely non-textual) |
| powerpuf-bot/mdeberta-v3-th-wiki-qa_hyp-params | 208,731 | ✅ | Too long (>100k tokens, likely non-textual) |
| lightonai/modernbert-embed-large | 208,730 | ✅ | Too long (>100k tokens, likely non-textual) |
| nomic-ai/modernbert-embed-base | 208,073 | ✅ | Too long (>100k tokens, likely non-textual) |
| Mihaiii/Venusaur | 207,202 | ✅ | Too long (>100k tokens, likely non-textual) |
| Mihaiii/Ivysaur | 207,123 | ✅ | Too long (>100k tokens, likely non-textual) |
| nomic-ai/modernbert-embed-base-unsupervised | 206,217 | ✅ | Too long (>100k tokens, likely non-textual) |

## Failures

Total failures: 2

| Type | ID | Error |
|------|-----|-------|
| chunking | 462734edb356470246a8f5d3a35c2533f65746ea7df6bc3881ad01cf6528d299 | Encountered text corresponding to disallowed special token '<|endoftext|>'.
If you want this text to |
| chunking | ea990d9ab0077380a244b92fdd6b623a7f4346a1a567f5255dfb056d8e1dd442 | Encountered text corresponding to disallowed special token '<|endoftext|>'.
If you want this text to |

## Next Steps

1. Verify chunk uniqueness constraint
2. Confirm excluded cards have no chunks
3. Test vector similarity search
4. Run sample RAG queries

---

**Report End**
