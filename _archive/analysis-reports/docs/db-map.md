# Database Schema Map

**Generated:** 2025-12-25  
**Database:** Supabase (PostgreSQL)

---

## Overview

This document provides a comprehensive map of all schemas, tables, and views in the Stack8s Supabase database, with a focus on compute/pricing and marketplace component tables.

### Schemas Present

- **auth** - Supabase authentication system (20 tables)
- **cloud** - Main business logic for compute, pricing, and marketplace (8 tables, 2 views)
- **public** - Application data for conversations and users (3 tables)
- **storage** - Supabase storage system (9 tables)
- **realtime** - Supabase realtime subscriptions (3 tables)
- **vault** - Secrets management (1 table, 1 view)
- **drizzle** - ORM migrations (1 table)
- **extensions** - PostgreSQL extensions (2 views)

---

## 1. Cloud Schema (Primary Business Logic)

### 1.1 `cloud.instances` - Compute & GPU Pricing Data

**Purpose:** Stores compute instance specifications and pricing across multiple cloud providers.

**Row Count:** 16,695

**Primary Key:** `id` (uuid, auto-generated)

**Important Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key, auto-generated |
| `provider` | varchar | Cloud provider (digitalocean, aws, gcp, etc.) |
| `instance_id` | varchar | Provider's instance identifier |
| `name` | varchar | Instance name/slug |
| `instance_type` | varchar | Instance type classification |
| `cpu_cores` | integer | Number of CPU cores |
| `cpu_threads` | integer | Number of CPU threads |
| `cpu_manufacturer` | varchar | CPU manufacturer (Intel, AMD) |
| `cpu_model` | varchar | Specific CPU model |
| `cpu_mhz` | integer | CPU clock speed in MHz |
| `memory_mb` | integer | RAM in megabytes |
| `memory_gb` | numeric | RAM in gigabytes |
| `disk_gb` | integer | Disk size in GB |
| `disk_type` | varchar | Disk type (SSD, NVMe, etc.) |
| `disk_count` | integer | Number of disks |
| `bandwidth_mbps` | integer | Bandwidth in Mbps |
| `transfer_tb` | numeric | Data transfer allowance in TB |
| `networking_throughput` | integer | Network throughput |
| `inbound_bandwidth` | integer | Inbound bandwidth |
| `outbound_bandwidth` | integer | Outbound bandwidth |
| `price_monthly` | numeric | Monthly price |
| `price_hourly` | numeric | Hourly price |
| `price_currency` | varchar | Currency (USD, EUR, etc.) |
| `gpu_count` | integer | Number of GPUs |
| `gpu_model` | varchar | GPU model (A100, V100, etc.) |
| `gpu_memory_gb` | integer | GPU memory in GB |
| `gpu_manufacturer` | varchar | GPU manufacturer (NVIDIA, AMD) |
| `regions` | jsonb | Array of region IDs where available |
| `available` | boolean | Availability status |
| `stock_status` | varchar | Stock availability status |
| `description` | text | Instance description |
| `capabilities` | jsonb | Additional capabilities |
| `os_type` | varchar | Operating system type |
| `quota` | integer | Quota limits |
| `created_at` | timestamp | Record creation timestamp |
| `updated_at` | timestamp | Record update timestamp |
| `data_source_timestamp` | timestamp | Source data timestamp |
| `raw_data` | jsonb | Raw API response data |
| `embedding` | vector | Vector embedding for semantic search |

**Relationships:** 
- Joins with `cloud.regions` via JSONB array matching on `regions` column

**Indexes/Notes:**
- Contains vector embedding for AI-powered semantic search
- Regions stored as JSONB array for many-to-many relationship

---

### 1.2 `cloud.bitnami_packages` - Kubernetes Marketplace Components

**Purpose:** Stores Kubernetes Helm charts and operators from Bitnami/ArtifactHub marketplace.

**Row Count:** 13,435

**Primary Key:** `package_id` (uuid)

