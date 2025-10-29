# Contextual AI-Driven Search Approach

## Overview

We've completely redesigned the search architecture from **hardcoded query templates** to **AI-generated contextual queries** based on the Just-In-Time framework with attribute dependency reasoning.

---

## The Problem with Hardcoded Queries

**Old Approach (simple_search.py):**
```python
# Hardcoded templates - same for every product
queries = [
    f"{product_name} recommendations reddit buy it for life",
    f"{product_name} how long does it last",
    f"{product_name} durability longevity reddit",
    # ... 10 more hardcoded templates
]
```

**Issues:**
- ❌ No context awareness (doesn't consider user's actual needs)
- ❌ One-size-fits-all approach
- ❌ Misses attribute dependencies (e.g., cooking method → material requirements)
- ❌ Can't identify marketing gimmicks vs real problems

---

## New Approach: 5-Phase Contextual Research

### Phase 1: Context Discovery
**Goal:** Understand how people actually use this product

**AI-Generated Queries Example:**
```
"how do people actually use cast iron skillet reddit"
"cast iron skillet daily cooking vs occasional use"
"cast iron skillet electric stove vs gas limitations"
```

**What We Learn:**
- Living situation constraints (kitchen setup, stove type)
- Usage patterns (daily vs occasional, cooking style)
- Existing tools and compatibility

### Phase 2: Material Science
**Goal:** Determine optimal materials based on context

**AI-Generated Queries Example:**
```
"cast iron vs carbon steel vs stainless steel skillet durability"
"what material skillet for metal utensils high heat"
"cast iron skillet material properties seasoning maintenance"
```

**What We Learn:**
- Material compatibility with cooking methods
- Durability characteristics
- Maintenance requirements
- **Attribute dependency:** cooking method + tools → material requirements

### Phase 3: Product Identification
**Goal:** Find products built with optimal materials (not just "most popular")

**AI-Generated Queries Example:**
```
"best cast iron skillet brands professional chefs reddit"
"buy it for life cast iron skillet recommendations"
"cast iron skillet lodge vs field company vs stargazer"
```

**What We Find:**
- Products correctly built for the use case
- Professional recommendations
- Specific brands and models

### Phase 4: Frustration Research
**Goal:** Discover real pain points from long-term users

**AI-Generated Queries Example:**
```
"cast iron skillet common problems failures reddit"
"cast iron skillet marketing gimmicks unnecessary features"
"what features don't matter cast iron skillet"
```

**What We Discover:**
- Real problems from actual users
- Marketing gimmicks (helper handles, "pre-seasoning gimmicks")
- Features that don't solve real problems

### Phase 5: Value Synthesis
**Goal:** Long-term ownership reality

**AI-Generated Queries Example:**
```
"cast iron skillet owned 10 years review"
"cast iron skillet true cost of ownership maintenance"
"is expensive cast iron worth it vs cheap"
```

**What We Learn:**
- Long-term experiences
- True cost of ownership
- Repair and maintenance reality

---

## How It Works

### Step 1: AI Generates Strategic Queries

```python
# Instead of templates, we ask AI to reason:
prompt = f"""Generate strategic search queries for {product_name}.

Use the 5-phase research framework:
1. CONTEXT DISCOVERY (2-3 queries)
2. MATERIAL SCIENCE (2-3 queries)
3. PRODUCT IDENTIFICATION (2-3 queries)
4. FRUSTRATION RESEARCH (2-3 queries)
5. VALUE SYNTHESIS (1-2 queries)

Return JSON with phase-organized queries."""

queries_by_phase = await ai.generate_queries(product_name, user_context)
```

### Step 2: Execute Queries by Phase (Parallel)

```python
# Run all phases concurrently for speed
results_by_phase = await execute_queries_by_phase(queries_by_phase)

# Results organized by research phase:
{
  "context_discovery": [source1, source2, ...],
  "material_science": [source1, source2, ...],
  "product_identification": [source1, source2, ...],
  "frustration_research": [source1, source2, ...],
  "value_synthesis": [source1, source2, ...]
}
```

### Step 3: Context-Aware Synthesis

```python
# AI synthesizes with full context:
synthesis_prompt = f"""Based on multi-phase research:

=== CONTEXT DISCOVERY ===
{context_results}

=== MATERIAL SCIENCE ===
{material_results}

=== PRODUCT IDENTIFICATION ===
{product_results}

=== FRUSTRATION RESEARCH ===
{frustration_results}

=== VALUE SYNTHESIS ===
{value_results}

Recommend products that:
1. Match the user's specific context
2. Use optimal materials for their use case
3. Avoid known frustrations
4. Provide long-term value"""
```

