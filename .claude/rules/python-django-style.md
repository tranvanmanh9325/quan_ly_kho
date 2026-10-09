---
paths:
  - "**/*.py"
---

# Python and Django Coding Standards

This document establishes coding conventions, PEP 8 compliance, naming rules, and documentation standards for all Python source code in the project.

## PEP 8 and Formatting Guidelines

- **Indentation**: Exactly 4 spaces per indentation level. Tabs are forbidden.
- **Line Length**: Limit all lines to 79-88 characters where practical to maintain readability across split editor panes.
- **Imports**: Group imports in standard PEP 8 order with one blank line separating each group:
  1. Standard library imports (e.g. `decimal`, `datetime`, `os`)
  2. Related third-party imports (e.g. `django`, `rest_framework`)
  3. Local application imports (e.g. `warehouse.models`, `warehouse.serializers`)
- **Blank Lines**: Two blank lines between top-level class and function definitions; one blank line between methods inside classes.

## Naming Conventions

- **Variables and Functions**: Use `snake_case` (e.g. `current_total_quantity`, `adjust_stock`, `validate_sku`).
- **Classes and Types**: Use `PascalCase` (e.g. `WarehouseViewSet`, `ProductSerializer`, `StockStatus`).
- **Constants and Enumeration Choices**: Use `UPPER_SNAKE_CASE` (e.g. `IN_STOCK`, `LOW_STOCK`, `OUT_OF_STOCK`, `MAX_CAPACITY_LIMIT`).
- **Database Tables**: Follow Django ORM table naming conventions (`warehouse_warehouse`, `warehouse_product`).
- **Test Modules and Methods**: Prefix test files with `test_` and test methods with `test_` followed by an explicit description of the behavior being verified (e.g. `test_adjust_stock_insufficient_quantity_returns_400`).

## Code Comments and Docstrings

- **Language Requirement**: All comments, inline notes, and docstrings must be written entirely in English.
- **Explain WHY, Not WHAT**:
  - Do not write redundant comments stating obvious logic (e.g. avoid `# Increment quantity by 1`).
  - Focus comments on explaining the rationale, business constraints, technical trade-offs, and edge case mitigation (e.g. `# Use select_related to prevent N+1 queries when computing warehouse capacity utilization`).
- **Docstring Format**: Write concise Sphinx or Google-style docstrings for public classes, service functions, and critical model methods.
