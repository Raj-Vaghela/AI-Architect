# Manual Test Checklist - Stack8s AI Architect

Quick reference for manual testing of tool acceptance criteria.

---

## ✅ Pre-Test Setup

- [ ] Backend server running (`python -m app.main`)
- [ ] Terminal visible to see tool logs
- [ ] Frontend running (if testing full UI)
- [ ] Test user logged in (if testing auth features)

---

## 🎯 Critical Tests (Must Pass)

### Test 1: CPU vs GPU - CPU Workload
**Query:** `"I need to deploy a REST API for my scikit-learn model"`

**Expected:**
- [ ] Tool called: `search_compute_instances`
- [ ] Terminal shows: `gpu_needed: False` (or omitted)
- [ ] Response recommends CPU instances
- [ ] No A100/H100/T4 mentioned

**Result:** ⬜ PASS | ⬜ FAIL

**Notes:**
```



```

---

### Test 2: CPU vs GPU - GPU Workload
**Query:** `"I want to train a YOLOv8 computer vision model"`

**Expected:**
- [ ] Tool called: `search_compute_instances`
- [ ] Terminal shows: `gpu_needed: True`
- [ ] Response recommends GPU instances (T4, A100, etc.)
- [ ] Mentions VRAM or GPU specs

**Result:** ⬜ PASS | ⬜ FAIL

**Notes:**
```



```

---

### Test 3: CPU vs GPU - Database (CPU)
**Query:** `"I need to run a PostgreSQL database"`

**Expected:**
- [ ] Tool called: `search_compute_instances`
- [ ] Terminal shows: `gpu_needed: False` (or omitted)
- [ ] Response focuses on RAM and CPU
- [ ] No GPU recommendations

**Result:** ⬜ PASS | ⬜ FAIL

**Notes:**
```



```

---

### Test 4: Kubernetes Tool - Monitoring
**Query:** `"I need a monitoring solution for Kubernetes"`

**Expected:**
- [ ] Tool called: `search_k8s_packages`
- [ ] Terminal shows arguments with "monitoring" or similar
- [ ] Response mentions Prometheus, Grafana
- [ ] Explains what they do

**Result:** ⬜ PASS | ⬜ FAIL

**Notes:**
```



```

---

### Test 5: HuggingFace Tool - Text Generation
**Query:** `"Find me a good text generation model"`

**Expected:**
- [ ] Tool called: `search_hf_models`
- [ ] Terminal shows: `pipeline_tag: text-generation`
- [ ] Response lists models (Llama, Mistral, Phi, etc.)
- [ ] Shows downloads or popularity metrics

**Result:** ⬜ PASS | ⬜ FAIL

**Notes:**
```



```

---

### Test 6: Multi-Tool - End-to-End
**Query:** `"I want to deploy Llama 2 70B for inference on GCP"`

**Expected:**
- [ ] Tool called: `search_hf_models` (for Llama 2 70B)
- [ ] Tool called: `search_compute_instances` (for GCP GPUs)
- [ ] Terminal shows: `provider: gcp`
- [ ] Response is coherent deployment plan
- [ ] Mentions VRAM requirements (~140GB)

**Result:** ⬜ PASS | ⬜ FAIL

**Notes:**
```



```

---

### Test 7: No Tool Call - Informational
**Query:** `"What is Kubernetes?"`

**Expected:**
- [ ] NO tool calls (check terminal)
- [ ] Direct informational answer
- [ ] Explains K8s concept
- [ ] Conversational tone

**Result:** ⬜ PASS | ⬜ FAIL

**Notes:**
```



```

---

### Test 8: Tool Logging - Visibility
**Query:** `"Find me an A100 GPU"`

**Check Terminal Output:**
- [ ] `🛠️ [TOOL CALL] search_compute_instances` visible
- [ ] `[ARGUMENTS]` section shows parameters
- [ ] `[OUTPUT]` section shows results preview
- [ ] `✓ [SUCCESS]` or error message shown
- [ ] Delimiter lines (`===`) make it readable

**Result:** ⬜ PASS | ⬜ FAIL

**Notes:**
```



```

---

## 🔍 Secondary Tests (Should Pass)

### Test 9: Price Filtering
**Query:** `"I need a GPU under $200/month"`

**Expected:**
- [ ] Terminal shows: `max_price_monthly: 200`
- [ ] Response only shows options under budget
- [ ] Recommends T4 or L4 (cost-effective)

**Result:** ⬜ PASS | ⬜ FAIL

---

### Test 10: Provider Filtering
**Query:** `"Show me AWS GPU options"`

**Expected:**
- [ ] Terminal shows: `provider: aws`
- [ ] Response only mentions AWS instances
- [ ] No GCP or Azure in results

