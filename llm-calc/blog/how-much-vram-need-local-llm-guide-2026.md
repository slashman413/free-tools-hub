---
title: "How Much VRAM Do You Need for Local LLMs? Full Guide 2026"
description: "Learn how to calculate VRAM requirements for running local LLMs. Complete reference for GPTQ, AWQ, GGUF quantization, GPU buying advice, and Mac vs NVIDIA comparison."
url: /blog/how-much-vram-need-local-llm-guide-2026
date: 2026-07-23
tags: [llm, vram, gpu, hardware, local-llm, quantization]
keywords: [LLM VRAM requirements, local LLM guide, GPU for AI, GGUF quantization, GPTQ vs AWQ, VRAM calculator, Mac M-series GPU, NVIDIA RTX AI]
internal_links:
  - { anchor: "token-cost-calculator", url: /blog/gpt-5-vs-claude-vs-deepseek-token-cost-comparison-2026, title: "Also see our Token Cost Comparison" }
  - { anchor: "llm-calc-tool", url: /, title: "Calculate Your LLM VRAM Needs" }
---

# How Much VRAM Do You Need for Local LLMs? Full Guide 2026

**Last updated July 2026. Tested on DGX GB10, NVIDIA RTX 4090, and Mac Studio M2 Max.**

## Quick Answer: VRAM Cheat Sheet

| Use Case | Minimum VRAM | Recommended VRAM | Example Models |
|----------|-------------|-------------------|----------------|
| Chat / Simple tasks | 6 GB | 8 GB | Llama 3.2 3B (Q4), Gemma 3 4B |
| Coding assistant | 12 GB | 16 GB | Llama 4 Scout 12B (Q4), Qwen 2.5 7B |
| Daily driver / general | 24 GB | 32 GB | Qwen 2.5 72B (Q4), Llama 3.3 70B |
| Research / heavy use | 48 GB | 64 GB | Mixtral 8x22B, Llama 4 Maverick (Q4) |
| Maximum local | 80 GB+ | 96 GB+ | Gemma 4 31B (FP16), Llama 4 Maverick (Q4) |

> 💡 **Rule of thumb**: Every 7B parameter model needs roughly **4 GB VRAM in Q4 quantization**. A 70B model needs about **40 GB in Q4** (or 140 GB in FP16).

---

## The VRAM Formula

Running an LLM locally requires VRAM for three components:

```
Total VRAM = Model Weights + KV Cache + Overhead
```

### 1. Model Weights

This is the dominant factor. The formula depends on the precision:

| Precision | Bytes per Parameter | 7B Model | 13B Model | 70B Model |
|-----------|-------------------|----------|-----------|-----------|
| FP16 (16-bit) | 2 bytes | 14 GB | 26 GB | 140 GB |
| Q8 (8-bit) | 1 byte | 7 GB | 13 GB | 70 GB |
| Q5 (5-bit) | 0.625 bytes | 4.4 GB | 8.1 GB | 44 GB |
| **Q4 (4-bit)** | **0.5 bytes** | **3.5 GB** | **6.5 GB** | **35 GB** |
| Q3 (3-bit) | 0.375 bytes | 2.6 GB | 4.9 GB | 26 GB |

Most local LLM users run **Q4 quantization** as the sweet spot between quality and VRAM efficiency.

### 2. KV Cache (Context Window)

The KV cache stores attention states for the context window. It grows linearly with context length:

```
KV Cache ≈ Context Length × Hidden Dim × Num Layers × Bytes per Head × 2 (key + value) × Batch
```

Rough estimate per million context tokens at Q4:
- **7B model**: ~1-2 GB per million tokens
- **70B model**: ~10-15 GB per million tokens

For a 128K context on a 70B model at Q4, expect **1.3-2 GB** of KV cache overhead.

### 3. Overhead (Runtime + GPU Utilization)

The inference engine (llama.cpp, vLLM, etc.) needs additional VRAM for:
- Graph compilation / kernel buffers: 1-2 GB
- System buffers: 0.5-1 GB
- Headroom for smooth operation: 10-20% of total

