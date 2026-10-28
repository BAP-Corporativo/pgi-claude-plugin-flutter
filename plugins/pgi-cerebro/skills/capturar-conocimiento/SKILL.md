---
name: capturar-conocimiento
description: Entrevista a un dev de United (API, BackOffice o App) y redacta su archivo de conocimiento en docs/knowledge/ a partir de la plantilla. Úsala cuando alguien quiera documentar lo que sabe de su área, dictar trampas, flujos críticos, deploy o incidentes, o cuando se pida "capturar conocimiento" o completar el paso 2.
---

# Capturar el conocimiento de un dev

Objetivo: dejar por escrito lo que **solo esa persona sabe** y no está en el código ni en
`docs/domain/`. El resultado es `docs/knowledge/<area>-<nombre>.md`, con la estructura de
`docs/knowledge/plantilla-conocimiento-dev.md`.

## 1. Arranque

- Debes estar en el repo cerebro del proyecto (en UNITED, `united-platform`): es el que tiene
  `docs/knowledge/plantilla-conocimiento-dev.md`. Si no lo encuentras, pide la ruta antes de seguir.
- Pregunta nombre y área (`api`, `backoffice`, `app`). Fecha de hoy en `AAAA-MM-DD`.
- Si ya existe `docs/knowledge/<area>-<nombre>.md`, léelo y continúa donde se quedó.
- Lee la plantilla. **No leas** `docs/domain/_fuentes/` ni el código completo; consulta un doc
  de dominio o un archivo puntual solo si la respuesta lo menciona.

## 2. Entrevista

Ve sección por sección de la plantilla. Por cada una:

- Haz **una o dos preguntas a la vez**, concretas, en español. Ejemplos:
  - Trampas: "¿Qué parte del código te da miedo tocar y por qué?", "¿Hay algo que parece bug
    pero es a propósito?"
  - Flujos críticos: "Si mañana se rompe una sola cosa, ¿cuál sería la peor?", "¿Cómo la pruebas
    a mano?"
  - Deploy: "Desde que se hace merge, ¿qué pasa hasta que está en producción? ¿Qué es manual?"
  - Incidentes: "Cuéntame el último incidente en producción: qué falló, cómo lo detectaron,
    cómo se resolvió."
  - Dependencias: "¿Qué credenciales o cuentas vencen o se renuevan? ¿Quién tiene acceso?"
- Repregunta cuando la respuesta sea vaga: pide el archivo, el endpoint, la tabla, el ambiente
  o un ejemplo con números.
- Si la persona menciona algo que contradice `docs/domain/`, anótalo para la sección final.
- Acepta "no sé" o "sáltala" sin insistir; la sección queda marcada como pendiente.

Al final de cada sección, muestra un resumen corto de lo que vas a escribir y pide confirmación.

## 3. Redacción

- Escribe en el archivo **conforme avanzas** (después de cada sección confirmada), para no
  perder nada si la sesión se corta.
- Lenguaje claro, frases cortas, con referencias concretas (`UnitedAPI/src/...`, endpoint,
  tabla, ambiente).
- **Nunca escribas secretos**: contraseñas, llaves, tokens, cadenas de conexión ni datos
  personales de clientes. Si la persona dicta uno, no lo copies; escribe solo dónde vive
  (p. ej. "en el secreto de GitHub `X`" o "en AWS Secrets Manager").
- Agrega al final:
  - `## Contradicciones con docs/domain`: lo que no coincide, con el archivo de dominio.
  - `## Pendientes`: secciones o preguntas que quedaron sin respuesta.

## 4. Cierre

- Muestra el archivo final y una lista de:
  - riesgos o bugs mencionados que merecen issue;
  - contradicciones que obligan a actualizar `docs/domain/`.
- Propón actualizar el estado del paso 2 en `README.md` si con esto se completa un área.
- No hagas commit sin aprobación.
