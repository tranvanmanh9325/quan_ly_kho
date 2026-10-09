# Workflow Templates Reference

This reference document provides standardized templates for feature planning, peer review evaluations, and technical verification reports.

## Feature Implementation Plan Template

```markdown
# Feature Plan: [Feature Name]

## 1. Problem Statement and Scope
- User story / Bug report:
- Affected domain objects:
- Success criteria:

## 2. Dependency Order
1. Model modifications:
2. Migration considerations:
3. Serializer input/output validation:
4. View and Service implementations:
5. URL routing:
6. Automated test scenarios:

## 3. Invariants and Safety Checks
- Capacity constraint checks:
- State machine transition rules:
- Data safety evaluation (soft delete / foreign keys):
- Potential backward incompatibility risks:

## 4. Verification Steps
- Commands to execute:
- Expected results:
```

## Peer Review Checklist Template

Use this checklist during cross-review and code reviews:

- [ ] Does the implementation maintain 100% backward compatibility for existing imports?
- [ ] Are all views thin, with business validation properly located in serializers/models/services?
- [ ] Are queries optimized using `select_related` or database-level aggregations?
- [ ] Are all docstrings and code comments written in English, explaining WHY?
- [ ] Is every test case behavior-driven, asserting explicit status codes and data states?
- [ ] Are sensitive environment variables isolated without hardcoded credentials?

## Verification Report Template

```markdown
# Verification Report: [Task Name]

## Command Outputs
### 1. System Check
- Command: `python manage.py check`
- Result: System check identified no issues (0 silenced).

### 2. Migration Check
- Command: `python manage.py makemigrations --check --dry-run`
- Result: No changes detected.

### 3. Automated Tests
- Command: `python manage.py test`
- Result: Ran X tests in Ys - OK.

### 4. Markdown Quality Check
- Command: `npx markdownlint-cli2 "README.md" ".claude/**/*.md"`
- Result: Summary: 0 issues in 0 files.
```
