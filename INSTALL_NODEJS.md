# Install Node.js to Run Kenny Frontend

## Quick Installation Guide

### Method 1: Official Installer (Easiest)

1. **Download Node.js**
   - Go to: https://nodejs.org/
   - Click the **LTS** (Long Term Support) button
   - Download will start automatically

2. **Run the Installer**
   - Open the downloaded `.pkg` file
   - Follow the installation wizard
   - Click "Continue" → "Agree" → "Install"
   - Enter your password when prompted

3. **Verify Installation**
   - Open a NEW terminal window
   - Run:
     ```bash
     node --version
     npm --version
     ```
   - You should see version numbers (e.g., v20.x.x)

### Method 2: Homebrew (For Advanced Users)

If you have Homebrew installed:

```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node

# Verify
node --version
npm --version
```

---

## After Node.js is Installed

### 1. Navigate to Frontend Directory
```bash
cd /Users/wenyichen/kenny-gem-finder/frontend
```

### 2. Install Dependencies
```bash
npm install
```

This will take 2-3 minutes and install:
- Next.js
- React
- TypeScript
- Tailwind CSS
- Axios
- React Query
- All other dependencies

### 3. Start the Development Server
```bash
npm run dev
```

You should see:
```
   ▲ Next.js 14.1.0
   - Local:        http://localhost:3000
   - Ready in 2.3s
```

### 4. Open in Browser
Navigate to: **http://localhost:3000**

---

## Quick Test

Once the frontend is running:

1. You'll see the Kenny search interface
2. Type or click: "I need a cast iron skillet that won't rust easily"
3. Click "Search for Kitchen Gems 🔍"
4. Wait 10-30 seconds for AI to research
5. See products organized in Good/Better/Best tiers!

---

## Troubleshooting

### "command not found: node" after installation
- **Solution**: Open a NEW terminal window
- The old terminal won't have the updated PATH

### "npm install" fails
```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

### Port 3000 already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or run on different port
npm run dev -- -p 3001
```

### Backend not connecting
Make sure the backend is still running:
```bash
cd /Users/wenyichen/kenny-gem-finder/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Backend should be at: http://localhost:8000

---

## Full Command Sequence

Once Node.js is installed:

```bash
# 1. Go to frontend directory
cd /Users/wenyichen/kenny-gem-finder/frontend

# 2. Install dependencies (first time only)
npm install

# 3. Start dev server
npm run dev

# 4. Open browser to http://localhost:3000
```

---

**Estimated Time:**
- Download Node.js: 1-2 minutes
- Install Node.js: 2-3 minutes
- npm install: 2-3 minutes
- npm run dev: 10 seconds
- **Total: ~7 minutes** to see Kenny live! 🚀
