# V1 Data Contract: AI Architect Recommender System

**Version:** 1.0  
**Last Updated:** 2025-12-25  
**Status:** Proposed

---

## Purpose

This document defines the **data contracts** for the AI Architect's two recommender systems, explicitly stating what recommendations can be made reliably with current data and what limitations exist.

---

## 1. Compute Recommender Contract

### 1.1 Input Schema

```typescript
interface ComputeRequest {
  // REQUIRED filters (user must specify at least one)
  min_vcpu?: number;           // Minimum vCPU cores
  min_ram_gb?: number;          // Minimum RAM in GB
  max_price_monthly?: number;   // Maximum monthly price
  
  // OPTIONAL filters
  providers?: string[];         // e.g., ["aws", "vultr", "runpod"]
  gpu_required?: boolean;       // true = must have GPU, false = no GPU
  gpu_count?: number;           // Specific GPU count (1, 2, 4, 8)
  regions?: string[];           // e.g., ["us-east-1", "eu-west-1"]
  
  // UI/display options
  limit?: number;               // Max results to return (default: 10)
  sort_by?: "price" | "vcpu" | "ram" | "gpu_count";
}
```

### 1.2 Output Schema

```typescript
interface ComputeRecommendation {
  // Instance identification
  instance_id: string;          // Unique instance ID
  provider: string;             // Cloud provider
  name: string;                 // Instance name/type
  
  // Compute specs (ALWAYS AVAILABLE)
  vcpu: number;                 // CPU cores (99.7% coverage)
  ram_gb: number;               // RAM in GB (99.7% coverage)
  
  // Pricing (ALWAYS AVAILABLE)
  price_monthly: number;        // Monthly price (98.5% coverage)
  price_hourly: number | null;  // Hourly price (98.1% coverage)
  price_currency: string;       // Currency code (100% coverage)
  
  // GPU info (PARTIAL - see limitations)
  gpu_count: number | null;     // GPU count (89.7% coverage)
  gpu_model: string | null;     // GPU model (4.7% coverage) ⚠️
  gpu_vram_gb: number | null;   // GPU VRAM (4.8% coverage) ⚠️
  
  // Geographic availability
  regions: string[];            // Available regions (99.7% coverage)
  
  // Data quality indicator
  data_quality: {
    has_gpu_details: boolean;   // true if gpu_model AND gpu_vram_gb present
    completeness_score: number; // 0.0-1.0
  };
}
```

### 1.3 Supported Decisions ✅

The Compute Recommender **CAN reliably** make the following decisions:

| Decision Type | Reliability | Data Coverage | Example Query |
|--------------|-------------|---------------|---------------|
| **Filter by provider** | ✅ Excellent | 100% | "Show me AWS instances" |
| **Filter by vCPU** | ✅ Excellent | 99.7% | "I need at least 8 cores" |
| **Filter by RAM** | ✅ Excellent | 99.7% | "I need 32GB RAM minimum" |
| **Filter by price** | ✅ Excellent | 98.5% | "Under $500/month" |
| **Filter by GPU presence** | ✅ Good | 89.7% | "I need a GPU instance" |
| **Filter by GPU count** | ✅ Good | 89.7% | "I need 2 GPUs" |
| **Filter by region** | ✅ Excellent | 99.7% | "Available in us-east-1" |
| **Sort by price** | ✅ Excellent | 98.5% | "Show cheapest first" |
| **Price comparison** | ✅ Excellent | 98.5% | "Compare prices across providers" |

### 1.4 Unsupported Decisions ❌

The Compute Recommender **CANNOT reliably** make these decisions with current data:

| Decision Type | Reliability | Data Coverage | Issue |
|--------------|-------------|---------------|-------|
| **Filter by GPU model** | ❌ Unreliable | 4.7% | "I need an A100" ➔ 95% of data missing |
| **Filter by GPU VRAM** | ❌ Unreliable | 4.8% | "I need 80GB VRAM" ➔ 95% of data missing |
| **Filter by GPU manufacturer** | ❌ Not Available | 0% | "I need NVIDIA GPUs" ➔ field empty |
| **Recommend specific GPU** | ❌ Unreliable | 4.7% | "Best GPU for training" ➔ insufficient data |