**Practical rule**: Subtract ~3-5 GB from your GPU's total VRAM for the overhead.

---

## Quantization: Quality vs VRAM Trade-off

Quantization reduces the precision of model weights, dramatically reducing VRAM usage with minimal quality loss.

| Method | Original Bits | Reduced To | VRAM Savings | Quality Impact | Best For |
|--------|-------------|-----------|-------------|---------------|----------|
| None | 16-bit | 16-bit | 0% | Reference | Baseline |
| GPTQ | 16-bit | 4-bit | 75% | ~2-5% drop | NVIDIA, stable |
| AWQ | 16-bit | 4-bit | 75% | ~2-4% drop | NVIDIA, fast |
| GGUF (Q4_K_M) | 16-bit | ~4.7-bit | ~71% | ~3-6% drop | All GPUs, most flexible |
| GGUF (Q5_K_M) | 16-bit | ~5.5-bit | ~66% | ~2-3% drop | When extra quality matters |
| GGUF (Q8_0) | 16-bit | 8-bit | 50% | ~1% drop | Max quality, low VRAM pressure |

### Which Quantization to Choose?

- **Q4_K_M** (GGUF): Best overall balance. Use for 90% of cases.
- **Q5_K_M** (GGUF): Choose when you have 20%+ headroom and want noticeably better outputs.
- **Q8_0** (GGUF): Choose when VRAM is abundant and quality is critical.
- **Q2_K / IQ2_XS**: Only when you're extremely constrained. Noticeable quality degradation.

---

## Common Models and Their VRAM Requirements

Here are the current most popular open-source models (July 2026) with their VRAM needs:

| Model | Parameters | Q4 (GB) | Q5 (GB) | Q8 (GB) | FP16 (GB) |
|-------|-----------|---------|---------|---------|-----------|
| Llama 3.2 1B | 1B | 0.8 | 1.0 | 1.2 | 2.0 |
| Llama 3.2 3B | 3B | 2.0 | 2.3 | 3.0 | 6.0 |
| Llama 3.2 11B | 11B | 6.5 | 7.5 | 11.0 | 22.0 |
| **Llama 4 Scout** | 12B | 7.0 | 8.1 | 12.0 | 24.0 |
| **Llama 4 Maverick** | 45B | 27.0 | 31.0 | 45.0 | 90.0 |
| Llama 3.1 70B | 70B | 40.0 | 46.0 | 70.0 | 140.0 |
| Llama 3.3 70B | 70B | 40.0 | 46.0 | 70.0 | 140.0 |
| Qwen 2.5 72B | 72B | 41.0 | 47.0 | 72.0 | 144.0 |
| Gemma 3 12B | 12B | 7.0 | 8.1 | 12.0 | 24.0 |
| Gemma 3 27B | 27B | 16.0 | 18.5 | 27.0 | 54.0 |
| Gemma 3n E4B | 14.4B (sparse) | 9.0 | 10.5 | 14.4 | 28.8 |
| Gemma 4 26B | 26B | 15.5 | 18.0 | 26.0 | 52.0 |
| Gemma 4 31B | 31B | 18.5 | 21.5 | 31.0 | 62.0 |
| Mixtral 8x22B | 56B (MoE) | 33.0 | 38.0 | 56.0 | 112.0 |
| Mistral Large 2512 | ~120B (MoE) | 70.0 | 81.0 | 120.0 | 240.0 |

> Note: MoE (Mixture of Experts) models activate only a subset of parameters per token, but VRAM must hold all parameters. Actual inference VRAM may be slightly lower at runtime.

---

## GPU Buying Guide: Consumer vs Mac vs Enterprise

### NVIDIA RTX (Consumer / Pro)

