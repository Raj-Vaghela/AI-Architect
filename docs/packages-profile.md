# Bitnami Packages Data Profiling Report

**Generated:** 2025-12-25  
**Table:** `cloud.bitnami_packages`  
**Total Packages:** 13,435

---

## Executive Summary

The `bitnami_packages` table contains **13,435 Kubernetes Helm charts and operators** from the Bitnami/ArtifactHub marketplace. While the table has excellent metadata coverage for descriptions (99.5%), versions (100%), and install identifiers (100%), there is a **critical gap in categorization**: only **31.93%** of packages are categorized, leaving **9,145 packages (68%)** without category assignments.

### Key Findings

✅ **Strengths:**
- 100% name and version coverage
- 99.5% description completeness
- 100% content URL (Helm install identifier)
- 42% keyword coverage (5,655 packages)
- Rich metadata: stars, licenses, security reports

⚠️ **Critical Gaps:**
- **Category coverage: only 31.93%** (4,290/13,435 packages)
- **68% of packages uncategorized** (9,145 packages)
- Existing 8 categories insufficient for AI/ML use cases
- No dedicated tags for AI stack components (vector DB, inference, pipelines, etc.)

---

## 1. Metadata Inventory & Fill Rates

### 1.1 Core Identification Fields

| Column | Data Type | Filled | Fill Rate | Distinct Values | Notes |
|--------|-----------|--------|-----------|-----------------|-------|
| `package_id` | uuid | 13,435 | 100% | 13,435 (unique) | Primary key |
| `name` | text | 13,435 | 100% | 9,244 distinct | Package name |
| `normalized_name` | text | 13,435 | 100% | - | URL-safe name |

**Note:** 9,244 distinct names across 13,435 packages indicates multiple versions of the same package.

### 1.2 Categorization & Tags ⚠️ **CRITICAL GAP**

| Column | Data Type | Filled | Fill Rate | Distinct Values | Notes |
|--------|-----------|--------|-----------|-----------------|-------|
| `category` | integer | 4,290 | **31.93%** | 8 categories | ❌ **68% uncategorized** |
| `keywords` (JSONB) | jsonb | 13,435 | 100% | - | Array field |
| `keywords` (populated) | jsonb | 5,655 | **42.09%** | - | ⚠️ 58% have empty arrays |
| `is_operator` | boolean | 13,435 | 100% | 685 operators | Operator flag (5.1%) |
| `official` | boolean | 360 | - | 360 official | Official packages |
| `cncf` | boolean | 45 | - | 45 CNCF | CNCF projects |

**Critical Issue:** Only 4,290 packages (32%) have categories assigned. The remaining 9,145 packages (68%) lack category information, making discovery and filtering extremely difficult.

### 1.3 Description & Documentation

| Column | Data Type | Filled | Fill Rate | Notes |
|--------|-----------|--------|-----------|-------|
| `description` | text | 13,364 | **99.47%** | ✅ **EXCELLENT** - primary search field |
| `readme` | text | 9,128 | **67.94%** | Full documentation |
| `home_url` | text | 7,169 | **53.37%** | Project homepage |

**Recommendation:** Use `description` for text search and filtering (99.5% complete).

### 1.4 Version Information

| Column | Data Type | Filled | Fill Rate | Notes |
|--------|-----------|--------|-----------|-------|
| `version` | text | 13,435 | **100%** | ✅ Helm chart version |
| `app_version` | text | 13,405 | **99.78%** | ✅ Application version |
| `digest` | text | 12,827 | **95.47%** | Package digest/hash |
| `deprecated` | boolean | 0 | 0% | No deprecated packages |
| `prerelease` | boolean | 124 | 0.92% | Pre-release versions |

**Stats:**
- **2,487 distinct Helm chart versions**
- **3,949 distinct application versions**
- **2,341 packages** where chart version matches app version
- **0 deprecated packages** in current dataset
- **124 pre-release packages** (0.92%)

### 1.5 Helm/Install Identifiers ✅ **EXCELLENT**

| Column | Data Type | Filled | Fill Rate | Notes |
|--------|-----------|--------|-----------|-------|
| `content_url` | text | 13,435 | **100%** | ✅ Helm chart download URL |
| `digest` | text | 12,827 | **95.47%** | Chart digest |
| `repository_name` | text | - | - | Source repository |
| `repository_url` | text | - | - | Repository URL |

