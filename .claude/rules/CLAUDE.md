# Warehouse Management Project Rules Index

Welcome to the Warehouse Management Backend project engineering rules directory. This repository organizes governance, coding conventions, database safety policies, and architectural standards into focused rule files under `.claude/rules/`.

## Claude Code Rules Architecture

Claude Code automatically loads rules from `.claude/rules/*.md` into context:

- **Global Rules**: Files without YAML frontmatter are loaded into context memory for all tasks and commands.
- **Path-Scoped Rules**: Files containing YAML frontmatter with `paths:` patterns are dynamically loaded when interacting with matching file paths.
- **Memory Inspection**: Use the `/memory` command in Claude Code CLI to inspect active rules and project memory context.

## Rules Directory Index

The engineering standards are organized into 11 focused rule documents:

### Core Architecture and Setup

- [Project Overview and Tech Stack](overview-and-stack.md): Technology components, Python 3.14+, Django 6.1+, DRF 3.18+, PostgreSQL 18, and local virtualenv configuration.
- [Project Structure and Modular Architecture](project-structure.md): Per-object package layout (`warehouse/models/`, `serializers/`, `views/`, `services/`, `tests/`) and backwards-compatible re-exports.
- [Core Collaboration Principles](collaboration-principles.md): Human-in-the-loop guidelines, Plan Before Code workflow, DRY, and clean architecture tenets.

### Coding and API Conventions

- [Python and Django Coding Standards](python-django-style.md): PEP 8 formatting, naming conventions, and English docstrings explaining *why* decisions were made. *(Scoped to `**/*.py`)*
- [RESTful API Conventions](rest-api-conventions.md): Resource naming, HTTP status codes, Token Authentication headers, and standardized JSON error envelopes. *(Scoped to views, serializers, urls)*
- [Database and ORM Guidelines](database-and-orm.md): Query optimization (`select_related`), model invariants (`clean()`, `full_clean()`), and migration safety. *(Scoped to models, services)*

### Safety, Security, and Governance

- [Data Safety and Database Deletion Policy](data-safety-and-deletion.md): Soft delete vs hard delete, analysis of `CASCADE` vs `PROTECT`, 8 strictly forbidden destructive operations for AI agents, 5-step backup/restore SOP, and test database isolation.
- [Security and Secrets Management](security-and-secrets.md): Zero leaks policy, `.env` protection, token authentication security, and view permissions.

### Testing, Operations, and Version Control

- [Automated Testing Standards](testing.md): Modular `warehouse/tests/` architecture, `APITestCase` conventions, required test coverage matrix, and test isolation. *(Scoped to tests)*
- [Git and Commit Standards](git-and-commits.md): Conventional Commits specification, English commit messages, and forbidden autonomous commits.
- [Standard Development Commands](dev-commands.md): Quick reference for virtualenv activation, server startup, migrations, seeding, testing, and markdownlint verification.
