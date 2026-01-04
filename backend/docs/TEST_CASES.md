# Stack8s AI Architect - Comprehensive Test Cases

**Purpose:** Verify the AI Architect is correctly understanding requirements, recommending compute, models, and Kubernetes components per the PRD requirements.

**Reference:** [Project Requirements Document - stack8s AI Architect (3).pdf](file:///e%3A/Stack8s/ProjectInfo/stack8s%20-%20AI%20Architect%20%283%29.pdf)

---

## Test Categories

1. **Intent Understanding** - Can the bot extract key requirements?
2. **Multi-turn Conversations** - Does it ask clarifying questions?
3. **GPU/Compute Recommendations** - Does it suggest appropriate hardware?
4. **Model Recommendations** - Does it suggest relevant models from HuggingFace?
5. **Kubernetes Stack Recommendations** - Does it suggest appropriate components?
6. **Deployment Plans** - Does it output complete architecture?
7. **Edge Cases** - How does it handle ambiguous or incomplete requests?

---

## Category 1: Intent Understanding (Basic)

### Test Case 1.1: Medical Imaging (PRD Example)
**Input:**
```
I have 2TB of MRI images and want to detect lung cancer. What GPUs should I choose? What architecture do I need?
```

**Expected Bot Behavior:**
- ✅ Identifies problem domain: Medical imaging
- ✅ Extracts dataset size: 2TB
- ✅ Recognizes task: Image classification/detection
- ✅ Asks clarifying questions:
  - Training from scratch or fine-tuning?
  - 2D or 3D MRI images?
  - HIPAA/GDPR compliance needed?
  - On-prem or cloud preference?

**Expected Recommendations Should Include:**
- GPU: H100, A100, or L40s for training
- Models: ViT, BioMedCLIP, MONAI
- Storage: MinIO or similar for 2TB dataset
- Pipeline: Argo Workflows or Kubeflow
- Compliance considerations if medical data

**Pass Criteria:**
- Bot identifies medical imaging domain ✅
- Bot asks at least 2-3 clarifying questions ✅
- Bot recommends appropriate GPU (A100/H100) ✅
- Bot suggests medical-specific models ✅

---

### Test Case 1.2: LLM Fine-tuning
**Input:**
```
I want to fine-tune a large language model on my company's documentation (50GB text). What do I need?
```

**Expected Bot Behavior:**
- ✅ Identifies task: LLM fine-tuning
- ✅ Extracts dataset: 50GB text
- ✅ Asks:
  - Which base model (Llama, Mixtral, Qwen)?
  - Full fine-tuning or LoRA/QLoRA?
  - Expected context length?
  - Budget constraints?

**Expected Recommendations:**
- GPU: A100 40GB/80GB or H100
- Models: Llama 3.1 7B/13B, Mistral, Qwen
- Framework: vLLM, DeepSpeed, or Hugging Face Transformers
- Storage: Object storage for dataset
- Training: Multi-GPU setup if larger models

**Pass Criteria:**
- Recognizes LLM fine-tuning task ✅
- Suggests appropriate GPU memory (40GB+) ✅
- Recommends relevant base models ✅
- Mentions LoRA/QLoRA as option ✅

---

### Test Case 1.3: Computer Vision - Object Detection
**Input:**
```
I need to build a real-time object detection system for autonomous vehicles. We have 10TB of dashcam footage.
```

**Expected Bot Behavior:**
- ✅ Identifies: Computer vision, real-time inference, large dataset
- ✅ Asks:
  - Training only or inference too?
  - Latency requirements (real-time = <100ms)?
  - Number of concurrent streams?
  - Edge deployment or cloud?

**Expected Recommendations:**
- Training GPU: A100 or H100
- Inference GPU: L4, T4, or A100 for low latency
- Models: YOLOv8, YOLOv9, or RT-DETR
- Framework: Triton Inference Server or TensorRT
- Pipeline: Argo Workflows for training
- Storage: Distributed storage for 10TB

**Pass Criteria:**
- Differentiates training vs inference needs ✅
- Recommends real-time capable models (YOLO) ✅
- Suggests inference optimization (Triton/TensorRT) ✅
- Mentions latency considerations ✅

---

## Category 2: Multi-turn Conversations

### Test Case 2.1: Progressive Refinement
**Conversation:**
```
User: I want to deploy an AI model.

Bot: [Should ask clarifying questions]

User: It's for text classification.

Bot: [Should narrow down recommendations]

User: I have 100k customer reviews to classify.

Bot: [Should provide specific recommendations]
```

**Expected Bot Behavior:**
- **Turn 1:** Asks about problem domain, data type, scale
- **Turn 2:** Asks about dataset size, languages, number of classes
- **Turn 3:** Provides specific GPU, model, and stack recommendations

**Pass Criteria:**
- Bot maintains context across turns ✅
- Questions become more specific over time ✅
- Final recommendation is tailored to all provided info ✅

---

### Test Case 2.2: Constraint Handling
**Conversation:**
```
User: I need to train a vision model but have a limited budget.

Bot: [Should ask about budget]

User: Maximum $500/month.

Bot: [Should suggest cost-effective options]

User: Can I use local GPU if I have one?

Bot: [Should check local availability and compare costs]
```

**Expected Bot Behavior:**
- Understands budget constraint
- Suggests T4 or L4 GPUs instead of H100
- Mentions spot instances
- Checks local cluster availability
- Compares local vs cloud costs

**Pass Criteria:**
- Bot respects budget constraint ✅
- Suggests cost-effective alternatives ✅
- Mentions local cluster option ✅
- Provides cost comparison ✅

---

## Category 3: GPU/Compute Recommendations

### Test Case 3.1: LLM Inference at Scale
**Input:**
```
I need to serve LLaMA 3.1 70B with 100 concurrent users, each with 4K context length.
```

**Expected Recommendations:**
- **GPU:** H100 80GB or A100 80GB (2-4 GPUs)
- **Memory calculation:** ~140GB for FP16, ~70GB for INT8
- **Framework:** vLLM with tensor parallelism
- **Load balancing:** Multiple replicas behind load balancer
- **Scaling:** Kubernetes HPA or KEDA
- **Cost estimate:** $X/hour based on cloud provider

**Pass Criteria:**
- Recommends 80GB+ VRAM GPUs ✅
- Mentions quantization options ✅
- Suggests vLLM for inference optimization ✅
- Addresses concurrency requirements ✅

---

### Test Case 3.2: Multi-GPU Training
**Input:**
```
I want to train a 13B parameter model from scratch. What multi-GPU setup do I need?
```

**Expected Recommendations:**
- **GPU:** 4-8x A100 40GB or 2-4x H100
- **Interconnect:** NVLink or InfiniBand for multi-node
- **Framework:** DeepSpeed ZeRO-3 or FSDP
- **Training time estimate:** Based on dataset size
- **Cost comparison:** Multi-cloud options

**Pass Criteria:**
- Recommends multi-GPU setup ✅
- Mentions GPU interconnect importance ✅
- Suggests distributed training frameworks ✅
- Provides multiple provider options ✅

---

### Test Case 3.3: Hybrid Cloud/Local
**Input:**
```
I have 2x A100 locally but need more GPUs for burst training. How should I architect this?
```

**Expected Recommendations:**
- **Primary:** Use local 2x A100 for base workload
- **Burst:** Cloud GPUs (same type preferred) for peaks
- **Orchestration:** Kubernetes federation or multi-cluster
- **Data:** Shared storage layer (S3-compatible)
- **Scheduling:** GPU time-sharing and queueing
- **Cost:** Only pay cloud costs during burst periods

**Pass Criteria:**
- Recognizes hybrid architecture need ✅
- Suggests local-first approach ✅
- Addresses data synchronization ✅
- Provides cost optimization strategy ✅

---

## Category 4: Model Recommendations

### Test Case 4.1: NLP Task
**Input:**
```
I need to build a customer support chatbot that understands technical questions.
```

**Expected Model Recommendations:**
- **Base Models:** Llama 3.1 8B, Mistral 7B, Qwen 7B
- **Fine-tuning:** LoRA on support tickets
- **Embedding:** For RAG retrieval (text-embedding-3-small)
- **Licensing:** Note commercial-friendly licenses
- **Size:** Smaller models (7-8B) for cost efficiency

**Pass Criteria:**
- Suggests appropriate size models (7-8B) ✅
- Mentions fine-tuning approach ✅
- Considers RAG architecture ✅
- Notes license compatibility ✅

---

### Test Case 4.2: Vision Model Selection
**Input:**
```
I need to classify satellite images into 20 categories. Dataset has 50k images.
```

**Expected Model Recommendations:**
- **Models:** ResNet-50, EfficientNet, ViT-Base
- **Pre-training:** ImageNet pre-trained models
- **Fine-tuning:** Transfer learning approach
- **Data augmentation:** Rotation, flip, color jitter
- **Validation:** K-fold cross-validation suggested

**Pass Criteria:**
- Recommends CNN or ViT models ✅
- Suggests transfer learning ✅
- Mentions data augmentation ✅
- Dataset size is appropriate for fine-tuning ✅

---

### Test Case 4.3: Multi-modal Task
**Input:**
```
I want to build a system that can answer questions about images.
```

**Expected Model Recommendations:**
- **Models:** CLIP, BLIP-2, LLaVA, GPT-4 Vision
- **Architecture:** Vision encoder + LLM decoder
- **Use case:** Visual Question Answering (VQA)
- **GPU:** A100 or H100 for larger models
- **Deployment:** Separate inference endpoints

**Pass Criteria:**
- Identifies multi-modal requirement ✅
- Suggests vision-language models ✅
- Explains architecture components ✅

---

## Category 5: Kubernetes Stack Recommendations

### Test Case 5.1: Complete ML Pipeline
**Input:**
```
I need a full ML training pipeline from data prep to model deployment.
```

**Expected Stack Components:**
- **Storage:** MinIO or S3-compatible
- **Pipeline:** Argo Workflows or Kubeflow Pipelines
- **Training:** PyTorch/TensorFlow operators
- **Model Registry:** MLflow or DVC
- **Serving:** Triton Inference Server or KServe
- **Monitoring:** Prometheus + Grafana
- **Logging:** Loki or EFK stack
- **GPU Scheduling:** NVIDIA GPU Operator

**Pass Criteria:**
- Covers data, training, serving, monitoring ✅
- All components are Kubernetes-native ✅
- Suggests integration patterns ✅
- Mentions observability ✅

---

### Test Case 5.2: Vector Database Integration
**Input:**
```
I'm building a RAG system and need to store embeddings for 10M documents.
```

**Expected Components:**
- **Vector DB:** Weaviate, Milvus, or pgvector
- **Embedding:** OpenAI or sentence-transformers
- **API Gateway:** Kong or Ambassador for rate limiting
- **Caching:** Redis for frequent queries
- **Search:** Hybrid search (vector + keyword)
- **Scaling:** Horizontal pod autoscaling

**Pass Criteria:**
- Recommends appropriate vector DB ✅
- Considers scale (10M vectors) ✅
- Mentions hybrid search ✅
- Addresses performance optimization ✅

---

### Test Case 5.3: Real-time Inference
**Input:**
```
I need to serve ML predictions with <50ms latency for 1000 requests/second.
```

**Expected Components:**
- **Inference:** Triton Inference Server with TensorRT
- **Load Balancer:** Nginx or Envoy
- **Autoscaling:** KEDA or HPA based on requests
- **GPU:** L4 or T4 for cost-effective inference
- **Caching:** Redis for repeated requests
- **Monitoring:** Latency tracking with Prometheus

**Pass Criteria:**
- Addresses latency requirement (<50ms) ✅
- Suggests optimization frameworks (TensorRT) ✅
- Recommends appropriate autoscaling ✅
- Includes caching strategy ✅

---

## Category 6: Deployment Plans

### Test Case 6.1: End-to-End Architecture
**Input:**
```
Give me a complete architecture for training and serving a text classification model.
```

**Expected Output:**
1. **Architecture Summary:**
   - Training: Batch processing on A100
   - Serving: Real-time inference on L4
   - Data: S3-compatible storage

2. **Components:**
   - Argo Workflows for training pipeline
   - MLflow for experiment tracking
   - Triton for serving
   - Prometheus for monitoring

3. **GPU Recommendations:**
   - Training: 1x A100 40GB ($2-3/hour)
   - Inference: 2x L4 ($0.50-0.75/hour each)

4. **Cost Estimate:**
   - Training: $X/month
   - Serving: $Y/month
   - Storage: $Z/month

5. **Deployment Steps:**
   - Install GPU operator
   - Deploy storage layer
   - Configure Argo Workflows
   - Deploy training job
   - Deploy inference service

**Pass Criteria:**
- Complete architecture diagram (text) ✅
- Separates training and inference ✅
- Provides cost breakdown ✅
- Includes deployment steps ✅

---

## Category 7: Edge Cases & Error Handling

### Test Case 7.1: Ambiguous Request
**Input:**
```
I need AI.
```

**Expected Bot Behavior:**
- Asks clarifying questions:
  - What problem are you solving?
  - What type of data do you have?
  - Training or inference?
  - Budget constraints?

**Pass Criteria:**
- Doesn't make assumptions ✅
- Asks specific questions ✅
- Guides user to provide more info ✅

---

### Test Case 7.2: Impossible Requirements
**Input:**
```
I want to train GPT-4 level model with $100 budget.
```

**Expected Bot Behavior:**
- Acknowledges constraint mismatch
- Explains why it's not feasible
- Suggests alternatives:
  - Fine-tune existing model instead
  - Use smaller model (7B instead of 175B)
  - Use API instead of self-hosting

**Pass Criteria:**
- Recognizes infeasibility ✅
- Explains constraints clearly ✅
- Offers practical alternatives ✅

---

### Test Case 7.3: Conflicting Requirements
**Input:**
```
I need the fastest GPU but have no budget.
```

**Expected Bot Behavior:**
- Points out the conflict
- Asks to prioritize: speed or cost?
- Offers middle-ground options:
  - Spot instances
  - Preemptible VMs
  - Time-sharing
  - Smaller model alternatives

**Pass Criteria:**
- Identifies conflict ✅
- Asks for prioritization ✅
- Suggests compromises ✅

---

## Test Suite Summary

### Minimum Passing Requirements

To be considered "working correctly" per PRD, the bot must pass:

#### Core Functionality (Must Pass All):
- ✅ Test 1.1 (Medical Imaging - PRD example)
- ✅ Test 1.2 (LLM Fine-tuning)
- ✅ Test 2.1 (Multi-turn conversation)
- ✅ Test 3.1 (GPU recommendations)
- ✅ Test 4.1 (Model recommendations)
- ✅ Test 5.1 (K8s stack recommendations)
- ✅ Test 6.1 (Complete deployment plan)

#### Additional Coverage (Pass 15/20):
- Intent Understanding: 3/3
- Multi-turn: 2/2
- GPU Recommendations: 3/3
- Model Recommendations: 3/3
- K8s Recommendations: 3/3
- Deployment Plans: 1/1
- Edge Cases: 2/3

---

## Automated Testing Script

You can run these tests using the provided Python script:

```bash
cd E:\Stack8s\backend
python scripts/test_ai_architect.py
```

Or test manually by chatting with the bot and checking responses against criteria.

---

## Scoring Rubric

For each test case:

| Score | Criteria |
|-------|----------|
| **5/5** | All pass criteria met, excellent response quality |
| **4/5** | Most criteria met, minor gaps in recommendations |
| **3/5** | Core functionality works, missing some details |
| **2/5** | Partial understanding, incomplete recommendations |
| **1/5** | Misunderstands intent or provides wrong recommendations |
| **0/5** | Bot fails to respond or crashes |

**Overall Pass:** Average score ≥ 4.0/5.0 across all test cases

---

## Next Steps

1. **Run Manual Tests:** Chat with bot using these prompts
2. **Document Results:** Note which tests pass/fail
3. **Create Automated Script:** Implement automated testing
4. **Iterate:** Fix issues and retest until all core tests pass

**Reference:** All test cases align with requirements in [stack8s AI Architect (3).pdf](file:///e%3A/Stack8s/ProjectInfo/stack8s%20-%20AI%20Architect%20%283%29.pdf)