**Result:** ⬜ PASS | ⬜ FAIL

---

### Test 11: K8s - Database Packages
**Query:** `"Help me set up a database in Kubernetes"`

**Expected:**
- [ ] Tool called: `search_k8s_packages`
- [ ] Response mentions PostgreSQL, MySQL, MongoDB
- [ ] Suggests Bitnami or official charts

**Result:** ⬜ PASS | ⬜ FAIL

---

### Test 12: K8s - Ingress
**Query:** `"I need an ingress controller"`

**Expected:**
- [ ] Tool called: `search_k8s_packages`
- [ ] Response recommends NGINX Ingress or Traefik
- [ ] Explains ingress role

**Result:** ⬜ PASS | ⬜ FAIL

---

### Test 13: HF - License Awareness
**Query:** `"Find me a commercial-friendly LLM"`

**Expected:**
- [ ] Tool called: `search_hf_models`
- [ ] Response mentions Apache-2.0, MIT licenses
- [ ] Warns about restrictive licenses

**Result:** ⬜ PASS | ⬜ FAIL

---

### Test 14: Conversational - Greeting
**Query:** `"Hey, I need help deploying a model"`

**Expected:**
- [ ] Friendly, natural response
- [ ] NOT rigid "RECOMMENDATION:" format
- [ ] Asks follow-up questions naturally

**Result:** ⬜ PASS | ⬜ FAIL

---

### Test 15: Context Retention - Multi-Turn
**Turn 1:** `"I need to deploy Llama 2 7B"`
**Turn 2:** `"What about on Azure?"`
**Turn 3:** `"Under $500/month"`

**Expected:**
- [ ] Turn 2: Remembers Llama 2 7B, searches Azure compute
- [ ] Turn 3: Applies budget filter to Azure results
- [ ] Doesn't re-ask about the model

**Result:** ⬜ PASS | ⬜ FAIL

---

## 🚨 Edge Cases

### Test 16: Empty Results
**Query:** `"Find me a GPU with 9999GB VRAM"`

**Expected:**
- [ ] Tool called (tries to search)
- [ ] Response: "No instances found with those specs"
- [ ] Suggests alternatives or multi-GPU

**Result:** ⬜ PASS | ⬜ FAIL

---

### Test 17: Ambiguous Query
**Query:** `"I need compute"`

**Expected:**
- [ ] Asks clarifying question OR shows both CPU/GPU
- [ ] Doesn't assume GPU automatically
- [ ] Helpful follow-up

**Result:** ⬜ PASS | ⬜ FAIL

---

## 🎨 Quality Checks

### Conversational Style
- [ ] Responses feel natural (not templated)
- [ ] Emojis used sparingly (2-3 max per response)
- [ ] Short paragraphs, scannable format
- [ ] Max 5 bullets per section

### Truthfulness
- [ ] No made-up prices (must come from tool)
- [ ] No made-up availability (must come from tool)
- [ ] Admits when unsure ("not found in results")
- [ ] Qualifies recommendations ("popular choices include...")

### Technical Accuracy
- [ ] VRAM estimates labeled as estimates
- [ ] Licenses cited from tool results
- [ ] Provider/region filters work correctly
- [ ] CPU vs GPU logic correct

---

## 📊 Test Summary

**Date:** _______________

**Tester:** _______________

**Results:**
- Critical Tests Passed: ____ / 8
- Secondary Tests Passed: ____ / 7
- Edge Cases Passed: ____ / 2
- Quality Checks: ____ / 12

**Overall Pass Rate:** _____% (_____ / 29)

**Critical Issues Found:**
```




```

**Nice-to-Have Improvements:**
```




```

**Notes:**
```




```

---

## 🔧 Troubleshooting

**If tool logs aren't showing:**
- Check if backend was restarted after latest changes
- Verify `unified_agent.py` has the updated `run_tool` function
- Check console output for errors

**If wrong tool is called:**
- Review system prompt in `unified_agent.py`
- Check tool descriptions in `ALL_TOOLS`
- Verify agent has correct context

**If responses are too "templatey":**
- Check if `get_system_prompt` was updated
- Backend may need restart
- Review exact wording of responses

**If CPU/GPU bias still exists:**
- Verify `gpu_needed` is not in `required` array
- Check tool description mentions both CPU and GPU
- Restart backend server

---

## ✅ Sign-Off

**Acceptance Criteria Met:**
- [ ] All Priority 1 tests passing (8/8)
- [ ] At least 85% of all tests passing (25/29)
- [ ] No critical issues
- [ ] Tool logging working
- [ ] CPU/GPU balance correct

**Approved By:** _______________

**Date:** _______________

**Ready for Production:** ⬜ YES | ⬜ NO (issues noted above)


