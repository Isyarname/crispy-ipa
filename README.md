# crispy-ipa

Fast English-to-IPA transcription in pure Python with zero external dependencies.

Designed as a fast, deterministic intermediate grapheme-to-phoneme (G2P) stage for practical transcription pipelines.

## Features

* **Zero external dependencies:** built entirely on the Python standard library.
* **Hybrid engine:** combines a 125,000+ word phonetic dictionary, compound-word splitting, and a non-destructive rule engine.
* **High performance:** sub-millisecond processing without neural networks, heavy parsing, or sentence-level context analysis, backed by LRU caching.
* **Custom vocabulary support:** easily extend or override transcriptions for domain-specific terms and proper nouns.

## Installation

```bash
pip install crispy-ipa
```

## Usage

```python
from crispy_ipa import Transcriber

t = Transcriber(custom_vocabulary={
    "nginx": "ˈɛndʒɪnˈɛks",
    "ChatGPT": "ˈtʃætˈdʒiˈpiˈti",
})
print(t.transcribe("ChatGPT and nginx"))
# ˈtʃætˈdʒiˈpiˈti ˈænd ˈɛndʒɪnˈɛks
```
