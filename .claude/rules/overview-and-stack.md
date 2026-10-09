# Project Overview and Tech Stack

This document defines the core architecture, technology stack, execution environment, and foundational components of the Warehouse Management Backend system.

## System Overview

The Warehouse Management System is a backend RESTful API designed to manage physical storage facilities and track inventory balances across multiple products. It provides inventory managers and warehouse operators with real-time visibility into warehouse capacity, stock levels, automated stock threshold alerts, and inventory movement auditability.

## Technology Stack

- **Programming Language**: Python 3.14+
- **Web Framework**: Django 6.1+
- **API Toolkit**: Django REST Framework (DRF) 3.18+
- **Relational Database**: PostgreSQL 18.x connected via `psycopg2-binary`
- **Authentication**: Token Authentication (`rest_framework.authtoken`) with fallback to Basic Authentication for development
- **Environment Management**: Virtual environment (`venv`) with environment variable isolation via `python-dotenv`

## Runtime Environment and Architecture

- **Host Environment**: Local Windows / PowerShell development workstation with dedicated Python virtualenv.
- **Database Architecture**: PostgreSQL running on default port 5432 with isolated databases for development (`quan_ly_kho_db`) and automated testing (`test_quan_ly_kho_db`).
- **Configuration Management**: All sensitive credentials, database connection strings, and runtime toggles are loaded exclusively from `.env` via `config/settings.py`.
- **Modular App Architecture**: The primary business domain is encapsulated in the `warehouse` application, organized into modular, per-object packages (`models/`, `serializers/`, `views/`, `services/`, and `tests/`).
