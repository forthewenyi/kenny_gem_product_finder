# Google Custom Search API Setup Guide

This guide will help you set up Google Custom Search API for Kenny Gem Finder to enable reliable web research with no rate limiting.

---

## 📊 **Why Use Google Custom Search API?**

| Feature | Free Library (googlesearch-python) | Custom Search API |
|---------|-----------------------------------|-------------------|
| **Reliability** | ❌ Often rate-limited | ✅ Guaranteed availability |
| **Speed** | ⚠️ Slow (2-3s per query) | ✅ Fast (0.2-0.5s per query) |
| **Data Quality** | ⚠️ Basic URLs only | ✅ Rich snippets, titles, metadata |
| **Cost** | Free | 100/day free, then $5/1000 queries |
| **Rate Limits** | ❌ Unpredictable blocks | ✅ No rate limiting |

**Recommendation:** Use Custom Search API for production. The free tier (100 queries/day) covers most development needs.

---

## 🚀 **Setup Instructions**

### **Step 1: Enable Custom Search API**

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create or Select a Project:**
   - Click "Select a project" → "New Project"
   - Name: `kenny-gem-finder` (or any name)
   - Click "Create"

3. **Enable Custom Search API:**
   - Navigate to: https://console.cloud.google.com/apis/library
   - Search for "Custom Search API"
   - Click on it → Click "Enable"

---

### **Step 2: Create API Key**

1. **Go to Credentials:**
   - Navigate to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" → "API Key"

2. **Copy the API Key:**
   - A popup will show your new API key
   - **Copy it immediately** (you'll need it in Step 4)

3. **Restrict the API Key (Recommended):**
   - Click "Edit API Key"
   - Under "API restrictions":
     - Select "Restrict key"
     - Check "Custom Search API"
   - Click "Save"

---

### **Step 3: Create Custom Search Engine**

1. **Go to Programmable Search Engine:**
   - Visit: https://programmablesearchengine.google.com/

2. **Create New Search Engine:**
   - Click "Add" or "Create new search engine"
   - **Name:** `Kenny Gem Finder Web Search`
   - **What to search:** Select "Search the entire web"
   - Click "Create"

3. **Get Your Search Engine ID:**
   - After creation, click on your new search engine
   - Find the "Search engine ID" (also called `cx` parameter)
   - **Copy this ID** (format: `0123456789abcdef:a1b2c3d4e5f`)

---

### **Step 4: Configure Environment Variables**

1. **Open your `.env` file:**
   ```bash
   cd /Users/wenyichen/kenny-gem-finder/backend
   nano .env
   ```

2. **Add the following lines:**
   ```bash
   # Google Custom Search API
   GOOGLE_SEARCH_API_KEY=YOUR_API_KEY_FROM_STEP_2
   GOOGLE_SEARCH_ENGINE_ID=YOUR_ENGINE_ID_FROM_STEP_3
   ```

3. **Example:**
   ```bash
   GOOGLE_SEARCH_API_KEY=AIzaSyDaGmWKa4JsXZ-HjGw7ISLan_KqsRO1234
   GOOGLE_SEARCH_ENGINE_ID=0123456789abcdef:a1b2c3d4e5f
   ```

4. **Save and exit** (Ctrl+X, then Y, then Enter)

---

### **Step 5: Verify Configuration**

1. **Check if the service detects the API:**
   ```bash
   cd /Users/wenyichen/kenny-gem-finder/backend
   source venv/bin/activate
   python -c "from google_search_service import get_google_search_service; service = get_google_search_service(); print(service.get_quota_info())"
   ```

2. **Expected output:**
   ```python
   ✓ Using Google Custom Search API (reliable)
   {
     'using_official_api': True,
     'api_key_configured': True,
     'search_engine_configured': True,
     'free_daily_quota': 100,
     'cost_per_1000_after_free': 5.0,
     'note': 'First 100 queries per day are free'
   }
   ```

3. **If you see warnings:**
   ```
   ⚠️  Google Custom Search API not configured
   ```
   - Double-check your `.env` file
   - Make sure keys are correct (no extra spaces)
   - Restart your backend server

---

## 💰 **Pricing & Quota**

### **Free Tier:**
- **100 queries per day**: Completely free
- Perfect for development and testing
- Resets every 24 hours (Pacific Time)

### **Paid Usage:**
- **$5 per 1,000 queries** after free tier
- Billed monthly through Google Cloud

### **Cost Calculator:**

| Scenario | Queries/Day | Cost/Month |
|----------|-------------|------------|
| Development | 50 | $0 (free tier) |
| Light usage | 100 | $0 (free tier) |
| Medium usage | 500 | ~$60 |
| Heavy usage | 1,000 | ~$135 |

**Kenny's Usage:**
- Each product search = 10 queries (5-phase research)
- 10 searches/day = 100 queries = **FREE**
- 50 searches/day = 500 queries = **$60/month**

---

## 🔄 **Fallback Behavior**

Kenny Gem Finder has built-in fallback:

1. **If Custom Search API is configured:**
   - Uses official API (fast, reliable)
   - No rate limiting

2. **If API keys are missing:**
   - Falls back to `googlesearch-python` (free library)
   - May be rate-limited
   - Prints warning message

3. **If both fail:**
   - AI generates products from training data
   - Less fresh/accurate but still functional

---

## 🧪 **Testing Your Setup**

Run a test search to verify everything works:

```bash
cd /Users/wenyichen/kenny-gem-finder/backend
source venv/bin/activate
python test_search_pretty.py
```

**Look for this line in the output:**
```
✓ Using Google Custom Search API (reliable)
```

**You should see actual search results:**
```
✓ Research complete! Collected 60 sources in 2.5s
  • Context Discovery: 12 sources
  • Material Science: 12 sources
  • Product Identification: 12 sources
  • Frustration Research: 12 sources
  • Value Synthesis: 12 sources
```

---

## ❓ **Troubleshooting**

### **Problem: "API not enabled"**
```
Error: The API is not enabled for this project
```
**Solution:** Go back to Step 1 and enable Custom Search API

---

### **Problem: "Invalid API key"**
```
Error: API key not valid. Please pass a valid API key.
```
**Solution:**
- Verify your API key is correct in `.env`
- Check for extra spaces or quotes
- Make sure you copied the entire key

---

### **Problem: "Quota exceeded"**
```
Error: Quota exceeded for quota metric 'Queries' and limit 'Queries per day'
```
**Solution:**
- You've used your 100 free queries for today
- Wait 24 hours for reset, or
- Enable billing in Google Cloud Console

---

### **Problem: "Search engine not found"**
```
Error: Invalid Value
```
**Solution:**
- Verify your Search Engine ID is correct
- Make sure you created the search engine (Step 3)
- The ID should look like: `0123456789abcdef:a1b2c3d4e5f`

---

## 📚 **Additional Resources**

- **Custom Search API Documentation:** https://developers.google.com/custom-search/v1/overview
- **Pricing Details:** https://developers.google.com/custom-search/v1/overview#pricing
- **API Console:** https://console.cloud.google.com/
- **Search Engine Management:** https://programmablesearchengine.google.com/

---

## 🎯 **Quick Start Checklist**

- [ ] Create Google Cloud project
- [ ] Enable Custom Search API
- [ ] Create API key
- [ ] Restrict API key to Custom Search API
- [ ] Create Programmable Search Engine
- [ ] Set "Search entire web" = YES
- [ ] Copy Search Engine ID
- [ ] Add both keys to `.env` file
- [ ] Run test search
- [ ] Verify 60 sources collected

---

**Need help?** Check the troubleshooting section or review the setup steps above.
