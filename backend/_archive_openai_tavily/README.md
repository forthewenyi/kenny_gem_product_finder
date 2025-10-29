# Archived: OpenAI + Tavily Implementation

These files contain the original implementation using OpenAI GPT-4 and Tavily search API.

**Archived on:** October 29, 2024

**Reason for archival:** Migrated to Google Gemini 2.0 Flash + Google Search to reduce costs and simplify the tech stack.

## Files in this archive:

- **simple_search.py** - Original search implementation using hardcoded query templates + Tavily
- **agent_service.py** - LangChain-based agent service with Tavily tool
- **test_search.py** - Unit tests for SimpleKennySearch (OpenAI/Tavily)
- **test_debug.py** - Debug script for OpenAI output

## Current implementation:

The production code now uses:
- **contextual_search.py** - Gemini 2.0 Flash for AI-driven query generation
- **characteristic_generator.py** - Gemini 2.0 Flash for characteristic generation
- **googlesearch-python** - Free Google Search (instead of Tavily)

## If you need to reference the old implementation:

These files are kept for reference but are no longer used by the application.
The main differences:
- Old: OpenAI GPT-4 (~$0.03 per 1K tokens) → New: Gemini 2.0 Flash (~$0.001 per 1K tokens)
- Old: Tavily Search (~$5/1000 searches) → New: Google Search (free tier)
- Old: LangChain wrapper → New: Direct Gemini SDK calls
