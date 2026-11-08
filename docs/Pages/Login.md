---
Project: AstroAlert

Document: Login Dialog

Version: 1.0.0

Status: Implemented

Author: Dereck Proaño

Design Language: Cosmic Glass

Last Updated: 2026-11-08
---

# Login Dialog

> "An account should open doors, not close them."

---

# Purpose

AstroAlert is **public**: every astronomical section works without an account. Logging in only enables optional email alerts.

API: `POST /api/login` → JWT valid for 7 days.

---

# Behaviour

* Opened from the "Iniciar sesión" button in the top bar, as a modal dialog (`role="dialog"`, `aria-modal`).
* Focus moves to the email field; **Esc**, the ✕ button or clicking outside closes it and returns focus to the button that opened it.
* Same error message whether the email does not exist or the password is wrong (does not reveal which accounts exist).
* Rate limited: more than 10 attempts per minute returns 429 with a human message.
* Once logged in, the button changes to "Mi cuenta" and the sidebar shows the email, an alerts toggle and "Cerrar sesión".
* An expired token closes the session automatically.

**AstroAlert Project**