**Example Content URLs:**
- OCI: `oci://registry-1.docker.io/bitnamicharts/redis:22.0.7`
- GitHub: `https://github.com/prometheus-community/helm-charts/releases/download/...`
- Chart repo: `https://charts.jetstack.io/charts/cert-manager-v1.18.2.tgz`

### 1.6 Popularity & Quality Metrics

| Column | Data Type | Filled | Fill Rate | Notes |
|--------|-----------|--------|-----------|-------|
| `stars` | integer | 12,379 | **92.14%** | GitHub stars / popularity |
| `license` | text | 1,693 | **12.60%** | ⚠️ Sparse license info |
| `production_organizations_count` | integer | - | - | Production usage count |
| `stats_subscriptions` | integer | - | - | Subscription count |

---

## 2. Existing Category Distribution

### 2.1 The 8 Official Categories

| Category ID | Category Name | Official Count | Actual Count | % of Total | % Coverage |
|-------------|---------------|----------------|--------------|------------|------------|
| **4** | **Monitoring and logging** | 1,243 | 1,060 | 7.9% | 24.7% |
| **5** | **Networking** | 1,175 | 713 | 5.3% | 16.6% |
| **6** | **Security** | 1,016 | 688 | 5.1% | 16.0% |
| **3** | **Integration and delivery** | 1,164 | 610 | 4.5% | 14.2% |
| **2** | **Database** | 606 | 527 | 3.9% | 12.3% |
| **7** | **Storage** | 337 | 291 | 2.2% | 6.8% |
| **8** | **Streaming and messaging** | 271 | 226 | 1.7% | 5.3% |
| **1** | **AI / Machine learning** | 228 | 175 | 1.3% | 4.1% |
| **(null)** | **Uncategorized** | - | **9,145** | **68.1%** | - |

**Key Insights:**
- **Monitoring & Logging** is the largest category (24.7% of categorized packages)
- **AI/ML category exists but is smallest** (only 4.1% of categorized packages)
- **68% of packages have no category** - massive gap
- Discrepancy between "official count" and "actual count" suggests stale data or misalignment

### 2.2 Packages Without Categories

**9,145 packages (68%)** have no category assigned, but:
- **9,083 (99.3%)** have descriptions
- **1,443 (15.8%)** have keywords

**Implication:** These packages can still be searched via description and keywords, but cannot be filtered by category.

---

## 3. Keyword/Tag Analysis

### 3.1 Top 50 Keywords

| Rank | Keyword | Package Count | % of Total |
|------|---------|---------------|------------|
| 1 | **kubernetes** | 576 | 4.29% |
| 2 | **database** | 395 | 2.94% |
| 3 | **monitoring** | 374 | 2.78% |
| 4 | **prometheus** | 285 | 2.12% |
| 5 | **cluster** | 216 | 1.61% |
| 6 | **operator** | 201 | 1.50% |
| 7 | **security** | 198 | 1.47% |
| 8 | **helm** | 161 | 1.20% |
| 9 | **storage** | 142 | 1.06% |
| 10 | **metrics** | 126 | 0.94% |
| 11 | **api** | 120 | 0.89% |
| 12 | **sql** | 119 | 0.89% |
| 13 | **web** | 112 | 0.83% |
| 14 | **infrastructure** | 110 | 0.82% |
| 15 | **http** | 108 | 0.80% |
| 16 | **ingress** | 106 | 0.79% |
| 17 | **exporter** | 104 | 0.77% |
| 18 | **redis** | 101 | 0.75% |
| 19 | **postgresql** | 100 | 0.74% |
| 20 | **postgres** | 99 | 0.74% |

**Full Top 50 (21-50):**
21. amd64 (97) | 22. blockchain (92) | 23. nginx (84) | 24. network (80) | 25. startx (77) | 26. application (77) | 27. observability (77) | 28. mysql (75) | 29. replication (74) | 30. aws (74) | 31. istio (73) | 32. Commercial (72) | 33. logging (71) | 34. docker (69) | 35. alerting (66) | 36. csi (65) | 37. nosql (64) | 38. metric (63) | 39. component (59) | 40. nlx (58) | 41. commonground (58) | 42. RHOCP (58) | 43. haven (58) | 44. mongodb (57) | 45. php (57) | 46. kafka (56) | 47. elasticsearch (56) | 48. cluster-chart (55) | 49. keyvalue (54) | 50. cassandra (53)