---

## Example: Cast Iron Skillet Search

### AI-Generated Research Plan

**Context Discovery (2 queries):**
1. "how do people actually use cast iron skillet cooking method frequency"
2. "cast iron skillet electric vs gas stove induction compatibility"

**Material Science (2 queries):**
1. "cast iron vs enameled cast iron vs carbon steel skillet durability comparison"
2. "cast iron skillet material properties heat retention seasoning"

**Product Identification (2 queries):**
1. "best cast iron skillet brands professional recommendations reddit buy it for life"
2. "lodge vs field company vs stargazer cast iron skillet comparison"

**Frustration Research (2 queries):**
1. "cast iron skillet common problems failures rust cracking"
2. "unnecessary features cast iron skillet marketing gimmicks"

**Value Synthesis (2 queries):**
1. "cast iron skillet owned 10 years still working review"
2. "cast iron skillet true cost maintenance seasoning time investment"

### Context-Aware Results

**Context Insights:**
```json
{
  "use_case_summary": "Daily cooking, occasional searing, induction-compatible needed",
  "key_constraints": ["metal utensils OK", "dishwasher unsafe", "heavy"],
  "optimal_materials": ["pre-seasoned cast iron", "enameled cast iron for acidic foods"],
  "material_reasoning": "Cast iron for daily use + high heat tolerance. Pre-seasoning reduces setup time. Enameled option for tomato-based dishes."
}
```

**Products with Context Fit:**
```json
{
  "name": "Lodge Cast Iron Skillet",
  "materials": ["cast iron", "pre-seasoned"],
  "context_fit": "Excellent for daily high-heat cooking with metal utensils. Pre-seasoned reduces 30min setup. Not dishwasher safe but easy hand-wash.",
  "frustrations_avoided": [
    "Skip: helper handles (adds weight, rarely used)",
    "Skip: pour spouts (don't seal well, hard to clean)"
  ]
}
```

---

## Benefits vs Old Approach

| Aspect | Old (Hardcoded) | New (Contextual) |
|--------|-----------------|------------------|
| **Query Generation** | Static templates | AI-driven, context-aware |
| **Context Awareness** | ❌ None | ✅ Based on use case |
| **Material Reasoning** | ❌ Not considered | ✅ Attribute dependency |
| **Frustration Discovery** | ✅ Generic | ✅ Specific to product |
| **Marketing Filter** | ❌ No | ✅ Identifies gimmicks |
| **Recommendations** | Generic | Context-matched |

---

## Testing

### Test the New Approach

```bash
# Run contextual search test
cd /Users/wenyichen/kenny-gem-finder/backend
source venv/bin/activate
python test_contextual_search.py "chef knife"
```

### Compare Old vs New

```bash
# Old approach (hardcoded queries)
python test_search_pretty.py

# New approach (AI-generated queries)
python test_contextual_search.py "chef knife"
```

---

## Implementation Files

- **`contextual_search.py`** - Main implementation
- **`test_contextual_search.py`** - Testing script
- **`main.py`** - Updated to use contextual search (line 296)

---

## Cost & Performance

### Query Generation
- **Old:** Free (hardcoded templates)
- **New:** ~$0.001 per search (GPT-4o-mini call)

### Total Search Time
- **Query generation:** ~1-2 seconds (AI call)
- **Web searches:** ~15-20 seconds (10 parallel queries with timeout)
- **Synthesis:** ~25-35 seconds (AI analysis)
- **Total:** ~40-55 seconds

### Cost Per Search
- **Query generation:** $0.001
- **Tavily searches:** $0.10 (10 queries × $0.01)
- **Synthesis:** $0.02 (GPT-4o-mini with 8k tokens)
- **Total:** ~$0.13 per search

---

## Philosophy

This approach embodies the **quality-first, anti-algorithm** framework:

1. ✅ **Not database search** - We reason about what the user needs
2. ✅ **Attribute dependency** - Understand how constraints interact
3. ✅ **Context-first** - Match products to actual use case
4. ✅ **Frustration-aware** - Filter marketing vs real problems
5. ✅ **Value-oriented** - Best for YOUR context, not just "most popular"

**Best valuable products = longest-lasting for YOUR specific context**

---

## Next Steps

1. **Test extensively** with different product types
2. **Gather feedback** on context accuracy
3. **Refine prompts** based on result quality
4. **Consider** adding optional context questions for users
5. **Measure** improvement in recommendation relevance
