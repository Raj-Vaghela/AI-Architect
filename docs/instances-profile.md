# Instances Table Data Profiling Report

**Generated:** 2025-12-25  
**Table:** `cloud.instances`  
**Total Rows:** 16,695

---

## Executive Summary

The `instances` table contains **16,695 compute instances** across **7 cloud providers**, with comprehensive pricing, CPU, memory, and GPU data. The table is **99.7% complete** for core fields (provider, CPU, RAM, price, regions) but has **significant gaps in GPU metadata** (only 4.7% have GPU model information despite 89.7% having GPU count data).

### Key Findings

✅ **Strengths:**
- 100% provider coverage
- 99.7% CPU/RAM data completeness
- 98.5% pricing data available
- 99.7% region information present

⚠️ **Data Gaps:**
- GPU model: only 4.7% populated (792/16,695 rows)
- GPU VRAM: only 4.8% populated (800/16,695 rows)
- GPU manufacturer: 0% populated (empty field)
- 14,179 instances have GPU count but missing model/VRAM

---

## 1. Column Inventory & Fill Rates

### 1.1 Primary Identification Columns

| Column | Data Type | Filled | Fill Rate | Distinct Values | Notes |
|--------|-----------|--------|-----------|-----------------|-------|
| `id` | uuid | 16,695 | 100% | 16,695 (unique) | Primary key |
| `provider` | varchar | 16,695 | 100% | 7 | AWS, OVH, Vultr, DigitalOcean, Contabo, RunPod, Civo |
| `instance_id` | varchar | 16,695 | 100% | - | Provider's internal ID |
| `name` | varchar | 16,695 | 100% | - | Instance name/slug |
| `instance_type` | varchar | 16,695 | 100% | - | Type classification (e.g., "ec2") |

### 1.2 CPU Columns (vCPU)

| Column | Data Type | Filled | Fill Rate | Notes |
|--------|-----------|--------|-----------|-------|
| `cpu_cores` | integer | 16,646 | **99.71%** | ✅ **TRUSTED** - primary vCPU field |
| `cpu_threads` | integer | 14,921 | 89.38% | Hyperthreading info |
| `cpu_manufacturer` | varchar | 14,871 | 89.08% | Intel/AMD |
| `cpu_model` | varchar | 14,826 | 88.81% | Specific CPU model |
| `cpu_mhz` | integer | - | - | Clock speed |

**Recommendation:** Use `cpu_cores` as the primary vCPU field.

### 1.3 Memory Columns (RAM)

| Column | Data Type | Filled | Fill Rate | Notes |
|--------|-----------|--------|-----------|-------|
| `memory_gb` | numeric | 16,646 | **99.71%** | ✅ **TRUSTED** - primary RAM field |
| `memory_mb` | integer | 16,624 | 99.58% | Alternative in megabytes |

**Recommendation:** Use `memory_gb` as the primary RAM field.

### 1.4 GPU Columns ⚠️ **CRITICAL DATA GAPS**

| Column | Data Type | Filled | Fill Rate | Status |
|--------|-----------|--------|-----------|--------|
| `gpu_count` | integer | 14,970 | **89.67%** | ✅ **TRUSTED** - GPU presence indicator |
| `gpu_model` | varchar | 792 | **4.74%** | ⚠️ **SPARSE** - major gap |
| `gpu_memory_gb` | integer | 800 | **4.79%** | ⚠️ **SPARSE** - major gap (VRAM) |
| `gpu_manufacturer` | varchar | 0 | **0%** | ❌ **EMPTY** - not populated |

**Critical Issue:** Only 791 instances (4.7%) have complete GPU information (model + count + VRAM). 14,179 instances have `gpu_count` set but are missing model and VRAM data.

### 1.5 Pricing Columns

