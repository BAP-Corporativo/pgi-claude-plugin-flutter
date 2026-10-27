# Figma → Flutter mapping (PGI design files, Material 3)

Verified against the PGI United (M3) Figma file. Other PGI projects use the same naming with their own palette class.

## Color variables

`Schemes/<Name With Spaces>` → `<ColorsClass>.<camelCaseName>` (static getter, never an instance).

| Figma variable | UNITED | Hex (check only) |
|---|---|---|
| `Schemes/Primary` | `UnitedColors.primary` | #FF7E2B |
| `Schemes/On Primary` | `UnitedColors.white` (no `onPrimary` token; confirm in palette) | #FFFFFF |
| `Schemes/Primary Container` | `UnitedColors.primaryContainer` | #FFDBCA |
| `Schemes/On Primary Container` | `UnitedColors.onPrimaryContainer` | #703715 |
| `Schemes/On Surface` | `UnitedColors.onSurface` | #221A15 |
| `Schemes/On Surface Variant` | `UnitedColors.onSurfaceVariant` | #9E8B81 |
| `Schemes/Outline` | `UnitedColors.outline` | #85746B |
| `Schemes/Outline Variant` | `UnitedColors.outlineVariant` | #D7C2B9 |
| `Schemes/Background` | `UnitedColors.background` | #FFF8F6 |
| `Schemes/Surface Container Low` | `UnitedColors.surfaceContainerLow` | #FFF1EB |
| `Schemes/Surface Dim` | `UnitedColors.surfaceDim` | #E8D7CF |
| `Schemes/Error` / `Error Container` / `On Error Container` | `UnitedColors.error` / `errorContainer` / `onErrorContainer` | #BA1A1A / #FFDAD6 / #93000A |
| `State Layers/<Role>/Opacity-<n>` | **No direct token.** If the base color is a palette token, use `<token>.withValues(alpha: n / 100)`; if not (e.g. `State Layers/Primary/Opacity-16` = #8D4E2A @16%), report it as a gap | — |

If the hex in Figma doesn't match the palette token with the same name, report it; don't silently pick either.

## Typography

`PGI United/<role>/<size>` → `Theme.of(context).textTheme.<role><Size>`:

| Figma style | Flutter | Font in Figma |
|---|---|---|
| `headline/medium` | `textTheme.headlineMedium` | Unbounded 28/36 |
| `title/medium` | `textTheme.titleMedium` | Montserrat Medium 16/24 |
| `title/small` | `textTheme.titleSmall` | Montserrat Medium 14/20 |
| `body/medium` | `textTheme.bodyMedium` | DM Sans 14/20 |
| `body/small` | `textTheme.bodySmall` | DM Sans 12/16 |
| `label/medium` | `textTheme.labelMedium` | DM Sans Medium 12/16 |
| `label large` (button) | `textTheme.labelLarge` | Montserrat Medium 14/20 |
| `headline/super small` | **Not an M3 role.** Use the project's helper if one exists; otherwise report it | Unbounded 20 |

Before the first use, confirm in `lib/flavors/theme/<project>/` that the text theme really assigns these fonts; if a role is missing or uses another font, report it instead of building a raw `TextStyle`.

## Other variables

| Figma | Flutter |
|---|---|
| `Border-Radius/Container` (16) | the project's container radius constant if it exists, else `BorderRadius.circular(16)` once in a shared constant |
| `Border-Radius/Button` (48) | handled by the project's button widget/theme; don't restyle buttons locally |
| Effect `Mockup` | ignore (presentation shadow of the frame) |

## Material 3 components

| Figma component / layer name | Flutter |
|---|---|
| `Button` · `Style=Filled` | project primary button (catalog) → else `FilledButton` |
| `Icon button` · `Style=Outlined` (top-bar back) | project app bar / back button (catalog) → else `IconButton.outlined` |
| `Horizontal/Full-width` (divider) | `Divider` |
| `linear-determinate progress indicator` (SVG segments) | `LinearProgressIndicator`, or a small segmented widget if the design shows discrete segments per level — never the SVG pieces |
| `Chip - …` inside a custom selector | project chip/segmented widget (catalog) → else `ChoiceChip` / custom feature widget |
| Text fields | project input widget from `lib/widgets/inputs/` |
| `.Building Blocks/status-bar`, `Camera Cutout`, `Home indicator` | ignore (device chrome) |

## Layout

- `flex flex-col gap-[16px]` → `Column` with `spacing: 16` (Flutter 3.27+) or `SizedBox` gaps, matching the project's style.
- Fixed widths like `w-[358px]` are the frame width minus padding → use full width with the page padding; keep fixed sizes only for intrinsic elements (icons, avatars, button height).
- `absolute bottom-0 … Buttons` → `persistentFooterButtons` (remember the transparent `dividerTheme` wrapper).
- `TopBar App` with back button + title + subtitle → the project's app bar / header widget from the catalog.