### 3.2 AI/ML Related Keywords

**Keywords found in AI/ML context:**
- **ai** - present in various packages (Ollama, MLflow, etc.)
- **ml** - machine learning packages
- **inference** - AI inference tools
- **vector** - vector databases (Qdrant, Milvus, vector observability tool)
- **llm** - large language models
- **llama**, **mistral** - specific LLM models
- **machine-learning**, **model-management** - MLOps tools

**However:** These keywords are sparse and inconsistent. No standardized AI stack taxonomy exists.

---

## 4. Top Packages by Popularity (Stars)

### 4.1 Top 20 Most Popular Packages

| Rank | Package | Category | Stars | Type | Description (truncated) |
|------|---------|----------|-------|------|------------------------|
| 1 | **kube-prometheus-stack** | Monitoring (4) | 1,109 | Operator | End-to-end Kubernetes monitoring with Prometheus |
| 2 | **cert-manager** | Security (6) | 878 | Chart | Certificate management for Kubernetes |
| 3 | **ingress-nginx** | Networking (5) | 803 | Chart | NGINX ingress controller |
| 4 | **argo-cd** | CI/CD (3) | 742 | Chart | GitOps continuous delivery |
| 5 | **grafana** | Monitoring (4) | 515 | Chart | Metrics visualization |
| 6 | **prometheus** | Monitoring (4) | 505 | Chart | Monitoring & time series DB |
| 7 | **redis** | Database (2) | 494 | Chart | Key-value store |
| 8 | **postgresql** | Database (2) | 401 | Chart | Relational database |
| 9 | **traefik** | Networking (5) | 354 | Chart | Ingress controller |
| 10 | **kubernetes-dashboard** | *Uncategorized* | 350 | Chart | Web UI for Kubernetes |
| 11 | **loki** | *Uncategorized* | 307 | Chart | Log aggregation system |
| 12 | **metrics-server** | Monitoring (4) | 269 | Chart | Container resource metrics |
| 13 | **vault** | Security (6) | 266 | Chart | Secrets management |
| 14 | **keycloak** | Security (6) | 261 | Chart | Identity & access management |
| 15 | **gitlab** | CI/CD (3) | 259 | Chart | DevSecOps platform |
| 16 | **harbor** | Security (6) | 233 | Chart | Container registry |
| 17 | **jenkins** | CI/CD (3) | 232 | Chart | CI/CD automation server |
| 18 | **rabbitmq** | Messaging (8) | 207 | Chart | Message broker |
| 19 | **external-dns** | Networking (5) | 200 | Chart | DNS management |
| 20 | **kafka** | Messaging (8) | 197 | Chart | Distributed streaming |

**Notable:** #10 (kubernetes-dashboard) and #11 (loki) are highly popular but **uncategorized**.

### 4.2 AI/ML Packages Found

| Package | Category | Stars | Description | Keywords |
|---------|----------|-------|-------------|----------|
| **spark** | AI/ML (1) | 47 | Large-scale data processing, ML | apache, spark |
| **ollama** | AI/ML (1) | 45 | Run large language models locally | ai, llm, llama, mistral |
| **airflow** (3 versions) | CI/CD (3) | 172, 59, 30 | Workflow orchestration (used for ML pipelines) | apache, airflow, workflow, dag |
| **mlflow** | AI/ML (1) | 28 | ML lifecycle management | docker, machine-learning, ai, ml, model-management |
| **qdrant** | Database (2) | 23 | Vector database for AI | vector database |
| **milvus** | Database (2) | 20 | Vector database for AI/search | milvus, elastic, vector, search |
| **vector** | Monitoring (4) | 26 | Observability pipelines (not vector DB) | vector, events, logs, metrics |

**Finding:** AI/ML packages exist but are:
1. Scattered across categories (AI/ML, Database, CI/CD)
2. Often uncategorized
3. Lack consistent tagging for AI stack components

---

## 5. Data/Storage Related Packages (Top 25)

