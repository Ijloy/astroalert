---
Project: AstroAlert

Document: Telescope Calculator Page

Version: 1.0.0

Status: Implemented

Author: Dereck Proaño

Design Language: Cosmic Glass

Last Updated: 2026-11-08
---

# Telescope Calculator Page

> "Understanding your instrument is the first step to using it well."

---

# Purpose

Let users experiment with their telescope and eyepiece and understand what the numbers mean.

URL: `/telescopio` · API: `POST /api/telescopio`

---

# Inputs

| Field | Range | Required |
|---|---|---|
| Aperture (mm) | 1 – 10 000 | Yes |
| Telescope focal length (mm) | 1 – 50 000 | Yes |
| Eyepiece focal length (mm) | 1 – 200 | Yes |
| Apparent field of view (°) | 10 – 120 | No (default 52°) |

Validation happens in the browser (empty fields marked with `aria-invalid`) and in the API (friendly 400 messages).

---

# Results

Magnification, true field of view, exit pupil, limiting magnitude, minimum and maximum useful magnification, focal ratio, recommended objects and warnings (e.g. magnification above the useful maximum).

---

# Layout

Two columns on desktop: form + results on the left; glossary ("¿Qué significan estos números?") and an image on the right. One column on mobile. The form submits with Enter.

**AstroAlert Project**
