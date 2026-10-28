# Widget catalog (one per project repo)

Lives in the project, not in the plugin: `docs/widget-catalog.md` (or the path set in `CLAUDE.md`). It is what lets the reuse ladder work without reading every widget file on each run.

## Build it when it doesn't exist

```bash
grep "^export" lib/widgets/widgets.dart          # every shared widget file
grep -rn "class .* extends \(StatelessWidget\|StatefulWidget\)" lib/widgets/ | sed 's/:.*class / /;s/ extends.*//'
```

Open each widget's constructor and write one row. Group by the folder (`app_bars`, `bottom_sheets`, `cards`, `custom_buttons`, `inputs`, `modals`, …). Feature-local widgets are not listed.

## Format

```markdown
# Widget catalog — UNITED

## custom_buttons
| Widget | Path | Use it for | Key params | Figma equivalent |
|---|---|---|---|---|
| PrimaryButton | lib/widgets/custom_buttons/primary_button.dart | Main action of a screen, footer buttons | text, onPressed (null = disabled), isLoading | Button · Style=Filled |

## cards
| Widget | Path | Use it for | Key params | Figma equivalent |
|---|---|---|---|---|
| AppCard | lib/widgets/cards/app_card.dart | Container card with optional gradient border | child, padding, gradientBorder | Card product |
```

(The rows above show the shape; fill them from the real constructors.)

## Keep it current

- Every widget created in `lib/widgets/` during a flow implementation gets a row in the same change.
- When an existing widget gains an optional parameter, update its "Key params".
- The "Figma equivalent" column is filled the first time a Figma component is matched to the widget; it is what makes later flows faster. If the team adopts Code Connect, the same pairs are the mappings to publish.
