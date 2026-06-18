![Autorea](assets/autorea-banner.png)

# LLM06 — Excessive Agency

## What is Excessive Agency?

**Excessive Agency** means an AI agent has more capabilities, permissions, or autonomy than its actual task requires — a generic, all-powerful tool where a narrow one would do, or full database access where read-only would be enough. It's rarely intentional; it's usually convenience ("one flexible tool is simpler to build than five narrow ones").

The risk stays invisible until something else goes wrong — most commonly, the agent gets manipulated through a hidden instruction (prompt injection). Excessive Agency doesn't cause that manipulation. It decides **how much damage the manipulation can do once it succeeds.** Think of it as the difference between handing someone a key to one room versus a master key to the whole building: if that key is ever misused, the first can only open one door — the second opens everything.

## The Demo

An AI customer-service agent is given a tool with far more access than its task requires. A hidden instruction inside a normal-looking support message manipulates it into reading and overwriting a different customer's data. Two versions of the same agent, same model, same attack — only the tool architecture differs.

![Vulnerable vs fixed agent flow](assets/excessive-agency-flow.png)

**Vulnerable:** one all-purpose database tool, no checks. The injected instruction succeeds — verified live, a different customer's email gets overwritten.

**Fixed:** narrow, single-purpose tools plus a policy check that compares each tool call against the actual session before anything runs. The model still gets manipulated the same way — but the action is rejected before it reaches the database.

For the full technical breakdown — how the vulnerability works, its relation to LLM01/ASI02/ASI03, the fixed version's two defense layers, honest limitations, and Autorea product reusability — see **[DOCS.md](DOCS.md)**.

## Running the Demo

Each version is self-contained.

```bash
cd vulnerable   # or: cd fixed
pip install -r requirements.txt
python setup_db.py
export OPENAI_API_KEY=sk-...   # PowerShell: $env:OPENAI_API_KEY = "sk-..."
python agent.py
```

`setup_db.py` creates each version's own isolated `shop.db` with identical dummy data — the two versions never share a physical database file, so running one doesn't affect the other's starting state.

## Repository Structure

```
llm06-excessive-agency/
├── README.md
├── DOCS.md
├── LINKEDIN-POST.md
├── OBSIDIAN-NOTE.md
├── assets/
│   ├── autorea-banner.png
│   └── excessive-agency-flow.png
├── shared_db_init.py      # Shared DB schema/seed logic, imported by both setup scripts
├── vulnerable/
│   ├── setup_db.py
│   ├── tools.py            # execute_sql — one generic, unrestricted tool
│   ├── agent.py
│   └── requirements.txt
└── fixed/
    ├── setup_db.py
    ├── tools.py             # Narrow, single-purpose tools (Layer 1)
    ├── policy.py            # Contextual policy check (Layer 2)
    ├── agent.py
    └── requirements.txt
```

## OWASP Reference

This repo addresses **LLM06 — Excessive Agency** from the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/). See [DOCS.md](DOCS.md) for its relationship to LLM01, ASI02, and ASI03.

---

Part of [Autorea Security Lab](#) — a 20-project series mapping the full OWASP Top 10 for LLMs and Top 10 for Agentic Applications, built by [Autorea](#).
