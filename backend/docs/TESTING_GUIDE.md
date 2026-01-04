# Testing Guide - Stack8s AI Architect

This guide explains how to test the tool acceptance criteria for the Stack8s AI Architect bot.

---

## 📁 What's Been Created

### 1. **TEST_SCENARIOS.md** - Comprehensive Test Documentation
- **Location:** `backend/docs/TEST_SCENARIOS.md`
- **Contents:** 
  - 60+ detailed test scenarios organized by category
  - Kubernetes tool tests (K8S-001 to K8S-004)
  - Compute tool tests with CPU/GPU bias checks (COMPUTE-001 to COMPUTE-004)
  - HuggingFace tool tests (HF-001 to HF-003)
  - Multi-tool orchestration tests (MULTI-001 to MULTI-002)
  - Truthfulness and grounding tests (TRUTH-001 to TRUTH-002)
  - Conversational quality tests (CONV-001 to CONV-002)
  - Tool logging verification (LOG-001)
  - Edge cases and error handling (EDGE-001 to EDGE-002)

### 2. **test_tool_acceptance.py** - Automated Test Script
- **Location:** `backend/scripts/test_tool_acceptance.py`
- **Purpose:** Automated testing of critical scenarios
- **Features:**
  - Tests 12 priority scenarios automatically
  - Checks tool selection accuracy
  - Verifies CPU/GPU balance (post-fix)
  - Reports pass/fail with detailed output

### 3. **MANUAL_TEST_CHECKLIST.md** - Interactive Testing Checklist
- **Location:** `backend/docs/MANUAL_TEST_CHECKLIST.md`
- **Purpose:** Step-by-step manual testing with checkboxes
- **Includes:**
  - 8 critical tests (must pass)
  - 7 secondary tests (should pass)
  - 2 edge case tests
  - 12 quality checks
  - Space for notes and sign-off

---

## 🚀 Quick Start

### Option 1: Manual Testing (Recommended First)

1. **Start the backend:**
   ```powershell
   cd E:\Stack8s\backend
   .\venv\Scripts\Activate.ps1
   python -m app.main
   ```

2. **Open the checklist:**
   - Navigate to `backend/docs/MANUAL_TEST_CHECKLIST.md`
   - Print it or keep it open in a second window

3. **Open the frontend:**
   - Start your frontend dev server
   - Log in with a test account

4. **Run through the tests:**
   - Follow each test case in order
   - Check the terminal for tool logs
   - Mark ✅ or ❌ for each test
   - Take notes on any issues

5. **Review results:**
   - Calculate your pass rate
   - Document any critical issues
   - Note improvements needed

---

### Option 2: Automated Testing

1. **Start the backend:**
   ```powershell
   cd E:\Stack8s\backend
   .\venv\Scripts\Activate.ps1
   python -m app.main
   ```

2. **Run the test script** (in a new terminal):
   ```powershell
   cd E:\Stack8s\backend
   .\venv\Scripts\Activate.ps1
   python scripts\test_tool_acceptance.py
   ```

3. **Review output:**
   - Script will show progress for each test
   - Final summary shows pass/fail count
   - Exit code 0 = all passed, 1 = some failed

**Note:** The automated script uses heuristics (keyword matching) since it can't directly inspect tool calls. For definitive results, use manual testing with terminal log inspection.

---

## 🎯 Critical Tests to Focus On

### 1. **CPU/GPU Balance** (Post-Bias Fix)

These tests verify that the compute tool is no longer GPU-biased:

| Test | Query | Expected | Check |
|------|-------|----------|-------|
| COMPUTE-001a | "Deploy REST API for scikit-learn" | CPU instances | `gpu_needed: False` in logs |
| COMPUTE-001b | "Train YOLOv8 model" | GPU instances | `gpu_needed: True` in logs |
| COMPUTE-001d | "Run PostgreSQL database" | CPU instances | CPU focus, no GPU |

**Why Critical:** This was the primary issue you identified - 15x more CPUs in DB but agent was GPU-biased.

---

### 2. **Kubernetes Tool Accuracy**

| Test | Query | Expected Tool | Expected Result |
|------|-------|--------------|-----------------|
| K8S-001a | "Need monitoring for K8s" | `search_k8s_packages` | Prometheus, Grafana |
| K8S-001b | "Set up database in K8s" | `search_k8s_packages` | PostgreSQL, MySQL, MongoDB |
| K8S-002a | "Need ingress controller" | `search_k8s_packages` | NGINX Ingress |

**Why Critical:** Kubernetes tool is a core feature of the Stack8s platform.

---

### 3. **Multi-Tool Orchestration**

| Test | Query | Expected Tools | Expected Result |
|------|-------|---------------|-----------------|
| MULTI-001a | "Deploy Llama 2 70B on GCP" | HF + Compute | End-to-end plan |

**Why Critical:** Real user queries often require multiple tools working together.

---

### 4. **Tool Logging Visibility**

| Test | Query | Check Terminal | Expected |
|------|-------|---------------|----------|
| LOG-001 | "Find me an A100 GPU" | Tool call logs | Clear, formatted output |

**Why Critical:** This was your most recent enhancement request.

---

## 📊 Acceptance Criteria

### Minimum Requirements (Must Pass)

- ✅ **All 8 Critical Tests** (COMPUTE-001a/b/d, K8S-001a, HF-001a, MULTI-001a, TRUTH-001a, LOG-001)
- ✅ **CPU/GPU Balance:** CPU workloads get CPU recommendations
- ✅ **Tool Accuracy:** 95%+ correct tool selection
- ✅ **No Hallucination:** 100% grounding in tool results (no made-up prices/stats)
- ✅ **Logging Works:** Tool calls visible in terminal with args and output

