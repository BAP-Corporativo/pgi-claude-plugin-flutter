# AppColors — UNITED (`UnitedColors`)

Reverse map (hex → token) for the UNITED project. When translating UNITED CSS, replace each hex with `AppColors.<token>` and keep the hex in a trailing comment.

Source of truth: `lib/flavors/united/united_colors.dart` (`UnitedColors extends ColorsTheme`) holds these hex values. In code you never touch that class directly — you use the **static getters** on `AppColors` (`lib/core/`), which resolve the active flavor via `ThemeManager`:

```dart
static Color get surface => ThemeManager.colors.surface;
```

So every token below is emitted as `AppColors.<token>` (static), e.g. `AppColors.surface, // #FFF8F6`.

## Ambiguity resolution

Several hex values map to more than one token. Pick by semantic context and flag the tie in the notes:

| Hex | Tokens sharing it | Prefer when… |
|---|---|---|
| `#FFFFFF` | `white`, `onSecondary`, `onTertiary`, `onError`, `surfaceContainerLowest`, `textInactive` | surface → `surfaceContainerLowest`; text on color → the `on*`; generic → `white` |
| `#000000` | `shadow`, `scrim`, `shadowandscrim` | shadows → `shadow`; overlays → `scrim` |
| `#331100` | `primary10`, `onPrimaryFixed` | text on primaryFixed → `onPrimaryFixed` |
| `#FFB690` | `primary80`, `primaryFixedDim`, `inversePrimary` | palette ramp → `primary80` |
| `#FFDBCA` | `primaryContainer`, `primaryFixed` | selected/container fill → `primaryContainer` |
| `#703715` | `onPrimaryContainer`, `onPrimaryFixedVariant` | on container → `onPrimaryContainer` |
| `#FF7E2B` | `primary`, `surfaceTint` | brand → `primary` |
| `#FFDEA5` | `secondaryContainer`, `secondaryFixed` | container fill → `secondaryContainer` |
| `#5D4200` | `onSecondaryContainer`, `onSecondaryFixedVariant` | on container → `onSecondaryContainer` |
| `#EBE4AA` | `tertiaryContainer`, `tertiaryFixed` | container fill → `tertiaryContainer` |
| `#1E1C00` | `tertiary10`, `onTertiaryFixed` | text on tertiaryFixed → `onTertiaryFixed` |
| `#4B481D` | `onTertiaryContainer`, `onTertiaryFixedVariant` | on container → `onTertiaryContainer` |
| `#FFF8F6` | `background`, `surface` | surface of a container → `surface`; page bg → `background` |
| `#221A15` | `onBackground`, `onSurface` | text on surface → `onSurface` |
| `#444444` | `inactive`, `textCancel` | fill → `inactive`; text → `textCancel` |

## Full reverse map (hex → token)

- `#FFFFFF` → white (see ambiguity table)
- `#000000` → shadow / scrim / shadowandscrim
- `#FF7E2B` → primary (also surfaceTint)
- `#FFEDE6` → primary95 (also inverseOnSurface)
- `#FFB690` → primary80 (also primaryFixedDim, inversePrimary)
- `#E86D18` → primary60
- `#331100` → primary10 (also onPrimaryFixed)
- `#FFDBCA` → primaryContainer (also primaryFixed)
- `#703715` → onPrimaryContainer (also onPrimaryFixedVariant)
- `#7A590C` → secondary
- `#FFDEA5` → secondaryContainer (also secondaryFixed)
- `#5D4200` → onSecondaryContainer (also onSecondaryFixedVariant)
- `#271900` → onSecondaryFixed
- `#ECC06C` → secondaryFixedDim
- `#646032` → tertiary
- `#1E1C00` → tertiary10 (also onTertiaryFixed)
- `#EBE4AA` → tertiaryContainer (also tertiaryFixed)
- `#4B481D` → onTertiaryContainer (also onTertiaryFixedVariant)
- `#CEC891` → tertiaryFixedDim
- `#006C52` → tertiary40
- `#008768` → tertiary50
- `#00A47F` → tertiary60
- `#4EDDB2` → tertiary80
- `#E7FFF3` → tertiary98
- `#BA1A1A` → error
- `#FFDAD6` → errorContainer
- `#93000A` → onErrorContainer
- `#FFEDEA` → error95
- `#FFB4AB` → error80
- `#FF897D` → error70
- `#FF5449` → error60
- `#DE3730` → error50
- `#A80710` → error35
- `#FFF8F6` → background (also surface)
- `#221A15` → onBackground (also onSurface)
- `#F4DED4` → surfaceVariant
- `#9E8B81` → onSurfaceVariant
- `#382E29` → inverseSurface
- `#85746B` → outline
- `#D7C2B9` → outlineVariant
- `#F0DFD8` → surfaceContainerHighest
- `#FFDCC6` → surfaceContainerHigh
- `#FCEAE3` → surfaceContainer
- `#FFF1EB` → surfaceContainerLow
- `#E8D7CF` → surfaceDim
- `#EDF4F6` → surface1
- `#EFEDE9` → surface2
- `#DBEAEF` → surface3
- `#EAE6DF` → surface4
- `#D8E2E5` → surface5
- `#D3911C` → seed
- `#EDEDED` → splashHome
- `#201A17` → neutral10
- `#655D59` → neutral40
- `#7F7571` → neutral50
- `#998F8A` → neutral60
- `#B4A9A4` → neutral70
- `#D0C4BF` → neutral80
- `#FBEDE9` → neutral95
- `#BDEAFF` → pending (also inProcess)
- `#FFEAC5` → waitingPayment
- `#C9FFDD` → approve
- `#FECACA` → rejected
- `#E9E7E7` → cancel
- `#444444` → inactive (also textCancel)
- `#2D7291` → textPending
- `#7C4A03` → textWaitingPayment
- `#0369A1` → textInProcess
- `#065F46` → textApprove
- `#991B1B` → textRejected
- `#DCDEE4` → disabledButton
- `#929599` → disabledText
- `#4BDFB4` → accent
- `#DE0B0B` → red0
- `#5F9975` → green0
- `#5B21B6` → onPurple