| Package | Category | Stars | Description (truncated) |
|---------|----------|-------|------------------------|
| **redis** | Database (2) | 494 | Key-value store |
| **postgresql** | Database (2) | 401 | Relational database |
| **kafka** | Messaging (8) | 197 | Distributed streaming |
| **mysql** | Database (2) | 196 | Relational database |
| **mongodb** | Database (2) | 190 | NoSQL document database |
| **elasticsearch** | *Uncategorized* | 185 | Search & analytics engine |
| **minio** | Storage (7) | 164 | S3-compatible object storage |
| **redis-cluster** | Database (2) | 68 | Distributed Redis |
| **postgresql-ha** | Database (2) | 63 | HA PostgreSQL with replication |
| **clickhouse** | Database (2) | 30 | OLAP column-oriented database |
| **cassandra** | Database (2) | 25 | Distributed NoSQL database |
| **qdrant** | Database (2) | 23 | **Vector database** for AI |
| **milvus** | Database (2) | 20 | **Vector database** for AI/search |

**Key Finding:** Traditional databases (Redis, PostgreSQL, MySQL, MongoDB) are well-represented and categorized. **Vector databases** (Qdrant, Milvus) exist but have low visibility (20-23 stars vs 400+ for PostgreSQL).

---

## 6. Operator Packages

### 6.1 Operator Statistics

- **Total Operators:** 685 (5.1% of all packages)
- **Operator Capabilities:** 5 levels (basic install → auto pilot)

### 6.2 Operator Capability Levels

| Capability | Operator Count | Description |
|------------|----------------|-------------|
| **Basic Install** | 235 | Can be installed via operator |
| **Seamless Upgrades** | 146 | Supports automated upgrades |
| **Full Lifecycle** | 88 | Complete lifecycle management |
| **Deep Insights** | 50 | Provides observability/metrics |
| **Auto Pilot** | 16 | Self-healing, auto-scaling |

**Note:** Most operators (235) provide only "basic install" capability. Only 16 operators achieve "auto pilot" level (full automation).

---

## 7. Proposed AI Stack Taxonomy

### 7.1 Problem Statement

The current category system has **two critical issues** for AI/ML use cases:

1. **Only 32% of packages are categorized** (68% uncategorized)
2. **Existing categories are too generic** for AI stacks:
   - "AI / Machine learning" (category 1) only has 175 packages (1.3% of total)
   - No granular categories for: vector DBs, inference servers, training platforms, feature stores, model registries, MLOps tools, data pipelines, etc.

### 7.2 Proposed Component Taxonomy for AI Stacks

Based on modern AI/ML infrastructure needs, we propose **13 component categories**:

| Category ID | Component Category | Description | Example Packages |
|-------------|-------------------|-------------|------------------|
| **ai-001** | **Vector Databases** | Vector similarity search, embeddings storage | Qdrant, Milvus, Weaviate, Pinecone |
| **ai-002** | **Model Training** | Training platforms, distributed training | Kubeflow, MLflow Training, Ray |
| **ai-003** | **Model Inference** | Inference servers, model serving | Ollama, KServe, Seldon Core, TorchServe, Triton |
| **ai-004** | **Model Registry** | Model versioning, storage, metadata | MLflow, DVC, ModelDB |
| **ai-005** | **Feature Store** | Feature management, serving | Feast, Tecton, Hopsworks |
| **ai-006** | **Data Pipelines** | ETL, data orchestration, workflow | Airflow, Prefect, Dagster, Argo Workflows |
| **ai-007** | **Compute/Training** | GPU/TPU orchestration, distributed compute | Spark, Dask, Ray, Horovod |
| **ai-008** | **MLOps Platform** | End-to-end ML lifecycle management | Kubeflow, MLflow, Weights & Biases |
| **ai-009** | **LLM Tools** | LLM serving, fine-tuning, evaluation | Ollama, vLLM, Text Generation Inference |
| **ai-010** | **API Gateway** | API management, routing, rate limiting | Kong, Traefik, Nginx, Envoy, Tyk |
| **ai-011** | **Observability** | Monitoring, logging, tracing for ML | Prometheus, Grafana, Loki, Tempo, Jaeger |
| **ai-012** | **Secrets Management** | API keys, credentials, config | Vault, Sealed Secrets, External Secrets |
| **ai-013** | **Storage/Caching** | Object storage, caching, data lakes | MinIO, Redis, S3, GCS, Ceph |

### 7.3 Mapping Examples

**Current State:**
```
Package: "qdrant"
Category: 2 (Database)
Keywords: ["vector database"]
```

**Proposed State:**
```
Package: "qdrant"
Category: 2 (Database) -- KEEP existing
Component Tags: ["ai-001"] (Vector Databases) -- ADD new
```

