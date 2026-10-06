"""Private local worker. Never downloads models, logs texts, or calls a provider."""

import importlib
import importlib.metadata
import json
import sys
import time
from pathlib import Path

from folkverse.guide_embeddings import MODEL_VERSION, file_hash


def main() -> None:
    started = time.monotonic()
    directory = Path(sys.argv[1])
    marker = json.loads((directory / "folkverse-model.json").read_text())
    if marker["model_version"] != MODEL_VERSION or not marker["files"]:
        raise ValueError("Model identity mismatch")
    # Verify the downloaded local model/configs; never resolve a network model name.
    for name, expected in marker["files"].items():
        target = directory / name
        if target.resolve().is_relative_to(directory.resolve()) is False:
            raise ValueError("Invalid model file")
        if file_hash(target) != expected:
            raise ValueError("Model file changed")
    payload = json.loads(sys.stdin.buffer.read(64 * 1024 * 1024 + 1))
    texts = payload["texts"]
    if not isinstance(texts, list) or not 1 <= len(texts) <= 5000:
        raise ValueError("Invalid embedding input")
    if any(not isinstance(t, str) or not 1 <= len(t) <= 12000 for t in texts):
        raise ValueError("Invalid embedding text")
    torch = importlib.import_module("torch")
    torch.set_num_threads(2)
    model = importlib.import_module("sentence_transformers").SentenceTransformer(
        str(directory),
        device="cpu",
        local_files_only=True,
        trust_remote_code=False,
        token=False,
        model_kwargs={"torch_dtype": torch.float32},
    )
    model.max_seq_length = 8192
    # Reject oversize text rather than silently embedding a truncated passage.
    for text in texts:
        if len(model.tokenizer(text, truncation=False)["input_ids"]) > 8192:
            raise ValueError("Embedding input exceeds model context")
    vectors = model.encode(
        texts,
        batch_size=1,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).tolist()
    versions = ";".join(
        f"{name}:{importlib.metadata.version(name)}"
        for name in ("sentence-transformers", "torch", "transformers")
    )
    print(
        json.dumps(
            {
                "vectors": vectors,
                "encoder_version": versions,
                "elapsed_ms": (time.monotonic() - started) * 1000,
            },
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Errors intentionally exclude private input, model paths and dependency tracebacks.
        sys.exit(1)
