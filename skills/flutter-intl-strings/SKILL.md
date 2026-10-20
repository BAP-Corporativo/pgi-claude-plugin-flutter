---
name: flutter-intl-strings
description: Add, change, or remove user-facing text in a Nextline PGI Flutter project (UNITED, FinsofApp and their flavors) using the legacy intl / ARB pipeline (flutter_intl + intl_utils), including placeholders and plurals. Use this whenever the user asks to add or change a text, label, copy, mensaje, título, texto, traducción, string, or error message shown in the UI, or when writing any widget that displays text — even if they only say "cambia el texto del botón" or "agrega el mensaje de error". Also use it when a hardcoded string should be moved to localization.
---

# Flutter intl strings

These projects use **intl_utils (flutter_intl)**, not Flutter's default `gen-l10n`. Source of truth: `lib/l10n/intl_*.arb`. Generated code: `lib/generated/` (never edited by hand).

## Step 0 — Resolve

```bash
ls lib/l10n/intl_*.arb                 # every locale file that must get the key
grep -A5 '^flutter_intl:' pubspec.yaml # main_locale and class_name (default class: S)
grep -rn "S.of(context)\|S.current" lib/ | head -3   # how the project reads strings
```

Read `CLAUDE.md` for the active locale (UNITED hardcodes `es_MX`). Write the Spanish text first; that is what users see.

## Worked example

Need: a title, a message with two values, and a plural.

Add to **every** `intl_*.arb` file (same keys, translated values):

```json
"beneficiariesTitle": "Beneficiarios",
"@beneficiariesTitle": {},

"transferSuccess": "Transferiste {amount} a {name}",
"@transferSuccess": {
  "placeholders": {
    "amount": { "type": "String" },
    "name": { "type": "String" }
  }
},

"pendingTransfers": "{count, plural, =0{Sin transferencias pendientes} =1{1 transferencia pendiente} other{{count} transferencias pendientes}}",
"@pendingTransfers": {
  "placeholders": {
    "count": { "type": "int" }
  }
}
```

Regenerate:
```bash
dart pub global run intl_utils:generate
```
(If the developer uses the IDE Flutter Intl plugin, it regenerates on save; running the command is still safe.)

Use it:
```dart
Text(S.of(context).beneficiariesTitle)
Text(S.of(context).transferSuccess(formattedAmount, beneficiary.name))
Text(S.of(context).pendingTransfers(provider.pendingCount))
```

Inside a provider (no `BuildContext`), use `S.current.someKey` — only if the project already does this; otherwise return a state/enum and resolve the text in the widget.

## Key naming

- lowerCamelCase, descriptive of meaning, not of position: `transferSuccess`, not `text3` or `homeLabel2`.
- Prefix by feature when the word is ambiguous: `beneficiariesEmptyState`, `kycSelfieInstructions`.
- Before adding, search for an existing key with the same text: `grep -n '"Continuar"' lib/l10n/intl_es*.arb`. Reuse it instead of duplicating.
- Format money and dates in Dart (with the project's formatter) and pass them as `String` placeholders; don't build currency strings inside the ARB.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| `Text('Beneficiarios')` hardcoded in a widget | Add a key and use `S.of(context)` | All UI text goes through ARB |
| Add the key only to the Spanish file | Add it to every `intl_*.arb` | Keeps locales in sync; missing keys silently fall back or fail generation |
| Edit `lib/generated/l10n.dart` or `messages_*.dart` | Edit ARB, rerun `intl_utils:generate` | Generated files are overwritten |
| `flutter gen-l10n` / `AppLocalizations.of(context)` / adding `l10n.yaml` | `intl_utils:generate` / `S.of(context)` | Different pipeline; mixing them creates two sources of truth |
| String concatenation: `S.of(context).youSent + ' ' + amount` | Placeholder in the ARB message | Word order changes between languages |
| `'$count transferencias'` with manual `if (count == 1)` | ICU plural in the ARB | Pluralization rules belong to the message |

## Finish

1. Every `intl_*.arb` has the new keys and the JSON is valid (trailing commas break it).
2. `dart pub global run intl_utils:generate` ran without errors.
3. `flutter analyze` passes.
4. Report the keys added and where they are used.
