# MOSAIC

**Multi-Platform Observational & Sociodynamic Analysis of Individual Configurations**

> **This repository is a proof of concept.**
> MOSAIC is a sociological framework for multi-platform behavioral analysis, built in papers before it was built in code. What you find here is its first test bench: the place where the theory meets real data, and where it is allowed to break.

![MOSAIC Demo](./demo_MOSAIC.gif)

---

## The idea

Consider an illustrative case. The same person takes part in different digital environments. On GitHub, their contributions appear methodical and collaborative. On Reddit, their exchanges are more confrontational. In YouTube comments, they are shorter and more dismissive.

Most tools would ask which description best captures the person. MOSAIC asks a different question: what explains the variation across contexts, and what can legitimately be inferred from it?

**Not *who* someone is. *Where* they stand.**

The framework's central hypothesis:

> Digital traces should not be interpreted as stable behavioral signals but as structured positional variance across socio-technical environments.

The variance between platforms is not noise to filter out. **It is the signal.** The framework proposes to read it through three components:

- **What holds**: what persists across contexts.
- **What adapts**: what varies coherently with the constraints and incentives of each platform.
- **What slips**: what neither of the first two fully accounts for.

These are analytical categories, not discoveries. "What slips" does not reveal a hidden "true self" behind the public presentation; it marks where the first two readings stop explaining the data. The three are read as a structure, never collapsed into a score.

This is a conceptual framework. Its hypotheses are not yet empirically validated, and the current code does not demonstrate them.

## What MOSAIC is designed to do, and not to do

These distinctions are methodological commitments, not guarantees. Theoretical intent alone does not determine what a system does: the data it collects, the outputs it generates and the uses it makes possible matter just as much.

| Designed not to | Designed to | What it takes to hold |
|---|---|---|
| Infer personality | Analyze how expression varies across contexts | Protocols that read variation without assigning stable traits |
| Predict behavior | Describe the moves a position makes plausible | "Plausible" remains an inference: not a validated prediction |
| Profile psychologically | Map a position within a field | A map turns into a portrait as soon as it attributes stable characteristics to a person |
| Surveil | Produce a reading at a given moment, indexed in time | Dating is not enough: collection, consent, retention and use must follow the same commitment |

> The grandmaster doesn't need to know the player. The position is enough.

## Framework vs. this repository

| | Status |
|---|---|
| **Theory**: three-level architecture, signal decomposition, positional capital, epistemological commitments | [Paper I](https://www.academia.edu/165289102/MOSAIC_A_Sociological_Framework_for_Multi_Platform_Positional_Analysis) — working paper, not peer-reviewed |
| **Method**: protocols for each component, grammar of analytical decisions, validation | Paper II — in preparation |
| **Code**: multi-platform collection, structuring, LLM-assisted reading | **Alpha PoC — this repo** |

The code is deliberately behind the theory. It collects, structures, and can produce LLM-assisted outputs. Those outputs are not yet a complete or reproducible application of the framework's protocols, which are being specified in Paper II. The current prompt templates predate the framework and will be rewritten to follow it.

MOSAIC provides a grammar of analysis. It does not produce the analysis. Whatever the code outputs, the analyst stays accountable for every reading.

![MOSAIC Architecture](./MOSAIC.png)

## Quick start

```bash
git clone https://github.com/Or1un/MOSAIC.git && cd MOSAIC
pip install -r requirements.txt
cp modules/config.yaml.example modules/config.yaml   # optional: YouTube, Telegram keys
python3 mosaic.py
```

Local LLM analysis (recommended):

```bash
pip install -r requirements_llm.txt
curl -fsSL https://ollama.com/install.sh | sh   # Windows: https://ollama.com/download
ollama serve &
ollama pull mistral:7b-instruct
```

**Sources:** GitHub, Stack Overflow · Reddit, Telegram, Mastodon, Bluesky · YouTube, Medium

## Data and use

**What happens to the data**
- MOSAIC collects public traces from the platforms you select and stores them locally, in `results/` (git-ignored).
- With a local model (Ollama), the analysis runs on your machine and nothing is sent to an LLM provider.
- With a remote LLM, the data you submit **leaves your machine** and is processed under that provider's terms. Local use is recommended; it is not enforced.
- Retention is up to you: delete `results/` when an analysis is over.

**Who it is for**

Self-analysis, sociodynamic research, and analyses with volunteer subjects. Knowing that an analysis exists is not the same as consenting to it, and consent alone does not settle proportionality, data minimization or reuse of results. For analyses involving volunteers, the conditions of consent and withdrawal will be specified with Paper II's call for participants.

**Not for** surveillance, stalking, harassment, profiling someone without their knowledge, or mass automated analysis.

**Compliance.** You are responsible for GDPR and local law. MOSAIC does not make a use compliant; this README describes the tool, not a legal guarantee.

## Go deeper

- **Start here:** [MOSAIC — A Field Guide](https://medium.com/@or1un), the map of the article series
- **Theory:** [Paper I — *Why*](https://www.academia.edu/165289102/MOSAIC_A_Sociological_Framework_for_Multi_Platform_Positional_Analysis) (working paper)
- **Article series:** [The Variance is the Signal, and what follows](https://medium.com/@or1un) on Medium
- **Coming next:** Paper II — *How* (in preparation, not yet available), with a call for volunteer analysts and subjects

## Break it

The goal is not to confirm the theory, but to see which parts survive contact with real data. Challenge the assumptions, the method, the ethics. Point out where it fails.

Issues and Discussions on GitHub · or1un@proton.me
