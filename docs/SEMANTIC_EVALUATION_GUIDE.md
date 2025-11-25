# Semantic Evaluation Guide

**Goal:** Validate that generated intents are semantically correct, not just schema-valid

---

## 🎯 The Problem

**Current Validation:** Schema correctness only
- ✅ Valid JSON format
- ✅ Correct characteristic names
- ✅ Valid units
- ❌ **NOT checking if values match requirements!**

**Example Problem:**

**Scenario:** "Network needs <10ms latency for surgery"

**Generated Intent (Schema-valid but WRONG):**
```json
{
  "serviceCharacteristic": [{
    "name": "Delay tolerance",
    "value": "100",  // ❌ Should be 10, not 100!
    "unit": "ms"
  }]
}
```

This would pass our current validation (100%) but is semantically WRONG.

---

## 📊 How to Perform Semantic Evaluation

### Step 1: Generated Sample ✅ DONE

**File:** `semantic_eval_sample.csv`
- 20 scenarios sampled (16 successes, 4 failures)
- Stratified to include both easy and hard cases

### Step 2: Human Review (YOU DO THIS)

Open `semantic_eval_sample.csv` and for each row:

**Review:**
1. **Scenario** - Original requirement
2. **Generated Intent JSON** - What the LLM produced
3. **Automated Valid** - Schema validation result

**Evaluate:**
- Does the intent **semantically match** the scenario?
- Are the **values correct**? (e.g., 10ms not 100ms)
- Are the **characteristics appropriate**?
- Is the **meaning preserved**?

**Fill in:**
- `human_valid`: `TRUE` or `FALSE`
- `semantic_errors`: Describe issues (e.g., "latency value too high")
- `notes`: Any observations

### Step 3: Analysis

After annotation, run:
```bash
python scripts/analyze_human_eval.py
```

This computes:
- **Precision:** When automated says valid, how often is it truly valid?
- **Recall:** Of truly valid intents, how many did automation catch?
- **False Positives:** Automated✅ but Human❌ (schema-valid but semantically wrong)
- **False Negatives:** Automated❌ but Human✅ (schema errors but semantically correct)

---

## 📋 Example Evaluation

### Example 1: Correct

**Scenario:** "Support IoT with 100 Mbps bandwidth"

**Generated:**
```json
{
  "serviceCharacteristic": [{
    "name": "DL_throughput",
    "value": "100",
    "unit": "Mbps"
  }]
}
```

**Evaluation:**
- ✅ Correct characteristic (DL_throughput)
- ✅ Correct value (100)
- ✅ Correct unit (Mbps)
- **human_valid:** `TRUE`

### Example 2: Schema-valid but Semantically Wrong

**Scenario:** "Low latency for autonomous vehicles <5ms"

**Generated:**
```json
{
  "serviceCharacteristic": [{
    "name": "Delay tolerance",
    "value": "50",  // ❌ Should be 5, not 50!
    "unit": "ms"
  }]
}
```

**Evaluation:**
- ✅ Valid schema
- ✅ Correct name
- ✅ Correct unit
- ❌ **WRONG VALUE** (50ms instead of 5ms)
- **human_valid:** `FALSE`
- **semantic_errors:** "Value is 10x too high (50ms vs 5ms)"

### Example 3: Missing Requirements

**Scenario:** "Network for smart city with low latency <10ms and high bandwidth 1Gbps"

**Generated:**
```json
{
  "serviceCharacteristic": [{
    "name": "Delay tolerance",
    "value": "10",
    "unit": "ms"
  }]
  // ❌ Missing bandwidth requirement!
}
```

**Evaluation:**
- ✅ Latency is correct
- ❌ **Missing bandwidth** requirement
- **human_valid:** `FALSE`
- **semantic_errors:** "Missing second requirement (1Gbps bandwidth)"

---

## 🎓 Why This Matters for Publication

### Current Claim
"95.3% accuracy" - **But this is schema validation only!**

### After Semantic Evaluation
"95.3% schema accuracy, X% semantic accuracy"

**Possible outcomes:**
- **Best case:** 95% semantic accuracy (nearly perfect!)
- **Realistic:** 80-90% semantic accuracy (some value errors)
- **Worst case:** <80% (many semantic errors)

### Publication Impact

**Before human eval:**
- Reviewers: "Schema-valid ≠ correct, where's human evaluation?"
- **Weakness:** Can't prove semantic correctness

**After human eval:**
- "95.3% schema accuracy, 87% semantic accuracy (κ=0.85 inter-annotator)"
- **Strength:** Rigorous validation of meaning, not just format

---

## 🚀 Next Steps

### For Quick Assessment (20 samples)
1. Open `semantic_eval_sample.csv`
2. You review 20 scenarios (~15 minutes)
3. Fill in `human_valid`, `semantic_errors`, `notes`
4. Save as `semantic_eval_completed.csv`
5. Run `python scripts/analyze_human_eval.py`

### For Publication (100 samples)
1. Generate 100-sample template
2. Get 3 independent annotators
3. Compute inter-annotator agreement (Cohen's Kappa)
4. Report automated vs human metrics

---

## 📊 Expected Results

Based on the 95.3% schema accuracy:

**Optimistic:** 90%+ semantic accuracy
- Most errors are JSON extraction (not semantic)
- RAG provides good context

**Realistic:** 80-90% semantic accuracy
- Some value mismatches
- Some missing requirements

**If <80%:** Need to improve prompting
- Add explicit value extraction instructions
- Improve RAG context

---

## ✅ Ready to Start

**File created:** `semantic_eval_sample.csv` (20 scenarios)

**Your action:** Review and annotate

**Time required:** ~15-20 minutes for 20 samples

**This will give us TRUE accuracy, not just schema validation!**

Want me to show you an example from the sample file?
