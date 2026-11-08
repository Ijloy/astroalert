---
Project: AstroAlert

Document: Visible Planets Page

Version: 1.0.0

Status: Implemented

Author: Dereck Proaño

Design Language: Cosmic Glass

Last Updated: 2026-11-08
---

# Visible Planets Page

> "Can I see Saturn tonight?"

---

# Purpose

Answer in seconds which naked-eye planets (Mercury, Venus, Mars, Jupiter, Saturn) can be seen **right now** from the city, and when the next opportunity is if none can.

URL: `/planetas` · API: `GET /api/planetas`

---

# Visibility rule

A planet counts as visible only if:

1. it is at least **5°** above the horizon, and
2. the Sun is more than **6°** below the horizon (end of civil twilight).

The response includes the sky condition (`día`, `crepúsculo`, `noche`) and the Sun's altitude so the interface can explain *why* nothing is visible during the day.

---

# Page Structure

1. **Header** with the rule above in plain language.
2. **If planets are visible:** one row per planet with altitude, compass direction and magnitude (with a short note: the lower the number, the brighter).
3. **If not:** the reason ("Ahora es de día en Quito…") and the next window (local time and "en X h Y min") with the planets that will be up.

---

# Home integration

The "Planetas visibles" card shows small planet icons (real approximate colours, not palette colours) with altitude and direction.

**AstroAlert Project**
