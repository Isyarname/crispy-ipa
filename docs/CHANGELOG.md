# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

## [0.1.1] - 2026-11-22

### Fixed
- Added context-sensitive vowel rules (`i -> aɪ`) for `-izer`/`-iser`, `-izing`/`-ising`, and `-ization`/`-isation` suffixes so segmented words (such as *dockerizing*) transcribe accurately.

## [0.1.0] - 2026-11-22

### Added
- Initial release of `crispy-ipa`.
- Hybrid English-to-simplified-IPA transcription engine combining a 125,000+ word dictionary, morpheme-aware right-to-left word segmentation, and a parallel non-destructive rule engine with LRU caching.
- Custom phonological DSL (`L -> R / C`) and build scripts (`scripts/build_rules.py`, `scripts/convert_dict.py`) for compiling dictionary and rules into `.pkl` artifacts.
- Support for case-insensitive and exact-case `custom_vocabulary` overrides.
