# Data contract: model from the design, DTO from the endpoint, mapper in between

## Rule

| Layer | Defined by | Changes when |
|---|---|---|
| `*Model` (domain) | What the screens need: HU + Figma | The design or the business rules change |
| `Dto*Response` | The endpoint JSON — real, or the agreed mock while the endpoint doesn't exist | The backend contract changes |
| `dto_*_mapper.dart` | Bridges both: renames, null → defaults, flags → nullable objects, sorting | Either side changes |

So: **design the model first** (it's ready as soon as the HU and Figma are), **write the DTO from the JSON** (real or mock), and **let the mapper absorb the differences**. When the real endpoint replaces the mock, only the DTO and the mapper may change; models, provider and UI stay intact.

## Steps

1. From the HU + Figma, list every value the screens show or use, and its type in Dart.
2. Put the JSON next to that list (real response, or the mock agreed with backend) and fill the "Source" column. Values with no source are gaps; values the app can compute itself stay out of the DTO.
3. Write models → DTOs → mappers → Api → Repository (`flutter-api-endpoint`).
4. If the endpoint doesn't exist yet: add the mock (see `flutter-api-endpoint`, "Mock-first"), and keep the JSON in the mock identical to what the DTO parses.

## Worked example — Investment simulator (UNITED)

### Endpoints

```
GET client/investment/simulator/levels?currency_id=3
GET client/investment/simulator?currency_id=3&amount=2600000
```

Both answer `{ "detail": "...", "content": { ... } }`.

### Screen value → source

| Screen (Figma) | Model field | Source | Notes |
|---|---|---|---|
| Progress bar with 3 segments + labels | `InvestmentLevelsModel.levels` | levels endpoint | Sorted by `min_amount` in the mapper |
| Level for the typed amount (optimistic) | `levelFor(amount)` | levels endpoint, computed locally | Replaces hardcoded thresholds; the HU minimums become a check, not constants |
| "Debes invertir al menos $20,000 MXN" | `minimumAmount` | levels endpoint (`levels.first.min_amount`) | If it differs from the HU, report it |
| "Nivel 1 - Control 16" | position + `title` | levels endpoint | "Nivel n" = index + 1 |
| "16% al año · sin plazo forzoso" | `annualReturn`, `termDays` | both endpoints | Copy for `term > 0` isn't in Figma → gap |
| "Ganarías $16,000.00" | `SimulationModel.totalReturn` | simulator endpoint | |
| "Cada mes recibirías $1,333.33" | `monthlyReturn` | simulator endpoint | |
| "Puedes retirar — Cuando quieras" | `termDays` (+ `withdrawalInfo` as fallback) | simulator endpoint | `withdrawal_info` comes as unlocalized text ("360 dias") and the app supports ES/EN → compose the copy from `termDays` in ARB |
| "Con $150,001 más llegas a Plus 17 · Ganarías 17% al año" | `nextLevel` (`amountNeeded`, `title`, `annualReturn`) | simulator endpoint | `is_highest: true` → `nextLevel == null` (Impulso 18 shows no suggestion) |
| "Invertir $[monto]" | `amount` + currency | provider state | Passed to the new-investment flow |
| MXN / USD / EUR chips | `SimulatorCurrency` (code + id) | **gap**: only `MXN = 3` is known | Look for an existing currency source in the project first |

### Models

```dart
// lib/domain/investment_simulator/investment_level_model.dart
class InvestmentLevelModel {
  final int id;
  final String title;
  final double annualReturn;
  final int termDays;
  final double minAmount;
  final double? maxAmount;
  final String currencyCode;

  const InvestmentLevelModel({
    required this.id,
    required this.title,
    required this.annualReturn,
    required this.termDays,
    required this.minAmount,
    required this.maxAmount,
    required this.currencyCode,
  });

  bool get hasForcedTerm => termDays > 0;

  bool contains(double amount) =>
      amount >= minAmount && (maxAmount == null || amount <= maxAmount!);
}
```

```dart
// lib/domain/investment_simulator/investment_levels_model.dart
class InvestmentLevelsModel {
  final List<InvestmentLevelModel> levels; // sorted by minAmount

  const InvestmentLevelsModel({required this.levels});

  double get minimumAmount => levels.isEmpty ? 0 : levels.first.minAmount;

  InvestmentLevelModel? levelFor(double amount) =>
      levels.where((level) => level.contains(amount)).firstOrNull;

  int indexOf(InvestmentLevelModel level) =>
      levels.indexWhere((item) => item.id == level.id);
}
```

```dart
// lib/domain/investment_simulator/simulation_model.dart
class SimulationModel {
  final int levelId;
  final String levelTitle;
  final double annualReturn;
  final int termDays;
  final double amount;
  final double monthlyReturn;
  final double totalReturn;
  final double finalAmount;
  final String withdrawalInfo;
  final String currencyCode;
  final NextLevelSuggestionModel? nextLevel; // null when the level is the highest

  const SimulationModel({
    required this.levelId,
    required this.levelTitle,
    required this.annualReturn,
    required this.termDays,
    required this.amount,
    required this.monthlyReturn,
    required this.totalReturn,
    required this.finalAmount,
    required this.withdrawalInfo,
    required this.currencyCode,
    required this.nextLevel,
  });
}

class NextLevelSuggestionModel {
  final String title;
  final double amountNeeded;
  final double annualReturn;

  const NextLevelSuggestionModel({
    required this.title,
    required this.amountNeeded,
    required this.annualReturn,
  });
}
```

Export the three files from `lib/domain/domain.dart`.

### DTOs — mirror the JSON exactly

```dart
// lib/core/services/network/dtos/investment_simulator/dto_investment_levels_response.dart
import 'package:json_annotation/json_annotation.dart';

part 'dto_investment_levels_response.g.dart';

@JsonSerializable()
class DtoInvestmentLevelsResponse {
  final String? detail;
  final DtoInvestmentLevelsContent content;

  DtoInvestmentLevelsResponse({this.detail, required this.content});

  factory DtoInvestmentLevelsResponse.fromJson(Map<String, dynamic> json) =>
      _$DtoInvestmentLevelsResponseFromJson(json);
  Map<String, dynamic> toJson() => _$DtoInvestmentLevelsResponseToJson(this);
}

@JsonSerializable()
class DtoInvestmentLevelsContent {
  final List<DtoInvestmentLevel> levels;

  DtoInvestmentLevelsContent({required this.levels});

  factory DtoInvestmentLevelsContent.fromJson(Map<String, dynamic> json) =>
      _$DtoInvestmentLevelsContentFromJson(json);
  Map<String, dynamic> toJson() => _$DtoInvestmentLevelsContentToJson(this);
}

@JsonSerializable()
class DtoInvestmentLevel {
  final int id;
  final String title;
  @JsonKey(name: 'annual_return')
  final num annualReturn;
  final int term;
  @JsonKey(name: 'min_amount')
  final num minAmount;
  @JsonKey(name: 'max_amount')
  final num? maxAmount;
  @JsonKey(name: 'currency_code')
  final String currencyCode;

  DtoInvestmentLevel({
    required this.id,
    required this.title,
    required this.annualReturn,
    required this.term,
    required this.minAmount,
    this.maxAmount,
    required this.currencyCode,
  });

  factory DtoInvestmentLevel.fromJson(Map<String, dynamic> json) =>
      _$DtoInvestmentLevelFromJson(json);
  Map<String, dynamic> toJson() => _$DtoInvestmentLevelToJson(this);
}
```

```dart
// lib/core/services/network/dtos/investment_simulator/dto_simulation_response.dart
import 'package:json_annotation/json_annotation.dart';

part 'dto_simulation_response.g.dart';

@JsonSerializable()
class DtoSimulationResponse {
  final String? detail;
  final DtoSimulationContent content;

  DtoSimulationResponse({this.detail, required this.content});

  factory DtoSimulationResponse.fromJson(Map<String, dynamic> json) =>
      _$DtoSimulationResponseFromJson(json);
  Map<String, dynamic> toJson() => _$DtoSimulationResponseToJson(this);
}

@JsonSerializable()
class DtoSimulationContent {
  final DtoSimulation simulation;
  @JsonKey(name: 'next_level')
  final DtoNextLevel nextLevel;

  DtoSimulationContent({required this.simulation, required this.nextLevel});

  factory DtoSimulationContent.fromJson(Map<String, dynamic> json) =>
      _$DtoSimulationContentFromJson(json);
  Map<String, dynamic> toJson() => _$DtoSimulationContentToJson(this);
}

@JsonSerializable()
class DtoSimulation {
  final DtoSimulationLevel level;
  final num amount;
  @JsonKey(name: 'monthly_return')
  final num monthlyReturn;
  @JsonKey(name: 'total_return')
  final num totalReturn;
  @JsonKey(name: 'final_amount')
  final num finalAmount;
  @JsonKey(name: 'withdrawal_info')
  final String? withdrawalInfo;
  @JsonKey(name: 'currency_code')
  final String currencyCode;

  DtoSimulation({
    required this.level,
    required this.amount,
    required this.monthlyReturn,
    required this.totalReturn,
    required this.finalAmount,
    this.withdrawalInfo,
    required this.currencyCode,
  });

  factory DtoSimulation.fromJson(Map<String, dynamic> json) => _$DtoSimulationFromJson(json);
  Map<String, dynamic> toJson() => _$DtoSimulationToJson(this);
}

@JsonSerializable()
class DtoSimulationLevel {
  final int id;
  final String title;
  @JsonKey(name: 'annual_return')
  final num annualReturn;
  final int term;

  DtoSimulationLevel({
    required this.id,
    required this.title,
    required this.annualReturn,
    required this.term,
  });

  factory DtoSimulationLevel.fromJson(Map<String, dynamic> json) =>
      _$DtoSimulationLevelFromJson(json);
  Map<String, dynamic> toJson() => _$DtoSimulationLevelToJson(this);
}

@JsonSerializable()
class DtoNextLevel {
  @JsonKey(name: 'is_highest')
  final bool isHighest;
  final String? title;
  @JsonKey(name: 'amount_needed')
  final num? amountNeeded;
  @JsonKey(name: 'annual_return')
  final num? annualReturn;

  DtoNextLevel({required this.isHighest, this.title, this.amountNeeded, this.annualReturn});

  factory DtoNextLevel.fromJson(Map<String, dynamic> json) => _$DtoNextLevelFromJson(json);
  Map<String, dynamic> toJson() => _$DtoNextLevelToJson(this);
}
```

Amounts are `num` because the backend sends `2600000` today and may send `2600000.5` tomorrow.

### Mappers — where the adaptation happens

```dart
// lib/core/services/network/dtos/investment_simulator/dto_investment_levels_mapper.dart
import 'package:united/core/services/network/dtos/investment_simulator/dto_investment_levels_response.dart';
import 'package:united/domain/domain.dart';

extension DtoInvestmentLevelsMapper on DtoInvestmentLevelsResponse {
  InvestmentLevelsModel toModel() {
    final levels = content.levels
        .map((dto) => InvestmentLevelModel(
              id: dto.id,
              title: dto.title,
              annualReturn: dto.annualReturn.toDouble(),
              termDays: dto.term,
              minAmount: dto.minAmount.toDouble(),
              maxAmount: dto.maxAmount?.toDouble(),
              currencyCode: dto.currencyCode,
            ))
        .toList()
      ..sort((a, b) => a.minAmount.compareTo(b.minAmount));
    return InvestmentLevelsModel(levels: levels);
  }
}
```

```dart
// lib/core/services/network/dtos/investment_simulator/dto_simulation_mapper.dart
import 'package:united/core/services/network/dtos/investment_simulator/dto_simulation_response.dart';
import 'package:united/domain/domain.dart';

extension DtoSimulationMapper on DtoSimulationResponse {
  SimulationModel toModel() {
    final simulation = content.simulation;
    final next = content.nextLevel;
    final hasNext = !next.isHighest && next.title != null && next.amountNeeded != null;
    return SimulationModel(
      levelId: simulation.level.id,
      levelTitle: simulation.level.title,
      annualReturn: simulation.level.annualReturn.toDouble(),
      termDays: simulation.level.term,
      amount: simulation.amount.toDouble(),
      monthlyReturn: simulation.monthlyReturn.toDouble(),
      totalReturn: simulation.totalReturn.toDouble(),
      finalAmount: simulation.finalAmount.toDouble(),
      withdrawalInfo: simulation.withdrawalInfo ?? '',
      currencyCode: simulation.currencyCode,
      nextLevel: hasNext
          ? NextLevelSuggestionModel(
              title: next.title!,
              amountNeeded: next.amountNeeded!.toDouble(),
              annualReturn: next.annualReturn?.toDouble() ?? 0,
            )
          : null,
    );
  }
}
```

### Api and Repository

```dart
class InvestmentSimulatorApi {
  InvestmentSimulatorApi({required this.apiClient});

  final ApiClient apiClient;

  Future<Response> getLevels(String token, int currencyId) async {
    try {
      final response = await apiClient.get(
        'client/investment/simulator/levels',
        params: {'currency_id': currencyId},
        options: Options(headers: {'Authorization': 'Bearer $token'}),
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  Future<Response> getSimulation(String token, int currencyId, double amount) async {
    try {
      final response = await apiClient.get(
        'client/investment/simulator',
        params: {'currency_id': currencyId, 'amount': amount},
        options: Options(headers: {'Authorization': 'Bearer $token'}),
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }
}
```

```dart
class InvestmentSimulatorRepository {
  InvestmentSimulatorRepository(this.investmentSimulatorApi);

  final InvestmentSimulatorApi investmentSimulatorApi;

  Future<InvestmentLevelsModel> getLevels(String token, int currencyId) async {
    try {
      final response = await investmentSimulatorApi.getLevels(token, currencyId);
      return DtoInvestmentLevelsResponse.fromJson(response.data).toModel();
    } on DioException catch (e) {
      if (e.response?.data != null) {
        throw e.response?.data['detail'] ?? 'Error desconocido';
      } else {
        throw ApiError.fromDioError(e).toString();
      }
    }
  }

  Future<SimulationModel> getSimulation(String token, int currencyId, double amount) async {
    try {
      final response = await investmentSimulatorApi.getSimulation(token, currencyId, amount);
      return DtoSimulationResponse.fromJson(response.data).toModel();
    } on DioException catch (e) {
      if (e.response?.data != null) {
        throw e.response?.data['detail'] ?? 'Error desconocido';
      } else {
        throw ApiError.fromDioError(e).toString();
      }
    }
  }
}
```

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Wait for the endpoint to design the model | Model from HU + Figma; DTO when the JSON (or mock) exists | The UI work starts earlier and survives contract changes |
| Model = copy of the DTO (`isHighest`, `withdrawal_info` strings in the UI) | Model in UI terms (`nextLevel == null`, `termDays`) | The mapper absorbs backend shapes |
| Show backend text (`"360 dias"`) directly | Compose localized copy from typed fields; backend text only as fallback | The app is bilingual; backend strings aren't |
| Hardcode level thresholds from the HU when an endpoint provides them | Load levels, compute the level locally (optimistic) | One source of truth; HU values become a validation check |
| Change the model when the backend renames a field | Change DTO `@JsonKey` + mapper only | Keeps provider and UI untouched |
