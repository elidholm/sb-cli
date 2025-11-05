# Second Brain CLI

A CLI tool for managing my personal note-taking system built around Obsidian vaults and Git version control.

<p align="center">
    <a href="https://github.com/elidholm/sb-cli/actions/workflows/ci.yml"><img align="center" src="https://github.com/elidholm/sb-cli/actions/workflows/ci.yml/badge.svg" alt="github actions"></a>
    <a href="https://github.com/elidholm/sb-cli/commits/master"><img align="center" src="https://img.shields.io/github/commit-activity/m/elidholm/sb-cli" alt="commit frequency"></a>
</p>

---

## Overview

This is my personal "Second Brain" management system - a CLI tool that helps me organize, sync, and maintain my digital notes using the PARA (Projects-Areas-Resources-Archives) methodology with an additional Inbox for quick capture.

**Note**: This tool is specifically tailored to my personal workflow and note-taking habits. While it might be useful to others, it's built around my specific needs and preferences. That said, I'm always open to suggestions, ideas, and contributions from the community!

## Features

- **Note Management**: Create new notes with structured templates
- **Git Sync**: Automatic synchronization with remote Git repositories
- **Vault Info**: Get overview of your note structure and status
- **PARA Structure**: Organized folder structure following PARA methodology:
  - `0_Inbox` - Quick capture and temporary notes
  - `1_Projects` - Active projects with deadlines
  - `2_Areas` - Ongoing areas of responsibility
  - `3_Resources` - Reference materials and knowledge
  - `4_Archive` - Completed projects and old notes

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/elidholm/sb-cli.git
cd sb-cli

# Install the CLI tool
pip install -e .
```

### Basic Usage

```bash
# Sync your vault with remote repository
sb sync

# Get vault information and status
sb info

# Create a new note
sb new empty "Note Title"

# Create a new note with extra hashtags at the bottom
sb new empty "Note Title" --tags "tag1,tag2,tag3"
```

## Configuration

Create a configuration file at `~/.sb_config.yml`:

```yaml
---
vault_path: /path/to/your/obsidian/vault
inbox_folder: 0_Inbox
```

## Commands

### Sync

Synchronize your vault with a remote Git repository:

```bash
sb sync [BRANCH] [OPTIONS]

# Examples
sb sync master
sb sync feature -m "Custom commit message"
sb sync master --path /custom/vault/path
```

### Info

Display information about your vault and system status:

```bash
sb info [OPTIONS]

# Examples
sb info
sb info --path /custom/vault/path
sb info --config ~/custom_config.yml
```

### New

Create new notes with templates (see `new` subcommand for more options):

```bash
sb new empty [NOTE_TITLE] [OPTIONS]
```

## Development

### Running Tests

The project includes comprehensive unit and integration tests:

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run with coverage
make coverage
```

### Code Style

This project follows PEP 8 guidelines and uses type hints for better code maintainability.

## Contributing

While this is primarily a personal tool, I welcome:

- Bug reports and fixes
- Documentation improvements
- Suggestions for features that might benefit others
- Testing improvements and edge case coverage

Please feel free to open issues or submit pull requests if you have ideas that could make this tool more useful!

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI functionality
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Inspired by the "Second Brain" concept and PARA methodology
- Integrated with Obsidian for note management

---

*Remember: This tool reflects my personal workflow. Your mileage may vary, but I'm happy to discuss how it might work for you!*
