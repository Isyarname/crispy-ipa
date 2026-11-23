# crispy-ipa

Fast English-to-IPA transcription.

Designed as a fast, deterministic intermediate grapheme-to-phoneme (G2P) stage for practical transcription pipelines.

## Features

* **Simple installation:** pure Python package with zero external dependencies.
* **No skipped unknown words:** covers 125,000+ common English words and falls back to compound splitting and phonetic rules for rare terms or neologisms.
* **Sub-millisecond speed for high-throughput pipelines:** operates without heavy neural models and uses built-in caching to accelerate repeated lookups.
* **Full control over jargon and brand names:** override or add custom pronunciations (like `nginx` or `ChatGPT`) in a single dictionary so your pipeline never mispronounces domain-specific terms.

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
