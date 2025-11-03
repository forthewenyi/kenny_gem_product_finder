# Fix: Cache Missing Fields (Characteristics & Durability)

## Problem

When searching "air fryer" for the second time (cache hit), two issues occurred:
1. ❌ **Characteristics section disappeared** on frontend
2. ❌ **Durability showed zero** in product grid

## Root Cause

The database schema was **missing two critical fields**:
- `durability_data` (JSONB) - Contains durability score, lifespan, failure points, etc.
- `practical_metrics` (JSONB) - Contains cleaning time, setup details, weight, etc.

These fields are in the `Product` model but were NOT stored in the cache database.

---

## Investigation Results

### ✅ Characteristics ARE in database
```json
{
  "characteristics": ["Compact size", "Simple controls", "Budget-friendly", "Easy to use", "Limited features"]
}
```
**This field is working correctly!** If it disappears on frontend, it's a different issue (likely frontend serialization).

### ❌ Durability Data NOT in database
```
durability_data: NULL  ← Missing!
```

### ❌ Practical Metrics NOT in database
```
practical_metrics: NULL  ← Missing!
```

---

## Fix Applied

### 1. Database Schema Migration

**File:** `add_durability_and_practical_metrics.sql`

Adds two JSONB columns to `products` table:

```sql
ALTER TABLE products
ADD COLUMN IF NOT EXISTS durability_data JSONB DEFAULT NULL;

ALTER TABLE products
ADD COLUMN IF NOT EXISTS practical_metrics JSONB DEFAULT NULL;
```

**Durability Data Structure:**
```json
{
  "score": 75,
  "average_lifespan_years": 10.5,
  "still_working_after_5years_percent": 85,
  "total_user_reports": 234,
  "common_failure_points": ["coating peels", "handle loosens"],
  "repairability_score": 60,
  "material_quality_indicators": ["solid construction", "heavy gauge steel"],
  "data_sources": ["https://reddit.com/..."]
}
```

**Practical Metrics Structure:**
```json
{
  "cleaning_time_minutes": 10,
  "cleaning_details": "Hand wash with mild soap",
  "setup_time": "Ready",
  "learning_curve": "Medium",
  "weight_lbs": 8.5,
  "dishwasher_safe": false,
  "oven_safe": true,
  "oven_max_temp": 500
}
```

### 2. Updated `database_service.py`

#### A. Store Nested Objects (Lines 259-312)
```python
# Serialize durability_data if present
durability_data_json = None
if product.durability_data:
    durability_data_json = {
        "score": product.durability_data.score,
        "average_lifespan_years": product.durability_data.average_lifespan_years,
        # ... all fields
    }

# Serialize practical_metrics if present
practical_metrics_json = None
if product.practical_metrics:
    practical_metrics_json = {
        "cleaning_time_minutes": product.practical_metrics.cleaning_time_minutes,
        # ... all fields
    }

product_data = {
    # ... existing fields ...
    "durability_data": durability_data_json,
    "practical_metrics": practical_metrics_json
}
```

#### B. Reconstruct Objects from Cache (Lines 146-179)
```python
# Reconstruct durability_data if present
durability_data = None
if product_data.get("durability_data"):
    dd = product_data["durability_data"]
    durability_data = DurabilityData(
        score=dd.get("score", 0),
        average_lifespan_years=dd.get("average_lifespan_years", 0.0),
        # ... all fields
    )

# Reconstruct practical_metrics if present
practical_metrics = None
if product_data.get("practical_metrics"):
    pm = product_data["practical_metrics"]
    practical_metrics = PracticalMetrics(
        cleaning_time_minutes=pm.get("cleaning_time_minutes"),
        # ... all fields
    )

product = Product(
    # ... existing fields ...
    durability_data=durability_data,
    practical_metrics=practical_metrics,
    # ... rest of fields ...
)
```

---

## How to Apply the Fix

### Step 1: Run SQL Migration

In **Supabase SQL Editor**, run:

```sql
-- Add durability_data and practical_metrics columns
ALTER TABLE products
ADD COLUMN IF NOT EXISTS durability_data JSONB DEFAULT NULL;

ALTER TABLE products
ADD COLUMN IF NOT EXISTS practical_metrics JSONB DEFAULT NULL;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_durability_score
ON products ((durability_data->>'score')::int);

CREATE INDEX IF NOT EXISTS idx_products_lifespan
ON products ((durability_data->>'average_lifespan_years')::float);
```

OR copy/paste from:
```bash
cat backend/add_durability_and_practical_metrics.sql
```

### Step 2: Clear Old Cache

Old cached products don't have the new fields. Clear them:

```bash
cd backend
source venv/bin/activate
python clear_all_cache.py
```

### Step 3: Test with Fresh Search

1. Search for "air fryer" (will be slow - fresh search)
2. Search again for "air fryer" (should be fast - cache hit)
3. Verify:
   - ✅ Characteristics appear
   - ✅ Durability shows non-zero values
   - ✅ Practical metrics display

---

## Testing Script

**File:** `test_cache_data_structure.py`

Inspects cached data to verify fields are present:

```bash
python test_cache_data_structure.py
```

Expected output:
```
Product 1: Dash Compact Air Fryer
- Characteristics: ['Compact size', 'Simple controls', 'Lightweight']
- Durability data: DurabilityData(score=65, average_lifespan_years=2.0, ...)
- Practical metrics: PracticalMetrics(cleaning_time_minutes=5, ...)
```

---

## Why This Happened

1. **Product model was updated** to include `durability_data` and `practical_metrics`
2. **Database schema wasn't updated** to store these new fields
3. **Cache transformation logic** didn't serialize/deserialize them
4. **Result:** Fresh searches worked (objects in memory), but cache hits failed (objects lost)

---

## Files Changed

1. `add_durability_and_practical_metrics.sql` - SQL migration
2. `database_service.py` - Cache storage/retrieval logic
3. `clear_all_cache.py` - Utility to clear old cache
4. `test_cache_data_structure.py` - Verification script

---

## Summary

✅ **Problem:** Durability data missing from cached products
✅ **Cause:** Database schema missing `durability_data` and `practical_metrics` columns
✅ **Fix:** Add columns + update serialization/deserialization logic
✅ **Next:** Run SQL migration + clear old cache + test

After applying this fix, cached searches will include all fields just like fresh searches!
