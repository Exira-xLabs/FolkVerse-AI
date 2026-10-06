# Versioned BGE-M3 and hybrid retrieval

Current integration update (6 October 2026): actual PostgreSQL and bounded Ollama EN/ZH
browser generation now pass; pinned BGE CPU inference/indexing is measured. The root
configuration remains demo/zero quota; live verification uses process-only bounded settings.
[Current report](../report/PHASE_03_COMPLETION.md), [personality policy](jinyao-personality.md),
[coverage](guide-coverage.md) and [handoff](phase-03-handoff.md) supersede earlier unavailable
integration statements below. Broader classified explanations and independent human quality
remain pending. Beginner/deeper presentation uses a lossless inventory grammar; exact
reviewed claims, attribution, revocation and browser publication validation remain enforced.


Push audit: the CPU worker environment now uses a runtime/localization allowlist, excluding database URLs and custom credential names as well as API keys. Cancellation/timeout checks cover this isolation.

Phase 03 Part 5, 6 October 2026 (Asia/Shanghai). The offline index/query path and explicit lexical fallback are implemented. Actual dense inference and production PostgreSQL integration are unverified here; semantic search stays disabled by default. New review candidates remain unpublished.

BGE-M3's official model card documents 1024-dimensional multilingual dense embeddings, an 8192-token context, and use without a special query instruction. It also supports sparse and multi-vector retrieval. This implementation uses its **dense** output plus the existing BM25/CJK baseline, rather than claiming to implement all three model heads. [BAAI model card](https://huggingface.co/BAAI/bge-m3), [Sentence Transformers reference](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html).

The pinned model revision is `5617a9f61b028005a4858fdac845db406aefb181`. Identity includes CLS pooling, unit-normalized float32 vectors, the 8192-token limit and pipeline version. Optional dependencies pin Sentence Transformers 6.1.0 and PyTorch 2.9.1 from the CPU index; the lockfile resolves Linux to `2.9.1+cpu`. Encoder artifacts also record the actual Sentence Transformers/PyTorch/Transformers versions. Different encoder versions cannot be silently mixed.

Model preparation is an explicit operator download. It fetches only the pinned model/config/tokenizer files and records their SHA-256 hashes. Visitor requests use a local path with offline loading, remote code disabled and no model download. The worker verifies files, checks token lengths without truncation, encodes whole passages in batches of one on two CPU threads, and emits normalized vectors. No question is passed in process arguments or written to disk/logs; operational credentials are removed from the child environment. Dense requests use a bounded subprocess, killed and reaped on timeout/cancellation. One query/build per encoder instance runs at a time; busy requests fall back explicitly. Each query reloads the model, so cold load/hash verification costs remain real. This favors bounded memory and reliable cancellation over warm-query throughput; multiple API workers can still run separate processes.

`guide_index build` reads only currently eligible reviewed evidence from PostgreSQL. It writes a private atomic JSON artifact containing passage IDs, fingerprints, model/encoder versions, corpus version and vectors, with no duplicate passage text or user queries. The build rechecks the whole corpus before publication. It preserves the previous complete index on failure. Artifacts are bounded to 5000 passages and 128 MiB. The small-corpus artifact is an initial implementation rather than a pgvector search service; production scale needs a measured indexing strategy. PostgreSQL remains the authority for eligibility and session/usage state.

Each retrieval refreshes publication/rights/locale/exhibit gates. A missing, malformed or oversized artifact, changed corpus/review/source attribution, changed model/encoder, absent model, timeout or busy encoder produces labelled lexical-only results. Any changed eligible metadata invalidates the entire index; rebuild explicitly rather than silently reuse stale rows. Final answer publication retains Part 3–4's evidence/ownership rechecks. Dense similarity never validates a claim or creates historical coverage.

Ranking unions the top 50 lexical and dense candidates using reciprocal rank fusion (`1 / (60 + rank)`), with stable passage-ID tie breaks. Dense candidates use an initial configurable cosine floor of 0.3. That floor is a heuristic, not a scored confidence threshold. Language and exhibit scope filter both rankings before fusion; complete-passage character/count limits still apply afterward. Answer metadata exposes retrieval/embedding mode, artifact versions and actual query embedding duration. Jinyao labels keyword-only versus keyword-and-semantic matching. The conservative complete-passage question/claim harness remains unchanged.

Configuration is optional. Relative model/index paths resolve against the repository root:

```dotenv
EMBEDDING_ENABLED=false
EMBEDDING_MODEL_DIR=.local/models/bge-m3
EMBEDDING_INDEX_PATH=.local/retrieval/bge-m3.json
EMBEDDING_QUERY_TIMEOUT_SECONDS=15
EMBEDDING_MIN_COSINE=0.3
```

Operator commands:

```sh
uv sync --project apps/api --extra embeddings
uv run --project apps/api --extra embeddings python -m folkverse.guide_index prepare
uv run --project apps/api --extra embeddings python -m folkverse.guide_index build
uv run --project apps/api --extra embeddings python -m folkverse.guide_index inspect
uv run --project apps/api --extra embeddings python -m folkverse.guide_index benchmark --output report/evidence/phase03-part5/current-runtime.json
```

Use the extra when starting a fresh installation with semantic retrieval enabled. Keep it disabled until the actual model, current DB index and hardware deadline are verified. Missing dependencies remain an explicit lexical fallback.

The benchmark can instead inspect the exported corpus in disposable SQLite with `--manifest data/manifests/corpus.json`. This is labelled `offline_export_not_live_database`; it never supplies the runtime corpus or writes the configured index. Its local timestamp adapter preserves ISO timezones so the unchanged restore/review fingerprint checks still apply. A modified approved passage fails those checks. Benchmark indexes are temporary. Lexical timings exclude eligibility/DB reads; dense timing includes cold worker/hash/model load. Diagnostic questions are not the held-out expert evaluation.

This machine installed the CPU dependencies, but the bounded four-minute model download timed out before weights completed; the model identity marker was not created. The actual exported corpus contains two eligible passages. Across six diagnostic EN/ZH questions and 100 lexical repetitions each, median ranking/bundle time was approximately **0.034 ms**, maximum **1.242 ms**, excluding DB reads. All hybrid attempts correctly used lexical-only fallback because no ready index existed. No BGE inference latency, semantic relevance improvement, historical score or production benchmark is claimed. [Runtime evidence](../report/evidence/phase03-part5/runtime-benchmark.json).

[Draft review packet](../data/review-candidates/phase03-part5.json) prepares 13 existing Liaoning bilingual inventory candidates and three previously fetched Met catalog candidates, with attributable URLs, retrieval dates, archive hashes, wording/rights context and required review steps. It creates no new approval, published passage or image eligibility. Human review must resolve exact wording, translation, rights and dependencies; catalog dates remain attributed. [Reproducible exporter](../scripts/prepare-guide-review-candidates.py).
