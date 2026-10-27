# HU handoff template → implementation

The design team's HU documents ("HU - <flujo> - Handoff") always use these five sections. Read each one for the items below and put them in the brief.

| HU section | Look for | Becomes |
|---|---|---|
| **1. Resumen Ejecutivo y Casos de Uso** | Objetivo; camino feliz; contingencias; criterio funcional; criterio no funcional | Feature name and folder; the list of states to support; visibility conditions (e.g. "solo visible si el wallet tiene saldo > $0.00") → a check **at the entry point**, not inside the page; performance requirements (Optimistic UI, no flicker) → provider design |
| **2. Reglas de Negocio y Compliance** | Permisos y roles; validaciones (mínimos, máximos, divisas, defaults); trazabilidad | Provider validation getters and constants; default values (MXN); reset rules (change currency → amount 0.00); exact error copy → ARB keys; "no persiste datos / no requiere bitácora" → no write endpoint, no audit call |
| **3. Orquestación y Estados de Pantalla** | Navegación de entrada y salida; validación en vivo; performance; loading / empty / error states; salida prematura | Push callsites (entry) and the destination flow + parameters (exit); which block is blocking vs. interactive; skeleton / empty / error widgets; "salida prematura sin efecto" → no confirmation dialog on back |
| **4. Implementación Visual y Componentes** | A. table Componente / Estado / Link de Figma; B. tokens semánticos | The list of Figma nodes to read (one per state); the token → usage table to validate the color mapping |
| **5. Ciberseguridad y Manejo de Errores Críticos** | Datos sensibles; políticas de reintentos | Masking / no-logging rules; retry limits (or "sin límite") on the retry button |

## Always a gap unless the HU states it

- Endpoints, request/response contracts, and which calculations are server-side.
- Numeric thresholds and limits for every variant/level and every currency.
- Parameters the destination flow must accept (e.g. preloaded amount and currency).
- How the entry-point condition is obtained (which provider/repository already knows the wallet balance).
- Tokens referenced in section 4B or in Figma that don't exist in the project palette.

## Mock data is not data

Amounts, names and dates visible in Figma frames are illustrative. They can contradict each other inside the same frame (e.g. "Si inviertes $100,000.00" next to a button "Invertir $500,000.00"). Never derive rules or constants from them; use them only to understand formatting (currency symbol, decimals, where the currency code goes).
