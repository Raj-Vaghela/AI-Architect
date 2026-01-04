// Dashboard Application
(function() {
    'use strict';

    const HELP_CONTENT = {
        "overview.total_instances": {
            title: "Compute Instances",
            subtitle: "Total rows in cloud.instances",
            analytical: [
                "Metric: COUNT(*) over cloud.instances (row count).",
                "Interpretation: size of the compute catalog available to the recommender."
            ],
            normal: [
                "How many instance entries we have in the database."
            ],
            business: [
                "More entries generally means broader coverage of providers and SKUs, but it can also include duplicates (e.g., regional pricing variants)."
            ]
        },
        "overview.total_packages": {
            title: "Marketplace Packages",
            subtitle: "Total rows in cloud.bitnami_packages",
            analytical: [
                "Metric: COUNT(*) over cloud.bitnami_packages (row count).",
                "Interpretation: size of the marketplace catalog."
            ],
            normal: [
                "How many Helm charts/operators we can recommend from the marketplace."
            ],
            business: [
                "A larger catalog improves choice, but categorization gaps can reduce discoverability without extra tagging."
            ]
        },
        "overview.total_providers": {
            title: "Cloud Providers",
            subtitle: "Distinct providers represented in instances data",
            analytical: [
                "Metric: COUNT(DISTINCT provider) in cloud.instances."
            ],
            normal: [
                "How many cloud vendors are included (AWS, OVH, etc.)."
            ],
            business: [
                "Provider coverage determines how often we can satisfy a user’s preferred vendor constraint."
            ]
        },
        "overview.total_regions": {
            title: "Geographic Regions",
            subtitle: "Rows in cloud.regions (available regions metadata)",
            analytical: [
                "Metric: COUNT(*) over cloud.regions (row count).",
                "Interpretation: number of region records available for location-aware filtering."
            ],
            normal: [
                "How many locations (regions/cities) the dataset knows about."
            ],
            business: [
                "More region coverage improves locality constraints (latency, compliance, residency)."
            ]
        },
        "instances.coverage.cpu_ram": {
            title: "CPU/RAM Coverage",
            subtitle: "How complete core compute specs are",
            analytical: [
                "Metric: non-null rate for cpu_cores and memory_gb in cloud.instances.",
                "Used to estimate reliability of vCPU/RAM filters."
            ],
            normal: [
                "Most rows have CPU and RAM filled in."
            ],
            business: [
                "High coverage means we can confidently recommend instances based on performance needs."
            ]
        },
        "instances.coverage.pricing": {
            title: "Pricing Coverage",
            subtitle: "How complete pricing is (monthly/hourly)",
            analytical: [
                "Metric: non-null rate for price_monthly and/or price_hourly in cloud.instances.",
                "Used to estimate reliability of max budget filters."
            ],
            normal: [
                "Most rows have a price, so we can sort/filter by cost."
            ],
            business: [
                "High coverage enables budget-based recommendations and comparisons."
            ]
        },
        "instances.coverage.gpu_model": {
            title: "GPU Model Coverage",
            subtitle: "How often gpu_model is present",
            analytical: [
                "Metric: non-null rate for gpu_model in cloud.instances.",
                "Low values mean GPU-type filtering will miss most relevant rows."
            ],
            normal: [
                "Only a small fraction of rows tell us the exact GPU type."
            ],
            business: [
                "We cannot reliably promise specific GPU models (A100/H100/etc.) without adding a mapping/backfill."
            ]
        },
        "instances.coverage.gpu_count": {
            title: "GPU Count Coverage",
            subtitle: "How often gpu_count is present",
            analytical: [
                "Metric: non-null rate for gpu_count in cloud.instances.",
                "This enables a 'has GPU' / 'how many GPUs' filter with caveats."
            ],
            normal: [
                "Most rows indicate how many GPUs an instance has."
            ],
            business: [
                "We can support GPU/no-GPU and GPU-count based filtering even if model/VRAM are missing."
            ]
        },
        "packages.coverage.description": {
            title: "Description Coverage",
            subtitle: "How often package descriptions are present",
            analytical: [
                "Metric: non-null rate for description in cloud.bitnami_packages.",
                "Supports text search relevance."
            ],
            normal: [
                "Almost all packages have a description."
            ],
            business: [
                "Good descriptions improve search and recommendation quality without manual tagging."
            ]
        },
        "packages.coverage.install_identifiers": {
            title: "Install Identifier Coverage",
            subtitle: "Whether we can provide Helm install coordinates/URLs",
            analytical: [
                "Metric: non-null rate for content_url and version in cloud.bitnami_packages.",
                "If present, we can output deterministic install commands."
            ],
            normal: [
                "We can almost always tell you how to install the package."
            ],
            business: [
                "Enables automation: copy/paste installation, golden paths, and templates."
            ]
        },
        "packages.coverage.category": {
            title: "Category Coverage",
            subtitle: "How often category is assigned",
            analytical: [
                "Metric: non-null rate for category in cloud.bitnami_packages.",
                "Low coverage makes category browsing incomplete."
            ],
            normal: [
                "Most packages are missing categories."
            ],
            business: [
                "Without better categorization/tags, users will struggle to discover the right components quickly."
            ]
        },
        "packages.coverage.keywords_populated": {
            title: "Keywords Populated",
            subtitle: "How often keywords[] contains at least one tag",
            analytical: [
                "Metric: share of rows where jsonb_array_length(keywords) > 0.",
                "Used to support keyword-based filtering."
            ],
            normal: [
                "Less than half the packages have useful keyword tags."
            ],
            business: [
                "Keyword gaps reduce discoverability; a component taxonomy/tag mapping improves precision."
            ]
        },
        "charts.provider_distribution": {
            title: "Provider Distribution Chart",
            subtitle: "Instance count per provider",
            analytical: [
                "Each bar is COUNT(*) grouped by provider from cloud.instances.",
                "Shows dataset skew (e.g., AWS dominance)."
            ],
            normal: [
                "Which provider has the most entries in our dataset."
            ],
            business: [
                "Skew can bias recommendations toward providers with more coverage unless we normalize or filter."
            ]
        },
        "charts.gpu_model_distribution": {
            title: "GPU Model Distribution Chart",
            subtitle: "Counts among rows where gpu_model is present",
            analytical: [
                "Each bar counts rows grouped by gpu_model (only where gpu_model is non-null).",
                "This is not the full GPU market — it’s the subset with populated GPU model metadata."
            ],
            normal: [
                "The most common GPU names we can see (where the data actually includes GPU type)."
            ],
            business: [
                "Useful for understanding what GPU types we can confidently describe; missing GPU model data is the main blocker."
            ]
        },
        "charts.package_category_distribution": {
            title: "Package Category Distribution Chart",
            subtitle: "Counts per marketplace category (plus Uncategorized)",
            analytical: [
                "Counts of packages grouped by category plus an explicit 'Uncategorized' bucket for NULL category.",
                "Highlights how incomplete category assignment is."
            ],
            normal: [
                "How packages are currently grouped (and how many aren’t grouped at all)."
            ],
            business: [
                "If most are uncategorized, category filters will miss relevant options and reduce conversion/UX."
            ]
        }
    };

    // State
    const state = {
        data: {
            dbMap: null,
            instancesProfile: null,
            packagesProfile: null,
            dataContract: null
        },
        loading: true
    };

    // Initialize
    document.addEventListener('DOMContentLoaded', init);

    async function init() {
        // Set timestamp
        document.getElementById('timestamp').textContent = new Date().toLocaleDateString();

        // Setup navigation
        setupNavigation();

        // Setup help system (delegated clicks)
        setupHelpSystem();

        // Load data
        await loadAllData();

        // Render sections
        if (state.loading === false) {
            renderOverview();
            renderCompute();
            renderMarketplace();
            renderContract();
        }
    }

    // Navigation
    function setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                switchSection(section);
            });
        });
    }

    function switchSection(sectionName) {
        // Update nav
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.dataset.section === sectionName);
        });

        // Update sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`).classList.add('active');
    }

    // Data Loading
    async function loadAllData() {
        try {
            const [dbMap, instancesProfile, packagesProfile, dataContract] = await Promise.all([
                fetchMarkdown('../docs/db-map.md'),
                fetchMarkdown('../docs/instances-profile.md'),
                fetchMarkdown('../docs/packages-profile.md'),
                fetchMarkdown('../docs/v1-data-contract.md')
            ]);

            state.data.dbMap = dbMap;
            state.data.instancesProfile = instancesProfile;
            state.data.packagesProfile = packagesProfile;
            state.data.dataContract = dataContract;
            state.loading = false;

            // Hide loading, show content
            document.getElementById('loading').style.display = 'none';
        } catch (error) {
            console.error('Failed to load data:', error);
            state.loading = true;
            document.getElementById('loading').style.display = 'none';
            document.getElementById('error').style.display = 'block';
        }
    }

    async function fetchMarkdown(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${url}`);
        }
        return await response.text();
    }

    // Help System
    function setupHelpSystem() {
        const modal = document.getElementById('help-modal');
        if (!modal) return;

        document.addEventListener('click', (e) => {
            // Close handlers
            const closeEl = e.target.closest('[data-help-close="true"]');
            if (closeEl) {
                closeHelpModal();
                return;
            }

            // Tab handlers
            const tabEl = e.target.closest('[data-help-tab]');
            if (tabEl) {
                setHelpTab(tabEl.getAttribute('data-help-tab'));
                return;
            }

            // Open handlers (any element with data-help)
            const helpEl = e.target.closest('[data-help]');
            if (!helpEl) return;
            if (modal.classList.contains('open') && modal.contains(e.target)) return;

            const meta = extractHelpMeta(helpEl);
            openHelpModal(meta);
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeHelpModal();
        });
    }

    function extractHelpMeta(el) {
        const ds = el.dataset || {};
        const rawText = (el.textContent || '').trim();
        return {
            key: ds.help,
            kind: ds.kind || inferKindFromText(rawText),
            value: ds.value || rawText,
            title: ds.title || ds.helpTitle || null,
            subtitle: ds.subtitle || null,
            source: ds.source || null
        };
    }

    function inferKindFromText(text) {
        if (!text) return 'unknown';
        if (text.includes('%')) return 'percent';
        if (text.startsWith('$')) return 'currency';
        if (/^\d[\d,]*$/.test(text)) return 'count';
        return 'unknown';
    }

    function openHelpModal(meta) {
        const modal = document.getElementById('help-modal');
        const titleEl = document.getElementById('help-title');
        const subtitleEl = document.getElementById('help-subtitle');
        const sourceEl = document.getElementById('help-source');

        const content = getHelpContent(meta);

        titleEl.textContent = content.title;
        subtitleEl.textContent = content.subtitle;

        document.getElementById('help-analytical').innerHTML = renderHelpBlock('Analytical meaning', content.analytical);
        document.getElementById('help-normal').innerHTML = renderHelpBlock('Normal meaning', content.normal);
        document.getElementById('help-business').innerHTML = renderHelpBlock('Business meaning', content.business);

        sourceEl.textContent = `Source: ${content.source || 'Not available yet'}`;

        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
        setHelpTab('analytical');
    }

    function closeHelpModal() {
        const modal = document.getElementById('help-modal');
        if (!modal) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }

    function setHelpTab(tabName) {
        document.querySelectorAll('.help-tab').forEach(btn => {
            const isActive = btn.getAttribute('data-help-tab') === tabName;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });

        document.querySelectorAll('.help-section').forEach(p => p.classList.remove('active'));
        const panel = document.getElementById(`help-${tabName}`);
        if (panel) panel.classList.add('active');
    }

    function renderHelpBlock(heading, items) {
        const safeItems = Array.isArray(items) ? items : [];
        return `
            <h4>${escapeHtml(heading)}</h4>
            <ul>
                ${safeItems.length ? safeItems.map(i => `<li>${escapeHtml(i)}</li>`).join('') : `<li>Not available yet.</li>`}
            </ul>
        `;
    }

    function getHelpContent(meta) {
        const entry = HELP_CONTENT[meta.key];
        if (entry) {
            return {
                title: entry.title || fallbackTitle(meta),
                subtitle: entry.subtitle || fallbackSubtitle(meta),
                analytical: entry.analytical || fallbackAnalytical(meta),
                normal: entry.normal || fallbackNormal(meta),
                business: entry.business || fallbackBusiness(meta),
                source: meta.source || entry.source || null
            };
        }

        return {
            title: fallbackTitle(meta),
            subtitle: fallbackSubtitle(meta),
            analytical: fallbackAnalytical(meta),
            normal: fallbackNormal(meta),
            business: fallbackBusiness(meta),
            source: meta.source || null
        };
    }

    function fallbackTitle(meta) {
        if (meta.title) return meta.title;
        const niceKey = (meta.key || 'Metric').split('.').slice(-1)[0].replace(/_/g, ' ');
        return `${niceKey}`.toUpperCase();
    }

    function fallbackSubtitle(meta) {
        const v = (meta.value || '').toString();
        if (meta.kind === 'percent') return `Value: ${v} (coverage / rate)`;
        if (meta.kind === 'currency') return `Value: ${v} (price / cost metric)`;
        if (meta.kind === 'count') return `Value: ${v} (count / volume metric)`;
        if (meta.kind === 'chart') return `Chart (aggregated metric)`;
        return `Value: ${v || '—'}`;
    }

    function fallbackAnalytical(meta) {
        if (meta.kind === 'percent') {
            return [
                "Metric type: percentage / rate.",
                "Typically computed as (non-null count / total) or (subset count / total) depending on context.",
                "Use this to judge data completeness or distribution."
            ];
        }
        if (meta.kind === 'count') {
            return [
                "Metric type: count.",
                "Typically computed via COUNT(*) or COUNT(DISTINCT ...) over a table or subset.",
                "Counts reflect volume, not quality."
            ];
        }
        if (meta.kind === 'currency') {
            return [
                "Metric type: currency amount.",
                "Usually an observed price from the dataset (monthly/hourly) and may vary by region/provider.",
                "Treat extreme outliers carefully."
            ];
        }
        if (meta.kind === 'chart') {
            return [
                "This is an aggregated visualization (group-by counts or rates).",
                "Bars represent categories; bar height is the metric value."
            ];
        }
        return ["Not available yet."];
    }

    function fallbackNormal(meta) {
        if (meta.kind === 'percent') return ["How much of the data has this field filled in (or how big this slice is)."];
        if (meta.kind === 'count') return ["How many items match this bucket/row/category."];
        if (meta.kind === 'currency') return ["How expensive this option is, as recorded in the dataset."];
        if (meta.kind === 'chart') return ["A picture showing which groups are bigger or smaller."];
        return ["Not available yet."];
    }

    function fallbackBusiness(meta) {
        if (meta.kind === 'percent') return ["Higher % generally means we can rely on this field for filtering and decision-making."];
        if (meta.kind === 'count') return ["Higher counts usually mean better coverage or popularity—but not necessarily better fit."];
        if (meta.kind === 'currency') return ["Directly affects cost recommendations and budget feasibility."];
        if (meta.kind === 'chart') return ["Helps you spot concentration (coverage skew) and data gaps quickly."];
        return ["Not available yet."];
    }

    function escapeHtml(str) {
        return String(str)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('\"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    // Overview Section
    function renderOverview() {
        // Extract key stats
        const stats = extractOverviewStats();
        
        document.getElementById('total-instances').textContent = stats.instances.toLocaleString();
        document.getElementById('total-packages').textContent = stats.packages.toLocaleString();
        document.getElementById('total-providers').textContent = stats.providers;
        document.getElementById('total-regions').textContent = stats.regions;

        // Schema summary
        const schemaSummary = document.getElementById('schema-summary');
        schemaSummary.innerHTML = `
            <li><strong>cloud</strong> schema: <span data-help="db.cloud_tables" data-kind="count" data-value="${stats.cloudTables}" data-source="docs/db-map.md">${stats.cloudTables}</span> tables, <span data-help="db.cloud_views" data-kind="count" data-value="2" data-source="docs/db-map.md">2</span> views</li>
            <li><strong>public</strong> schema: 3 tables (users, conversations, messages)</li>
            <li><strong>auth, storage, realtime</strong>: Supabase system schemas</li>
            <li>Vector embeddings for semantic search</li>
        `;

        // Quality summary
        const qualitySummary = document.getElementById('quality-summary');
        qualitySummary.innerHTML = `
            <li>CPU/RAM: <span class="text-success" data-help="instances.coverage.cpu_ram" data-kind="percent" data-value="99.7" data-source="docs/instances-profile.md">99.7% complete</span></li>
            <li>Pricing: <span class="text-success" data-help="instances.coverage.pricing" data-kind="percent" data-value="98.5" data-source="docs/instances-profile.md">98.5% complete</span></li>
            <li>Package descriptions: <span class="text-success" data-help="packages.coverage.description" data-kind="percent" data-value="99.5" data-source="docs/packages-profile.md">99.5% complete</span></li>
            <li>Install URLs: <span class="text-success" data-help="packages.coverage.install_identifiers" data-kind="percent" data-value="100" data-source="docs/packages-profile.md">100% complete</span></li>
        `;

        // Gaps summary
        const gapsSummary = document.getElementById('gaps-summary');
        gapsSummary.innerHTML = `
            <li>GPU model: <span class="text-danger" data-help="instances.coverage.gpu_model" data-kind="percent" data-value="4.7" data-source="docs/instances-profile.md">Only 4.7% coverage</span></li>
            <li>GPU VRAM: <span class="text-danger" data-help="instances.coverage.gpu_vram" data-kind="percent" data-value="4.8" data-source="docs/instances-profile.md">Only 4.8% coverage</span></li>
            <li>Package categories: <span class="text-danger" data-help="packages.coverage.category" data-kind="percent" data-value="31.9" data-source="docs/packages-profile.md">Only 31.9% assigned</span></li>
            <li>GPU manufacturer: <span class="text-danger" data-help="instances.coverage.gpu_manufacturer" data-kind="percent" data-value="0" data-source="docs/instances-profile.md">0% (field empty)</span></li>
        `;

        // Findings summary
        const findingsSummary = document.getElementById('findings-summary');
        findingsSummary.innerHTML = `
            <li>AWS dominates: <span data-help="instances.provider.aws_share" data-kind="percent" data-value="89" data-source="docs/instances-profile.md">89%</span> of compute instances</li>
            <li><span data-help="instances.gpu_instances" data-kind="count" data-value="728" data-source="docs/instances-profile.md">728</span> GPU instances (<span data-help="instances.gpu_instances_share" data-kind="percent" data-value="4.4" data-source="docs/instances-profile.md">4.4%</span> of total)</li>
            <li><span data-help="packages.uncategorized_count" data-kind="count" data-value="9145" data-source="docs/packages-profile.md">9,145</span> packages uncategorized (<span data-help="packages.uncategorized_share" data-kind="percent" data-value="68.1" data-source="docs/packages-profile.md">68.1%</span>)</li>
            <li>Proposed: 13-category AI stack taxonomy</li>
        `;

        // Provider chart
        drawProviderChart();
    }

    function extractOverviewStats() {
        return {
            instances: 16695,
            packages: 13435,
            providers: 7,
            regions: 234,
            cloudTables: 8
        };
    }

    function drawProviderChart() {
        const canvas = document.getElementById('provider-chart');
        const ctx = canvas.getContext('2d');
        
        const data = [
            { name: 'AWS', count: 14858, color: '#FFEB00' },
            { name: 'OVH', count: 1353, color: '#00F5FF' },
            { name: 'Vultr', count: 203, color: '#FF00F5' },
            { name: 'DigitalOcean', count: 147, color: '#0066FF' },
            { name: 'Contabo', count: 75, color: '#00FF88' },
            { name: 'RunPod', count: 38, color: '#FF8C00' },
            { name: 'Civo', count: 21, color: '#FF1744' }
        ];

        drawBarChart(ctx, canvas, data, 'Provider Distribution');
    }

    // Compute Section
    function renderCompute() {
        // Trusted fields
        const trustedFields = document.getElementById('trusted-fields');
        trustedFields.innerHTML = `
            <div class="field-item">
                <span class="field-name">provider</span>
                <span class="field-coverage high" data-help="instances.field.provider.coverage" data-kind="percent" data-value="100" data-source="docs/instances-profile.md">100%</span>
            </div>
            <div class="field-item">
                <span class="field-name">cpu_cores</span>
                <span class="field-coverage high" data-help="instances.field.cpu_cores.coverage" data-kind="percent" data-value="99.7" data-source="docs/instances-profile.md">99.7%</span>
            </div>
            <div class="field-item">
                <span class="field-name">memory_gb</span>
                <span class="field-coverage high" data-help="instances.field.memory_gb.coverage" data-kind="percent" data-value="99.7" data-source="docs/instances-profile.md">99.7%</span>
            </div>
            <div class="field-item">
                <span class="field-name">price_monthly</span>
                <span class="field-coverage high" data-help="instances.field.price_monthly.coverage" data-kind="percent" data-value="98.5" data-source="docs/instances-profile.md">98.5%</span>
            </div>
            <div class="field-item">
                <span class="field-name">regions</span>
                <span class="field-coverage high" data-help="instances.field.regions.coverage" data-kind="percent" data-value="99.7" data-source="docs/instances-profile.md">99.7%</span>
            </div>
        `;

        // Sparse fields
        const sparseFields = document.getElementById('sparse-fields');
        sparseFields.innerHTML = `
            <div class="field-item">
                <span class="field-name">gpu_model</span>
                <span class="field-coverage low" data-help="instances.coverage.gpu_model" data-kind="percent" data-value="4.7" data-source="docs/instances-profile.md">4.7%</span>
            </div>
            <div class="field-item">
                <span class="field-name">gpu_memory_gb</span>
                <span class="field-coverage low" data-help="instances.coverage.gpu_vram" data-kind="percent" data-value="4.8" data-source="docs/instances-profile.md">4.8%</span>
            </div>
            <div class="field-item">
                <span class="field-name">gpu_manufacturer</span>
                <span class="field-coverage low" data-help="instances.coverage.gpu_manufacturer" data-kind="percent" data-value="0" data-source="docs/instances-profile.md">0%</span>
            </div>
            <div class="field-item">
                <span class="field-name">license</span>
                <span class="field-coverage low" data-help="packages.coverage.license" data-kind="percent" data-value="12.6" data-source="docs/packages-profile.md">12.6%</span>
            </div>
        `;

        // Insights
        const insights = document.getElementById('compute-insights');
        insights.innerHTML = `
            <li><span data-help="instances.gpu_partial_count" data-kind="count" data-value="14179" data-source="docs/instances-profile.md">14,179</span> instances have GPU count but missing model/VRAM (<span data-help="instances.gpu_partial_share" data-kind="percent" data-value="84.9" data-source="docs/instances-profile.md">84.9%</span>)</li>
            <li>Only <span data-help="instances.gpu_complete_count" data-kind="count" data-value="791" data-source="docs/instances-profile.md">791</span> instances (<span data-help="instances.gpu_complete_share" data-kind="percent" data-value="4.7" data-source="docs/instances-profile.md">4.7%</span>) have complete GPU specs</li>
            <li><span data-help="instances.duplicate_groups_note" data-kind="note" data-source="docs/instances-profile.md">Duplicates are typically regional pricing variations</span></li>
            <li>Median GPU instance price: <span data-help="instances.price.gpu_median" data-kind="currency" data-value="$817" data-source="docs/instances-profile.md">$817/month</span> vs <span data-help="instances.price.nongpu_median" data-kind="currency" data-value="$425" data-source="docs/instances-profile.md">$425</span> for non-GPU</li>
            <li>Proposed fix: <span data-help="proposals.gpu_specs_table" data-kind="proposal" data-source="docs/v1-data-contract.md">gpu_specs mapping table (~50 rows)</span></li>
        `;

        // Pricing stats
        const pricingStats = document.getElementById('pricing-stats');
        pricingStats.innerHTML = `
            <div class="pricing-item">
                <div class="pricing-value" data-help="instances.price.min_monthly" data-kind="currency" data-value="$0.37" data-source="docs/instances-profile.md">$0.37</div>
                <div class="pricing-label">Minimum (Monthly)</div>
            </div>
            <div class="pricing-item">
                <div class="pricing-value" data-help="instances.price.max_monthly" data-kind="currency" data-value="$857,604" data-source="docs/instances-profile.md">$857,604</div>
                <div class="pricing-label">Maximum (Monthly)</div>
            </div>
            <div class="pricing-item">
                <div class="pricing-value" data-help="instances.price.median_monthly" data-kind="currency" data-value="$427" data-source="docs/instances-profile.md">$427</div>
                <div class="pricing-label">Median (Monthly)</div>
            </div>
            <div class="pricing-item">
                <div class="pricing-value" data-help="instances.price.avg_monthly" data-kind="currency" data-value="$838" data-source="docs/instances-profile.md">$838</div>
                <div class="pricing-label">Avg (Monthly)</div>
            </div>
        `;

        // GPU chart
        drawGPUChart();
    }

    function drawGPUChart() {
        const canvas = document.getElementById('gpu-chart');
        const ctx = canvas.getContext('2d');
        
        const data = [
            { name: 'L4', count: 216, color: '#00FF41' },
            { name: 'T4', count: 147, color: '#FFEB00' },
            { name: 'A10G', count: 112, color: '#00F5FF' },
            { name: 'L40S', count: 69, color: '#FF00F5' },
            { name: 'T4g', count: 42, color: '#0066FF' },
            { name: 'Radeon Pro V520', count: 40, color: '#FF1744' },
            { name: 'V100', count: 37, color: '#FF8C00' },
            { name: 'A100', count: 24, color: '#00FF88' },
            { name: 'H100', count: 23, color: '#CCFF00' },
            { name: 'H200', count: 10, color: '#00F0FF' }
        ];

        drawBarChart(ctx, canvas, data, 'Top 10 GPU Models by Instance Count');
    }

    // Marketplace Section
    function renderMarketplace() {
        // Categories
        const categoriesList = document.getElementById('categories-list');
        categoriesList.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                        <th>%</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Monitoring and logging</td><td><span data-help="packages.category.monitoring.count" data-kind="count" data-value="1060" data-source="docs/packages-profile.md">1,060</span></td><td><span data-help="packages.category.monitoring.share" data-kind="percent" data-value="7.9" data-source="docs/packages-profile.md">7.9%</span></td></tr>
                    <tr><td>Networking</td><td><span data-help="packages.category.networking.count" data-kind="count" data-value="713" data-source="docs/packages-profile.md">713</span></td><td><span data-help="packages.category.networking.share" data-kind="percent" data-value="5.3" data-source="docs/packages-profile.md">5.3%</span></td></tr>
                    <tr><td>Security</td><td><span data-help="packages.category.security.count" data-kind="count" data-value="688" data-source="docs/packages-profile.md">688</span></td><td><span data-help="packages.category.security.share" data-kind="percent" data-value="5.1" data-source="docs/packages-profile.md">5.1%</span></td></tr>
                    <tr><td>Integration and delivery</td><td><span data-help="packages.category.cicd.count" data-kind="count" data-value="610" data-source="docs/packages-profile.md">610</span></td><td><span data-help="packages.category.cicd.share" data-kind="percent" data-value="4.5" data-source="docs/packages-profile.md">4.5%</span></td></tr>
                    <tr><td>Database</td><td><span data-help="packages.category.database.count" data-kind="count" data-value="527" data-source="docs/packages-profile.md">527</span></td><td><span data-help="packages.category.database.share" data-kind="percent" data-value="3.9" data-source="docs/packages-profile.md">3.9%</span></td></tr>
                    <tr><td>Storage</td><td><span data-help="packages.category.storage.count" data-kind="count" data-value="291" data-source="docs/packages-profile.md">291</span></td><td><span data-help="packages.category.storage.share" data-kind="percent" data-value="2.2" data-source="docs/packages-profile.md">2.2%</span></td></tr>
                    <tr><td>Streaming and messaging</td><td><span data-help="packages.category.messaging.count" data-kind="count" data-value="226" data-source="docs/packages-profile.md">226</span></td><td><span data-help="packages.category.messaging.share" data-kind="percent" data-value="1.7" data-source="docs/packages-profile.md">1.7%</span></td></tr>
                    <tr><td>AI / Machine learning</td><td><span data-help="packages.category.aiml.count" data-kind="count" data-value="175" data-source="docs/packages-profile.md">175</span></td><td><span data-help="packages.category.aiml.share" data-kind="percent" data-value="1.3" data-source="docs/packages-profile.md">1.3%</span></td></tr>
                    <tr><td><strong>Uncategorized</strong></td><td><strong><span data-help="packages.uncategorized_count" data-kind="count" data-value="9145" data-source="docs/packages-profile.md">9,145</span></strong></td><td><strong><span data-help="packages.uncategorized_share" data-kind="percent" data-value="68.1" data-source="docs/packages-profile.md">68.1%</span></strong></td></tr>
                </tbody>
            </table>
        `;

        // Top keywords
        const keywordsList = document.getElementById('keywords-list');
        keywordsList.innerHTML = `
            <div style="columns: 2; column-gap: 1rem; font-size: 0.875rem;">
                <div>1. kubernetes (<span data-help="packages.keyword.kubernetes" data-kind="count" data-value="576" data-source="docs/packages-profile.md">576</span>)</div>
                <div>2. database (<span data-help="packages.keyword.database" data-kind="count" data-value="395" data-source="docs/packages-profile.md">395</span>)</div>
                <div>3. monitoring (<span data-help="packages.keyword.monitoring" data-kind="count" data-value="374" data-source="docs/packages-profile.md">374</span>)</div>
                <div>4. prometheus (<span data-help="packages.keyword.prometheus" data-kind="count" data-value="285" data-source="docs/packages-profile.md">285</span>)</div>
                <div>5. cluster (<span data-help="packages.keyword.cluster" data-kind="count" data-value="216" data-source="docs/packages-profile.md">216</span>)</div>
                <div>6. operator (<span data-help="packages.keyword.operator" data-kind="count" data-value="201" data-source="docs/packages-profile.md">201</span>)</div>
                <div>7. security (<span data-help="packages.keyword.security" data-kind="count" data-value="198" data-source="docs/packages-profile.md">198</span>)</div>
                <div>8. helm (<span data-help="packages.keyword.helm" data-kind="count" data-value="161" data-source="docs/packages-profile.md">161</span>)</div>
                <div>9. storage (<span data-help="packages.keyword.storage" data-kind="count" data-value="142" data-source="docs/packages-profile.md">142</span>)</div>
                <div>10. metrics (<span data-help="packages.keyword.metrics" data-kind="count" data-value="126" data-source="docs/packages-profile.md">126</span>)</div>
                <div>11. api (<span data-help="packages.keyword.api" data-kind="count" data-value="120" data-source="docs/packages-profile.md">120</span>)</div>
                <div>12. sql (<span data-help="packages.keyword.sql" data-kind="count" data-value="119" data-source="docs/packages-profile.md">119</span>)</div>
                <div>13. web (<span data-help="packages.keyword.web" data-kind="count" data-value="112" data-source="docs/packages-profile.md">112</span>)</div>
                <div>14. infrastructure (<span data-help="packages.keyword.infrastructure" data-kind="count" data-value="110" data-source="docs/packages-profile.md">110</span>)</div>
                <div>15. http (<span data-help="packages.keyword.http" data-kind="count" data-value="108" data-source="docs/packages-profile.md">108</span>)</div>
                <div>16. ingress (<span data-help="packages.keyword.ingress" data-kind="count" data-value="106" data-source="docs/packages-profile.md">106</span>)</div>
                <div>17. exporter (<span data-help="packages.keyword.exporter" data-kind="count" data-value="104" data-source="docs/packages-profile.md">104</span>)</div>
                <div>18. redis (<span data-help="packages.keyword.redis" data-kind="count" data-value="101" data-source="docs/packages-profile.md">101</span>)</div>
                <div>19. postgresql (<span data-help="packages.keyword.postgresql" data-kind="count" data-value="100" data-source="docs/packages-profile.md">100</span>)</div>
                <div>20. postgres (<span data-help="packages.keyword.postgres" data-kind="count" data-value="99" data-source="docs/packages-profile.md">99</span>)</div>
            </div>
        `;

        // Insights
        const insights = document.getElementById('marketplace-insights');
        insights.innerHTML = `
            <li><span data-help="packages.uncategorized_share" data-kind="percent" data-value="68.1" data-source="docs/packages-profile.md">68%</span> of packages (<span data-help="packages.uncategorized_count" data-kind="count" data-value="9145" data-source="docs/packages-profile.md">9,145</span>) have no category assigned</li>
            <li>Only <span data-help="packages.coverage.keywords_populated" data-kind="percent" data-value="42" data-source="docs/packages-profile.md">42%</span> of packages have populated keywords</li>
            <li>AI/ML category is smallest: <span data-help="packages.category.aiml.count" data-kind="count" data-value="175" data-source="docs/packages-profile.md">175</span> packages (<span data-help="packages.category.aiml.share" data-kind="percent" data-value="1.3" data-source="docs/packages-profile.md">1.3%</span> of total)</li>
            <li>Top package: kube-prometheus-stack (<span data-help="packages.top.kube_prometheus_stars" data-kind="count" data-value="1109" data-source="docs/packages-profile.md">1,109</span> stars)</li>
            <li>Vector DBs exist but have low visibility (<span data-help="packages.vector_db.low_visibility" data-kind="note" data-source="docs/packages-profile.md">~20-23 stars</span>)</li>
        `;

        // Taxonomy
        const taxonomy = document.getElementById('taxonomy-grid');
        const taxonomyItems = [
            { id: 'ai-001', name: 'Vector Databases', desc: 'Qdrant, Milvus, Weaviate' },
            { id: 'ai-002', name: 'Model Training', desc: 'Kubeflow, Ray' },
            { id: 'ai-003', name: 'Model Inference', desc: 'Ollama, KServe, Triton' },
            { id: 'ai-004', name: 'Model Registry', desc: 'MLflow, DVC' },
            { id: 'ai-005', name: 'Feature Store', desc: 'Feast, Tecton' },
            { id: 'ai-006', name: 'Data Pipelines', desc: 'Airflow, Prefect' },
            { id: 'ai-007', name: 'Compute/Training', desc: 'Spark, Dask, Ray' },
            { id: 'ai-008', name: 'MLOps Platform', desc: 'Kubeflow, MLflow' },
            { id: 'ai-009', name: 'LLM Tools', desc: 'Ollama, vLLM' },
            { id: 'ai-010', name: 'API Gateway', desc: 'Kong, Traefik' },
            { id: 'ai-011', name: 'Observability', desc: 'Prometheus, Grafana' },
            { id: 'ai-012', name: 'Secrets Management', desc: 'Vault, Sealed Secrets' },
            { id: 'ai-013', name: 'Storage/Caching', desc: 'MinIO, Redis, S3' }
        ];

        taxonomy.innerHTML = taxonomyItems.map(item => `
            <div class="taxonomy-item">
                <h4>${item.id.toUpperCase()}: ${item.name}</h4>
                <p>${item.desc}</p>
            </div>
        `).join('');

        // Category chart
        drawCategoryChart();
    }

    function drawCategoryChart() {
        const canvas = document.getElementById('category-chart');
        const ctx = canvas.getContext('2d');
        
        const data = [
            { name: 'Uncategorized', count: 9145, color: '#FF1744' },
            { name: 'Monitoring & Logging', count: 1060, color: '#0066FF' },
            { name: 'Networking', count: 713, color: '#FF00F5' },
            { name: 'Security', count: 688, color: '#00FF41' },
            { name: 'CI/CD', count: 610, color: '#FF8C00' },
            { name: 'Database', count: 527, color: '#00F5FF' },
            { name: 'Storage', count: 291, color: '#FFEB00' },
            { name: 'Messaging', count: 226, color: '#FF00A8' },
            { name: 'AI/ML', count: 175, color: '#CCFF00' }
        ];

        drawBarChart(ctx, canvas, data, 'Package Category Distribution');
    }

    // Data Contract Section
    function renderContract() {
        // Supported decisions
        const supported = document.getElementById('supported-decisions');
        supported.innerHTML = `
            <h3>Compute Recommender</h3>
            <ul>
                <li>Filter by provider, vCPU, RAM, price</li>
                <li>Filter by GPU presence/count</li>
                <li>Filter by region</li>
                <li>Sort by price, specs</li>
                <li>Compare pricing across providers</li>
            </ul>
            <h3>Marketplace Recommender</h3>
            <ul>
                <li>Search by package name, description</li>
                <li>Filter by operator flag, official, CNCF</li>
                <li>Filter by popularity (stars)</li>
                <li>Provide Helm install commands</li>
            </ul>
        `;

        // Unsupported decisions
        const unsupported = document.getElementById('unsupported-decisions');
        unsupported.innerHTML = `
            <h3>Compute Recommender</h3>
            <ul>
                <li>Filter by GPU model (4.7% coverage)</li>
                <li>Filter by GPU VRAM (4.8% coverage)</li>
                <li>Filter by GPU manufacturer (0% coverage)</li>
            </ul>
            <h3>Marketplace Recommender</h3>
            <ul>
                <li>Browse by AI stack component (N/A)</li>
                <li>Filter "vector databases" (manual search only)</li>
                <li>Filter "inference servers" (manual search only)</li>
                <li>Recommend complete stacks (N/A)</li>
            </ul>
        `;

        // Proposed fixes
        const fixes = document.getElementById('proposed-fixes');
        fixes.innerHTML = `
            <h3>1. GPU Specs Mapping Table</h3>
            <p>Create <code>cloud.gpu_specs</code> table with ~50 rows mapping GPU models to specs (VRAM, manufacturer, architecture, etc.)</p>
            <p><strong>Impact:</strong> Enables GPU model and VRAM filtering</p>
            
            <h3>2. Component Tags System</h3>
            <p>Create <code>cloud.component_taxonomy</code> and <code>cloud.package_component_tags</code> tables for AI stack categorization</p>
            <p><strong>Impact:</strong> Enables AI component discovery and stack recommendations</p>
        `;

        // Limitations
        const computeLimitations = document.getElementById('compute-limitations');
        computeLimitations.innerHTML = `
            <li>Cannot guarantee specific GPU models without verification</li>
            <li><span data-help="instances.gpu_partial_count" data-kind="count" data-value="14179" data-source="docs/instances-profile.md">14,179</span> instances have GPU count but missing model/VRAM</li>
            <li>User must verify GPU specs with provider</li>
            <li>Regional pricing variations may cause duplicates</li>
        `;

        const marketplaceLimitations = document.getElementById('marketplace-limitations');
        marketplaceLimitations.innerHTML = `
            <li><span data-help="packages.uncategorized_share" data-kind="percent" data-value="68.1" data-source="docs/packages-profile.md">68%</span> of packages uncategorized - fallback to text search</li>
            <li><span data-help="packages.keywords_empty_share" data-kind="percent" data-value="58" data-source="docs/packages-profile.md">58%</span> of packages have no keywords</li>
            <li>No structured AI stack component taxonomy</li>
            <li>Cannot recommend complete stacks without relationships</li>
        `;

        // Schemas
        document.getElementById('compute-input-schema').textContent = `{
  min_vcpu?: number;
  min_ram_gb?: number;
  max_price_monthly?: number;
  providers?: string[];
  gpu_required?: boolean;
  gpu_count?: number;
  regions?: string[];
}`;

        document.getElementById('marketplace-input-schema').textContent = `{
  component_category?: string;
  keywords?: string[];
  search_text?: string;
  categories?: number[];
  min_stars?: number;
  is_operator?: boolean;
}`;

        // Tiers
        const tiers = document.getElementById('tiers-table');
        tiers.innerHTML = `
            <div class="tier-item tier-1">
                <div class="tier-header">Tier 1: High Confidence (>95% coverage)</div>
                <div class="tier-description">Provider, vCPU, RAM, Price, Regions, Package name/version/description. NO disclaimers needed.</div>
            </div>
            <div class="tier-item tier-2">
                <div class="tier-header">Tier 2: Medium Confidence (80-95% coverage)</div>
                <div class="tier-description">GPU count, stars/popularity. Optional warning about potential incompleteness.</div>
            </div>
            <div class="tier-item tier-3">
                <div class="tier-header">Tier 3: Low Confidence (<80% coverage)</div>
                <div class="tier-description">GPU model, GPU VRAM, categories, keywords. Required warning with explanation and verification needed.</div>
            </div>
            <div class="tier-item tier-4">
                <div class="tier-header">Tier 4: Not Recommended (<10% or 0% coverage)</div>
                <div class="tier-description">GPU manufacturer, package license filtering. Block feature or redirect to alternatives.</div>
            </div>
        `;
    }

    // Chart Drawing Utility - Neo-Brutalist Style
    function drawBarChart(ctx, canvas, data, title) {
        const padding = 80;
        const width = canvas.width;
        const height = canvas.height;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2 - 60; // Extra space for title
        
        // Clear canvas with white background
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, width, height);
        
        // Draw title - Neo-Brutalist style
        ctx.fillStyle = '#000000';
        ctx.font = 'bold 20px "Courier New", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(title.toUpperCase(), width / 2, 20);
        
        // Draw title underline
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(width / 2 - 150, 45);
        ctx.lineTo(width / 2 + 150, 45);
        ctx.stroke();
        
        // Calculate max value
        const maxValue = Math.max(...data.map(d => d.count));
        
        // Calculate bar dimensions
        const barWidth = chartWidth / data.length - 12;
        const barSpacing = 12;
        
        // Draw bars with Neo-Brutalist style
        data.forEach((item, index) => {
            const barHeight = (item.count / maxValue) * chartHeight;
            const x = padding + index * (barWidth + barSpacing);
            const y = height - padding - barHeight;
            
            // Draw bar with bright color
            ctx.fillStyle = item.color || '#0000FF';
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw black border around bar (thick)
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 4;
            ctx.strokeRect(x, y, barWidth, barHeight);
            
            // Draw value on top of bar - bold black text
            ctx.fillStyle = '#000000';
            ctx.font = 'bold 14px "Courier New", monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            ctx.fillText(item.count.toLocaleString(), x + barWidth / 2, y - 8);
            
            // Draw label - rotated, bold
            ctx.save();
            ctx.translate(x + barWidth / 2, height - padding + 20);
            ctx.rotate(-Math.PI / 4);
            ctx.fillStyle = '#000000';
            ctx.font = 'bold 11px "Courier New", monospace';
            ctx.textAlign = 'right';
            ctx.textBaseline = 'middle';
            ctx.fillText(item.name.toUpperCase(), 0, 0);
            ctx.restore();
        });
        
        // Draw axes - thick black lines
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 6;
        ctx.beginPath();
        // X-axis
        ctx.moveTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        // Y-axis
        ctx.moveTo(padding, height - padding);
        ctx.lineTo(padding, padding + 20);
        ctx.stroke();
        
        // Draw axis labels
        ctx.fillStyle = '#000000';
        ctx.font = 'bold 12px "Courier New", monospace';
        ctx.textAlign = 'center';
        ctx.fillText('COUNT', padding / 2, height / 2);
    }

})();

