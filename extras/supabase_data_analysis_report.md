# Stack8s Supabase Database Analysis Report
**Date:** December 25, 2025  
**Analyst:** Senior AI Engineer Analysis  
**Database:** Supabase (cloud schema)

---

## Executive Summary

The Stack8s Supabase database contains comprehensive data for the **AI Architect** system across two primary domains:
- **GPU/Compute Instances**: 16,695 instances from 7 cloud providers
- **Kubernetes Marketplace**: 13,435 Bitnami packages across 9 categories

### Critical Findings
✅ **Good**: Extensive GPU instance catalog with pricing data  
⚠️ **Issue**: 68% of Bitnami packages lack category classification  
⚠️ **Issue**: 255 instances (1.5%) missing pricing data  
✅ **Good**: Rich AI/ML package ecosystem (175 packages)

---

## 1. Database Schema Overview

### Available Schemas
- `public` - Application tables (conversations, messages, users)
- `cloud` - **Core data for AI Architect** (instances, bitnami_packages, categories, providers, regions)
- `auth` - Supabase authentication
- `storage` - File storage
- `realtime` - Realtime subscriptions

### Key Tables for AI Architect

| Table | Schema | Rows | Purpose |
|-------|--------|------|---------|
| `instances` | cloud | 16,695 | GPU/compute instance catalog with pricing |
| `bitnami_packages` | cloud | 13,435 | Kubernetes marketplace components |
| `bitnami_categories` | cloud | ~9 | Package categorization |
| `providers` | cloud | 7+ | Cloud provider metadata |
| `regions` | cloud | Many | Geographic availability data |

---

## 2. GPU/Compute Instances Analysis (`cloud.instances`)

### 2.1 Schema Structure (39 columns)

**Critical Fields for AI Architect:**
| Field | Type | Nullable | Coverage | Notes |
|-------|------|----------|----------|-------|
| `instance_id` | varchar | YES | 100% | Provider's instance identifier |
| `provider` | varchar | YES | 100% | aws, vultr, digitalocean, etc. |
| `name` | varchar | YES | 100% | Display name |
| `instance_type` | varchar | YES | 100% | e.g., "regular" |
| **GPU Fields** |
| `gpu_count` | integer | YES | Sparse | Often NULL |
| `gpu_model` | varchar | YES | ~15% | L4, T4, A100, H100, etc. |
| `gpu_memory_gb` | integer | YES | Sparse | GPU VRAM |
| `gpu_manufacturer` | varchar | YES | Sparse | NVIDIA, AMD |
| **Compute Resources** |
| `cpu_cores` | integer | YES | 99.7% | 8-96+ cores |
| `memory_gb` | numeric | YES | 99.7% | 4-2048+ GB |
| `memory_mb` | integer | YES | 99.7% | Same as above |
| **Pricing** |
| `price_monthly` | numeric | YES | 98.5% | USD pricing |
| `price_hourly` | numeric | YES | 98.5% | USD pricing |
| `price_currency` | varchar | YES | 98.5% | "USD" |
| **Other** |
| `regions` | jsonb | YES | ~100% | Array of region codes |
| `available` | boolean | YES | ~100% | Stock status |
| `description` | text | YES | ~100% | Human-readable description |
| `capabilities` | jsonb | YES | Sparse | Feature flags |
| `embedding` | USER-DEFINED | YES | Present | Vector embeddings for search |

### 2.2 Provider Distribution

| Provider | Instances | GPU Instances | Avg Monthly Price | Price Range |
|----------|-----------|---------------|-------------------|-------------|
| **AWS** | 14,858 (89%) | 14,858 | $838.34 | $0.37 - $52,232 |
| **OVH** | 1,353 (8%) | 0 | $87,923.47 | $788 - $857,604 |
| **Vultr** | 203 (1.2%) | 29 | $760.12 | $2.50 - $14,000 |
| **DigitalOcean** | 147 (0.9%) | 0 | $1,145.39 | $4 - $35,414 |
| **Contabo** | 75 (0.4%) | 30 | $57.53 | $4.95 - $156 |
| **RunPod** | 38 (0.2%) | 38 | $868.24 | $167.90 - $4,664 |
| **Civo** | 21 (0.1%) | 15 | $3,125.38 | $0 - $17,461 |

**Key Insight**: AWS dominates with 89% market share. All RunPod instances are GPU-focused.

### 2.3 GPU Model Distribution (Top 15)