| Column | Data Type | Filled | Fill Rate | Currency | Notes |
|--------|-----------|--------|-----------|----------|-------|
| `price_monthly` | numeric | 16,440 | **98.47%** | Various | ✅ **TRUSTED** - primary pricing field |
| `price_hourly` | numeric | 16,371 | **98.06%** | Various | Alternative hourly rate |
| `price_currency` | varchar | 16,695 | **100%** | - | Currency code (USD, EUR, etc.) |

**Recommendation:** Use `price_monthly` as the primary pricing field. Only 249 instances (1.5%) are missing pricing.

### 1.6 Geographic Columns

| Column | Data Type | Filled | Fill Rate | Notes |
|--------|-----------|--------|-----------|-------|
| `regions` | jsonb | 16,649 | **99.72%** | ✅ **TRUSTED** - JSONB array of region IDs |

**Note:** Region data is stored as a JSONB array. Only 46 instances (0.3%) lack region information. Join with `cloud.regions` table for geographic details (city, country, continent).

---

## 2. Provider Distribution

| Provider | Instance Count | % of Total | GPU Instances | Avg Monthly Price | Price Range |
|----------|---------------|------------|---------------|-------------------|-------------|
| **AWS** | 14,858 | 89.0% | 646 | $838.34 | $0.37 - $52,232.96 |
| **OVH** | 1,353 | 8.1% | 0 | $87,923.47 | $788.40 - $857,604.00 |
| **Vultr** | 203 | 1.2% | 29 | $760.12 | $2.50 - $14,000.00 |
| **DigitalOcean** | 147 | 0.9% | 0 | $1,145.39 | $4.00 - $35,414.40 |
| **Contabo** | 75 | 0.4% | 0 | $57.53 | $4.95 - $156.00 |
| **RunPod** | 38 | 0.2% | 38 | $868.24 | $167.90 - $4,664.70 |
| **Civo** | 21 | 0.1% | 15 | $3,125.38 | $0.00 - $17,461.60 |

**Key Insights:**
- AWS dominates with 89% of instances
- OVH has the highest average prices (likely enterprise/bare metal)
- RunPod and Civo specialize in GPU instances (100% and 71% GPU respectively)
- Contabo offers budget instances (avg $57.53/month)

---

## 3. GPU Analysis

### 3.1 GPU Tier Distribution

| GPU Tier | Instance Count | % of Total | Providers | With Model Info | With VRAM Info | Avg Price/Month |
|----------|---------------|------------|-----------|-----------------|----------------|-----------------|
| **No GPU info** | 1,725 | 10.3% | 5 | 0 | 0 | $69,113.51 |
| **0 GPUs** | 14,242 | 85.3% | 2 | 64 | 73 | $765.38 |
| **1 GPU** | 461 | 2.8% | 4 | 461 | 461 | $725.07 |
| **2-4 GPUs** | 145 | 0.9% | 2 | 145 | 145 | $2,207.65 |
| **5-8 GPUs** | 122 | 0.7% | 2 | 122 | 121 | $8,597.04 |

**Key Finding:** Only 728 instances (4.4%) have GPUs with complete metadata. The "0 GPUs" category includes CPU-only instances that correctly report zero GPU count.

### 3.2 Top GPU Models (by instance count)

| GPU Model | Instances | GPU Count Range | VRAM Range (GB) | Avg Price/Month | Providers |
|-----------|-----------|-----------------|-----------------|-----------------|-----------|
| **L4** | 216 | 0-8 | 3-24 | $951.33 | 2 |
| **T4** | 147 | 1-8 | 16 | $948.49 | 1 |
| **A10G** | 112 | 1-8 | 22 | $1,814.31 | 1 |
| **L40S** | 69 | 1-8 | 40-48 | $3,354.22 | 3 |
| **T4g** | 42 | 1-2 | 16 | $398.17 | 1 |
| **Radeon Pro V520** | 40 | 1-4 | 8 | $464.88 | 1 |
| **V100** | 37 | 1-8 | 16-32 | $5,178.29 | 1 |
| **A100** | 24 | 1-8 | 40-80 | $6,612.60 | 2 |
| **H100** | 23 | 0-8 | 80 | $13,257.45 | 2 |
| **H200** | 10 | 8 | 141 | $14,624.45 | 1 |
| **B200** | 6 | 1-8 | 179-185 | $10,250.15 | 3 |

