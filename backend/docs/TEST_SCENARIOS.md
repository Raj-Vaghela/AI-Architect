# Test Scenarios - Stack8s AI Architect

## Purpose
This document contains test scenarios to verify that the AI Architect bot correctly uses tools, provides accurate recommendations, and meets acceptance criteria.

---

## 1. Kubernetes Tool Testing

### Test Case K8S-001: Basic Package Search
**Objective:** Verify K8s tool returns relevant results for common queries

**Test Scenarios:**

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| K8S-001a | "I need a monitoring solution for Kubernetes" | Should call `search_k8s_packages("monitoring")` and recommend Prometheus, Grafana | ✅ Tool called<br>✅ Results include official packages<br>✅ Explains what each does |
| K8S-001b | "Help me set up a database in Kubernetes" | Should call `search_k8s_packages("database")` and suggest PostgreSQL, MySQL, MongoDB | ✅ Tool called<br>✅ Multiple database options shown<br>✅ Mentions Bitnami charts |
| K8S-001c | "I want to deploy Redis" | Should call `search_k8s_packages("redis")` | ✅ Tool called<br>✅ Redis chart found<br>✅ Provides deployment guidance |

---

### Test Case K8S-002: Specific Infrastructure Components
**Objective:** Test tool accuracy for specific infrastructure needs

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| K8S-002a | "I need an ingress controller" | Should search for "ingress" and recommend NGINX, Traefik | ✅ NGINX ingress mentioned<br>✅ Explains ingress role |
| K8S-002b | "How do I handle secrets in K8s?" | Should search for "secrets" or "vault" and suggest External Secrets Operator, Sealed Secrets | ✅ Security-focused recommendations<br>✅ Multiple options |
| K8S-002c | "I need a service mesh" | Should search "service mesh" and recommend Istio, Linkerd | ✅ CNCF packages prioritized<br>✅ Explains service mesh benefits |

---

### Test Case K8S-003: Official vs Community Packages
**Objective:** Verify preference for official/CNCF packages

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| K8S-003a | "Show me Kubernetes packages for logging" | Should prioritize official packages (Fluentd, Elasticsearch) | ✅ Official packages ranked higher<br>✅ Mentions package source |
| K8S-003b | "I need cert management" | Should recommend cert-manager (CNCF) | ✅ CNCF badge highlighted<br>✅ Explains why it's trusted |

---

### Test Case K8S-004: Edge Cases
**Objective:** Test handling of ambiguous or no-result queries

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| K8S-004a | "xyz123 kubernetes package" | Should search but likely find no results, inform user politely | ✅ Tool called<br>✅ "No packages found" message<br>✅ Suggests alternatives |
| K8S-004b | "What's in your K8s catalog?" | Should explain what's available without calling tool unnecessarily | ✅ No tool call (informational)<br>✅ Describes Bitnami/Helm charts |

---

## 2. Compute Tool Testing

### Test Case COMPUTE-001: CPU vs GPU Selection (Post-Bias Fix)
**Objective:** Verify tool is no longer GPU-biased

**Test Scenarios:**

| Scenario | User Query | Expected Behavior | Tool Call | Acceptance Criteria |
|----------|-----------|-------------------|-----------|---------------------|
| COMPUTE-001a | "I need to deploy a REST API for my scikit-learn model" | Should recommend CPU instances | `search_compute_instances(gpu_needed=False, ...)` | ✅ `gpu_needed=False`<br>✅ CPU instances returned<br>✅ Cost-effective options |
| COMPUTE-001b | "I want to train a YOLOv8 model" | Should recommend GPU instances | `search_compute_instances(gpu_needed=True, min_vram_gb=16)` | ✅ `gpu_needed=True`<br>✅ GPU with sufficient VRAM<br>✅ Mentions T4/A100 |
| COMPUTE-001c | "I need compute for my ML pipeline, not sure what" | Should search without GPU filter to show both | `search_compute_instances()` or `gpu_needed=None` | ✅ Both CPU and GPU shown<br>✅ Explains when to use each |
| COMPUTE-001d | "Run a PostgreSQL database" | Should recommend CPU instances | `search_compute_instances(gpu_needed=False, ...)` | ✅ CPU instances only<br>✅ Focuses on RAM/storage |
| COMPUTE-001e | "Fine-tune Llama 3 70B" | Should recommend high-VRAM GPUs | `search_compute_instances(gpu_needed=True, min_vram_gb=140)` | ✅ A100 80GB or H100<br>✅ Multi-GPU recommendation<br>✅ Mentions interconnect |