**Current State:**
```
Package: "ollama"
Category: 1 (AI / Machine learning)
Keywords: ["ai", "llm", "llama", "mistral"]
```

**Proposed State:**
```
Package: "ollama"
Category: 1 (AI / Machine learning) -- KEEP existing
Component Tags: ["ai-003", "ai-009"] (Inference, LLM Tools) -- ADD new
```

**Current State:**
```
Package: "airflow"
Category: 3 (Integration and delivery)
Keywords: ["apache", "airflow", "workflow", "dag"]
```

**Proposed State:**
```
Package: "airflow"
Category: 3 (Integration and delivery) -- KEEP existing
Component Tags: ["ai-006"] (Data Pipelines) -- ADD new
```

---

## 8. Proposed Database Schema: `component_tags` Mapping Table

### 8.1 Design Rationale

**Why not modify existing `category` field?**
- Don't break existing queries/filters
- Existing categories are still useful for general browsing
- Packages can belong to multiple component categories (e.g., MLflow is both "Model Registry" AND "MLOps Platform")

**Why a separate mapping table?**
- Enables **many-to-many relationship** (one package → multiple component tags)
- Non-destructive: doesn't modify existing schema
- Easy to extend/modify without data migration
- Can be populated incrementally

### 8.2 Proposed Schema

```sql
-- DO NOT CREATE YET - PROPOSAL ONLY

-- Table: cloud.component_taxonomy
-- Defines the taxonomy of AI stack component categories
CREATE TABLE IF NOT EXISTS cloud.component_taxonomy (
    component_id VARCHAR(10) PRIMARY KEY,  -- e.g., "ai-001"
    component_name TEXT NOT NULL,          -- e.g., "Vector Databases"
    component_description TEXT,            -- Description of the category
    parent_category TEXT,                  -- Optional parent grouping (e.g., "ai-storage", "ai-compute")
    icon_name VARCHAR(50),                 -- Optional UI icon reference
    display_order INTEGER,                 -- Display order in UI
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: cloud.package_component_tags
-- Maps packages to component categories (many-to-many)
CREATE TABLE IF NOT EXISTS cloud.package_component_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_id UUID NOT NULL REFERENCES cloud.bitnami_packages(package_id) ON DELETE CASCADE,
    component_id VARCHAR(10) NOT NULL REFERENCES cloud.component_taxonomy(component_id) ON DELETE CASCADE,
    confidence_score NUMERIC(3, 2),        -- Optional: 0.00-1.00 (for auto-tagging confidence)
    source VARCHAR(20),                    -- 'manual', 'auto-keyword', 'auto-description', 'ml-model'
    tagged_by VARCHAR(100),                -- User ID or system process
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(package_id, component_id)       -- Prevent duplicate tags
);

-- Indexes for fast lookups
CREATE INDEX idx_package_component_package ON cloud.package_component_tags(package_id);
CREATE INDEX idx_package_component_component ON cloud.package_component_tags(component_id);
CREATE INDEX idx_package_component_source ON cloud.package_component_tags(source);
```

### 8.3 Sample Data

