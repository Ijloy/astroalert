---
Project: AstroAlert

Document: Color System

Version: 1.0.0

Status: Approved

Author: Dereck Proaño

Design Language: Cosmic Glass

Last Updated: 2026-06-29
---

# Color System

> "Light is information. Color is emotion."

---

# Purpose

The AstroAlert Color System defines how color is used throughout the entire product.

Colors are not decorative elements.

They communicate hierarchy, importance, emotion and meaning.

The purpose of the color system is to create an interface that feels:

- Calm.
- Scientific.
- Elegant.
- Immersive.
- Modern.

Every color must have a reason to exist.

The universe provides infinite colors, but the interface requires discipline.

---

# Content

# Color Philosophy

Cosmic Glass uses color as a representation of the universe.

Dark environments represent the depth of space.

Light represents discovery.

Highlights represent important information.

Subtle gradients represent cosmic atmosphere.

The objective is not to recreate space visually.

The objective is to create the feeling of exploring it.

---

# Primary Color Groups

AstroAlert colors are divided into five main groups:

1. Cosmic Backgrounds
2. Glass Surfaces
3. Stellar Highlights
4. Information Colors
5. Semantic Colors

---

# 1. Cosmic Backgrounds

Background colors represent the infinite space surrounding the interface.

They create depth and allow astronomical content to become the main focus.

## Deep Space

Purpose:

Main application background.

Usage:

- Main screens.
- Navigation areas.
- Large visual sections.

Characteristics:

- Extremely dark.
- Calm.
- Neutral.
- Creates contrast with celestial elements.

---

## Cosmic Atmosphere

Purpose:

Secondary background layers.

Usage:

- Hero sections.
- Large cards.
- Visual transitions.

Characteristics:

- Slight color variation.
- Creates depth without distraction.

---

## Nebula Environment

Purpose:

Special immersive areas.

Usage:

- Astronomy experiences.
- Featured discoveries.
- Educational sections.

Characteristics:

- Soft gradients.
- Subtle color blending.
- Never overpowering content.

---

# 2. Glass Surfaces

Glass colors define the Cosmic Glass interface.

They represent information floating above space.

## Glass Primary

Usage:

Main cards.

Characteristics:

- Semi-transparent.
- Soft contrast.
- Creates separation from background.

---

## Glass Secondary

Usage:

Secondary containers.

Characteristics:

- Lower visual priority.
- Supports hierarchy.

---

## Glass Highlight

Usage:

Important information.

Characteristics:

- Slight brightness.
- Used carefully.

---

# 3. Stellar Highlights

These colors represent light in the universe.

They should attract attention without becoming decoration.

## Stellar Blue

Represents:

- Discovery.
- Technology.
- Real-time information.

Usage:

- Primary actions.
- Active states.
- Important astronomical data.

---

## Nebula Purple

Represents:

- Mystery.
- Exploration.
- The unknown.

Usage:

- Special experiences.
- Featured content.

---

## Cosmic Cyan

Represents:

- Clarity.
- Scientific information.
- Precision.

Usage:

- Data visualization.
- Measurements.
- Technical information.

---

## Solar Gold

Represents:

- Important discoveries.
- Energy.
- Exceptional events.

Usage:

- Featured astronomical events.
- Achievements.
- Highlights.

---

# 4. Information Colors

Information colors communicate different types of content.

## Discovery

Used for:

- New findings.
- Exploration content.
- Interesting facts.

---

## Observation

Used for:

- Visibility.
- Real-time astronomical conditions.
- Tracking information.

---

## Education

Used for:

- Learning content.
- Explanations.
- Scientific concepts.

---

## Community

Used for:

- User interaction.
- Shared experiences.

---

# 5. Semantic Colors

Semantic colors follow standard interface conventions.

## Success

Used for:

- Completed actions.
- Positive states.

---

## Warning

Used for:

- Important attention.
- Upcoming events.

---

## Error

Used for:

- Problems.
- Failed actions.

---