---

### Test Case COMPUTE-002: Price Filtering
**Objective:** Verify budget constraints are respected

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| COMPUTE-002a | "I need a GPU for inference under $200/month" | Should call tool with `max_price_monthly=200` | ✅ Price filter applied<br>✅ Results under budget<br>✅ Recommends T4/L4 |
| COMPUTE-002b | "Cheapest CPU instance for testing" | Should search CPUs, sort by price | ✅ Small CPU instances<br>✅ Mentions it's for testing |

---

### Test Case COMPUTE-003: Provider Preferences
**Objective:** Test provider filtering

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| COMPUTE-003a | "I need an AWS GPU" | Should filter by `provider="aws"` | ✅ Provider filter applied<br>✅ Only AWS results |
| COMPUTE-003b | "GCP or Azure options for my model" | Should make 2 separate calls or show both | ✅ Multiple providers shown<br>✅ Compares options |

---

### Test Case COMPUTE-004: VRAM Estimation
**Objective:** Test LLM VRAM guidance

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| COMPUTE-004a | "How much VRAM for Llama 2 13B?" | Should estimate ~26GB (2GB/B param) and search accordingly | ✅ Rough estimate given<br>✅ Labeled as estimate<br>✅ Suggests verification |
| COMPUTE-004b | "Can I run Mistral 7B on a T4?" | Should explain T4 has 16GB, 7B needs ~14GB, yes | ✅ Factual VRAM check<br>✅ Margin for inference overhead<br>✅ Clear answer |

---

## 3. HuggingFace Tool Testing

### Test Case HF-001: Model Search
**Objective:** Verify model search returns relevant results

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| HF-001a | "Find me a text generation model" | Should search with `pipeline_tag="text-generation"` | ✅ Tool called correctly<br>✅ Llama/Mistral/Phi in results<br>✅ Shows downloads/likes |
| HF-001b | "I need an image classifier" | Should search `pipeline_tag="image-classification"` | ✅ Vision models returned<br>✅ Explains use cases |
| HF-001c | "Open source LLM for chatbot" | Should search and prioritize permissive licenses | ✅ License filter considered<br>✅ Apache-2.0/MIT highlighted |

---

### Test Case HF-002: License Awareness
**Objective:** Verify license checking for commercial use

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| HF-002a | "Commercial LLM for my startup" | Should filter by commercial-friendly licenses | ✅ License filter applied<br>✅ Warns about restrictive licenses<br>✅ Suggests Llama 3, Mistral |
| HF-002b | "Can I use model X commercially?" | Should check license field from tool results | ✅ States actual license<br>✅ Explains implications<br>✅ No guessing |

---

### Test Case HF-003: Popularity Metrics
**Objective:** Test grounding in downloads/likes data

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| HF-003a | "Most popular text generation model" | Should use tool results, cite downloads/likes | ✅ Shows actual numbers<br>✅ Doesn't hallucinate rankings |
| HF-003b | "Is model X well-maintained?" | Should check downloads/likes as proxy | ✅ Uses tool data<br>✅ Qualifies assessment |

---

## 4. Multi-Tool Orchestration

### Test Case MULTI-001: End-to-End Workflow
**Objective:** Verify agent can chain tools for complete solutions

| Scenario | User Query | Expected Tools Called | Acceptance Criteria |
|----------|-----------|----------------------|---------------------|
| MULTI-001a | "I want to deploy Llama 2 70B for inference on GCP" | 1. `search_hf_models("llama 2 70b")`<br>2. `search_compute_instances(gpu_needed=True, min_vram_gb=140, provider="gcp")`<br>3. `search_k8s_packages("llm serving")` | ✅ All 3 tools called<br>✅ Recommendations aligned<br>✅ Coherent deployment plan |
| MULTI-001b | "Set up a monitoring stack for my ML cluster" | 1. `search_k8s_packages("prometheus")`<br>2. `search_k8s_packages("grafana")`<br>3. Maybe `search_compute_instances` for resources | ✅ K8s tools called<br>✅ Stack components explained<br>✅ Integration guidance |
| MULTI-001c | "I need a complete MLOps pipeline" | Multiple calls to K8s tool (Kubeflow, MLflow, Airflow, monitoring) | ✅ Comprehensive search<br>✅ Explains each component<br>✅ Architecture diagram (text) |

---

### Test Case MULTI-002: Tool Selection Logic
**Objective:** Verify agent picks the RIGHT tool for the job