**Notable Models:**
- **NVIDIA L4:** Most common GPU (216 instances), mid-range AI inference
- **NVIDIA A100/H100/H200:** High-end training GPUs, limited availability
- **AMD Radeon Pro V520:** Only AMD GPU in dataset (40 instances)
- **Consumer GPUs:** RTX 4090, 5090, 3090 Ti (1 instance each, likely RunPod)

### 3.3 GPU vs Non-GPU Pricing Comparison

| Instance Type | Count | Avg Monthly | Median Monthly | Min | Max | Avg vCPU | Avg RAM (GB) |
|---------------|-------|-------------|----------------|-----|-----|----------|--------------|
| **GPU Instance** | 721 | $2,353.19 | $817.97 | $0.00 | $52,232.96 | 27.78 | 309.44 |
| **Non-GPU Instance** | 15,719 | $8,265.89 | $425.88 | $0.37 | $857,604.00 | 26.33 | 229.37 |

**Insight:** Non-GPU instances have higher average prices due to OVH's expensive bare-metal servers pulling the average up. However, GPU instances have a higher median price ($817 vs $425), indicating they're generally more expensive.

---

## 4. CPU & Memory Distribution

### 4.1 Top vCPU/RAM Configurations

| vCPU Tier | RAM Tier | Instance Count | Avg Price |
|-----------|----------|----------------|-----------|
| **33+ vCPU** | **129+ GB** | 3,881 | $19,422.22 |
| **1-2 vCPU** | **≤8 GB** | 2,277 | $397.66 |
| **17-32 vCPU** | **129+ GB** | 1,692 | $5,906.34 |
| **1-2 vCPU** | **9-16 GB** | 1,049 | $554.70 |
| **17-32 vCPU** | **65-128 GB** | 725 | $21,050.61 |
| **3-4 vCPU** | **17-32 GB** | 645 | $656.35 |
| **5-8 vCPU** | **33-64 GB** | 624 | $4,017.15 |
| **9-16 vCPU** | **65-128 GB** | 580 | $6,416.42 |

**Insights:**
- Most common: High-end (33+ vCPU, 129+ GB RAM) and entry-level (1-2 vCPU, ≤8 GB)
- Wide range of configurations available
- Price scales roughly with resources

---

## 5. Region Distribution (Top 25)

| Region ID | Provider | City | Country | Continent | Instance Count |
|-----------|----------|------|---------|-----------|----------------|
| BHS5 | OVH | Beauharnois | Canada | North America | 182 |
| GRA7 | OVH | Gravelines | France | Europe | 179 |
| UK1 | OVH | London | United Kingdom | Europe | 173 |
| DE1 | OVH | Frankfurt | Germany | Europe | 173 |
| WAW1 | OVH | Warsaw | Poland | Europe | 173 |
| lon1 | Civo, DigitalOcean | London | United Kingdom | Europe | 154 each |
| nyc1 | Civo, DigitalOcean | New York | United States | North America | 143 each |
| fra1 | Civo, DigitalOcean | Frankfurt | Germany | Europe | 143 each |
| tor1 | DigitalOcean | Toronto | Canada | North America | 141 |
| ams3 | DigitalOcean | Amsterdam | Netherlands | Europe | 138 |

**Geographic Coverage:**
- **234 unique regions** across all providers
- Major coverage: North America, Europe, Asia
- Key hubs: London, New York, Frankfurt, Singapore, Tokyo

---

## 6. Data Quality Assessment

### 6.1 Completeness Matrix