| GPU | VRAM | Price (USD) | Best For |
|-----|------|-----------|----------|
| RTX 4060 Ti 16GB | 16 GB | $450 | Entry-level local LLM |
| RTX 4070 Ti Super 16GB | 16 GB | $800 | 7B-13B models |
| RTX 4080 Super 16GB | 16 GB | $1,000 | 7B models, fast |
| **RTX 4090 24GB** | **24 GB** | **$1,600** | **Sweet spot for local LLM** |
| RTX 5090 32GB | 32 GB | ~$2,000 | 13B-30B models |
| RTX 6000 Ada 48GB | 48 GB | $6,800 | 70B at Q4 |
| H100 80GB | 80 GB | $3,000-4,000 (used) | 70B at Q5+, multi-GPU |
| H100 80GB x2 | 160 GB | $6,000-8,000 | FP16 70B, multi-model |

### Apple Mac (Unified Memory)

| Machine | Unified Memory | Best For |
|---------|---------------|----------|
| MacBook Pro M4 24GB | 24 GB | 7B models at Q4/Q5 |
| MacBook Pro M4 32GB | 32 GB | 13B models at Q4 |
| Mac Studio M2 Max 64GB | 64 GB | 70B at Q4, slow |
| **Mac Studio M3 Max 128GB** | **128 GB** | **70B at Q5/Q8, 26B at FP16** |
| Mac Studio M4 Ultra 192GB | 192 GB | 70B at FP16, 31B Q4 fast |

**Mac vs NVIDIA**: Mac unified memory lets you load much larger models but inference is **3-8x slower** than NVIDIA. For 7B-13B models, NVIDIA wins on speed. For 70B+, Mac is often the only affordable option.

### Multi-GPU Scaling

If a single GPU can't hold your model:

| Setup | Effective VRAM | Models Possible |
|-------|---------------|-----------------|
| 2× RTX 4090 | 48 GB (split) | 13B at Q5, 70B at Q3 |
| 2× RTX 4090 + vLLM | 48 GB (tensor parallel) | 70B at Q4 |
| 4× RTX 4090 | 96 GB (split) | 70B at Q5/Q8 |
| 8× A100 80GB | 640 GB | Any model at FP16 |

---

## Recommended VRAM by Budget

### $500 Budget → 16 GB VRAM

- RTX 4060 Ti 16 GB (used)
- Good for: Llama 3.2 11B at Q4, Gemma 3 12B at Q4
- Use GGUF Q4_K_M quantization

### $1,600 Budget → 24 GB VRAM (Best Value)

- RTX 4090 24 GB
- Good for: Llama 4 Scout at Q4, 70B at Q3 (cramped)
- Best single-GPU local LLM card

### $2,000 Budget → 32 GB VRAM

- RTX 5090 32 GB (or two used RTX 3090s = 24 GB)
- Good for: Llama 4 Maverick at Q4, 70B at Q4
- Strong daily driver

### $6,500+ Budget → 48-80 GB VRAM

- RTX 6000 Ada 48 GB or used H100 80 GB
- Good for: 70B at Q5/Q8, multi-GPU setups
- Production / research grade

---

## Key Takeaways

1. **Q4 quantization is the sweet spot** — 75% VRAM reduction with minimal quality loss.
2. **24 GB (RTX 4090) is the sweet spot GPU** — fits 13B at Q5 and 70B at Q3.
3. **Mac unified memory wins for size** — a 128 GB Mac can run 70B at Q5 where NVIDIA needs two cards.
4. **Always leave 3-5 GB headroom** for KV cache and runtime overhead.
5. **MoE models** require VRAM for all parameters but activate only a fraction — VRAM doesn't scale with active params.

---

## Calculate Your Exact VRAM Needs

Don't guess — use our **[free VRAM calculator](/)** to get exact requirements for any model. Input the model name, quantization level, and context window, and see precisely how much VRAM you need.

Compare GPTQ, AWQ, and GGUF formats side by side.

---

## Further Reading

- Compare API costs across GPT-5.6, Claude Opus 4.8, and DeepSeek V4 in our **[Token Cost Comparison](/blog/gpt-5-vs-claude-vs-deepseek-token-cost-comparison-2026)**.
- Try the **[Token Cost Calculator](/)** for your specific usage patterns.