| Scenario | User Query | Expected Tool(s) | Should NOT Call | Acceptance Criteria |
|----------|-----------|-----------------|----------------|---------------------|
| MULTI-002a | "What's Kubernetes?" | None (informational) | Any tool | ✅ Direct answer<br>✅ No unnecessary tool call |
| MULTI-002b | "Compare AWS and GCP pricing" | `search_compute_instances` (2 calls) | HF/K8s tools | ✅ Only compute tool<br>✅ Both providers queried |
| MULTI-002c | "Install kubectl" | None or K8s tool | Compute/HF tools | ✅ Installation instructions<br>✅ K8s context provided |

---

## 5. Truthfulness & Grounding

### Test Case TRUTH-001: No Hallucination
**Objective:** Verify agent doesn't invent data

| Scenario | User Query | Expected Behavior | Red Flags (FAIL) |
|----------|-----------|-------------------|------------------|
| TRUTH-001a | "What's the price of GCP A100?" | Must use tool, cite actual result | ❌ Makes up a price<br>❌ Says "around $X" without tool |
| TRUTH-001b | "How many downloads does model X have?" | Must use HF tool and cite exact number | ❌ Guesses<br>❌ Says "popular" without data |
| TRUTH-001c | "Is model X available?" | Must search HF tool | ❌ Says yes/no without checking |

---

### Test Case TRUTH-002: Uncertainty Handling
**Objective:** Verify agent admits when it doesn't know

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| TRUTH-002a | "Does provider X have GPU Y?" | Search tool, if not found → "Not found in results" | ✅ Honest about limitations<br>✅ Suggests alternatives |
| TRUTH-002b | "What's the best model for task X?" | Qualifies recommendation ("popular choices include...") | ✅ Doesn't claim absolute "best"<br>✅ Shows multiple options |

---

## 6. Conversational Quality

### Test Case CONV-001: Natural Interaction
**Objective:** Test post-fix for "templatey" system prompt

| Scenario | User Query | Expected Style | Red Flags (FAIL) |
|----------|-----------|---------------|------------------|
| CONV-001a | "Hey, I need help deploying a model" | Friendly, conversational response | ❌ Rigid "RECOMMENDATION:" format<br>❌ Too formal |
| CONV-001b | "Thanks!" | Natural acknowledgment | ❌ Ignores<br>❌ Launches into recommendations |
| CONV-001c | "Not sure what I need" | Asks clarifying questions naturally | ❌ "CLARIFICATION NEEDED:" header<br>❌ Bullet-point interrogation |

---

### Test Case CONV-002: Context Retention
**Objective:** Verify multi-turn conversations work

| Turn | Message | Expected Behavior | Acceptance Criteria |
|------|---------|-------------------|---------------------|
| 1 | "I need to deploy Llama 2 7B" | Searches HF, compute, provides plan | ✅ Initial recommendation |
| 2 | "What about on Azure?" | Remembers Llama 2 7B, searches Azure compute | ✅ Doesn't re-ask model<br>✅ Focuses on Azure |
| 3 | "Under $500/month" | Applies budget to previous context | ✅ Filters previous results<br>✅ Updates recommendation |

---

## 7. Tool Logging Verification

### Test Case LOG-001: Tool Visibility
**Objective:** Verify new logging feature works (post-enhancement)

**Test Method:** Check terminal output during tool calls

**Acceptance Criteria:**
- ✅ Tool name clearly logged: `🛠️ [TOOL CALL] search_compute_instances`
- ✅ Arguments shown:
  ```
  [ARGUMENTS]
    • gpu_needed: True
    • min_vram_gb: 16
  ```
- ✅ Output preview shown (first 3 results + metadata)
- ✅ Success/failure status logged
- ✅ Delimiter lines make output readable

**Test Queries:**
1. "Find me an A100 GPU" → Check compute tool logs
2. "Search for Prometheus" → Check K8s tool logs
3. "Find Llama models" → Check HF tool logs

---

## 8. Performance & Efficiency

### Test Case PERF-001: Minimal Tool Calls
**Objective:** Verify agent doesn't spam tools

| Scenario | User Query | Max Tool Calls | Acceptance Criteria |
|----------|-----------|---------------|---------------------|
| PERF-001a | "Find me a GPU" | 1 | ✅ Single compute call<br>✅ Doesn't re-query |
| PERF-001b | "Compare 3 cloud providers" | 3 | ✅ One call per provider<br>✅ No redundant calls |
| PERF-001c | "What's Kubernetes?" | 0 | ✅ No tool call needed<br>✅ Direct answer |