## Neutral

Used for:

- Secondary information.
- Supporting elements.

---

# Color Usage Rules

## Rule 1

Never use color only for decoration.

Every color must communicate something.

---

## Rule 2

The background should never compete with content.

Space creates the environment.

Information creates the experience.

---

## Rule 3

Bright colors are reserved for important moments.

Light is valuable.

Too much light loses meaning.

---

## Rule 4

Gradients should represent atmosphere, not decoration.

A gradient should create depth or emotion.

It should never exist without purpose.

---

# Contrast Principles

AstroAlert must always prioritize readability.

Scientific information requires clarity.

The interface should support:

- Long reading sessions.
- Different screen conditions.
- Accessibility standards.

Beauty should never reduce usability.

---

# Design Implications

The color system influences:

- Components.
- Cards.
- Navigation.
- Data visualization.
- Astronomy experiences.
- Animations.
 
Every interface element should use colors from this system.

Random colors should never be introduced.

---

---

# Palette: Cosmic Nebula

AstroAlert uses the **Cosmic Nebula** palette (30 tones of indigo, violet, orchid, magenta and night blue).
The tokens live in `static/style.css` (`:root`). Components never use raw hex values; they use the role tokens.

## Readability rule

Contrast was measured (WCAG 2.1) against the main background `#0B0718`.
Only colors with **≥ 4.5:1** may be used for text. Darker tones are reserved for surfaces, borders and filled buttons with white text.

| Token | Hex | Contrast on background | Allowed use |
|---|---|---|---|
| `--nebula-orquidea` | `#BA55D3` | 5.0:1 | Accent text, numbers, links, logo |
| `--nebula-purpura-medio` | `#9370DB` | 5.3:1 | Secondary accent text, background icons |
| `--nebula-lavanda` | `#7B68EE` | 4.8:1 | Secondary accent text |
| `--nebula-rosa` | `#DB7093` | 6.4:1 | Warnings, errors, highlighted text |
| `--nebula-azul-violeta` | `#8A2BE2` | white on it 6.0:1 | Primary button background |
| `--nebula-violeta-osc` | `#9400D3` | white on it 6.6:1 | Primary button hover |
| `--nebula-magenta` | `#C71585` | white on it 5.4:1 | Eclipse badge, gradients |
| `--nebula-pizarra-media` | `#6A5ACD` | white on it 5.3:1 | Conjunction badge |
| `--nebula-azul-noche` | `#1E3A5F` | white on it 11.5:1 | Comet badge, nebula atmosphere |
| `--nebula-indigo` | `#4B0082` | 1.5:1 | Background atmosphere only |
| `--nebula-indigo-profundo` | `#2C1E5C` | 1.4:1 | Glass surfaces only |

## Role tokens

| Role | Value |
|---|---|
| `--fondo` | `#0B0718` (deep indigo, darkened from `#2C1E5C` for long reading) |
| `--fondo-card` | `rgba(44,30,92,0.22)` |
| `--borde` | `rgba(147,112,219,0.18)` |
| `--texto` | `#ECE8F5` |
| `--texto-sub` | `rgba(236,232,245,0.62)` |
| `--acento` | `#BA55D3` |
| `--primario` | `#8A2BE2` |
| `--exito` | `#4ade80` (semantic green for "visible"; intentionally outside the palette so it is never confused with an accent) |
| `--error` | `#DB7093` |

## Gradients

* Hero title: `#9370DB → #BA55D3 → #DB7093`
* Primary hero button: `#6A0DAD → #8A2BE2 → #C71585`
* Page atmosphere: very soft radial glows of `#4B0082`, `#1E3A5F` and `#C71585` over `#0B0718`.

Planet colors in illustrations keep their real tones (scientific accuracy over palette).

---

# Final Statement

Color in AstroAlert is not decoration.

It is a language.

Darkness represents the unknown.

Light represents discovery.

Color connects humans with the universe.

---

> "The universe communicates through light. AstroAlert communicates through meaning."
