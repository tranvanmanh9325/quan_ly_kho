# Git and Commit Standards

This document establishes Git version control protocols, commit message conventions, and commit authorization policies for the project.

## Commit Authorization Policy

- **No Autonomous Commits**: AI agents are strictly forbidden from executing `git commit` or `git push` autonomously unless explicitly instructed to do so by the human engineer or user request.
- **Review Before Staging**: Prior to staging files, conduct a complete diff review (`git diff`, `git status`) to ensure only relevant, intended modifications are included.

## Conventional Commits Specification

Commit messages must strictly follow the Conventional Commits specification written in English:

- **Format**: `<type>(<scope>): <short description>` (scope is optional).
- **Message Guidelines**:
  - Use imperative, present tense: "add" instead of "added" or "adds".
  - Do not capitalize the first letter of the description.
  - Do not end the description line with a period.

## Standard Commit Types

- `feat`: A new user-facing or API feature (e.g. `feat: add warehouse stock adjustment endpoint`).
- `fix`: A bug fix or error correction (e.g. `fix: resolve capacity overflow validation check`).
- `refactor`: Code restructuring without modifying behavior or fixing bugs (e.g. `refactor: split warehouse models into per-object modules`).
- `test`: Adding or modifying automated tests (e.g. `test: add unit tests for warehouse crud and auth`).
- `docs`: Documentation updates, skill definitions, or markdown adjustments (e.g. `docs: update api documentation and postman collection`).
- `chore`: Maintenance tasks, configuration changes, or dependency updates (e.g. `chore: update environment configurations`).

## Atomic and Reviewable Commits

- Group related changes logically into atomic commits that represent a single coherent unit of work.
- Never bundle unrelated refactorings or cosmetic changes into critical feature or bug-fix commits.