```sql
-- Component Taxonomy (Sample)
INSERT INTO cloud.component_taxonomy (component_id, component_name, component_description, parent_category, display_order) VALUES
('ai-001', 'Vector Databases', 'Vector similarity search and embeddings storage', 'ai-storage', 1),
('ai-002', 'Model Training', 'Training platforms and distributed training frameworks', 'ai-compute', 2),
('ai-003', 'Model Inference', 'Inference servers and model serving platforms', 'ai-compute', 3),
('ai-004', 'Model Registry', 'Model versioning, storage, and metadata management', 'ai-storage', 4),
('ai-005', 'Feature Store', 'Feature engineering, management, and serving', 'ai-storage', 5),
('ai-006', 'Data Pipelines', 'ETL, data orchestration, and workflow management', 'ai-pipelines', 6),
('ai-007', 'Compute/Training', 'GPU/TPU orchestration and distributed compute', 'ai-compute', 7),
('ai-008', 'MLOps Platform', 'End-to-end ML lifecycle management', 'ai-platforms', 8),
('ai-009', 'LLM Tools', 'LLM serving, fine-tuning, and evaluation tools', 'ai-llm', 9),
('ai-010', 'API Gateway', 'API management, routing, and rate limiting', 'ai-gateway', 10),
('ai-011', 'Observability', 'Monitoring, logging, and tracing for ML systems', 'ai-ops', 11),
('ai-012', 'Secrets Management', 'API keys, credentials, and configuration management', 'ai-security', 12),
('ai-013', 'Storage/Caching', 'Object storage, caching, and data lakes', 'ai-storage', 13);

-- Package Component Tags (Sample)
-- Qdrant: Vector Database
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-001', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'qdrant' LIMIT 1;

-- Milvus: Vector Database
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-001', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'milvus' LIMIT 1;

-- Ollama: Inference + LLM Tools
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-003', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'ollama' LIMIT 1;

INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-009', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'ollama' LIMIT 1;

-- MLflow: Model Registry + MLOps Platform
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-004', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'mlflow' LIMIT 1;

INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-008', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'mlflow' LIMIT 1;

-- Airflow: Data Pipelines
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-006', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'airflow' LIMIT 3;

-- Redis: Storage/Caching
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-013', 0.95, 'auto-keyword', 'system'
FROM cloud.bitnami_packages WHERE name = 'redis' LIMIT 1;

-- MinIO: Storage/Caching
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-013', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'minio' LIMIT 1;

-- Prometheus: Observability
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-011', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'prometheus' LIMIT 1;

-- Grafana: Observability
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-011', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'grafana' LIMIT 1;

-- Vault: Secrets Management
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-012', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'vault' LIMIT 1;

-- Traefik: API Gateway
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-010', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'traefik' LIMIT 1;

-- Kong: API Gateway
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-010', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'kong' LIMIT 1;

-- Spark: Compute/Training + Data Pipelines
INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-007', 1.00, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'spark' LIMIT 1;

INSERT INTO cloud.package_component_tags (package_id, component_id, confidence_score, source, tagged_by)
SELECT package_id, 'ai-006', 0.90, 'manual', 'data-engineer'
FROM cloud.bitnami_packages WHERE name = 'spark' LIMIT 1;
```

### 8.4 Query Examples

**Query 1: Get all packages for a specific component category**
```sql
SELECT 
    p.name,
    p.description,
    p.stars,
    p.version,
    t.component_name
FROM cloud.bitnami_packages p
JOIN cloud.package_component_tags pct ON p.package_id = pct.package_id
JOIN cloud.component_taxonomy t ON pct.component_id = t.component_id
WHERE t.component_id = 'ai-001'  -- Vector Databases
ORDER BY p.stars DESC;
```

**Query 2: Get all component tags for a specific package**
```sql
SELECT 
    p.name,
    t.component_id,
    t.component_name,
    pct.confidence_score,
    pct.source
FROM cloud.bitnami_packages p
JOIN cloud.package_component_tags pct ON p.package_id = pct.package_id
JOIN cloud.component_taxonomy t ON pct.component_id = t.component_id
WHERE p.name = 'mlflow';
```

**Query 3: Find packages tagged as both Inference AND LLM Tools**
```sql
SELECT 
    p.name,
    p.description,
    p.stars,
    STRING_AGG(t.component_name, ', ' ORDER BY t.display_order) as components
FROM cloud.bitnami_packages p
JOIN cloud.package_component_tags pct ON p.package_id = pct.package_id
JOIN cloud.component_taxonomy t ON pct.component_id = t.component_id
WHERE p.package_id IN (
    SELECT package_id 
    FROM cloud.package_component_tags 
    WHERE component_id IN ('ai-003', 'ai-009')
    GROUP BY package_id
    HAVING COUNT(DISTINCT component_id) = 2
)
GROUP BY p.package_id, p.name, p.description, p.stars
ORDER BY p.stars DESC;
```

**Query 4: Get package count by component category**
```sql
SELECT 
    t.component_id,
    t.component_name,
    COUNT(DISTINCT pct.package_id) as package_count
FROM cloud.component_taxonomy t
LEFT JOIN cloud.package_component_tags pct ON t.component_id = pct.component_id
GROUP BY t.component_id, t.component_name, t.display_order
ORDER BY t.display_order;
```

---

## 9. Auto-Tagging Strategy (Future Enhancement)

### 9.1 Rule-Based Auto-Tagging

**Approach:** Use keywords and descriptions to automatically suggest component tags.

