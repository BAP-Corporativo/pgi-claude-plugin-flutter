# CSS → Flutter cheat sheet

Read this when a mapping is unclear or when the CSS uses a feature not covered by the quick rules in SKILL.md.

## Auto-layout mapping

| Figma CSS | Flutter |
|---|---|
| `display: flex; flex-direction: row` | `Row` |
| `display: flex; flex-direction: column` | `Column` |
| `display: none` | omit the widget entirely (note it) |
| `justify-content: flex-start` | `mainAxisAlignment: MainAxisAlignment.start` |
| `justify-content: center` | `mainAxisAlignment: MainAxisAlignment.center` |
| `justify-content: flex-end` | `mainAxisAlignment: MainAxisAlignment.end` |
| `justify-content: space-between` | `mainAxisAlignment: MainAxisAlignment.spaceBetween` |
| `align-items: flex-start` | `crossAxisAlignment: CrossAxisAlignment.start` |
| `align-items: center` | `crossAxisAlignment: CrossAxisAlignment.center` |
| `align-items: flex-end` | `crossAxisAlignment: CrossAxisAlignment.end` |
| `align-self: stretch` | usually `crossAxisAlignment: stretch` on parent, or width to fill |
| `gap: N` | `SizedBox(width/height: N)` between each child (Flutter Row/Column has no gap) |
| `flex-grow: 1` | wrap child in `Expanded` |
| `flex: none` | leave intrinsic size (default) |
| `padding: T R B L` | `Padding(padding: EdgeInsets.fromLTRB(L, T, R, B))` or `Container(padding: ...)` |
| `margin: 0 auto` | centering — use `Center` or `mainAxisAlignment.center` on parent |
| `width` / `height` fixed | `SizedBox` / `Container` with `width`/`height` |
| `position: absolute` | parent becomes `Stack`, child becomes `Positioned` |
| `border-radius: N` | `BorderRadius.circular(N)` |
| `border-radius: A B 0 0` | `BorderRadius.vertical(top: Radius.circular(A))` (bottom sheets) |
| `background: #hex` | `Container(color:)` or `BoxDecoration(color:)` (needed if also radius/border) |
| `background: linear-gradient(...)` | `BoxDecoration(gradient: LinearGradient(...))` |
| `background: url(image.png)` | `Image.asset(...)` — it is an image, not a widget; confirm asset |
| `box-shadow` | `BoxDecoration(boxShadow: [BoxShadow(...)])` |
| `border: Npx solid #hex` | `BoxDecoration(border: Border.all(width: N, color: ...))` |
| `opacity` | `Opacity(opacity:)` |

## Typography mapping

Every text style maps to a `TextStyle`:

| CSS | Flutter |
|---|---|
| `font-family: 'X'` | `fontFamily: 'X'` |
| `font-weight: 400/500/700` | `FontWeight.w400 / w500 / w700` |
| `font-size: Npx` | `fontSize: N` |
| `line-height: Mpx` | `height: M / N` (M = line-height px, N = font-size px) — keep as division |
| `letter-spacing: Kpx` | `letterSpacing: K` |
| `color: #hex` | `color:` (mapped to token if palette loaded) |
| `text-align` | `textAlign:` on the `Text` |

Leave `height` written as the division (e.g. `height: 20 / 14`) so the reviewer can see it came from `line-height: 20px` on a 14px font.

## Structural conventions

- Output a **widget tree only** — no imports, no class, no `build()`.
- Factor repeated children into one named helper (`_ItemCard(...)`, `_Row(...)`) shown once, then referenced with the varying params.
- Keep a `// #hex` comment next to every `AppColors.<token>` so the mapping is auditable.
- Note anything the CSS can't express: tap handlers, real asset names, dynamic data, scroll behavior, whether a container should be a `showModalBottomSheet` shape.
- Bottom sheets: mention the `showModalBottomSheet(shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(N))))` in a comment; the root container carries the fill.

## Worked example

**Input (abridged Figma CSS):**
```
/* Card */
display: flex; flex-direction: row; justify-content: space-between;
align-items: center; padding: 16px; gap: 8px;
width: 358px; height: 74px; background: #FFDBCA; border-radius: 8px;
/* Label */ font-family: 'Montserrat'; font-weight: 500; font-size: 16px;
line-height: 24px; letter-spacing: 0.15px; color: #221A15;
```

**Output:**

A single row card (selected state: filled `primaryContainer`), label on the left, trailing check.

```dart
Container(
  height: 74,
  padding: const EdgeInsets.all(16),
  decoration: BoxDecoration(
    color: AppColors.primaryContainer,          // #FFDBCA
    borderRadius: BorderRadius.circular(8),
  ),
  child: Row(
    mainAxisAlignment: MainAxisAlignment.spaceBetween,
    crossAxisAlignment: CrossAxisAlignment.center,
    children: [
      Text(
        label,
        style: TextStyle(
          fontFamily: 'Montserrat',
          fontWeight: FontWeight.w500,
          fontSize: 16,
          height: 24 / 16,
          letterSpacing: 0.15,
          color: AppColors.onSurface,           // #221A15
        ),
      ),
      const SizedBox(width: 8),                  // gap
      Icon(Icons.check, size: 24, color: AppColors.onPrimaryContainer),
    ],
  ),
)
```

| Hex | Token |
|---|---|
| `#FFDBCA` | `primaryContainer` |
| `#221A15` | `onSurface` |

Notes: `#FFDBCA` also matches `primaryFixed`; chose `primaryContainer` for the selected-fill semantics. Confirm the check is a native `Icons.check` vs a project asset.
