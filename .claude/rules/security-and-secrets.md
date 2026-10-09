# Security and Secrets Management

This document defines confidentiality policies, environment variable handling, credential isolation, and token security standards across the codebase.

## Zero Security Leaks Policy

- **No Hardcoded Secrets**: Under no circumstances should API keys, database passwords, secret keys, or authentication tokens be hardcoded into Python source files, settings, test cases, or fixtures.
- **Git Commit Immunity**: Secrets must never be committed into Git history. All secret credentials must reside in local configuration files excluded by `.gitignore`.
- **Pre-Commit Verification**: Developers and AI agents must review all file diffs before staging to confirm that no credentials or internal infrastructure addresses are exposed.

## Environment Variables and File Isolation

- **Configuration File**: All project settings depend on `.env` loaded via `python-dotenv` within `config/settings.py`.
- **Fail-Fast Validation**: Essential secrets (`SECRET_KEY`, `DB_PASSWORD`) must be validated at startup via `get_required_env()`. Missing values must immediately raise a descriptive `RuntimeError` to abort boot instead of falling back to insecure defaults.
- **Sensitive Variables Managed**:
  - `SECRET_KEY`: Django cryptographic signing key (strictly from environment).
  - `DEBUG`: Must be set to `False` in production contexts.
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL connection parameters.
  - `ALLOWED_HOSTS`: Explicit comma-separated host list parsed from environment (wildcard forbidden in production).
  - `CORS_ALLOWED_ORIGINS`: Explicit origins list parsed from environment (`CORS_ALLOW_ALL_ORIGINS = True` forbidden).
  - `SEED_ADMIN_PASSWORD`: Optional initial admin password for seed_data command.
- **Gitignore Compliance**: Ensure `.env`, `.env.local`, and any database dumps (`*.dump`, `*.sql`) are strictly ignored by `.gitignore`.
- **Seed Data Credential Security**: Management commands (e.g. `seed_data`) must never hardcode or log passwords/tokens. If `SEED_ADMIN_PASSWORD` is unset, a one-time cryptographically secure random token must be generated and displayed only once, with zero token logging.

## Authentication and API Authorization Standards

- **Token Security**:
  - API authentication relies on Django REST Framework Token Authentication (`Authorization: Token <key>`).
  - Tokens must be transmitted exclusively over secure HTTPS channels in staging and production.
- **View Permission Classes**:
  - Explicitly declare `permission_classes` on every API view or ViewSet.
  - State-altering endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) must enforce `IsAuthenticated`.
  - Public read endpoints must be deliberately configured with `AllowAny`.
- **Authentication Token Lifecycle**:
  - Tokens should be revoked or rotated when user credentials change or upon security breach investigation.