| GPU Model | Instances | Avg Monthly Price | Avg RAM (GB) | Avg CPU Cores |
|-----------|-----------|-------------------|--------------|---------------|
| **L4** | 216 | $951.33 | 177.60 | 20.04 |
| **T4** | 147 | $948.49 | 153.14 | 19.14 |
| **A10G** | 112 | $1,814.31 | 230.00 | 28.75 |
| **L40S** | 69 | $3,354.22 | 448.43 | 29.51 |
| **T4g** | 42 | $398.17 | 62.67 | 31.33 |
| **Radeon Pro V520** | 40 | $464.88 | 99.20 | 12.40 |
| **V100** | 37 | $5,178.29 | 318.78 | 20.65 |
| **A100** | 24 | $6,612.60 | 863.00 | 44.50 |
| **H100** 🚀 | 23 | $13,257.45 | 1,221.22 | 62.22 |
| **H200** 🚀 | 10 | $14,624.45 | 2,048.00 | 96.00 |
| **B200** 🚀 | 6 | $10,250.15 | 1,657.83 | 113.33 |

**Key Insights**:
- L4 and T4 are most common (entry-level GPUs)
- H100/H200 are premium options at $13K-15K/month
- Clear pricing tiers: Entry ($400-1K), Mid ($2K-5K), Premium ($6K-15K)

### 2.4 Sample GPU Instances

**Example 1: DigitalOcean RTX 6000 Ada**
```json
{
  "provider": "digitalocean",
  "instance_id": "gpu-6000adax1-48gb",
  "gpu_model": null,  // ⚠️ Missing
  "cpu_cores": 8,
  "memory_gb": 64,
  "price_monthly": "$1,406.16",
  "regions": ["tor1"],
  "description": "RTX 6000 Ada GPU Droplet - 1X"
}
```

**Example 2: DigitalOcean H100**
```json
{
  "provider": "digitalocean",
  "instance_id": "gpu-h100x1-80gb",
  "gpu_model": null,  // ⚠️ Missing
  "cpu_cores": 20,
  "memory_gb": 240,
  "price_monthly": "$2,522.16",
  "regions": ["nyc2", "tor1"],
  "description": "H100 GPU - 1X"
}
```

---

## 3. Kubernetes Marketplace (`cloud.bitnami_packages`)

### 3.1 Schema Structure (52 columns)

**Critical Fields for AI Architect:**
| Field | Type | Purpose |
|-------|------|---------|
| `package_id` | uuid | Primary key |
| `name` | text | Package name |
| `normalized_name` | text | Searchable name |
| `category` | integer | FK to bitnami_categories |
| `is_operator` | boolean | Kubernetes operator flag |
| `description` | text | Package description |
| `version` | text | Chart version |
| `app_version` | text | Application version |
| `license` | text | SPDX license identifier |
| `stars` | integer | Popularity metric |
| `deprecated` | boolean | Lifecycle status |
| `repository_name` | text | Source repo |
| `repository_official` | boolean | Official package flag |

### 3.2 Category Distribution

| Category ID | Category Name | Packages | Operators | % of Total |
|-------------|---------------|----------|-----------|------------|
| **NULL** | ⚠️ Uncategorized | 9,145 | 321 | 68.1% |
| **4** | Monitoring & Logging | 1,060 | 72 | 7.9% |
| **5** | Networking | 713 | 37 | 5.3% |
| **6** | Security | 688 | 49 | 5.1% |
| **3** | Integration & Delivery | 610 | 108 | 4.5% |
| **2** | Database | 527 | 41 | 3.9% |
| **7** | Storage | 291 | 23 | 2.2% |
| **8** | Streaming & Messaging | 226 | 22 | 1.7% |
| **1** | AI / Machine Learning | 175 | 12 | 1.3% |

**Critical Issue**: 68% of packages lack category classification. This will impact recommendation quality.

### 3.3 AI/ML Packages (Top 10 by Stars)

| Name | Version | Stars | Description |
|------|---------|-------|-------------|
| **jupyterhub** | 4.2.1 | 70⭐ | Multi-user Jupyter installation |
| **superset** | 0.15.0 | 49⭐ | Enterprise BI web application |
| **spark** | 10.0.3 | 47⭐ | Large-scale data processing engine |
| **ollama** | 1.31.0 | 45⭐ | Local LLM platform 🚀 |
| **mlflow** | 1.7.1 | 28⭐ | ML lifecycle management |
| **openmetadata** | 1.9.11 | 23⭐ | Metadata management |
| **jupyterhub** (alt) | 10.0.5 | 18⭐ | Notebook platform for groups |
| **clearml** | 7.14.7 | 18⭐ | MLOps platform |
| **moodle** | 28.0.0 | 17⭐ | Learning management system |
| **pytorch** | 4.3.31 | 12⭐ | Deep learning platform |