| Data Category | Complete Rows | % Complete | Notes |
|---------------|---------------|------------|-------|
| **Complete Core Specs** (CPU + RAM + Price) | 16,425 | **98.4%** | ✅ Excellent |
| **Has Pricing** (monthly OR hourly) | 16,446 | **98.5%** | ✅ Excellent |
| **Has Region Info** | 16,649 | **99.7%** | ✅ Excellent |
| **Complete GPU Info** (model + count + vram) | 791 | **4.7%** | ❌ Critical gap |
| **Partial GPU Info** (count only) | 14,179 | 84.9% | ⚠️ Count present, details missing |
| **No GPU Info** | 1,725 | 10.3% | ℹ️ Unclear if 0 GPU or missing data |
| **Missing Pricing** | 249 | 1.5% | Minor issue |
| **Missing Region Info** | 46 | 0.3% | Negligible |

### 6.2 Duplicate Detection

**Found:** 20 sets of duplicates in AWS data

**Example:** `aws.i3en.metal` has **29 duplicate entries** with 28 price variations across different regions.

**Analysis:** These are NOT true duplicates—they represent the same instance type available in multiple regions with region-specific pricing. The duplication is **intentional and correct** for per-region pricing.

**Recommendation:** Filter by specific region when querying to avoid duplicate results.

---

## 7. Trusted Fields ✅

These fields are **production-ready** and can be safely used for filtering, sorting, and calculations:

| Field | Completeness | Data Type | Use Case |
|-------|--------------|-----------|----------|
| **`provider`** | 100% | varchar | Filter by cloud provider |
| **`cpu_cores`** | 99.7% | integer | Filter by vCPU count |
| **`memory_gb`** | 99.7% | numeric | Filter by RAM |
| **`price_monthly`** | 98.5% | numeric | Filter/sort by price |
| **`price_hourly`** | 98.1% | numeric | Alternative pricing |
| **`gpu_count`** | 89.7% | integer | Filter by GPU presence (0, 1, 2, etc.) |
| **`regions`** | 99.7% | jsonb | Filter by geographic availability |
| **`name`** | 100% | varchar | Instance type identifier |
| **`instance_id`** | 100% | varchar | Provider's instance ID |

**Safe Query Pattern:**
```sql
SELECT * FROM cloud.instances
WHERE 
    provider = 'aws'
    AND cpu_cores >= 8
    AND memory_gb >= 16
    AND gpu_count >= 1
    AND price_monthly <= 1000
    AND regions @> '["us-east-1"]'::jsonb
ORDER BY price_monthly ASC;
```

---

## 8. Missing/Sparse Fields ⚠️

### 8.1 Critical Gaps (Not Recommended for Production Use)

| Field | Completeness | Issue | Impact |
|-------|--------------|-------|--------|
| **`gpu_model`** | 4.7% | 95% missing | ❌ Cannot filter by GPU type reliably |
| **`gpu_memory_gb`** | 4.8% | 95% missing | ❌ Cannot filter by VRAM |
| **`gpu_manufacturer`** | 0% | 100% missing | ❌ Field not populated |

### 8.2 Minor Gaps (Use with Caution)

| Field | Completeness | Issue |
|-------|--------------|-------|
| `cpu_threads` | 89.4% | 10% missing |
| `cpu_manufacturer` | 89.1% | 11% missing |
| `cpu_model` | 88.8% | 11% missing |

### 8.3 Implications for AI Architect

**Problem:** Users requesting specific GPU models (e.g., "A100 80GB") cannot be reliably served because:
1. Only 792/16,695 instances have GPU model information
2. Of the 728 GPU instances, only 791 have complete specs
3. GPU manufacturer field is completely empty

**Workaround:**
- Use `gpu_count` to filter for GPU presence
- Provide pricing estimates based on GPU count tiers
- Warn users that specific GPU model filtering is limited
- Suggest broader queries: "1 GPU instance" instead of "A100"

