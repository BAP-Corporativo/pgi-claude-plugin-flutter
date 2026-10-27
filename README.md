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
| `figma-hu-to-flutter` | Implementar un flujo desde el HU de diseño + nodos de Figma, reutilizando widgets |

## Cómo trabajan juntas

Cada skill funciona sola. `figma-hu-to-flutter` es la única que orquesta a las demás:

| Pides | Se usa |
|---|---|
| Un flujo completo desde su HU / Figma | `figma-hu-to-flutter` → `flutter-feature-scaffold` + `flutter-api-endpoint` + `flutter-intl-strings` |
| Solo una pantalla nueva sin diseño | `flutter-feature-scaffold` |
| Solo integrar un endpoint o un mock | `flutter-api-endpoint` |
| Solo textos | `flutter-intl-strings` |
| CSS pegado de Figma | `figma-css-to-flutter` |

## Prompt para un flujo completo

```
Implementa el flujo "Simulador de inversión" (HU en el índice de flujos).
Endpoints (disponibles | mock acordado):
- GET client/investment/simulator/levels?currency_id={id}
  <JSON>
- GET client/investment/simulator?currency_id={id}&amount={monto}
  <JSON>
Divisas: MXN=3, USD=?, EUR=?
Entrada: opción "Simular inversión" del bottom sheet de la alcancía.
Salida: "Invertir" → flujo de nueva inversión con monto y divisa precargados.
Alcance de esta sesión: brief + capa de datos. La UI en la siguiente.
```

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