**Key Insights**:
- Ollama present for local LLM deployment
- Strong Jupyter ecosystem
- MLOps tools well-represented (MLflow, ClearML)
- Popular frameworks: PyTorch, Spark

---

## 4. Data Quality Assessment

### 4.1 Instances Table Issues

| Issue | Affected Rows | Impact |
|-------|---------------|--------|
| Missing GPU info (in GPU instances) | 9 | Low - Only 0.05% affected |
| Missing pricing | 255 (1.5%) | **Medium** - Cannot recommend without price |
| Missing memory info | 49 (0.3%) | Low - Small subset |
| Missing CPU info | 49 (0.3%) | Low - Same subset as memory |

**Overall Quality**: ✅ **GOOD** (98.5% completeness for critical fields)

### 4.2 Bitnami Packages Issues

| Issue | Affected Rows | Impact |
|-------|---------------|--------|
| Packages without category | 9,145 (68%) | **🚨 CRITICAL** - Hard to filter/recommend |
| Packages without description | 71 (0.5%) | Low - Minimal impact |
| Deprecated packages | 0 (0%) | ✅ None - Good data hygiene |

**Overall Quality**: ⚠️ **NEEDS IMPROVEMENT** (68% lack categorization)

---

## 5. Recommendations for AI Architect System

### 5.1 Immediate Actions Required

#### **🚨 CRITICAL: Bitnami Package Categorization**
- **Problem**: 68% of packages (9,145) have no category
- **Impact**: Agent cannot effectively filter/recommend by domain
- **Solutions**:
  1. **Option A**: Use embeddings + clustering to auto-categorize
  2. **Option B**: Manual tagging sprint for top 1,000 most-used packages
  3. **Option C**: Fallback to text search on `description` field
  
**Recommendation**: Implement Option C immediately (use description text), plan Option A for v2.

#### **🔧 Medium Priority: GPU Model Standardization**
- **Problem**: `gpu_model` field is NULL for many GPU instances
- **Impact**: Cannot filter by specific GPU types (H100, A100, etc.)
- **Solution**: Parse from `description` field:
  ```sql
  -- Example: "H100 GPU - 1X" → extract "H100"
  -- Example: "RTX 6000 Ada GPU Droplet - 1X" → extract "RTX 6000 Ada"
  ```

#### **🔧 Medium Priority: Missing Pricing**
- **Problem**: 255 instances lack pricing
- **Impact**: Cannot include in cost-based recommendations
- **Solution**: Mark as "Contact Provider" or exclude from results

### 5.2 Data Contracts for AI Architect

#### **Instances Table - Reliable Fields**
```typescript
interface ReliableInstanceFields {
  provider: string;          // ✅ 100% populated
  instance_id: string;       // ✅ 100% populated
  name: string;              // ✅ 100% populated
  description: string;       // ✅ ~100% populated
  cpu_cores: number;         // ✅ 99.7% populated
  memory_gb: number;         // ✅ 99.7% populated
  price_monthly: number;     // ✅ 98.5% populated
  regions: string[];         // ✅ ~100% populated
  available: boolean;        // ✅ ~100% populated
  embedding: vector;         // ✅ Present for semantic search
}
```

#### **Instances Table - Unreliable Fields (Use with Caution)**
```typescript
interface UnreliableInstanceFields {
  gpu_model: string | null;      // ⚠️ Often NULL - parse from description
  gpu_count: number | null;      // ⚠️ Sparse
  gpu_memory_gb: number | null;  // ⚠️ Sparse
  capabilities: object | null;   // ⚠️ Sparse
}
```

#### **Bitnami Packages - Reliable Fields**
```typescript
interface ReliablePackageFields {
  name: string;               // ✅ 100% populated
  normalized_name: string;    // ✅ 100% populated
  description: string;        // ✅ 99.5% populated
  version: string;            // ✅ ~100% populated
  is_operator: boolean;       // ✅ Reliable
  deprecated: boolean;        // ✅ Reliable (0 deprecated)
  stars: number;              // ✅ Popularity metric
}
```

#### **Bitnami Packages - Unreliable Fields**
```typescript
interface UnreliablePackageFields {
  category: number | null;    // ⚠️ 68% NULL - implement fallback
  license: string | null;     // ⚠️ Often NULL
}
```

### 5.3 Embedding Strategy

**Good News**: The `embedding` column exists in `cloud.instances` table!

**Type**: `USER-DEFINED` (likely `vector` type from pgvector extension)

**Usage for Agent 2 (Solutions Architect)**:
```sql
-- Semantic search for GPU instances based on user requirements
SELECT instance_id, name, description, price_monthly
FROM cloud.instances
WHERE embedding <=> embedding_from_text($user_query)
ORDER BY embedding <=> embedding_from_text($user_query)
LIMIT 10;
```