**Example Rules:**
```python
AUTO_TAG_RULES = {
    'ai-001': {  # Vector Databases
        'keywords': ['vector', 'embedding', 'similarity', 'qdrant', 'milvus', 'weaviate', 'pinecone'],
        'description_patterns': ['vector database', 'vector search', 'similarity search', 'embeddings']
    },
    'ai-003': {  # Model Inference
        'keywords': ['inference', 'serving', 'model serving', 'kserve', 'seldon', 'triton', 'torchserve'],
        'description_patterns': ['inference server', 'model serving', 'prediction']
    },
    'ai-006': {  # Data Pipelines
        'keywords': ['airflow', 'workflow', 'dag', 'pipeline', 'etl', 'orchestration', 'prefect', 'dagster'],
        'description_patterns': ['workflow', 'pipeline', 'orchestration', 'data processing']
    },
    'ai-009': {  # LLM Tools
        'keywords': ['llm', 'llama', 'mistral', 'gpt', 'language model', 'ollama', 'vllm'],
        'description_patterns': ['large language model', 'llm', 'language model', 'text generation']
    },
    'ai-011': {  # Observability
        'keywords': ['prometheus', 'grafana', 'monitoring', 'metrics', 'observability', 'loki', 'jaeger'],
        'description_patterns': ['monitoring', 'observability', 'metrics', 'logging', 'tracing']
    },
    'ai-012': {  # Secrets Management
        'keywords': ['vault', 'secrets', 'credentials', 'sealed-secrets'],
        'description_patterns': ['secrets management', 'credentials', 'api keys']
    },
    'ai-013': {  # Storage/Caching
        'keywords': ['redis', 'minio', 's3', 'object storage', 'cache', 'memcached'],
        'description_patterns': ['object storage', 'caching', 'cache', 'key-value']
    }
}
```

### 9.2 ML-Based Auto-Tagging (Advanced)

Use vector embeddings (`description_embedding`, `readme_embedding`, `keywords_embedding`) to:
1. Find similar packages to manually tagged ones
2. Suggest tags based on semantic similarity
3. Continuously improve with user feedback

**Example SQL Query:**
```sql
-- Find packages similar to "qdrant" (a known vector DB)
SELECT 
    p1.name,
    p1.description,
    1 - (p1.description_embedding <=> p2.description_embedding) as similarity
FROM cloud.bitnami_packages p1,
    (SELECT description_embedding FROM cloud.bitnami_packages WHERE name = 'qdrant' LIMIT 1) p2
WHERE p1.name != 'qdrant'
    AND p1.description_embedding IS NOT NULL
ORDER BY similarity DESC
LIMIT 10;

-- These similar packages should also be tagged as 'ai-001' (Vector Databases)
```

---

## 10. Implementation Recommendations

### 10.1 Phase 1: Immediate (No Schema Changes)

**Use existing fields for basic filtering:**
1. **Description search** (99.5% complete) - full-text search on `description` field
2. **Keyword filtering** (42% have keywords) - JSONB operators on `keywords` field
3. **Category filtering** (32% categorized) - filter by existing 8 categories
4. **Operator flag** - filter by `is_operator` (5.1% are operators)

**Sample Query:**
```sql
SELECT name, description, stars, keywords
FROM cloud.bitnami_packages
WHERE 
    (description ILIKE '%vector%' OR description ILIKE '%embedding%')
    AND keywords @> '["database"]'::jsonb
ORDER BY stars DESC;
```

### 10.2 Phase 2: Schema Extension (Proposed)

**Create component taxonomy tables:**
1. Create `cloud.component_taxonomy` table (13 AI stack categories)
2. Create `cloud.package_component_tags` mapping table (many-to-many)
3. Manually tag top 100 packages (by stars) for each component category
4. Implement rule-based auto-tagging for remaining packages

**Priority Packages to Tag Manually (Top 50 by Stars):**
- Monitoring: kube-prometheus-stack, grafana, prometheus, loki, metrics-server
- Security: cert-manager, vault, keycloak, harbor
- Networking: ingress-nginx, traefik, external-dns
- CI/CD: argo-cd, gitlab, jenkins
- Databases: redis, postgresql, mysql, mongodb, elasticsearch
- Messaging: kafka, rabbitmq
- Storage: minio
- AI/ML: spark, ollama, mlflow, airflow
- Vector DBs: qdrant, milvus

### 10.3 Phase 3: AI Architect Integration

**Enhance AI Architect with component-aware recommendations:**
1. User asks: "I need vector database for embeddings"
   - Filter: `component_id = 'ai-001'`
   - Return: Qdrant, Milvus, Weaviate (with specs, pricing, popularity)

