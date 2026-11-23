# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased]

## [0.1.2] - 2026-11-23

### Fixed
- Transcribe `-ed` suffix as `/ɪd/` after `t` and `d` in fallback phonetic rules.

## [0.1.1] - 2026-11-22

### Fixed
- Added context-sensitive vowel rules (`i -> aɪ`) for `-izer`/`-iser`, `-izing`/`-ising`, and `-ization`/`-isation` suffixes so segmented words (such as *dockerizing*) transcribe accurately.

## [0.1.0] - 2026-11-22

### Added
- Support for case-insensitive and exact-case `custom_vocabulary` overrides.

### Fixed
- Corrected prevocalic `/ɝ/` and `/ɜr/` -> `/ɜɹ/` transcription errors in the base phonetic dictionary.