---

*Built by @slashman413. Pricing and model availability accurate as of July 2026. Check [ko-fi.com/ytstories0413](https://ko-fi.com/ytstories0413) to support.*

---

## 中文對照 — 本地 LLM 需要多少顯存？2026 完整指南

**最後更新：2026 年 7 月。測試環境：DGX GB10、NVIDIA RTX 4090、Mac Studio M2 Max。**

## 快速答案：顯存速查表

| 使用情境 | 最低顯存 | 推薦顯存 | 示例模型 |
|---------|---------|---------|---------|
| 聊天 / 簡單任務 | 6 GB | 8 GB | Llama 3.2 3B (Q4)、Gemma 3 4B |
| 程式碼助手 | 12 GB | 16 GB | Llama 4 Scout 12B (Q4)、Qwen 2.5 7B |
| 日常使用 / 通用 | 24 GB | 32 GB | Qwen 2.5 72B (Q4)、Llama 3.3 70B |
| 研究 / 重度使用 | 48 GB | 64 GB | Mixtral 8x22B、Llama 4 Maverick (Q4) |
| 最大本地部署 | 80 GB+ | 96 GB+ | Gemma 4 31B (FP16)、Llama 4 Maverick (Q4) |

> 💡 **經驗法則**：每 7B 參數模型在 Q4 量化下大約需要 **4 GB 顯存**。70B 模型在 Q4 下需要約 **40 GB**（或 FP16 下 140 GB）。

---

## 顯存估算公式

在本地運行 LLM 需要為三個組分配顯存：

```
總顯存 = 模型權重 + KV 快取 + 額外負荷
```

### 1. 模型權重（主要因素）

取決於精度：

| 精度 | 每參數字節數 | 7B 模型 | 13B 模型 | 70B 模型 |
|------|------------|--------|---------|---------|
| FP16（16 位元） | 2 位元組 | 14 GB | 26 GB | 140 GB |
| Q8（8 位元） | 1 位元組 | 7 GB | 13 GB | 70 GB |
| Q5（5 位元） | 0.625 位元組 | 4.4 GB | 8.1 GB | 44 GB |
| **Q4（4 位元）** | **0.5 位元組** | **3.5 GB** | **6.5 GB** | **35 GB** |
| Q3（3 位元） | 0.375 位元組 | 2.6 GB | 4.9 GB | 26 GB |

大多數本地 LLM 使用者以 **Q4 量化** 作為品質與顯存效率的最佳平衡點。

### 2. KV 快取（上下文窗口）

KV 快取儲存上下文窗口的注意力狀態，隨上下文長度線性增長：

```
KV 快取 ≈ 上下文長度 × 隱藏維度 × 層數 × 每頭位元數 × 2（key + value）× 批次
```

Q4 下每百萬上下文 token 的粗略估計：
- **7B 模型**：每百萬 token 約 1-2 GB
- **70B 模型**：每百萬 token 約 10-15 GB

對 70B 模型在 128K 上下文下使用 Q4，預計 KV 快取額外負荷為 **1.3-2 GB**。

### 3. 額外負荷（執行時間 + GPU 利用率）

推理引擎（llama.cpp、vLLM 等）需要額外顯存：
- 圖表編譯 / 核心緩衝區：1-2 GB
- 系統緩衝區：0.5-1 GB
- 平滑運行的緩衝：總體的 10-20%

**實用規則**：從 GPU 總顯存中扣除約 3-5 GB 作為額外負荷。

---

## 量化：品質與顯存的權衡

量化降低模型權重的精度，大幅減少顯存使用，品質損失最小。

| 方法 | 原始位元數 | 降低至 | 顯存節省 | 品質影響 | 最佳場景 |
|------|-----------|-------|---------|---------|---------|
| 無量化 | 16 位元 | 16 位元 | 0% | 基準 | 對照 |
| GPTQ | 16 位元 | 4 位元 | 75% | 約 2-5% 下降 | NVIDIA、穩定 |
| AWQ | 16 位元 | 4 位元 | 75% | 約 2-4% 下降 | NVIDIA、快速 |
| GGUF（Q4_K_M） | 16 位元 | ~4.7 位元 | ~71% | 約 3-6% 下降 | 所有 GPU、最靈活 |
| GGUF（Q5_K_M） | 16 位元 | ~5.5 位元 | ~66% | 約 2-3% 下降 | 需要額外面質時 |
| GGUF（Q8_0） | 16 位元 | 8 位元 | 50% | 約 1% 下降 | 最大品質、低顯存壓力 |

### 應該選擇哪種量化？

- **Q4_K_M**（GGUF）：整體最佳平衡。90% 的情境使用此選項。
- **Q5_K_M**（GGUF）：當你有 20%+ 緩衝空間且需要明顯更好的輸出時選擇。
- **Q8_0**（GGUF）：當顯存充足且品質至關重要時選擇。
- **Q2_K / IQ2_XS**：僅在你極度受限時使用。品質有明顯下降。

---

## 常見模型及其顯存需求

以下是 2026 年 7 月目前最流行的開源模型及其顯存需求：

| 模型 | 參數 | Q4 (GB) | Q5 (GB) | Q8 (GB) | FP16 (GB) |
|------|------|--------|--------|--------|----------|
| Llama 3.2 1B | 1B | 0.8 | 1.0 | 1.2 | 2.0 |
| Llama 3.2 3B | 3B | 2.0 | 2.3 | 3.0 | 6.0 |
| Llama 3.2 11B | 11B | 6.5 | 7.5 | 11.0 | 22.0 |
| **Llama 4 Scout** | 12B | 7.0 | 8.1 | 12.0 | 24.0 |
| **Llama 4 Maverick** | 45B | 27.0 | 31.0 | 45.0 | 90.0 |
| Llama 3.1 70B | 70B | 40.0 | 46.0 | 70.0 | 140.0 |
| Llama 3.3 70B | 70B | 40.0 | 46.0 | 70.0 | 140.0 |
| Qwen 2.5 72B | 72B | 41.0 | 47.0 | 72.0 | 144.0 |
| Gemma 3 12B | 12B | 7.0 | 8.1 | 12.0 | 24.0 |
| Gemma 3 27B | 27B | 16.0 | 18.5 | 27.0 | 54.0 |
| Gemma 3n E4B | 14.4B (稀疏) | 9.0 | 10.5 | 14.4 | 28.8 |
| Gemma 4 26B | 26B | 15.5 | 18.0 | 26.0 | 52.0 |
| Gemma 4 31B | 31B | 18.5 | 21.5 | 31.0 | 62.0 |
| Mixtral 8x22B | 56B (MoE) | 33.0 | 38.0 | 56.0 | 112.0 |
| Mistral Large 2512 | ~120B (MoE) | 70.0 | 81.0 | 120.0 | 240.0 |

> 注意：MoE（混合專家）模型每個 token 只激活部分參數，但顯存必須容納所有參數。實際推理時的顯存可能略低。

---

## GPU 選購指南：消費級 vs Mac vs 企業級

### NVIDIA RTX（消費級 / 專業級）

| 顯示卡 | 顯存 | 價格（美元） | 最佳場景 |
|-------|------|------------|---------|
| RTX 4060 Ti 16GB | 16 GB | $450 | 入門級本地 LLM |
| RTX 4070 Ti Super 16GB | 16 GB | $800 | 7B-13B 模型 |
| RTX 4080 Super 16GB | 16 GB | $1,000 | 7B 模型、快速 |
| **RTX 4090 24GB** | **24 GB** | **$1,600** | **本地 LLM 最佳平衡點** |
| RTX 5090 32GB | 32 GB | ~$2,000 | 13B-30B 模型 |
| RTX 6000 Ada 48GB | 48 GB | $6,800 | 70B Q4 |
| H100 80GB | 80 GB | $3,000-4,000（二手） | 70B Q5+、多 GPU |
| H100 80GB x2 | 160 GB | $6,000-8,000 | FP16 70B、多模型 |

### Apple Mac（統一記憶體）

| 機型 | 統一記憶體 | 最佳場景 |
|------|-----------|---------|
| MacBook Pro M4 24GB | 24 GB | 7B 模型 Q4/Q5 |
| MacBook Pro M4 32GB | 32 GB | 13B 模型 Q4 |
| Mac Studio M2 Max 64GB | 64 GB | 70B Q4、速度較慢 |
| **Mac Studio M3 Max 128GB** | **128 GB** | **70B Q5/Q8、26B FP16** |
| Mac Studio M4 Ultra 192GB | 192 GB | 70B FP16、31B Q4 快速 |

**Mac vs NVIDIA**：Mac 統一記憶體讓你可以載入更大的模型，但推理速度比 NVIDIA **慢 3-8 倍**。對於 7B-13B 模型，NVIDIA 在速度上取勝。對於 70B+，Mac 通常是唯一負擔得起的選擇。

### 多 GPU 擴展

如果單張 GPU 無法容納你的模型：

| 設定 | 有效顯存 | 可跑模型 |
|------|---------|---------|
| 2× RTX 4090 | 48 GB（分割） | 13B Q5、70B Q3（擁擠） |
| 2× RTX 4090 + vLLM | 48 GB（張量平行） | 70B Q4 |
| 4× RTX 4090 | 96 GB（分割） | 70B Q5/Q8 |
| 8× A100 80GB | 640 GB | 任何模型 FP16 |

---

## 依預算推薦顯存

### 500 美元預算 → 16 GB 顯存

- RTX 4060 Ti 16 GB（二手）
- 適用：Llama 3.2 11B Q4、Gemma 3 12B Q4
- 使用 GGUF Q4_K_M 量化

### 1,600 美元預算 → 24 GB 顯存（最佳性價比）

- RTX 4090 24 GB
- 適用：Llama 4 Scout Q4、70B Q3（擁擠）
- 最佳單 GPU 本地 LLM 顯示卡

### 2,000 美元預算 → 32 GB 顯存

- RTX 5090 32 GB（或兩張二手 RTX 3090 = 24 GB）
- 適用：Llama 4 Maverick Q4、70B Q4
- 強大的日常使用

### 6,500 美元以上預算 → 48-80 GB 顯存

- RTX 6000 Ada 48 GB 或二手 H100 80 GB
- 適用：70B Q5/Q8、多 GPU 設定
- 生產 / 研究級

---

## 重點總結

1. **Q4 量化是最佳平衡點** — 顯存減少 75%，品質損失最小。
2. **24 GB（RTX 4090）是最佳平衡點 GPU** — 可在 Q5 下運行 13B，在 Q3 下運行 70B。
3. **Mac 統一記憶體在容量上取勝** — 128 GB Mac 可在 NVIDIA 需要兩張卡的狀況下運行 70B Q5。
4. **始終保留 3-5 GB 緩衝** 給 KV 快取和執行時間額外負荷。
5. **MoE 模型** 的顯存需求取決於所有參數，而非激活參數 — 顯存不會隨激活參數縮減。

---

## 計算你的精確顯存需求

不要猜測 — 使用我們的 **[免費顯存計算器](/)** 來獲得任何模型的精確需求。輸入模型名稱、量化級別和上下文窗口，即可查看你確切需要多少顯存。

並排比較 GPTQ、AWQ 和 GGUF 格式。

---

## 延伸閱讀

- 在我們的 **[Token 成本比較](/blog/gpt-5-vs-claude-vs-deepseek-token-cost-comparison-2026)** 中比較 GPT-5.6、Claude Opus 4.8 和 DeepSeek V4 的 API 成本。
- 使用 **[Token 成本計算器](/)** 來模擬你的特定使用模式。

---

*由 @slashman413 打造。定價和模型可用性於 2026 年 7 月準確。查看 [ko-fi.com/ytstories0413](https://ko-fi.com/ytstories0413) 支持開發。*