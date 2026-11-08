---
Project: AstroAlert

Document: Register Dialog

Version: 1.0.0

Status: Implemented

Author: Dereck Proaño

Design Language: Cosmic Glass

Last Updated: 2026-11-08
---

# Register Dialog

> "Ask only for what you need."

---

# Purpose

Create an optional account to receive sky alerts by email.

API: `POST /api/registro`

---

# Fields

| Field | Rule |
|---|---|
| Email | Valid format, stored in lowercase, unique |
| Password | 8–128 characters |
| Confirm password | Must match |
| Username | Optional, 3–30 characters (letters, numbers, `.`, `_`, `-`) |
| "Quiero recibir alertas" | Optional checkbox, **off by default** |

Phone number and date of birth were removed: they were never used (data minimisation).

---

# Behaviour

* Same dialog pattern as Login (focus, Esc, return focus).
* After success the Login dialog opens with the email pre-filled and a confirmation message.
* Rate limited (5 per minute, 30 per hour).

**AstroAlert Project**