---

## 9. Recommended Minimal Filters

Based on field completeness and user needs, these filters are **safe and recommended** for the AI Architect:

### 9.1 Core Filters (Highly Reliable)

| Filter | Column | Operators | Notes |
|--------|--------|-----------|-------|
| **Provider** | `provider` | `=`, `IN` | 100% coverage, 7 values |
| **vCPU** | `cpu_cores` | `>=`, `<=`, `BETWEEN` | 99.7% coverage |
| **RAM (GB)** | `memory_gb` | `>=`, `<=`, `BETWEEN` | 99.7% coverage |
| **Max Price** | `price_monthly` | `<=`, `BETWEEN` | 98.5% coverage |
| **GPU Presence** | `gpu_count` | `>= 1`, `= 0`, `>= 2` | 89.7% coverage |

### 9.2 Secondary Filters (Use with Caution)

| Filter | Column | Completeness | Notes |
|--------|--------|--------------|-------|
| **Region** | `regions` (JSONB) | 99.7% | Requires JSONB operators (`@>`) |
| **GPU Count** | `gpu_count` | 89.7% | Specific count (1, 2, 4, 8) |

### 9.3 Filters to AVOID (Unreliable)

| Filter | Column | Issue |
|--------|--------|-------|
| ❌ GPU Model | `gpu_model` | Only 4.7% populated |
| ❌ GPU VRAM | `gpu_memory_gb` | Only 4.8% populated |
| ❌ GPU Manufacturer | `gpu_manufacturer` | 0% populated |

### 9.4 Example Query Template

```sql
-- Safe, production-ready query
SELECT 
    provider,
    name,
    cpu_cores as vcpu,
    memory_gb as ram_gb,
    gpu_count,
    gpu_model,  -- Include but expect NULLs
    gpu_memory_gb as vram_gb,  -- Include but expect NULLs
    price_monthly,
    price_hourly,
    regions
FROM cloud.instances
WHERE 
    -- TRUSTED FILTERS (high completeness)
    provider = ANY(ARRAY['aws', 'vultr', 'runpod'])  -- Filter by providers
    AND cpu_cores >= 4                                -- Min 4 vCPUs
    AND memory_gb >= 16                               -- Min 16 GB RAM
    AND gpu_count >= 1                                -- At least 1 GPU
    AND price_monthly <= 2000                         -- Max $2000/month
    AND price_monthly IS NOT NULL                     -- Exclude missing prices
    
    -- OPTIONAL: Region filter (JSONB contains operator)
    AND regions @> '["us-east-1"]'::jsonb            -- Available in us-east-1
    
ORDER BY price_monthly ASC
LIMIT 10;
```

---

## 10. Recommendations for AI Architect Implementation

### 10.1 Tier 1 Filters (Implement First)

✅ **Safe to implement immediately:**
1. **Provider selection** (dropdown/multi-select)
2. **Min/Max vCPU** (slider or input)
3. **Min/Max RAM** (slider or input)
4. **Max monthly price** (slider or input)
5. **GPU presence** (checkbox: "Has GPU" / "GPU count >= 1")

### 10.2 Tier 2 Filters (Implement with Warnings)

⚠️ **Implement with user warnings:**
1. **GPU count** (1, 2, 4, 8) - warn that 10% of data missing GPU info
2. **Region filter** - works well (99.7% coverage)

### 10.3 NOT Recommended (Wait for Data Improvement)

❌ **Do NOT implement until data improves:**
1. GPU model filter (e.g., "A100", "H100") - only 4.7% coverage
2. VRAM filter (e.g., "80GB VRAM") - only 4.8% coverage
3. GPU manufacturer filter - 0% coverage

### 10.4 User Experience Recommendations

1. **Set Expectations:** Display warning when GPU count filter is used:
   > "⚠️ Note: Only 728 instances (4.4%) have detailed GPU specifications (model/VRAM). Results are based on GPU count only."