**Recommendation**: Test if embeddings exist for `bitnami_packages`. If not, generate them.

### 5.4 Query Patterns for AI Architect

#### **Pattern 1: Find GPU instances by budget**
```sql
SELECT 
  provider, instance_id, name, description,
  cpu_cores, memory_gb, price_monthly, regions
FROM cloud.instances
WHERE price_monthly IS NOT NULL
  AND price_monthly BETWEEN $min_budget AND $max_budget
  AND description ILIKE '%gpu%'
ORDER BY price_monthly ASC
LIMIT 20;
```

#### **Pattern 2: Find AI/ML packages**
```sql
SELECT 
  name, version, app_version, description, stars, license
FROM cloud.bitnami_packages
WHERE category = 1  -- AI/ML category
   OR description ILIKE ANY(ARRAY['%machine learning%', '%AI%', '%jupyter%', '%ml%'])
ORDER BY stars DESC NULLS LAST
LIMIT 20;
```

#### **Pattern 3: Find monitoring stack components**
```sql
SELECT name, description, version, stars
FROM cloud.bitnami_packages
WHERE category = 4  -- Monitoring & Logging
   OR name IN ('prometheus', 'grafana', 'loki', 'elasticsearch')
ORDER BY stars DESC NULLS LAST;
```

---

## 6. Gaps vs. PRD Requirements

### ✅ **SATISFIED Requirements**
- [x] GPU compute data available (7 providers, 16K+ instances)
- [x] Pricing data present (98.5% coverage)
- [x] Kubernetes marketplace data (13K+ packages)
- [x] Multi-cloud coverage (AWS, Vultr, DigitalOcean, etc.)
- [x] Vector embeddings for semantic search

### ⚠️ **PARTIALLY SATISFIED Requirements**
- [~] GPU model classification (needs parsing from descriptions)
- [~] Package categorization (68% uncategorized - needs fallback)
- [~] Local cluster compute (not present in current data)

### ❌ **MISSING Requirements**
- [ ] Real-time stock/availability (field exists but not validated)
- [ ] Model compatibility matrix (not in database)
- [ ] Hugging Face model metadata (not in database - will query API)

---

## 7. Technical Notes

### Database Features Detected
- ✅ **pgvector extension** - Embeddings for semantic search
- ✅ **JSONB fields** - `regions`, `capabilities`, `raw_data`
- ✅ **Foreign keys** - Proper relational structure
- ✅ **Timestamps** - `created_at`, `updated_at` for data freshness

### Performance Considerations
- Large tables: `instances` (16K rows), `bitnami_packages` (13K rows)
- Indexes likely needed on: `provider`, `category`, `price_monthly`, `gpu_model`
- Vector search on `embedding` column should be efficient with proper index

---

## 8. Next Steps for Implementation

### Day 1: Data Foundation ✅
- [x] Explore database schema
- [x] Validate data quality
- [x] Identify reliable vs unreliable fields
- [ ] Write data access layer with fallbacks

### Day 2: Agent Intelligence
- [ ] Implement GPU model extraction from descriptions
- [ ] Implement category fallback (text search on descriptions)
- [ ] Test embedding-based semantic search
- [ ] Connect to Hugging Face API for model data

### Day 3: Recommendation Logic
- [ ] Build GPU ranking algorithm (price, performance, availability)
- [ ] Build package matching logic (by category, description, stars)
- [ ] Implement cost estimation
- [ ] Generate alternatives

### Day 4: Polish & Edge Cases
- [ ] Handle missing pricing gracefully
- [ ] Handle uncategorized packages
- [ ] Add confidence scores to recommendations
- [ ] Test with real scenarios

---

## 9. Conclusion

### ✅ **READY TO BUILD**
The Supabase database contains sufficient data to build the AI Architect system. Key strengths:
- Extensive GPU catalog (16,695 instances)
- Rich Kubernetes marketplace (13,435 packages)
- Vector embeddings for intelligent search
- Multi-cloud coverage

### ⚠️ **TECHNICAL DEBT TO ADDRESS**
- Implement GPU model parsing from descriptions
- Build category fallback logic for 68% uncategorized packages
- Add graceful handling of missing pricing data

### 🚀 **RECOMMENDED APPROACH**
Build v1 with **pragmatic fallbacks** rather than perfect data. The agent can:
1. Use description text when GPU model is NULL
2. Use description text search when category is NULL
3. Mark instances without pricing as "Contact Provider"
4. Rely on embeddings for intelligent matching

This aligns perfectly with **Option 2.5** from the PRD - data-aware, structured reasoning with graceful degradation.

---

**End of Report**

