# Kenny Gem Finder - Testing Guide

This guide explains how to test and refine the AI search process.

---

## 🚀 Quick Start - Pretty Print Search Results

The easiest way to test search results and refine the output:

### Method 1: Standalone Script (Easiest)

```bash
# Edit the QUERY variable in the script
nano test_search_pretty.py  # Change QUERY = "chef knife" to whatever you want

# Run it
python test_search_pretty.py
```

**Output:**
- Pretty-formatted console output showing all products
- Quality checks (product counts, characteristics, materials)
- Full JSON saved to `/tmp/kenny_search_<query>.json`

**Cost:** ~$0.10-0.20 per search (Tavily + OpenAI)
**Time:** 30-60 seconds

---

### Method 2: Pytest (More Control)

```bash
# Run the pretty-print test
pytest test_search.py::TestIntegration::test_pretty_print_search_results -v -s

# Change the test_query in the test to try different products
```

The `-s` flag shows all print output.

---

## 🧪 Unit Tests (Fast, Free)

Run fast unit tests that don't call external APIs:

```bash
# All fast tests (0.3 seconds)
pytest test_search.py -v -m "not slow"

# Specific test
pytest test_search.py::TestSimpleKennySearch::test_generate_durability_queries -v
```

**What's tested:**
- ✅ Query generation (13 durability-focused queries)
- ✅ Alternative solutions generation
- ✅ Search result formatting
- ✅ Reddit vs expert review counting
- ✅ Configuration checks (search depth, tokens, temperature)
- ✅ Minimum product requirements

---

## 💰 Integration Tests (Slow, Costs Money)

Run tests that call real APIs:

```bash
# All tests including integration (costs money!)
pytest test_search.py -v

# Specific integration test
pytest test_search.py::TestIntegration::test_real_search_cast_iron -v -s
```

**Warning:** These tests cost $0.10-0.20 each and take 30-60 seconds.

---

## 📊 Refining Search Output

### Common Issues and How to Fix Them

#### Issue: Not enough products (< 9)

**Fix:** Update the prompt in `simple_search.py`:

```python
# Make the requirement even more explicit
CRITICAL REQUIREMENT: You MUST return EXACTLY 3 products per tier (9 total).
Do not return fewer products. If you only find 2 products in a tier, infer
a third product based on the search results.
```

#### Issue: Missing characteristics

**Check:** Are characteristics being extracted?

```bash
python test_search_pretty.py
# Look for: "⚠️  NO CHARACTERISTICS EXTRACTED"
```

**Fix:** Strengthen the characteristics instructions:

```python
- characteristics (ABSOLUTELY CRITICAL - REQUIRED!): You MUST extract 5-8
  characteristics for EVERY product. This is not optional.
```

#### Issue: Missing materials

**Check:** Look for "⚠️  NO MATERIALS EXTRACTED" in test output

**Fix:** Add materials to the prompt:

```python
- materials (REQUIRED): Extract materials from product specs. Examples:
  "Cast iron", "Stainless steel", "Carbon steel", "Ceramic", "Aluminum"
```

#### Issue: Poor quality descriptions

**Check:** Read the "Why It's a Gem" sections in test output

**Fix:** Add examples to the prompt:

```python
Good example: "Lodge skillets are known for their exceptional heat retention
and virtually indestructible construction. Multiple Reddit users report using
theirs for 10+ years with no degradation."

Bad example: "It's good quality and durable."
```

---

## 🔧 Testing Workflow

1. **Make prompt changes** in `simple_search.py`

2. **Test quickly** with the standalone script:
   ```bash
   python test_search_pretty.py
   ```

3. **Review output:**
   - Check product counts (should be 9+)
   - Check characteristics (all products should have 5-8)
   - Check materials (most products should have materials)
   - Read quality checks at the end

4. **Inspect full JSON** for details:
   ```bash
   cat /tmp/kenny_search_<query>.json | python -m json.tool | less
   ```

5. **Iterate** until output quality is good

6. **Run unit tests** to verify nothing broke:
   ```bash
   pytest test_search.py -v -m "not slow"
   ```

---

## 📁 Test Files

### `test_search.py`
- Full test suite (unit + integration)
- 13 tests total
- Run with `pytest test_search.py -v`

### `test_search_pretty.py`
- Standalone script for manual testing
- No pytest required
- Pretty-formatted output
- Quality checks included
- Run with `python test_search_pretty.py`

### Output Files

All test outputs are saved to `/tmp/`:
- `/tmp/kenny_search_<query>.json` - Full search results
- `/tmp/kenny-backend.log` - Backend server logs
- `/tmp/kenny-dev.log` - Frontend dev server logs

---

## 🎯 What Makes Good Search Output?

### ✅ Good Search Results

```
📦 PRODUCTS FOUND: 9 total
  💚 GOOD tier: 3 products
  💛 BETTER tier: 3 products
  ❤️  BEST tier: 3 products

Product 1: Lodge Cast Iron Skillet
  🏷️  Characteristics (6):
     • Pre-seasoned
     • Heavy bottom
     • 10-12 inch
     • Smooth interior
     • Oven safe
     • Helper handle

  🔧 Materials (1):
     • Cast iron

  📋 Practical Metrics:
     🧼 Cleaning time: 10 min
     ⚖️  Weight: 5.0 lbs
     🚿 Dishwasher safe: ❌
     🔥 Oven safe: ✅
```

### ❌ Poor Search Results

```
📦 PRODUCTS FOUND: 3 total
  💚 GOOD tier: 1 products  ← Not enough variety

Product 1: Cast Iron Pan
  🏷️  Characteristics (0):  ← Missing!
     ⚠️  NO CHARACTERISTICS EXTRACTED

  🔧 Materials (0):  ← Missing!
     ⚠️  NO MATERIALS EXTRACTED
```

---

## 💡 Tips

1. **Test different product categories:**
   - Kitchen: "chef knife", "dutch oven", "blender"
   - Appliances: "coffee maker", "toaster", "stand mixer"
   - Cookware: "wok", "saucepan", "baking sheet"

2. **Watch for patterns:**
   - Some categories may consistently lack materials
   - Some tiers may have fewer products
   - Characteristics quality varies by category

3. **Use the JSON for deep inspection:**
   ```bash
   # Pretty print with colors
   cat /tmp/kenny_search_chef_knife.json | jq . | less -R

   # Extract just characteristics
   cat /tmp/kenny_search_chef_knife.json | jq '.good_tier[].characteristics'
   ```

4. **Compare before/after:**
   - Save test outputs before making prompt changes
   - Run same query after changes
   - Compare outputs to see improvement

---

## 🐛 Troubleshooting

### "OpenAIError: API key not set"

```bash
# Make sure .env file has keys
cat .env | grep -E "OPENAI_API_KEY|TAVILY_API_KEY"

# Or set manually
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

### "Search taking too long (> 60s)"

This is expected. Search takes 30-60 seconds because:
- 4 sequential web searches (6-8s each)
- OpenAI analysis (15-25s)
- Network overhead

To speed up, see FEATURES_IMPLEMENTED.md section on parallelization.

### "Only getting 3 products"

Check if the prompt updates are actually being used:
```bash
# Verify changes are in the code
grep "MUST include at least 3 products" simple_search.py
```

If not found, your changes didn't save. Edit `simple_search.py` again.

---

## 📚 Further Reading

- `simple_search.py` - Main search implementation
- `DURABILITY_SCORE_FEATURE.md` - Durability scoring system
- `FEATURES_IMPLEMENTED.md` - Complete feature list
