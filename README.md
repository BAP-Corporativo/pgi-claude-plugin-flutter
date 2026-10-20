# nextline-pgi-flutter

Plugin de Claude Code con las convenciones compartidas de los proyectos Flutter de Nextline PGI.

| Skill | Cuándo se activa |
|---|---|
| `flutter-feature-scaffold` | Crear un feature, pantalla o flujo nuevo |
| `flutter-api-endpoint` | Consumir un endpoint, crear o cambiar un DTO |
| `flutter-intl-strings` | Agregar o cambiar textos (ARB + intl_utils) |
| `flutter-add-flavor` | Agregar un ambiente / flavor |
| `flutter-build-release` | Generar APK / IPA por flavor |
| `figma-css-to-flutter` | Traducir CSS de Figma a widgets |

Las skills no tienen valores de proyecto fijos: leen el `CLAUDE.md` de cada repo (tabla de variables) o los descubren con `pubspec.yaml` y `lib/main_*_*.dart`.

## Instalar (una vez por máquina)

Dentro de Claude Code:

```
/plugin marketplace add <usuario-u-org>/nextline-pgi-flutter
/plugin install nextline-pgi-flutter@nextline-pgi
```

## Actualizar después de un push

`plugin.json` no fija `version`, así que cada commit cuenta como versión nueva.

```bash
claude plugin update nextline-pgi-flutter@nextline-pgi
```

O activa el auto-update del marketplace en `/plugin` → Marketplaces.

## Declararlo en un proyecto

Desde la raíz del proyecto Flutter:

```bash
claude plugin marketplace add <usuario-u-org>/nextline-pgi-flutter --scope project
```

Commitea el `.claude/settings.json` que se genera. Debe quedar así:

```json
{
  "extraKnownMarketplaces": {
    "nextline-pgi": { "source": { "source": "github", "repo": "<usuario-u-org>/nextline-pgi-flutter" } }
  },
  "enabledPlugins": { "nextline-pgi-flutter@nextline-pgi": true }
}
```

## Desarrollar y probar sin publicar

```bash
claude --plugin-dir ./nextline-pgi-flutter
claude plugin validate .
```
