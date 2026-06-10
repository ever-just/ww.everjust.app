# Agent Skills

Reusable skills for agents to accomplish complex tasks.

## Available Skills

### Deep Research
**Directory:** `deep-research/`

A comprehensive skill for agents to conduct thorough internet research on any topic, organization, or event.

**What it does:**
- Finds all available data on a topic (not just top search results)
- Discovers hidden documents (PDFs, Excel files, archived pages)
- Extracts data from multiple platforms (websites, social media, APIs)
- Builds comprehensive databases from scattered sources
- Creates authoritative reports with proper source attribution
- Triangulates findings across 3+ sources for confidence

**Time Investment:** 2-3 hours for comprehensive research

**Files:**
- `AGENT_SKILL_INDEX.md` — Start here (navigation guide)
- `AGENT_SKILL_QUICK_REFERENCE.md` — Quick start (30 min)
- `AGENT_SKILL_DEEP_RESEARCH.md` — Complete guide (~1,500 lines)
- `AGENT_SKILL_REAL_EXAMPLES.md` — Real case studies from TCSW
- `RESEARCH_METHODOLOGY.md` — Original research documentation
- `RESEARCH_PROMPT_TEMPLATE.md` — Reusable research prompt template
- `SEARCH_SYNTHESIS_WALKTHROUGH.md` — Step-by-step process walkthrough

**Quick Start:**
1. Read `AGENT_SKILL_QUICK_REFERENCE.md` (30 minutes)
2. Follow the 7-phase pipeline
3. Adapt code snippets to your topic
4. Generate reports in Excel + PDF

**The 7-Phase Pipeline:**
```
1. PLAN (5 min)      → Sequential thinking + research checklist
2. LOCAL (5 min)     → Parse existing files
3. SEARCH (15 min)   → Broad → Targeted → Domain-specific
4. WAYBACK (30 min)  → CDX API for hidden documents
5. SCRAPE (30 min)   → Multi-platform extraction
6. SYNTHESIZE (30 min) → Triangulation + confidence tagging
7. REPORT (30 min)   → Excel + PDF reports
```

**Based on:** Twin Cities Startup Week comprehensive research project (June 2026)

---

## How to Use

1. **For quick start:** Read the Quick Reference card
2. **For complete understanding:** Read the main Deep Research guide
3. **For learning by example:** Study the real examples from TCSW
4. **For your own research:** Use the Research Prompt Template

---

## Contributing

To add new agent skills:
1. Create a new directory under `agentskills/`
2. Add comprehensive documentation
3. Include quick reference card
4. Add real examples
5. Update this README

---

**Created:** June 10, 2026  
**Status:** Ready for use by any agent