### 1.5 Handling Missing GPU Data

**Current Behavior:**
```typescript
// When user asks: "I need an A100 instance"
if (gpu_model_query) {
  const results = await queryByGPUModel("A100");
  
  if (results.length === 0) {
    // FALLBACK: Return GPU instances without model filter
    return {
      instances: await queryByGPUCount(1),
      warning: "⚠️ GPU model data is limited (only 4.7% of instances have GPU specs). " +
               "Showing instances with 1+ GPU. Please verify GPU model with provider."
    };
  }
}
```

**User-Facing Message:**
> "⚠️ **GPU Details Limited:** Only 5% of our instance data includes GPU model and VRAM information. We're showing instances with GPUs, but you'll need to verify the specific GPU type with your cloud provider."

### 1.6 Proposed Fix: `gpu_specs` Mapping Table

To enable GPU model filtering, we propose a lightweight mapping table:

```sql
-- DO NOT CREATE YET - PROPOSAL ONLY

CREATE TABLE IF NOT EXISTS cloud.gpu_specs (
    gpu_model VARCHAR(100) PRIMARY KEY,          -- e.g., "A100", "H100", "L4"
    gpu_manufacturer VARCHAR(50),                 -- e.g., "NVIDIA", "AMD"
    vram_gb INTEGER NOT NULL,                     -- VRAM in GB (e.g., 80)
    architecture VARCHAR(50),                     -- e.g., "Ampere", "Hopper"
    compute_capability VARCHAR(10),               -- e.g., "8.0", "9.0"
    tensor_cores BOOLEAN,                         -- Has tensor cores
    fp16_tflops NUMERIC(8, 2),                   -- FP16 performance
    fp32_tflops NUMERIC(8, 2),                   -- FP32 performance
    typical_use_cases TEXT[],                    -- e.g., ['training', 'inference', 'llm']
    release_year INTEGER,                        -- GPU release year
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample data
INSERT INTO cloud.gpu_specs (gpu_model, gpu_manufacturer, vram_gb, architecture, typical_use_cases) VALUES
('A100', 'NVIDIA', 80, 'Ampere', ARRAY['training', 'inference', 'hpc']),
('A100', 'NVIDIA', 40, 'Ampere', ARRAY['training', 'inference']),
('H100', 'NVIDIA', 80, 'Hopper', ARRAY['training', 'llm', 'inference']),
('H200', 'NVIDIA', 141, 'Hopper', ARRAY['training', 'llm', 'inference']),
('L4', 'NVIDIA', 24, 'Ada Lovelace', ARRAY['inference', 'video']),
('L40S', 'NVIDIA', 48, 'Ada Lovelace', ARRAY['training', 'inference', 'graphics']),
('T4', 'NVIDIA', 16, 'Turing', ARRAY['inference', 'edge']),
('V100', 'NVIDIA', 32, 'Volta', ARRAY['training', 'inference']),
('V100', 'NVIDIA', 16, 'Volta', ARRAY['training', 'inference']),
('A10G', 'NVIDIA', 22, 'Ampere', ARRAY['inference', 'graphics']),
('Radeon Pro V520', 'AMD', 8, 'RDNA 2', ARRAY['graphics', 'inference']);
```

**Usage Pattern:**
```sql
-- User asks: "I need A100 with 80GB VRAM"
-- 1. Look up GPU specs
SELECT vram_gb FROM cloud.gpu_specs WHERE gpu_model = 'A100' AND vram_gb >= 80;

-- 2. Query instances (with fallback)
SELECT * FROM cloud.instances
WHERE 
    gpu_model = 'A100' 
    AND gpu_memory_gb >= 80
UNION ALL
-- FALLBACK: If no results, use gpu_count as proxy
SELECT * FROM cloud.instances
WHERE 
    gpu_count >= 1
    AND gpu_model IS NULL
    AND provider IN ('aws', 'runpod')  -- Known to have A100s
ORDER BY price_monthly
LIMIT 10;
```

