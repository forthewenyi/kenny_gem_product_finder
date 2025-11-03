# Category-Relative Tier Structure

## Problem Solved

**Before:** Hardcoded price ranges and lifespans didn't work across categories.
- A $50 chef knife is reasonable (good tier)
- A $50 stand mixer is terrible quality (should be rejected)
- A $300 cast iron skillet is premium (best tier)
- A $300 stand mixer is entry-level (good tier)

**Rigid structure failed:**
```python
"good_tier": [3 products - $20-80, 2-5 years],    # Too rigid!
"better_tier": [3 products - $80-200, 8-15 years],
"best_tier": [3 products - $200-600+, 15-30+ years]
```

---

## Solution: Category-Relative Percentiles

Tiers are now **relative to each product category**, not absolute dollar amounts.

### How It Works

#### Step 1: Determine Category Price Range
AI researches the product category and finds:
- **Minimum viable price:** Cheapest products that actually work
- **Maximum premium price:** High-end products
- **Category range:** Min to max

#### Step 2: Distribute Products by Percentiles
- **GOOD tier:** Bottom 25% of category price range
- **BETTER tier:** 25-75% of category price range
- **BEST tier:** Top 25% of category price range

---

## Examples Across Categories

### Chef Knife
**Category research finds:**
- Minimum viable: $15 (basic stamped blade)
- Maximum premium: $400 (handcrafted Japanese)
- Range: $15-400

**Tier distribution:**
- GOOD: $15-110 (25% of range = bottom quartile)
  - Example: Victorinox Fibrox ($50)
  - Value: Low upfront cost, adequate performance
  - Lifespan: 5-10 years

- BETTER: $110-300 (middle 50% = mainstream)
  - Example: Wüsthof Classic ($150)
  - Value: Best cost-per-year, optimal durability
  - Lifespan: 15-25 years

- BEST: $300-400+ (top 25% = premium)
  - Example: Shun Premier ($380)
  - Value: Maximum lifespan, heirloom quality
  - Lifespan: 30+ years with care

---

### Stand Mixer
**Category research finds:**
- Minimum viable: $150 (basic hand mixer alternatives fail)
- Maximum premium: $700 (commercial-grade KitchenAid)
- Range: $150-700

**Tier distribution:**
- GOOD: $150-287 (25% of range)
  - Example: Hamilton Beach 6-Speed ($200)
  - Value: Entry-level, basic tasks
  - Lifespan: 3-5 years

- BETTER: $287-525 (middle 50%)
  - Example: KitchenAid Artisan ($400)
  - Value: Industry standard, reliable
  - Lifespan: 10-15 years

- BEST: $525-700+ (top 25%)
  - Example: KitchenAid Pro 600 ($600)
  - Value: Commercial durability
  - Lifespan: 20-30+ years

---

### Cast Iron Skillet
**Category research finds:**
- Minimum viable: $15 (Lodge, mass-produced)
- Maximum premium: $200 (Finex, Smithey, hand-polished)
- Range: $15-200

**Tier distribution:**
- GOOD: $15-62 (25% of range)
  - Example: Lodge 10.25" ($25)
  - Value: Budget-friendly, proven
  - Lifespan: 30+ years (cast iron lasts)

- BETTER: $62-150 (middle 50%)
  - Example: Field Company No. 8 ($125)
  - Value: Lighter, smoother surface
  - Lifespan: 50+ years (heirloom)

- BEST: $150-200+ (top 25%)
  - Example: Finex 10" ($180)
  - Value: Hand-polished, octagonal
  - Lifespan: 100+ years (literally forever)

---

### Air Fryer
**Category research finds:**
- Minimum viable: $50 (cheap basket models)
- Maximum premium: $400 (Breville Smart Oven Air)
- Range: $50-400

**Tier distribution:**
- GOOD: $50-137 (25% of range)
  - Example: Ninja AF101 ($80)
  - Value: Budget-friendly, compact
  - Lifespan: 3-5 years

- BETTER: $137-312 (middle 50%)
  - Example: Cosori Pro ($170)
  - Value: Larger capacity, better build
  - Lifespan: 5-8 years

- BEST: $312-400+ (top 25%)
  - Example: Breville Smart Oven Air ($400)
  - Value: Multi-function, commercial quality
  - Lifespan: 10-15 years

---

## Key Principle

**The same dollar amount means different things in different categories:**

