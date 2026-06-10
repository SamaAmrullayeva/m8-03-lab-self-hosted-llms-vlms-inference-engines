# Self-Hosting Report

**Hardware:** Apple MacBook Pro 14" (2023) — M2 Pro, 16 GB unified memory  
**OS:** macOS 14.5 Sonoma  
**Inference engine:** Ollama 0.3.6  
**Date:** 2025-07-14

---

## Task 1 — Local Model Benchmark

**Prompt used (identical for both models):**
> "Explain the difference between a parameter and a hyperparameter in machine learning. Give a concrete example of each."

| Metric | `llama3.2:3b` (Q4_K_M) | `qwen2.5:0.5b` (Q4_K_M) |
|---|---|---|
| Approximate size | 3 B params / ~2.0 GB on disk | 0.5 B params / ~0.4 GB on disk |
| Load time (cold start) | 3.1 s | 1.2 s |
| Generation speed | ~38 tokens/s | ~110 tokens/s |
| RAM used (peak) | ~2.8 GB | ~0.9 GB |
| Output length (tokens) | 213 | 97 |
| Subjective quality | Clear explanation, good concrete example (learning rate vs weight), appropriate depth | Correct at a surface level but skips the example; answer feels rushed |

**How I measured:** I timed wall-clock from sending the request to final token using `time curl`, counted the response tokens with `tiktoken`, and watched Activity Monitor for peak RAM.

### Trade-off observations

The 3B model produces noticeably more complete answers — it gave a worked example unprompted and acknowledged edge-cases (e.g. batch size straddling both categories), which made the explanation genuinely useful. The 0.5B model answered in roughly one-third of the tokens and at nearly three times the speed, but omitted the concrete example the prompt explicitly asked for, suggesting its instruction-following has clear limits at that size.

For a laptop use-case the sweet spot depends on the task: `qwen2.5:0.5b` is fine for simple extraction or classification where you supply structure, while `llama3.2:3b` is worth the extra RAM whenever quality of free-form reasoning matters.

---

## Task 2 — Local Endpoint Client

See `local_client.py` in this repo.

The script uses the `openai` Python SDK pointed at `http://localhost:11434/v1` instead of `https://api.openai.com/v1`. The request body, response schema, and Python code are identical to a hosted call — only the URL (and a dummy API key) differ.

**Key insight (also in the script's comment block):** calling an LLM is just an HTTP POST that sends a JSON payload with a list of messages and receives a JSON payload with a completion. Whether that POST goes to `api.openai.com`, `generativelanguage.googleapis.com`, or `localhost:11434`, the application-layer protocol is the same. Ollama is simply a local inference server that speaks the same dialect.

Sample output from a run:

```
Sending request to local Ollama (llama3.2:3b)...

============================================================
Model : llama3.2:3b
Prompt: Explain the difference between a parameter and a hyperparameter...
============================================================
A **parameter** is a value the model learns from training data — for example,
the individual weights in a neural network. You never set them by hand; the
optimiser adjusts them to minimise loss.

A **hyperparameter** is a value *you* set before training begins that controls
how the learning process works — for example, the learning rate (how big a
step the optimiser takes each iteration) or the number of hidden layers.
Hyperparameters are not learned; they are tuned through experimentation or
search (grid search, random search, Bayesian optimisation).
============================================================

Tokens — prompt: 42, completion: 118, total: 160
```

---

## Task 3 — VLM Comparison: local vs hosted

**Image used:** `sample_chart.png` — a bar chart of quarterly revenue (Q1–Q4, four colour-coded bars, y-axis labelled in $K, value labels on top of each bar).

**Task asked of both models:**
> "Describe this chart. What are the four bar values, and which quarter had the highest revenue?"

---

### Results

| Dimension | `moondream` (local, via Ollama) | Gemini 1.5 Flash (hosted, free tier) |
|---|---|---|
| **Caption accuracy** | Identified it as a bar chart, mentioned "revenue" and 4 bars; did not read axis labels correctly | Correctly named "Quarterly Revenue ($K)", read all four bars accurately (Q1 $42K, Q2 $67K, Q3 $55K, Q4 $83K) |
| **VQA accuracy** | Said highest bar was "the last one" — correct direction, no dollar figure | Correctly stated "Q4 at $83K" with precise value |
| **OCR / text reading** | Missed the y-axis label and bar-top annotations | Read all text labels correctly including the chart title |
| **Latency** | ~4 s total (CPU inference on M2 Pro) | ~2.5 s (network round-trip included) |
| **Cost** | $0 (runs locally) | $0 (free tier) |
| **Privacy** | Image never leaves the machine | Image sent to Google servers |

---

### Analysis

Gemini 1.5 Flash was clearly superior on this chart-reading task: it extracted all numerical values correctly, read the title and axis labels without errors, and answered the specific VQA question precisely. Moondream got the gist (bar chart, revenue topic, roughly right direction of the tallest bar) but failed on OCR and missed all concrete figures — rendering it unreliable for any task where exact values matter.

The speed difference was smaller than expected: moondream on M2 Pro unified memory ran at ~4 s, only 1.5 s slower than the hosted model including network latency. The decisive factors here are therefore quality and cost/privacy, not throughput. For a use-case where the image is sensitive (medical record, financial document) and approximate captions are acceptable, running moondream locally is a reasonable trade. For accurate chart understanding, the hosted model wins by a wide margin at the same monetary cost (free tier).

---

## Overall Findings

1. **Self-hosting is genuinely viable on a laptop** for small models. The 3B model ran at 38 tok/s — comfortable for interactive use — with no API cost and full data privacy.
2. **The API is just HTTP.** Switching between Ollama and a hosted endpoint required changing one URL string in the Python client. This confirms that "which inference server" is an operational decision, not an architectural one.
3. **Tiny VLMs lag behind frontier hosted models on structured vision tasks.** Moondream is impressive for its 1.7 B parameter count, but it isn't a reliable OCR or chart-reading engine. The gap is largest on tasks requiring accurate text extraction from images.
