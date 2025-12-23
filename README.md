# 🎯 MOSAIC — v1.0.0-alpha
**Behavioral Intelligence Across Platforms**

> A privacy-first, multi-platform framework for behavioral and sociodynamic analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)]()

![MOSAIC Architecture](./MOSAIC.png)

## 📺 Demo

![MOSAIC Démo](./demo_MOSAIC.gif)

## 🧭 What is MOSAIC?

**MOSAIC is not a simple OSINT aggregator.**
It is a **behavioral analysis framework** designed to help researchers, analysts, and security professionals **observe, structure, and interpret behavioral signals** across multiple online platforms.

MOSAIC collects heterogeneous public data and organizes it into **behavioral dimensions**, enabling comparative and longitudinal analysis that is not possible with single-source approaches.

⚠️ MOSAIC does **not** produce psychological diagnoses or absolute truths.
It provides **structured signals and analytical hypotheses** that must be interpreted by a human analyst.

## 🎯 Vision

Most tools focus on *what* a person publishes.
MOSAIC focuses on **how behavior emerges across environments**.

Instead of aggregating profiles, MOSAIC builds **behavioral fingerprints** across three complementary dimensions:

- **Technical**
Skills, expertise, problem-solving strategies
(GitHub, StackOverflow)

- **Social**
Interactions, affiliations, discourse patterns, community dynamics
(Telegram, Reddit, Mastodon, Bluesky)

- **Influence**
Content production, themes, visibility, narrative consistency
(YouTube, Medium)

This multi-angle approach enables **sociodynamic, security, and credibility analyses** that remain contextual, explainable, and privacy-aware.

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Or1un/MOSAIC.git
cd MOSAIC
pip install -r requirements.txt
```

### Configuration (Optional)

```bash
# Most platforms work without credentials
# Some sources (YouTube, Telegram) require API keys
cp modules/config.yaml.example modules/config.yaml
nano modules/config.yaml
```

### Run
```bash 
python3 mosaic.py
```

## 🤖 LLM Setup

### 1. Install Python dependencies
```bash
pip install -r requirements_llm.txt
```

### 2. Install Ollama server (one-time)
```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

### 3. Start Ollama & pull models - Qwen:0.5b (PoC)
```bash
ollama serve &
ollama pull qwen:0.5b
```

## 🌍 Use Cases

### 🎯 Talent & Expertise Assessment

Go beyond resumes by analyzing:
- technical depth
- communication style
- peer recognition
- community engagement

**Example:** Assess a senior DevSecOps profile via GitHub activity (technical rigor), StackOverflow answers (problem-solving style), and Medium publications (knowledge transmission).

### 🔒 Digital Footprint & OPSEC Analysis

Identify exposure risks, oversharing patterns, and inconsistencies in public presence.

**Example:** Audit the online footprint of an executive or security-sensitive role to detect potential attack surfaces or reputational risks.

### 🕵️ Due Diligence & Credibility Analysis

Cross-validate claims and behavioral consistency across platforms.

**Example:** Before a partnership or investment, evaluate whether public behavior aligns with stated expertise and responsibilities.

### 🔬 Behavioral & Sociodynamic Research

Study:
- discourse evolution
- expertise diffusion
- community influence patterns
- cross-platform behavioral shifts

**Example:** Analyze how technical authority translates (or not) into social influence across different ecosystems.

## 🧩 Core Workflow
### 1️⃣ Collect — Multi-Source Signals

MOSAIC gathers **heterogeneous public data** to avoid mono-platform bias.

**Currently supported sources:**
- Technical: GitHub, StackOverflow
- Social: Telegram, Reddit, Mastodon, Bluesky
- Influence: YouTube, Medium

💡 MOSAIC works best when you already know where your target is active. Focused collection improves signal quality and reduces noise.

Future sources (research ideas): professional platforms, forums, niche communities. Contributions and discussions are welcome.

### 2️⃣ Context — Analytical Framing

Analysis is guided by **contextual prompts**, not generic instructions.

Available contexts (Alpha):
- ``Recruitment.md`` — technical & soft skills assessment
- ``OPSEC_audit.md`` — digital footprint & exposure analysis
- ``Threat_Intelligence.md`` — attribution & consistency research
- ``PoC.md`` — quick exploratory analysis

Prompts are Markdown templates stored in ``modules/prompts/``.

⚠️ Alpha note
Current prompts prioritize **architecture and extensibility** over refinement. MOSAIC assumes analysts will adapt prompts to their methodology and domain.

### 3️⃣ Analysis — AI as an Assistant

MOSAIC supports two analysis modes:

✅ **Local (Privacy-First — Recommended)**
- Uses local LLMs via Ollama
- Data never leaves your machine
- Best for security-sensitive contexts

```bash
ollama pull mistral:7b-instruct
```

Supported models: mistral, llama, qwen, etc.

⚠️ **Cloud (Optional)**
- Higher performance
- User-managed privacy trade-offs
- Upload only exported JSON files from ``results/``

💡 Best results are obtained when combining MOSAIC outputs with external context (CVs, interviews, references, timelines).

### 4️⃣ Insights — Human-Centered Interpretation

Insight quality depends on:
- data diversity
- prompt precision
- analyst expertise
- model capabilities

MOSAIC provides structure and signals. You provide judgment.

## ⚠️ Ethical & Legal Framework

MOSAIC is designed for legitimate, consensual, and lawful use.

### ❌ Not Intended For

- Surveillance or stalking
- Harassment or intimidation
- Unauthorized background checks
- Mass automated profiling
- Violations of platform Terms of Service

### 🔐 Privacy & Responsibility

- No mandatory cloud usage
- Local analysis by default
- Results stored locally (``results/``, ``.git-ignored``)
- Users are responsible for GDPR and local compliance
- Credentials stored securely in ``config.yaml``

By using MOSAIC, you agree to use it **ethically, responsibly, and legally**.

## 🤝 Community & Contributions

Questions, ideas, or research directions?
- 📧 Email: Or1un@proton.me
- 🐛 Issues: GitHub Issues
- 💡 Discussions: GitHub Discussions
- 📖 Wiki: coming soon

MOSAIC is a **methodological framework** — contributions that improve prompts, analysis logic, or ethical safeguards are especially welcome.

Made with 🔍 by Or1un