| Price | Chef Knife | Stand Mixer | Cast Iron | Air Fryer |
|-------|------------|-------------|-----------|-----------|
| $50   | GOOD tier  | ❌ Too cheap | BETTER tier | GOOD tier |
| $150  | BETTER tier | GOOD tier   | BEST tier | BETTER tier |
| $300  | BEST tier  | BETTER tier | ❌ Overpriced | BETTER tier |
| $600  | ❌ Overpriced | BEST tier | ❌ Overpriced | BEST tier |

---

## Implementation

### Updated Synthesis Prompt (contextual_search.py:328-375)

```python
TIER STRUCTURE (CATEGORY-RELATIVE, NOT ABSOLUTE):
First, determine the typical price range for this product category from research:
- Find minimum viable price (cheapest products that actually work)
- Find maximum premium price (high-end products)
- Calculate category price range

Then distribute products across tiers using PERCENTILES:
- GOOD tier: Bottom 25% of category price range (budget-conscious, entry-level)
- BETTER tier: 25-75% of category price range (mainstream, sweet spot)
- BEST tier: Top 25% of category price range (premium, buy-it-for-life)

CRITICAL: Tiers are relative to CATEGORY, not absolute dollar amounts.
A $200 chef knife is "best tier" but a $200 stand mixer is "good tier".
```

### AI Returns Category Range

```json
{
  "category_price_range": {
    "minimum": 150,
    "maximum": 700,
    "currency": "USD"
  },
  "good_tier": [
    // Products in $150-287 range
  ],
  "better_tier": [
    // Products in $287-525 range
  ],
  "best_tier": [
    // Products in $525-700+ range
  ]
}
```

---

## Benefits

### 1. Works Across All Categories
- No more "$20-80 good tier" that breaks for expensive categories
- Each category gets appropriate price ranges
- AI determines ranges from research, not hardcoded

### 2. Meaningful Value Comparisons
- "Good tier" means "budget option FOR THIS CATEGORY"
- "Best tier" means "premium option FOR THIS CATEGORY"
- Users understand relative value within category

### 3. Scales Automatically
- New categories work without code changes
- AI researches typical prices
- Percentiles adapt to category norms

### 4. Accurate Cost-Per-Year
- Tiers reflect actual quality-price tradeoffs
- Budget options have shorter lifespans (appropriate)
- Premium options justify cost with longevity

---

## Examples of Better Recommendations

### Before (Rigid Tiers):
```
Stand Mixer Search:
GOOD tier: ❌ No products (nothing decent under $80)
BETTER tier: ❌ Wrong products ($80-200 is still cheap)
BEST tier: ✅ All the good products ($200-600)
Result: Two empty tiers, one overcrowded tier
```

### After (Category-Relative):
```
Stand Mixer Search:
GOOD tier: $150-287
  - Hamilton Beach 6-Speed ($200)
  - Cuisinart Precision Master ($250)
  - Oster Planetary ($180)

BETTER tier: $287-525
  - KitchenAid Artisan ($400)
  - Cuisinart Stand Mixer 5.5Q ($350)
  - Bosch Universal Plus ($450)

BEST tier: $525-700+
  - KitchenAid Professional 600 ($600)
  - Ankarsrum Original ($650)
  - KitchenAid Commercial ($700)

Result: Balanced tiers, meaningful comparisons
```

---

## Testing

To verify category-relative tiers work:

1. **Search for cheap category** (e.g., "chef knife"):
   - Good tier should be ~$20-50
   - Best tier should be ~$150-400

2. **Search for expensive category** (e.g., "stand mixer"):
   - Good tier should be ~$150-250
   - Best tier should be ~$400-700

3. **Check tier balance:**
   - Each tier should have 3 products
   - Prices should cluster in appropriate ranges
   - No empty tiers

---

## Edge Cases Handled

### 1. Narrow Price Range
If category has narrow range (e.g., $20-50):
- Good: $20-27
- Better: $27-42
- Best: $42-50
Still creates meaningful tiers

### 2. Wide Price Range
If category has wide range (e.g., $10-2000):
- Good: $10-500
- Better: $500-1500
- Best: $1500-2000
Percentiles still make sense

### 3. No Premium Products
If research finds no products above $100:
- Max becomes $100
- Tiers adjust accordingly
- No artificial inflation

---

## Summary

✅ **Problem:** Rigid price tiers don't work across categories
✅ **Solution:** Category-relative percentiles (25%, 50%, 25%)
✅ **Benefit:** Meaningful tiers for ANY product category
✅ **Implementation:** AI determines category range from research

**Your tier structure now scales to any product category!** 🎯