---

## 9. Edge Cases & Error Handling

### Test Case EDGE-001: Empty Results
**Objective:** Handle no-result scenarios gracefully

| Scenario | Tool Call | Expected Results | Expected Response |
|----------|-----------|-----------------|-------------------|
| EDGE-001a | `search_compute_instances(min_vram_gb=9999)` | 0 results | "No instances found with 9999GB VRAM. Consider multi-GPU..." |
| EDGE-001b | `search_k8s_packages("xyznonexistent")` | 0 results | "No K8s packages found. Did you mean...?" |
| EDGE-001c | `search_hf_models("nonsense12345")` | 0 results | "No models found. Try broader terms..." |

---

### Test Case EDGE-002: Ambiguous Queries
**Objective:** Handle vague requests well

| Scenario | User Query | Expected Behavior | Acceptance Criteria |
|----------|-----------|-------------------|---------------------|
| EDGE-002a | "I need compute" | Asks clarifying questions OR shows both CPU/GPU | ✅ Doesn't assume GPU<br>✅ Helpful follow-up |
| EDGE-002b | "Help me deploy" | Asks what they want to deploy | ✅ Polite clarification<br>✅ No guessing |

---

## 10. System Prompt Compliance

### Test Case PROMPT-001: Emoji Usage
**Objective:** Verify "sparingly" means sparingly

| Scenario | Response | Acceptance Criteria |
|----------|----------|---------------------|
| PROMPT-001a | Any response | ✅ Max 2-3 emojis total<br>✅ Not every line<br>✅ Adds to readability |

---

### Test Case PROMPT-002: Conciseness
**Objective:** Verify responses aren't walls of text

| Scenario | Response | Acceptance Criteria |
|----------|----------|---------------------|
| PROMPT-002a | Any recommendation | ✅ Short paragraphs<br>✅ Max 5 bullets per section<br>✅ Scannable format |

---

## Quick Test Script

### Priority 1 Tests (Must Pass)
```
1. K8S-001a: "I need monitoring for Kubernetes"
2. COMPUTE-001a: "Deploy a REST API for scikit-learn" (CPU test)
3. COMPUTE-001b: "Train YOLOv8" (GPU test)
4. HF-001a: "Find a text generation model"
5. MULTI-001a: "Deploy Llama 2 70B on GCP" (full workflow)
6. TRUTH-001a: "What's the price of GCP A100?" (no hallucination)
7. CONV-001a: "Hey, I need help" (natural style)
8. LOG-001: Check terminal for tool logs
```

### Priority 2 Tests (Should Pass)
```
9. COMPUTE-001c: "Need compute, not sure" (show both)
10. COMPUTE-001d: "PostgreSQL database" (CPU bias fix)
11. K8S-003a: Logging packages (official preference)
12. MULTI-002a: "What's Kubernetes?" (no tool spam)
13. TRUTH-002a: Handle "not found" gracefully
14. CONV-002: Multi-turn context retention
```

---

## Test Execution Checklist

**Before Testing:**
- [ ] Backend server restarted after latest changes
- [ ] Terminal visible to check tool logs
- [ ] Test user logged in (if testing chat persistence)

**During Testing:**
- [ ] Note which tool(s) are called
- [ ] Check tool arguments match query intent
- [ ] Verify response accuracy against tool results
- [ ] Check terminal logs for detailed tool output
- [ ] Assess conversational quality

**After Testing:**
- [ ] Document any failures with screenshots
- [ ] Note unexpected behaviors
- [ ] Suggest improvements

---

## Success Metrics

**Tool Accuracy:**
- ✅ 95%+ tool selection correctness (right tool for the query)
- ✅ 100% grounding (no made-up prices/stats/availability)

**CPU/GPU Balance:**
- ✅ CPU recommendations for appropriate workloads
- ✅ GPU recommendations for deep learning
- ✅ Both shown when ambiguous

**Conversational Quality:**
- ✅ Natural, human-like responses
- ✅ Not overly formal or templated
- ✅ Context retained across turns

**Logging:**
- ✅ Tool calls visible in terminal
- ✅ Arguments and output preview shown
- ✅ Readable format

---

## Notes
- These tests should be run after any changes to tools or system prompt
- Tests can be automated with scripts (see `test_ai_architect.py`)
- Document edge cases discovered during user testing
- Update scenarios as new features are added