2. User asks: "Show me a full ML stack"
   - Suggest packages from each component category:
     - Vector DB: Qdrant
     - Inference: Ollama
     - Observability: Prometheus + Grafana
     - Storage: MinIO
     - Secrets: Vault
     - Gateway: Traefik
     - Pipelines: Airflow

3. User asks: "What components do I need for RAG?"
   - Return component checklist:
     - ✅ Vector Database (ai-001) - Qdrant, Milvus
     - ✅ LLM Tools (ai-009) - Ollama, vLLM
     - ✅ Storage (ai-013) - MinIO, S3
     - ✅ API Gateway (ai-010) - Traefik, Kong
     - ⚠️ Observability (ai-011) - Prometheus, Grafana

---

## 11. Data Quality Summary

### 11.1 Strengths ✅

| Field | Completeness | Status |
|-------|--------------|--------|
| Name, Version, Content URL | 100% | ✅ Excellent |
| Description | 99.47% | ✅ Excellent |
| Stars (popularity) | 92.14% | ✅ Very Good |
| README | 67.94% | ✅ Good |

### 11.2 Weaknesses ⚠️

| Field | Completeness | Issue |
|-------|--------------|-------|
| Category | 31.93% | ❌ 68% uncategorized |
| Keywords (populated) | 42.09% | ⚠️ 58% have empty arrays |
| License | 12.60% | ⚠️ Sparse license info |

### 11.3 Critical Gap: Categorization

**Problem:** 9,145 packages (68.1%) have no category assigned.

**Impact:**
- Cannot filter by category for most packages
- Difficult to discover relevant packages
- No way to browse by AI stack component type

**Solution:** Implement the proposed `component_tags` system to enable granular, multi-category tagging.

---

## 12. Trusted Fields ✅

These fields are **production-ready** for filtering, sorting, and search:

| Field | Completeness | Use Case |
|-------|--------------|----------|
| **`name`** | 100% | Package identification |
| **`description`** | 99.5% | Full-text search, semantic search |
| **`version`** | 100% | Version filtering |
| **`content_url`** | 100% | Helm install command |
| **`stars`** | 92.1% | Popularity sorting |
| **`is_operator`** | 100% | Operator filtering |
| **`keywords`** | 42% | Keyword filtering (partial coverage) |
| **`category`** | 32% | Category filtering (partial coverage) |

---

## 13. NOT Recommended Fields ⚠️

These fields have poor coverage or reliability:

| Field | Completeness | Issue |
|-------|--------------|-------|
| **`license`** | 12.6% | Only 1,693/13,435 have license info |
| **`category`** | 31.9% | 68% uncategorized (use with caution) |

---

## Appendix: Complete Component Taxonomy Reference

### AI Stack Component Categories (Proposed)

| ID | Category | Parent Group | Example Packages | Priority |
|----|----------|--------------|------------------|----------|
| ai-001 | Vector Databases | ai-storage | Qdrant, Milvus, Weaviate, Pinecone | High |
| ai-002 | Model Training | ai-compute | Kubeflow, Ray, Horovod | High |
| ai-003 | Model Inference | ai-compute | Ollama, KServe, Seldon, Triton, TorchServe | High |
| ai-004 | Model Registry | ai-storage | MLflow, DVC, ModelDB | High |
| ai-005 | Feature Store | ai-storage | Feast, Tecton, Hopsworks | Medium |
| ai-006 | Data Pipelines | ai-pipelines | Airflow, Prefect, Dagster, Argo Workflows | High |
| ai-007 | Compute/Training | ai-compute | Spark, Dask, Ray | Medium |
| ai-008 | MLOps Platform | ai-platforms | Kubeflow, MLflow, W&B | High |
| ai-009 | LLM Tools | ai-llm | Ollama, vLLM, TGI | High |
| ai-010 | API Gateway | ai-gateway | Kong, Traefik, Nginx, Envoy, Tyk | High |
| ai-011 | Observability | ai-ops | Prometheus, Grafana, Loki, Tempo, Jaeger | High |
| ai-012 | Secrets Management | ai-security | Vault, Sealed Secrets, External Secrets | High |
| ai-013 | Storage/Caching | ai-storage | MinIO, Redis, S3, Ceph | High |

---

**End of Data Profiling Report**