### Quality Goals (Should Pass)

- ✅ **85%+ overall pass rate** (25/29 tests)
- ✅ **Conversational style:** Natural, not templated
- ✅ **Context retention:** Multi-turn conversations work
- ✅ **Edge cases handled:** Empty results, ambiguous queries

---

## 🔍 How to Verify Each Test

### Example: Test COMPUTE-001a (CPU for scikit-learn API)

1. **Send query:** "I need to deploy a REST API for my scikit-learn model"

2. **Check terminal for:**
   ```
   ==================== [TOOL CALL] ====================
   🛠️  [TOOL CALL] search_compute_instances
   ====================
   [ARGUMENTS]
      • gpu_needed: False
      (or gpu_needed not present)
   ```

3. **Check response for:**
   - CPU instances mentioned (e.g., "c6i.large", "n2-standard")
   - No A100/H100/T4 in recommendations
   - Focus on CPU cores and RAM, not VRAM

4. **Mark result:**
   - ✅ PASS if all criteria met
   - ❌ FAIL if GPU instances recommended or `gpu_needed: True`

---

## 🐛 Common Issues & Fixes

### Issue: Tool logs not showing
**Symptom:** Terminal doesn't show detailed tool calls  
**Fix:** Restart backend server after latest changes to `unified_agent.py`

### Issue: Still GPU-biased
**Symptom:** CPU workloads get GPU recommendations  
**Fix:** 
1. Check `unified_agent.py` - `gpu_needed` should NOT be in `required` array
2. Restart backend
3. Clear any cached responses

### Issue: Responses too "templatey"
**Symptom:** Rigid format, "RECOMMENDATION:", "CLARIFICATION:" headers  
**Fix:** 
1. Check `get_system_prompt()` in `unified_agent.py`
2. Should emphasize natural conversation
3. Restart backend

### Issue: Wrong tool called
**Symptom:** Searches HF when should search compute  
**Fix:** 
1. Review tool descriptions in `ALL_TOOLS`
2. Check system prompt for guidance
3. May need to refine tool descriptions

---

## 📈 Test Report Template

After completing tests, fill out this summary:

```
# Test Report

**Date:** _______________
**Tester:** _______________
**Backend Version/Commit:** _______________

## Results Summary
- Critical Tests: ___/8 passed
- Secondary Tests: ___/7 passed
- Edge Cases: ___/2 passed
- Overall: ___/29 (___%)

## Critical Issues
1. 
2. 
3. 

## Observations
- CPU/GPU balance: [Good / Needs Work]
- Tool selection accuracy: [Good / Needs Work]
- Conversational quality: [Good / Needs Work]
- Logging visibility: [Good / Needs Work]

## Recommendations
1. 
2. 
3. 

## Sign-Off
- [ ] Ready for production
- [ ] Needs fixes (see issues above)
```

---

## 🧪 Advanced Testing

### Testing Against Real User Scenarios

Use queries from the project document (`stack8s - AI Architect (3).pdf`):

1. "I need to deploy a Llama 2 model for internal use"
2. "What compute do I need for fine-tuning GPT-2?"
3. "Help me set up monitoring for my ML cluster"
4. "Find me a cost-effective GPU for inference"
5. "I want to run Stable Diffusion"

### Performance Testing

- **Response time:** Should be < 5s for single-tool queries
- **Token usage:** Monitor for excessive tokens
- **Tool call efficiency:** Max 1 retry per tool

### Stress Testing

- **Ambiguous queries:** "I need help" → Should ask clarifying questions
- **Conflicting requirements:** "Cheapest A100" → Should explain tradeoffs
- **Missing data:** "GPU in Antarctica" → Should handle gracefully

---

## 📚 Reference Documents

- **TEST_SCENARIOS.md**: Full test scenario details
- **MANUAL_TEST_CHECKLIST.md**: Interactive checklist
- **test_tool_acceptance.py**: Automated test script
- **unified_agent.py**: Agent implementation (to debug issues)

---

## 🎓 Tips for Effective Testing

1. **Test in order:** Start with Critical Tests, then Secondary, then Edge Cases
2. **Always check terminal:** Tool logs are crucial for debugging
3. **Take notes:** Document unexpected behaviors immediately
4. **Test multi-turn:** Don't just test single queries
5. **Test edge cases:** Ambiguous queries, typos, unreasonable requests
6. **Compare responses:** Same query should give consistent results
7. **Check grounding:** Verify all prices/stats come from tool results

---

## ✅ Final Checklist Before Sign-Off

- [ ] All Critical Tests passing (8/8)
- [ ] CPU workloads get CPU recommendations
- [ ] GPU workloads get GPU recommendations
- [ ] K8s tool returns relevant packages
- [ ] HF tool returns relevant models
- [ ] Multi-tool queries work end-to-end
- [ ] No hallucinated prices or availability
- [ ] Tool logging visible and readable
- [ ] Conversational style (not templated)
- [ ] Context retained across turns
- [ ] Edge cases handled gracefully
- [ ] Test report completed

**Ready for production:** ⬜ YES | ⬜ NO

---

## 🚦 Next Steps

After testing:

1. **Document results** in test report
2. **File issues** for any failures
3. **Prioritize fixes** (critical vs nice-to-have)
4. **Retest after fixes**
5. **Sign off** when all critical tests pass

---

## 📞 Support

If you encounter issues during testing:

1. Check the **Common Issues & Fixes** section above
2. Review the relevant test scenario in **TEST_SCENARIOS.md**
3. Inspect the agent code in **unified_agent.py**
4. Check backend logs for errors

---

**Last Updated:** Dec 31, 2025  
**Version:** 1.0  
**Author:** Stack8s Testing Team


