---
name: figma-css-to-flutter
description: Convert Figma-exported CSS of a component into a Flutter widget tree written as semi-pseudocode, using only native Flutter widgets and mapping hex colors to the project's AppColors tokens. Use this whenever the user pastes CSS copied from Figma (auto-layout blocks with display flex, padding, gap, flex-direction, border-radius, font-family, etc.) and wants it turned into Flutter, or asks to "translate this component", "pass this design to Flutter", "resume el diseño", or hand a widget layout to a coding agent. Trigger even if the user does not say "Figma" explicitly but the pasted CSS clearly describes a UI component with auto-layout and design tokens.
---

# Figma CSS to Flutter

Turn Figma-exported CSS into a Flutter widget tree written as semi-pseudocode, ready for a coding agent (or the developer) to finish. The output describes *structure, layout, spacing, sizing, color, and typography* faithfully, not a compilable file.

## Output contract

Always produce output in this exact shape and style. The developer relies on it being consistent:

1. **One-line summary** of what the component is and its states/variants (e.g. "selector list with a selected item that gets a fill + trailing check").
2. **A short structural note** describing the widget hierarchy in Flutter terms (Column / Row / Stack, main/cross axis alignment) when the layout is non-trivial.
3. **Semi-pseudocode Flutter** — a widget tree, not a full file. See rules below.
4. **A color mapping table** (`Hex | Token`) listing every color used, if the project has an AppColors palette loaded (see `references/`). Skip the table if colors are left raw.
5. **Notes for the agent** — ambiguous matches, assets to confirm, placeholders, anything that couldn't be inferred from CSS alone.

### Semi-pseudocode rules

- **Native Flutter widgets only.** No `ui_kit_next` or any private/custom UI library, even if the project has one. Use `Container`, `Padding`, `Column`, `Row`, `Stack`, `Text`, `Image`, `ClipRRect`, `Icon`, `SizedBox`, `Expanded`, `DecoratedBox`, etc.
- It is a **tree, not a file**: no imports, no `class`, no `build()` boilerplate, no `Widget build(...)`. Start directly at the root widget. Repeated children may be factored into a small named helper widget (e.g. `_ItemCard(...)`) with its body shown once.
- Preserve **exact numeric values** from the CSS: padding, gap → `SizedBox` between children, width/height, border-radius, letter-spacing, font-size. Convert CSS `line-height` to Flutter `height` as `lineHeightPx / fontSizePx` and leave it as that division so the source is visible (e.g. `height: 32 / 24`).
- Map CSS auto-layout to Flutter directly:
  - `flex-direction: row` → `Row`, `column` → `Column`
  - `justify-content` → `mainAxisAlignment`, `align-items` → `crossAxisAlignment`
  - `gap` → `SizedBox(width/height: gap)` inserted between children (Flutter has no gap on Row/Column)
  - `flex-grow: 1` / a child that should fill → `Expanded`
  - `padding` → `Padding` or `Container(padding: EdgeInsets...)`
  - `position: absolute` inside a parent → `Stack` + `Positioned`
  - `border-radius` → `BorderRadius.circular` / `BorderRadius.vertical(top: ...)` for sheets
- See `references/output-conventions.md` for the full CSS→Flutter cheat sheet and a worked example. Read it before producing output if anything about the mapping is unclear.

## Color architecture (how AppColors works in these projects)

Most of the developer's projects share the same flavor-based color system. Understand it so the tokens you emit are correct and resolvable:

- `lib/flavors/colors_theme.dart` — an abstract class `ColorsTheme` declaring every color of the project as a getter (the full token list). This is the contract.
- `lib/flavors/<flavor>/<flavor>_colors.dart` — one class per flavor (e.g. `UnitedColors` in `united/united_colors.dart`) that `extends ColorsTheme` and returns the actual hex values. **This file is the source of truth for the hex → token mapping.**
- `lib/core/` — the `AppColors` class exposes each color as a **static getter** that resolves the active flavor at runtime:
  ```dart
  static Color get surface => ThemeManager.colors.surface;
  ```

Because usage across the whole project goes through `AppColors`, the pseudocode **must reference colors as `AppColors.<token>`** (static access), e.g. `color: AppColors.surface`. Do not use instance access or read the flavor class directly. Keep the raw hex in a trailing comment so the mapping is auditable (`AppColors.surface, // #FFF8F6`).

The `references/appcolors-<project>.md` files hold the reverse map (hex → token) extracted from that project's `<flavor>_colors.dart`, which is exactly what you need to go from a CSS hex to the right `AppColors.<token>`.

## Colors: map to AppColors tokens

The developer works across several projects, each with its own flavor color class. Color handling depends on whether that project's palette is loaded:

1. **Identify the project first.** If the user did not say which project the CSS belongs to, ASK before producing output — the wrong palette produces wrong tokens. A one-line question is enough.
2. **If a palette file for that project exists** in `references/` (files named `appcolors-<project>.md`), map every hex in the CSS to its token. Use `AppColors.<token>` in the pseudocode and keep the raw hex in a trailing comment (`// #FFF1EB`). Produce the `Hex | Token` table.
3. **If no palette is loaded for that project**, leave colors as raw `Color(0xFF......)` and say so — do not invent tokens. Offer to store the palette if the user pastes the AppColors class.
4. **Ambiguous matches:** when several tokens share the same hex, pick the one that fits the semantic context (e.g. for a selected-item fill prefer `primaryContainer` over `primaryFixed`) and flag the tie in the notes so the developer can confirm.

### Available palettes

- `references/appcolors-united.md` — UNITED project (`UnitedColors`). Reverse map hex → token.

When the user loads a new project's AppColors, add a `references/appcolors-<project>.md` file following the same format and list it here.

## Asking clarifying questions

Keep questions minimal and only when they change the output:
- Which project (if unstated and colors need mapping).
- Whether the component has states/variants not visible in the pasted CSS (selected/disabled/error), if the CSS hints at one state but the component likely has more.

Do not ask about output format — it is fixed by this skill.