**Important Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `package_id` | uuid | Primary key |
| `name` | text | Package name |
| `normalized_name` | text | Normalized package name |
| `category` | integer | Category ID (references bitnami_categories) |
| `is_operator` | boolean | Whether package is a Kubernetes operator |
| `official` | boolean | Official package status |
| `cncf` | boolean | CNCF project status |
| `description` | text | Package description |
| `home_url` | text | Package home URL |
| `readme` | text | Full README content |
| `version` | text | Latest version |
| `app_version` | text | Application version |
| `digest` | text | Package digest/hash |
| `deprecated` | boolean | Deprecation status |
| `contains_security_updates` | boolean | Security updates flag |
| `prerelease` | boolean | Pre-release status |
| `signed` | boolean | Package signature status |
| `content_url` | text | Content download URL |
| `stats_subscriptions` | integer | Subscription count |
| `stats_webhooks` | integer | Webhook count |
| `production_organizations_count` | integer | Production usage count |
| `repository_name` | text | Repository name |
| `repository_display_name` | text | Repository display name |
| `repository_url` | text | Repository URL |
| `repository_verified_publisher` | boolean | Verified publisher flag |
| `repository_official` | boolean | Official repository flag |
| `logo_image_id` | text | Logo image identifier |
| `internal_logo_url` | text | Internal logo URL |
| `stars` | integer | Package stars/popularity |
| `license` | text | Package license |
| `has_values_schema` | boolean | Values schema availability |
| `security_report_summary` | jsonb | Security report data |
| `security_report_created_at` | bigint | Security report timestamp |
| `all_containers_images_whitelisted` | boolean | Container whitelist status |
| `ts` | bigint | Timestamp |
| `repository_id` | text | Repository identifier |
| `repository_kind` | integer | Repository kind/type |
| `repository_scanner_disabled` | boolean | Scanner status |
| `repository_organization_name` | text | Organization name |
| `repository_organization_display_name` | text | Organization display name |
| `keywords` | jsonb | Package keywords array |
| `links` | jsonb | Related links array |
| `available_versions` | jsonb | Available versions array |
| `dependencies` | jsonb | Package dependencies array |
| `container_images` | jsonb | Container images array |
| `security_reports` | jsonb | Security reports object |
| `statistics` | jsonb | Usage statistics object |
| `description_embedding` | vector | Description vector embedding |
| `readme_embedding` | vector | README vector embedding |
| `keywords_embedding` | vector | Keywords vector embedding |
| `search_tsv` | tsvector | Full-text search vector |
| `created_at` | timestamptz | Record creation timestamp |

**Relationships:**
- `category` → `cloud.bitnami_categories.category_id` (informal, no FK constraint)

**Indexes/Notes:**
- Multiple vector embeddings for semantic search (description, readme, keywords)
- Full-text search capabilities via `search_tsv`
- Rich metadata including security reports and statistics

---

### 1.3 `cloud.bitnami_categories` - Package Categories

**Purpose:** Categories for organizing Bitnami packages.

**Row Count:** 8

**Primary Key:** `category_id` (integer)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `category_id` | integer | Primary key |
| `name` | text | Category name |
| `total` | integer | Total packages in category |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Update timestamp |

**Relationships:**
- Referenced by `cloud.bitnami_packages.category` (informal)

---

### 1.4 `cloud.bitnami_operator_capabilities` - Operator Capabilities

**Purpose:** Stores Kubernetes operator capability levels and metadata.

**Row Count:** 5

**Primary Key:** `capability_id` (text)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `capability_id` | text | Primary key (capability identifier) |
| `name` | text | Capability name |
| `total` | integer | Total operators with this capability |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Update timestamp |

---

### 1.5 `cloud.providers` - Cloud Provider Registry

**Purpose:** Registry of cloud providers with credentials and metadata.

**Row Count:** 9

**Primary Key:** None explicitly defined (uses `id` uuid)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Identifier |
| `provider` | varchar | Provider name |
| `created_at` | timestamptz | Creation timestamp |
| `provider_credentials` | jsonb | Provider API credentials (encrypted) |
| `logo_url` | varchar | Provider logo URL |

**Notes:**
- Stores credentials for accessing provider APIs

---

### 1.6 `cloud.regions` - Geographic Regions

**Purpose:** Geographic regions available across cloud providers.

**Row Count:** 234

**Primary Key:** None explicitly defined (uses `id` uuid)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Identifier |
| `provider` | varchar | Cloud provider name |
| `region_id` | varchar | Provider's region identifier |
| `continent` | varchar | Continent name |
| `country` | varchar | Country name |
| `city` | varchar | City name |
| `status` | varchar | Region status |
| `extra_info` | jsonb | Additional region metadata |

**Relationships:**
- Joined with `cloud.instances` via JSONB region matching

---

### 1.7 `cloud.cred` - Legacy Credentials Table

**Purpose:** Legacy credentials storage (appears to be superseded by `providers`).

**Row Count:** 7

**Primary Key:** None explicitly defined (uses `id` integer)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Identifier |
| `created_at` | timestamptz | Creation timestamp |
| `provider` | varchar | Provider name |
| `provider_credentials` | jsonb | Provider credentials |

---

### 1.8 `cloud.data` - Generic Key-Value Store

**Purpose:** Generic key-value storage for provider-specific data.

**Row Count:** 52

**Primary Key:** None explicitly defined (uses `id` integer with sequence)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Auto-incrementing ID |
| `created_at` | timestamptz | Creation timestamp |
| `provider` | varchar | Provider name |
| `key` | varchar | Data key |
| `value` | jsonb | Data value (JSONB) |

---

### Cloud Schema Views

#### 1.9 `cloud.instances_with_city` (VIEW)

**Purpose:** Joins instances with region city information.

**Definition:** 
```sql
SELECT i.*, r.city, r.country, r.continent
FROM cloud.instances i
JOIN cloud.regions r ON (
  EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(i.regions) region
    WHERE region.value = r.region_id::text
  )
)
```

**Use Case:** Query instances filtered by city/country/continent