2. **Fallback Strategy:** When users ask for specific GPU models:
   - Try to match by name first
   - If no results, fall back to GPU count approximation
   - Inform user: "Specific GPU model data is limited. Showing instances with 1+ GPU."

3. **Data Quality Badge:** Display completeness percentage for each filter:
   - Provider: ✅ 100%
   - CPU: ✅ 99.7%
   - RAM: ✅ 99.7%
   - Price: ✅ 98.5%
   - GPU Count: ⚠️ 89.7%
   - GPU Model: ❌ 4.7%

4. **Graceful Degradation:** When GPU model is unknown but GPU count is known:
   ```
   Provider: AWS
   vCPU: 32 cores
   RAM: 256 GB
   GPU: 1 GPU (model unknown)
   Price: $1,800/month
   ```

---

## 11. Data Quality Action Items

### For Data Engineering Team:

1. **Priority 1 (Critical):** Populate `gpu_model` for the 14,179 instances that have `gpu_count` but missing model info
2. **Priority 2 (High):** Populate `gpu_memory_gb` for those same instances
3. **Priority 3 (Medium):** Populate `gpu_manufacturer` field (currently 0%)
4. **Priority 4 (Low):** Investigate 249 instances missing pricing data
5. **Priority 5 (Low):** Standardize GPU naming (e.g., "NVIDIA_A100" vs "A100")

### Data Sources to Consider:

- AWS EC2 API: Provides GPU model info for GPU instances
- Provider documentation: Map instance types to GPU specs
- Cloud pricing APIs: Most provide GPU metadata
- Manual mapping: Create lookup table for common GPU instance types

---

## 12. Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Instances** | 16,695 |
| **Unique Instance IDs** | 16,695 |
| **Cloud Providers** | 7 |
| **Geographic Regions** | 234 |
| **GPU Models** | 30+ (but only in 4.7% of data) |
| **Price Range** | $0.37 - $857,604/month |
| **Median Price** | $427.41/month |
| **GPU Instances** | 728 (4.4%) |
| **Data Completeness (Core Fields)** | 98.4% |
| **Data Completeness (GPU Details)** | 4.7% |

---

## Appendix: Column Reference

### Complete Column List

1. `id` - uuid, PK
2. `provider` - varchar
3. `instance_id` - varchar
4. `name` - varchar
5. `instance_type` - varchar
6. `cpu_cores` - integer ✅
7. `cpu_threads` - integer
8. `cpu_manufacturer` - varchar
9. `cpu_model` - varchar
10. `cpu_mhz` - integer
11. `memory_mb` - integer
12. `memory_gb` - numeric ✅
13. `disk_gb` - integer
14. `disk_type` - varchar
15. `disk_count` - integer
16. `bandwidth_mbps` - integer
17. `transfer_tb` - numeric
18. `networking_throughput` - integer
19. `inbound_bandwidth` - integer
20. `outbound_bandwidth` - integer
21. `price_monthly` - numeric ✅
22. `price_hourly` - numeric ✅
23. `price_currency` - varchar ✅
24. `gpu_count` - integer ✅
25. `gpu_model` - varchar ⚠️
26. `gpu_memory_gb` - integer ⚠️
27. `gpu_manufacturer` - varchar ❌
28. `regions` - jsonb ✅
29. `available` - boolean
30. `stock_status` - varchar
31. `description` - text
32. `capabilities` - jsonb
33. `os_type` - varchar
34. `quota` - integer
35. `created_at` - timestamp
36. `updated_at` - timestamp
37. `data_source_timestamp` - timestamp
38. `raw_data` - jsonb
39. `embedding` - vector

**Legend:**
- ✅ Trusted (>95% complete)
- ⚠️ Sparse (<10% complete)
- ❌ Empty (0% complete)

---

**End of Data Profiling Report**


