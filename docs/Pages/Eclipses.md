---
Project: AstroAlert

Document: Eclipses Page

Version: 1.0.0

Status: Implemented

Author: Dereck Proaño

Design Language: Cosmic Glass

Last Updated: 2026-11-08
---

# Eclipses Page

> "An eclipse is not only a date. It is an alignment you can understand."

---

# Purpose

Show upcoming solar and lunar eclipses and, above all, **how each one will look from the user's city**.

URL: `/eclipses` · API: `GET /api/eclipses`

---

# How the data is produced

* **Solar eclipses** are computed with Skyfield. At every new Moon the app checks whether the Moon's shadow touches the Earth (global type: total, annular or partial) and then simulates the local sky minute by minute to obtain the local type, the fraction of the Sun's diameter covered, start / maximum / end times and the duration of the central phase.
* **Lunar eclipses** come from `skyfield.eclipselib`; an eclipse is visible when the Moon is above the horizon at maximum.
* Results are cached for 6 hours. The countdown is recalculated on every request.
* Accuracy is validated in `tests/test_astronomia.py` against published NASA data.

---

# Page Structure

1. **Header** — title and a one-sentence explanation of the source (JPL DE421).
2. **Event list** — one event card per eclipse, in chronological order:
   * Icon and name (e.g. "Eclipse solar anular").
   * Visibility badge: green "✓ Visible desde Quito" or neutral "No visible".
   * Countdown in days, hours and minutes.
   * Local date and time.
   * For visible solar eclipses: start, maximum, end and % of the Sun covered.
   * A human explanation (e.g. "Parcial desde Quito: la Luna cubrirá el 86% del diámetro del Sol").
3. Events that are not visible locally are shown dimmed, never hidden.

---

# States

* **Loading:** skeleton lines.
* **Error:** human message + "Reintentar" button.
* **Empty:** "No hay eclipses en los próximos meses."

---

# Home integration

The Home "Eclipse" card shows the next eclipse **visible from the city**; if none, the next eclipse anywhere.

**AstroAlert Project**
