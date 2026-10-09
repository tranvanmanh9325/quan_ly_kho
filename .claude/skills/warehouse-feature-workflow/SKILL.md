---
name: warehouse-feature-workflow
description: Use this skill when planning, implementing, reviewing, or verifying any feature or bug fix in the warehouse management system, following the Plan-Before-Code workflow, verification checklists, and quality standards.
---

# Warehouse Feature Workflow Skill

This skill defines the end-to-end development methodology, Plan-Before-Code workflow, quality assurance gates, verification checklists, and peer review standards for the Warehouse Management Backend.

## The Plan-Before-Code Workflow

Every feature implementation, bug fix, or architectural refactoring must strictly follow this 4-step sequence:

### Phase 1: Investigation and Impact Assessment

- Inspect existing domain models (`warehouse/models/`), serializers (`warehouse/serializers/`), and views (`warehouse/views/`).
- Trace all calling dependencies (e.g. `urls.py`, `admin.py`, `management/commands/seed_data.py`).
- Identify affected business invariants, such as capacity limits or status state transitions.

### Phase 2: Step-by-Step Architecture Plan

- Formulate a written plan broken into distinct, reviewable steps.
- Specify exact changes across the dependency chain:
  1. Models and migrations (if permitted)
  2. Serializers and validation rules
  3. Domain services or view methods
  4. URL routing definitions
  5. Automated test suites covering happy paths and edge cases
- Obtain engineering alignment before modifying files.

### Phase 3: Ordered Implementation

- Implement changes adhering strictly to the minimal change principle.
- Write clean code adhering to DRY and PEP 8 guidelines.
- Add English comments and docstrings explaining *why* logic was structured.

### Phase 4: Real Execution Verification

- Execute verification commands directly against the runtime environment.
- Never rely on theoretical correctness without observing actual command exit codes and test outputs.

## Mandatory Verification Checklist

Before completing any task or opening a pull request, verify that every item passes:

- [ ] System Configuration Check: `python manage.py check` reports 0 issues.
- [ ] Schema Drift Check: `python manage.py makemigrations --check --dry-run` reports `No changes detected`.
- [ ] Automated Test Suite: `python manage.py test` passes completely (total tests >= 12).
- [ ] Real Smoke Test: Verify key endpoints return correct HTTP status codes against a running development server.
- [ ] Markdown Documentation Quality: `npx markdownlint-cli2 "README.md" ".claude/**/*.md"` reports 0 issues.
- [ ] Code Quality and Security: No hardcoded secrets, clean separation of concerns, backwards-compatible re-exports.

## Detailed Workflow Templates Reference

For feature planning templates, peer review rubrics, and verification logging formats, see [Workflow Templates Reference](references/workflow-templates.md).