**Data Entry Strategy:**
- Start with top 30 GPU models (covers 90% of actual GPU instances)
- Source data from NVIDIA/AMD spec sheets
- Low maintenance (GPUs don't change often)
- ~50 rows total

---

## 2. Marketplace Recommender Contract

### 2.1 Input Schema

```typescript
interface MarketplaceRequest {
  // OPTION A: Component-based query
  component_category?: string;   // e.g., "vector-database", "inference"
  
  // OPTION B: Keyword-based query
  keywords?: string[];           // e.g., ["redis", "database"]
  
  // OPTION C: Text search
  search_text?: string;          // Free-text search in description
  
  // OPTIONAL filters
  categories?: number[];         // Existing category IDs (1-8)
  min_stars?: number;            // Minimum popularity
  is_operator?: boolean;         // Operators only
  official_only?: boolean;       // Official packages only
  cncf_only?: boolean;           // CNCF projects only
  exclude_deprecated?: boolean;  // Exclude deprecated (default: true)
  
  // UI/display options
  limit?: number;                // Max results (default: 10)
  sort_by?: "stars" | "relevance";
}
```

### 2.2 Output Schema

```typescript
interface MarketplaceRecommendation {
  // Package identification
  package_id: string;            // Unique package ID
  name: string;                  // Package name (100% coverage)
  
  // Installation info (ALWAYS AVAILABLE)
  version: string;               // Helm chart version (100% coverage)
  app_version: string;           // Application version (99.8% coverage)
  content_url: string;           // Helm install URL (100% coverage)
  
  // Description (ALWAYS AVAILABLE)
  description: string;           // Package description (99.5% coverage)
  home_url: string | null;       // Project homepage (53% coverage)
  
  // Categorization (PARTIAL - see limitations)
  category: number | null;       // Category ID (31.9% coverage) ⚠️
  category_name: string | null;  // Category name
  keywords: string[];            // Keywords array (42% populated) ⚠️
  
  // Quality indicators (GOOD COVERAGE)
  stars: number | null;          // Popularity (92% coverage)
  is_operator: boolean;          // Operator flag (100% coverage)
  official: boolean | null;      // Official package
  cncf: boolean | null;          // CNCF project
  
  // Data quality indicator
  data_quality: {
    has_category: boolean;       // true if category assigned
    has_keywords: boolean;       // true if keywords populated
    completeness_score: number;  // 0.0-1.0
  };
}
```

### 2.3 Supported Decisions ✅

The Marketplace Recommender **CAN reliably** make the following decisions:

| Decision Type | Reliability | Data Coverage | Example Query |
|--------------|-------------|---------------|---------------|
| **Text search in description** | ✅ Excellent | 99.5% | "Show me Redis packages" |
| **Filter by package name** | ✅ Excellent | 100% | "Find postgres" |
| **Filter by version** | ✅ Excellent | 100% | "Show latest versions" |
| **Filter by popularity (stars)** | ✅ Excellent | 92% | "Most popular packages" |
| **Filter by operator flag** | ✅ Excellent | 100% | "Show only operators" |
| **Filter by official status** | ✅ Good | 360 official | "Official packages only" |
| **Filter by CNCF status** | ✅ Good | 45 CNCF | "CNCF projects only" |
| **Install via Helm** | ✅ Excellent | 100% | content_url always available |

### 2.4 Partially Supported Decisions ⚠️

These decisions work but have **significant data gaps**:

| Decision Type | Reliability | Data Coverage | Limitation |
|--------------|-------------|---------------|------------|
| **Filter by category** | ⚠️ Partial | 31.9% | "Show databases" ➔ 68% uncategorized |
| **Filter by keywords** | ⚠️ Partial | 42% | "Packages tagged 'monitoring'" ➔ 58% no keywords |
| **Browse by category** | ⚠️ Partial | 31.9% | Most packages won't appear |

**Fallback Strategy:**
```typescript
// When filtering by category and result count is low
if (results.length < 5 && category_filter) {
  // FALLBACK: Search by keyword + description
  const fallbackResults = await searchByText(getCategoryKeywords(category));
  return {
    categorized: results,
    suggested: fallbackResults,
    warning: "⚠️ Only 32% of packages are categorized. Showing additional suggestions."
  };
}
```

### 2.5 Unsupported Decisions ❌

The Marketplace Recommender **CANNOT reliably** make these decisions:

| Decision Type | Reliability | Data Coverage | Issue |
|--------------|-------------|---------------|-------|
| **Browse by AI stack component** | ❌ Not Available | N/A | No component taxonomy exists |
| **Filter "vector databases"** | ❌ Unreliable | Manual search only | Not a standard category |
| **Filter "inference servers"** | ❌ Unreliable | Manual search only | Not a standard category |
| **Filter "MLOps platforms"** | ❌ Unreliable | Manual search only | Not a standard category |
| **Recommend complete stack** | ❌ Not Available | N/A | No component relationships defined |

### 2.6 User-Facing Messages

**When category filtering returns few results:**
> "⚠️ **Limited Categorization:** Only 32% of packages have category assignments. We've included additional suggestions based on keyword matching."

**When AI stack components are requested:**
> "ℹ️ **Component Tags Coming Soon:** We're currently building a component taxonomy for AI stacks (vector databases, inference servers, etc.). For now, try searching by name (e.g., 'qdrant', 'milvus') or description keywords."

---

## 3. Data Contract Rules

### 3.1 General Principles

1. **Never Claim Certainty on Missing Data**
   - ❌ BAD: "This instance has an A100 GPU"
   - ✅ GOOD: "This instance has 1 GPU (model unknown)"

2. **Always Provide Data Quality Context**
   - Include `data_quality` object in every response
   - Show warnings when filtering on sparse fields

3. **Graceful Degradation**
   - When specific filters fail, fall back to broader criteria
   - Always explain the fallback to the user

4. **Explicit About Limitations**
   - Tell users when they need to verify with provider
   - Suggest workarounds when data is missing

### 3.2 Response Quality Tiers

**Tier 1: High Confidence** (>95% data coverage)
- Provider, vCPU, RAM, Price, Regions
- Package name, version, description, install URL
- **NO disclaimers needed**

**Tier 2: Medium Confidence** (80-95% data coverage)
- GPU count, stars/popularity
- **Optional warning**: "Some results may be incomplete"

**Tier 3: Low Confidence** (<80% data coverage)
- GPU model, GPU VRAM, categories, keywords
- **Required warning**: Explain data gap and verification needed

**Tier 4: Not Recommended** (<10% coverage or 0%)
- GPU manufacturer, package license (for filtering)
- **Block feature or redirect**: Suggest alternatives

### 3.3 Error Handling

```typescript
interface RecommenderError {
  code: string;
  message: string;
  suggestion: string;
  data_availability?: string;
}

// Example error responses
const ERRORS = {
  GPU_MODEL_UNAVAILABLE: {
    code: "GPU_MODEL_UNAVAILABLE",
    message: "GPU model filtering is not available with current data.",
    suggestion: "Try filtering by GPU count instead (e.g., 'instances with 2+ GPUs').",
    data_availability: "Only 4.7% of instances have GPU model information."
  },
  
  CATEGORY_SPARSE: {
    code: "CATEGORY_SPARSE",
    message: "Category filtering may miss relevant packages.",
    suggestion: "Use text search or keyword filtering for better coverage.",
    data_availability: "Only 31.9% of packages are categorized."
  },
  
  NO_RESULTS_GPU_MODEL: {
    code: "NO_RESULTS_GPU_MODEL",
    message: "No instances found with specified GPU model.",
    suggestion: "This may be due to missing GPU specs in our data. " +
                "Try searching by provider (e.g., 'AWS GPU instances').",
    data_availability: "GPU model data: 4.7% coverage"
  }
};
```

---

## 4. Implementation Checklist

### 4.1 Before V1 Launch

**Must Have:**
- [x] Document data contracts (this document)
- [ ] Implement Tier 1 filters (provider, vCPU, RAM, price)
- [ ] Implement Tier 2 filters (GPU count, stars)
- [ ] Add data quality indicators to API responses
- [ ] Write user-facing warning messages
- [ ] Test fallback logic for missing data

**Should Have:**
- [ ] Create `gpu_specs` mapping table (30 GPU models)
- [ ] Populate top 100 packages with manual category tags
- [ ] Implement description-based text search
- [ ] Add keyword filtering with warnings

**Nice to Have:**
- [ ] Build component taxonomy system (docs/packages-profile.md proposal)
- [ ] Auto-tag packages based on keywords
- [ ] Create "complete stack" recommendations

### 4.2 Post-V1 Improvements

**Data Quality Enhancements:**
1. Backfill GPU model/VRAM data (Priority: High)
   - Target: 80%+ coverage
   - Method: Provider API calls + manual mapping

2. Categorize uncategorized packages (Priority: High)
   - Target: 80%+ coverage
   - Method: ML-based classification using embeddings

3. Implement component taxonomy (Priority: Medium)
   - Target: Top 500 packages tagged
   - Method: Manual tagging + rule-based auto-tagging

4. Populate GPU manufacturer field (Priority: Low)
   - Target: 100% coverage
   - Method: Derive from GPU model via gpu_specs table

---

## 5. Quick Reference: What Can We Do?

### ✅ RELIABLE (Ship in V1)

**Compute Recommender:**
- Filter by: provider, vCPU, RAM, price, GPU presence, GPU count, region
- Sort by: price, specs
- Compare: pricing across providers

**Marketplace Recommender:**
- Search by: package name, description text
- Filter by: operator flag, official status, CNCF status, popularity
- Install: via Helm (content_url always available)

### ⚠️ PARTIAL (Ship with Warnings)

**Compute Recommender:**
- Filter by GPU count (89.7% coverage) - show warnings

**Marketplace Recommender:**
- Filter by category (31.9% coverage) - use fallback
- Filter by keywords (42% coverage) - supplement with text search

### ❌ NOT RELIABLE (Block or Redirect)

**Compute Recommender:**
- Filter by GPU model (4.7% coverage) - need gpu_specs table
- Filter by GPU VRAM (4.8% coverage) - need gpu_specs table
- Filter by GPU manufacturer (0% coverage) - derive from gpu_specs

**Marketplace Recommender:**
- Browse by AI stack component (0% coverage) - need component_tags system
- Recommend complete stacks (N/A) - need component relationships

---

## 6. SLA: Data Freshness & Availability

**Compute Data (`cloud.instances`):**
- Update frequency: Daily (provider APIs)
- Expected availability: 99.5%
- Stale data threshold: 7 days

**Marketplace Data (`cloud.bitnami_packages`):**
- Update frequency: Daily (ArtifactHub scraping)
- Expected availability: 99.5%
- Stale data threshold: 7 days

**GPU Specs (`cloud.gpu_specs`) - Proposed:**
- Update frequency: Quarterly (GPU releases are infrequent)
- Expected availability: 100%
- Stale data threshold: 90 days

---

## Summary

### What We CAN Do (V1)
- ✅ Recommend compute instances by CPU, RAM, price, GPU count, region
- ✅ Search marketplace packages by name, description, popularity
- ✅ Provide installation instructions (Helm)
- ✅ Compare prices across providers

### What We CANNOT Do (V1)
- ❌ Filter by specific GPU models (A100, H100, etc.)
- ❌ Filter by GPU VRAM requirements
- ❌ Browse packages by AI stack component (vector DB, inference, etc.)
- ❌ Recommend complete AI stacks

### Proposed Fixes
1. **Create `gpu_specs` table** (~50 rows) → Enables GPU model filtering
2. **Implement `component_tags` system** (docs/packages-profile.md) → Enables AI stack component discovery

### Timeline
- **V1 (Week 1-2):** Ship with Tier 1 & 2 features + warnings
- **V1.1 (Week 3-4):** Add gpu_specs table + GPU model filtering
- **V2 (Month 2):** Implement component taxonomy + stack recommendations

---

**End of Data Contract**


