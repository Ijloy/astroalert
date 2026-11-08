---
Project: AstroAlert

Document: Spacing System

Version: 1.0.0

Status: Approved

Author: Dereck Proaño

Design Language: Cosmic Glass

Last Updated: 2026-06-29
---

# Spacing System

> "Space is not empty. Space gives meaning."

---

# Purpose

The AstroAlert Spacing System defines how distance and empty space are used throughout the interface.

Spacing is not only a technical measurement.

It is a visual language.

The correct use of space creates:

- Hierarchy.
- Focus.
- Calmness.
- Readability.
- Visual balance.

Because AstroAlert represents the universe, space itself becomes part of the experience.

The interface should feel open, intentional and immersive.

---

# Content

# Spacing Philosophy

Cosmic Glass follows a simple principle:

**Every element needs room to breathe.**

The universe is not crowded.

Stars exist separated by enormous distances.

AstroAlert applies the same idea to digital experiences.

Information should never fight for attention.

Each element should have enough space to communicate its importance.

---

# The Role of Empty Space

Empty space has three main purposes:

## Focus

Space directs attention toward important information.

A planet, event or discovery becomes more meaningful when surrounded by visual calm.

---

## Hierarchy

Spacing helps users understand relationships between elements.

Closer elements belong together.

Separated elements represent different concepts.

---

## Emotion

Large areas of empty space create a feeling of:

- Exploration.
- Calm.
- Wonder.
- Depth.

The interface should feel like looking into space.

---

# Spacing Scale

AstroAlert uses a consistent spacing system based on progressive values.

Small spacing values are used for close relationships.

Large spacing values are used to create separation and importance.

---

## Micro Spacing

Purpose:

Small relationships inside components.

Examples:

- Icon and text.
- Label and value.
- Small metadata.

Characteristics:

Subtle and precise.

---

## Component Spacing

Purpose:

Internal organization of components.

Examples:

- Card content.
- Buttons.
- Information blocks.

Characteristics:

Creates clarity without increasing visual weight.

---

## Section Spacing

Purpose:

Separates major content areas.

Examples:

- Different astronomical sections.
- Page blocks.
- Educational sections.

Characteristics:

Creates rhythm throughout the experience.

---

## Experience Spacing

Purpose:

Large visual breathing areas.

Examples:

- Hero sections.
- Featured discoveries.
- Immersive astronomy experiences.

Characteristics:

Creates emotion and a sense of scale.

---

# Layout Rhythm

A consistent rhythm makes the interface predictable.

Users should naturally understand:

- What belongs together.
- What is important.
- Where to look next.

Spacing should guide the user without requiring explanation.

---

# Density Principles

AstroAlert avoids excessive information density.

Scientific information can be complex.

The interface should make complexity feel organized.

A screen should never communicate:

"Everything is important."

Instead:

"The most important thing is here."

---

# Content Priority Through Space

The amount of space around an element communicates importance.

More space can indicate:

- Greater importance.
- A moment of discovery.
- A featured experience.

Less space can indicate:

- Supporting information.
- Secondary details.
- Metadata.

---

# Spacing in Components

## Cards

Cards should have enough internal space to feel like independent information objects.

They should not feel compressed.

---

## Navigation

Navigation should remain compact and efficient.

It guides exploration without becoming the main focus.

---

## Data Visualization

Important astronomical values should have visual room.

Numbers representing:

- Distance.
- Temperature.
- Speed.
- Size.

Should feel significant.

---

## Images

Astronomical images require breathing room.

The image itself should become the experience.

---

# Responsive Spacing

Spacing must adapt across different devices.

The experience should maintain:

- Visual balance.
- Readability.
- Clear hierarchy.

A smaller screen does not mean a crowded interface.

It means a more carefully organized one.

---

# Spacing Rules

## Rule 1

Never add elements only to fill empty space.

Empty space can be intentional.

---

## Rule 2

Do not remove spacing only to show more information.

Clarity is more valuable than quantity.

---

## Rule 3

Important content deserves visual room.

---

## Rule 4

Consistency is more important than individual preference.

---

# Design Implications

The spacing system affects:

- Page layouts.
- Components.
- Cards.
- Navigation.
- Astronomy experiences.
- Responsive behavior.

Every screen should feel balanced before adding visual decoration.

---

# Implementation Tokens

Defined in `static/style.css` (`:root`). The four spacing levels of this document map to the scale:

| Level | Tokens | Values |
|---|---|---|
| Micro spacing | `--sp-1`, `--sp-2` | 4px, 8px |
| Component spacing | `--sp-3`, `--sp-4` | 12px, 16px |
| Section spacing | `--sp-5`, `--sp-6` | 24px, 32px |
| Experience spacing | `--sp-7`, `--sp-8` | 48px, 72px |

Radii: `--r-sm` 8px · `--r-md` 12px · `--r-lg` 16px. Minimum touch target: 44px.

---

# Final Statement

Space is one of the most important elements of AstroAlert.

Not only because the platform explores the universe.

But because the way we use empty space determines how users experience it.

A calm interface creates room for curiosity.

---

> "In the universe, distance creates beauty. In design, space creates meaning."

**AstroAlert Project**