---

#### 1.10 `cloud.instances_with_country` (VIEW)

**Purpose:** Joins instances with region country information.

**Definition:**
```sql
SELECT i.*, r.country
FROM cloud.instances i
JOIN cloud.regions r ON (
  EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(i.regions) region
    WHERE region.value = r.region_id::text
  )
)
```

**Use Case:** Query instances filtered by country

---

## 2. Public Schema (Application Data)

### 2.1 `public.users` - User Accounts

**Purpose:** Application user accounts.

**Row Count:** 4

**Primary Key:** `id` (integer)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Primary key |
| `email` | text | User email (nullable) |
| `first_name` | text | First name |
| `last_name` | text | Last name |
| `created_at` | timestamp | Creation timestamp |

**Relationships:**
- Referenced by `public.conversations.user_id`

---

### 2.2 `public.conversations` - Chat Conversations

**Purpose:** User conversation threads.

**Row Count:** 6

**Primary Key:** `id` (uuid)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `user_id` | integer | Foreign key to users |
| `title` | text | Conversation title |
| `created_at` | timestamp | Creation timestamp |

**Relationships:**
- **FK:** `user_id` → `public.users.id`
- Referenced by `public.messages.conversation_id`

---

### 2.3 `public.messages` - Chat Messages

**Purpose:** Individual messages within conversations.

**Row Count:** 26

**Primary Key:** `id` (uuid)

**Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `conversation_id` | uuid | Foreign key to conversations |
| `role` | text | Message role (user/assistant/system) |
| `content` | text | Message content |
| `created_at` | timestamp | Creation timestamp |

**Relationships:**
- **FK:** `conversation_id` → `public.conversations.id`

---

## 3. Other Schemas (Summary)

### 3.1 Auth Schema
- **Purpose:** Supabase authentication system
- **Tables:** 20 (users, sessions, refresh_tokens, mfa_factors, oauth_*, saml_*, etc.)
- **Use:** User authentication, session management, OAuth, SAML

### 3.2 Storage Schema
- **Purpose:** Supabase file storage
- **Tables:** 9 (buckets, objects, migrations, s3_multipart_uploads, etc.)
- **Use:** File storage and management

### 3.3 Realtime Schema
- **Purpose:** Supabase realtime subscriptions
- **Tables:** 3 (messages, subscription, schema_migrations)
- **Use:** Real-time pub/sub functionality

### 3.4 Vault Schema
- **Purpose:** Secrets management
- **Tables:** 1 (secrets)
- **Views:** 1 (decrypted_secrets)
- **Use:** Encrypted secrets storage

---

## Key Relationships & Data Flow

### Compute/Pricing Flow
```
cloud.providers (9 providers)
    ↓
cloud.instances (16,695 instances)
    ↔ cloud.regions (234 regions) [via JSONB array matching]
    ↓
cloud.instances_with_city (VIEW)
cloud.instances_with_country (VIEW)
```

### Marketplace Flow
```
cloud.bitnami_categories (8 categories)
    ↓
cloud.bitnami_packages (13,435 packages)
    ← cloud.bitnami_operator_capabilities (5 capabilities)
```

### Application Flow
```
public.users (4 users)
    ↓ FK: user_id
public.conversations (6 conversations)
    ↓ FK: conversation_id
public.messages (26 messages)
```

---

## Important Notes

1. **No Foreign Key Constraints in Cloud Schema:** While there are logical relationships between `instances`, `regions`, and `bitnami_packages`, they are not enforced by database constraints.

2. **Vector Embeddings:** Both `cloud.instances` and `cloud.bitnami_packages` have vector embedding columns for semantic search capabilities.

3. **JSONB Storage:** Heavy use of JSONB for flexible data storage:
   - `instances.regions` (array of region IDs)
   - `instances.capabilities`, `raw_data`
   - `bitnami_packages` (keywords, links, versions, dependencies, etc.)
   - `providers.provider_credentials`

4. **Full-Text Search:** `bitnami_packages` includes a `search_tsv` column for PostgreSQL full-text search.

5. **Data Sources:**
   - **Compute Data:** Aggregated from multiple cloud providers (9 providers)
   - **Marketplace Data:** Sourced from Bitnami/ArtifactHub
   - **User Data:** Application-generated

---

## Query Patterns

### Find GPU Instances by Provider
```sql
SELECT provider, name, gpu_model, gpu_count, price_monthly
FROM cloud.instances
WHERE gpu_count > 0
ORDER BY price_monthly;
```

### Find Packages by Category
```sql
SELECT p.name, p.version, p.stars, c.name as category
FROM cloud.bitnami_packages p
LEFT JOIN cloud.bitnami_categories c ON p.category = c.category_id
WHERE p.deprecated = false
ORDER BY p.stars DESC;
```

### Find Instances in Specific Region
```sql
SELECT i.*, r.city, r.country
FROM cloud.instances_with_city i
WHERE i.country = 'United States'
  AND i.gpu_count > 0;
```

---

**End of Database Map**


