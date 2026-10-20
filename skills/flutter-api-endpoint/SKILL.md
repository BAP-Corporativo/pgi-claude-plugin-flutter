---
name: flutter-api-endpoint
description: Add or change a REST endpoint, DTO, mapper, or repository method in a Nextline PGI Flutter project (UNITED, FinsofApp and their flavors) — *Api method receiving the token and sending the manual "Authorization Bearer" header through ApiClient, @JsonSerializable Dto*Response plus build_runner, a dto_*_mapper extension with toModel(), and a repository method that returns a *Model and translates DioException into a readable error. Use this whenever the user asks to consume, integrate, connect, or add an endpoint, servicio, petición, request, API call, or "conectar con el back", create or modify a DTO / model from a JSON response, add a field to a response, or fix a parsing or 401/403 error in a request — even if they just paste a JSON or a Swagger/Postman snippet and say "intégralo".
---

# Flutter API endpoint

Every request goes through three tiers: **`*Api` → `*Repository` → provider**. The Api talks HTTP, the repository turns the response into a domain `*Model` (or a readable error), the provider only sees models and error strings.

## Step 0 — Resolve

1. Read `CLAUDE.md` for the package name; otherwise `grep '^name:' pubspec.yaml`. Examples below use `united`.
2. Canonical reference in UNITED: `ProductChangeApi` / `ProductChangeRepository` and `lib/core/services/network/dtos/product_change/`. In another project, open its closest equivalent and confirm the same shapes before writing.

## Files involved

```
lib/core/services/network/api/endpoints/<feature>/<feature>_api.dart      # *Api
lib/core/services/network/dtos/<feature>/dto_<name>_response.dart         # DTO (+ .g.dart)
lib/core/services/network/dtos/<feature>/dto_<name>_mapper.dart           # extension toModel()
lib/core/services/repositories/<feature>/<feature>_repository.dart        # *Repository
lib/domain/<feature>/<name>_model.dart                                    # *Model, exported from domain.dart
```

## Worked example: preview + create a transfer

Backend response for `GET client/transfers/{accountId}/preview?beneficiary_id=..&amount=..`:
```json
{ "fee": 12.5, "total": 1512.5, "applied_at": "2026-10-12T18:20:00Z", "reference": null }
```

### 1. DTO

```dart
// lib/core/services/network/dtos/transfers/dto_transfer_preview_response.dart
import 'package:json_annotation/json_annotation.dart';

part 'dto_transfer_preview_response.g.dart';

@JsonSerializable()
class DtoTransferPreviewResponse {
  final double fee;
  final double total;
  @JsonKey(name: 'applied_at')
  final String appliedAt;
  final String? reference;

  DtoTransferPreviewResponse({
    required this.fee,
    required this.total,
    required this.appliedAt,
    this.reference,
  });

  factory DtoTransferPreviewResponse.fromJson(Map<String, dynamic> json) =>
      _$DtoTransferPreviewResponseFromJson(json);

  Map<String, dynamic> toJson() => _$DtoTransferPreviewResponseToJson(this);
}
```

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

DTO rules:
- Class `Dto<Name>Response`, file `dto_<name>_response.dart`, `part '<same>.g.dart';`.
- snake_case → camelCase with `@JsonKey(name: ...)`.
- Every field the backend can omit or send as `null` is nullable.
- Numeric fields that may arrive as `1500` or `1500.0` → `double` or `num`, never `int`.

### 2. Domain model

```dart
// lib/domain/transfers/transfer_preview_model.dart
class TransferPreviewModel {
  final double fee;
  final double total;
  final DateTime appliedAt;
  final String reference;

  const TransferPreviewModel({
    required this.fee,
    required this.total,
    required this.appliedAt,
    required this.reference,
  });
}
```

Add `export 'transfers/transfer_preview_model.dart';` to `lib/domain/domain.dart`.

### 3. Mapper

```dart
// lib/core/services/network/dtos/transfers/dto_transfer_preview_mapper.dart
import 'package:united/core/services/network/dtos/transfers/dto_transfer_preview_response.dart';
import 'package:united/domain/domain.dart';

extension DtoTransferPreviewMapper on DtoTransferPreviewResponse {
  TransferPreviewModel toModel() => TransferPreviewModel(
        fee: fee,
        total: total,
        appliedAt: DateTime.parse(appliedAt).toLocal(),
        reference: reference ?? '',
      );
}
```

The model holds Dart types the UI can use directly (`DateTime`, enums, non-null defaults).

### 4. Api — token as parameter, header attached here

```dart
// lib/core/services/network/api/endpoints/transfers/transfers_api.dart
import 'package:dio/dio.dart';
import 'package:united/core/core.dart';

class TransfersApi {
  TransfersApi({required this.apiClient});

  final ApiClient apiClient;

  Future<Response> getTransferPreview(String token, int accountId, int beneficiaryId, double amount) async {
    try {
      final response = await apiClient.get(
        'client/transfers/$accountId/preview',
        params: {
          'beneficiary_id': beneficiaryId,
          'amount': amount,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $token',
          },
        ),
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  Future<Response> createTransfer(String token, int accountId, int beneficiaryId, double amount) async {
    try {
      final response = await apiClient.post(
        'client/transfers/$accountId/request',
        params: {
          'beneficiary_id': beneficiaryId,
          'amount': amount,
        },
        options: Options(
          headers: {
            'Authorization': 'Bearer $token',
          },
        ),
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }
}
```

- Paths are relative and without a leading `/`; `ApiClient` holds the flavor base URL.
- `params` sends query parameters. If the backend expects a JSON body, check `ApiClient.post`'s signature for the body argument instead of guessing.
- Constructor uses the named `required this.apiClient`.

### 5. Repository — returns `*Model`, translates errors

```dart
// lib/core/services/repositories/transfers/transfers_repository.dart
import 'package:dio/dio.dart';
import 'package:united/core/core.dart';
import 'package:united/core/services/network/dtos/transfers/dto_transfer_preview_mapper.dart';
import 'package:united/core/services/network/dtos/transfers/dto_transfer_preview_response.dart';
import 'package:united/domain/domain.dart';

class TransfersRepository {
  TransfersRepository(this.transfersApi);

  final TransfersApi transfersApi;

  Future<TransferPreviewModel> getTransferPreview(String token, int accountId, int beneficiaryId, double amount) async {
    try {
      final response = await transfersApi.getTransferPreview(token, accountId, beneficiaryId, amount);
      final dto = DtoTransferPreviewResponse.fromJson(response.data);
      return dto.toModel();
    } on DioException catch (e) {
      if (e.response?.data != null) {
        throw e.response?.data['detail'] ?? 'Error desconocido';
      } else {
        throw ApiError.fromDioError(e).toString();
      }
    }
  }

  Future<void> createTransfer(String token, int accountId, int beneficiaryId, double amount) async {
    try {
      await transfersApi.createTransfer(token, accountId, beneficiaryId, amount);
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

The repository throws a **`String`** (backend `detail` or `ApiError` text). That is the contract the provider relies on to show `e.toString()`.

DTO and mapper files are imported directly by path in the repository; they are networking-internal and not part of the `core.dart` barrel. Everything else goes through barrels.

### 6. Provider usage

```dart
final secureRepository = ServiceLocator.getIt<SecureRepositoryImpl>();
final transfersRepository = ServiceLocator.getIt<TransfersRepository>();

Future<String> _token() async => await secureRepository.token ?? '';

bool _isLoadingPreview = false;
bool get isLoadingPreview => _isLoadingPreview;

TransferPreviewModel? _preview;
TransferPreviewModel? get preview => _preview;

String? previewError;

Future<void> getTransferPreview() async {
  final beneficiary = _selected;
  final amount = selectedAmount;
  if (beneficiary == null || amount == null) return;
  _isLoadingPreview = true;
  notifyListeners();
  try {
    final token = await _token();
    _preview = await transfersRepository.getTransferPreview(token, accountId, beneficiary.id, amount);
    previewError = null;
  } catch (e) {
    _preview = null;
    previewError = e.toString();
  } finally {
    _isLoadingPreview = false;
    notifyListeners();
  }
}

bool _isCreatingTransfer = false;
bool get isCreatingTransfer => _isCreatingTransfer;

String? createTransferError;

Future<bool> createTransfer() async {
  final beneficiary = _selected;
  final amount = selectedAmount;
  if (beneficiary == null || amount == null) return false;
  _isCreatingTransfer = true;
  notifyListeners();
  try {
    final token = await _token();
    await transfersRepository.createTransfer(token, accountId, beneficiary.id, amount);
    createTransferError = null;
    return true;
  } catch (e) {
    createTransferError = e.toString();
    return false;
  } finally {
    _isCreatingTransfer = false;
    notifyListeners();
  }
}
```

- The token is read **on every request** via `_token()`; never cache it in a field.
- Write operations can still return `bool` to the page for navigation, but the provider keeps the backend's message in `createTransferError` so the page can show it.
- Guard clauses at the top (`if (... == null) return`) avoid calling the API with incomplete data.

If the Api/Repository classes are new, register them (see `flutter-feature-scaffold`, step 5):
```dart
getIt.registerLazySingleton<TransfersApi>(() => TransfersApi(apiClient: getIt<ApiClient>()));
getIt.registerLazySingleton<TransfersRepository>(() => TransfersRepository(getIt<TransfersApi>()));
```

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Omit `Options(headers: {'Authorization': 'Bearer $token'})` because "the interceptor handles auth" | Attach it in every Api method | The interceptor only reacts to 401/403 — by **forcing logout**. A missing header looks like the user being randomly logged out |
| Read the token inside the Api or Repository | Receive `String token` as the first parameter | Existing contract: the provider supplies the token |
| Cache the token in a provider field during `init()` | `await _token()` inside each request | A stale token gets a 401 → forced logout mid-flow |
| Write operation that returns `bool` and swallows `DioException` (`on DioException { return false; }`) | Return `void`/`*Model` and throw the same translated error as reads | `false` loses the backend's `detail`; for money operations the user must see why it failed |
| Return `Response`, `Map<String, dynamic>` or a `Dto*` from the repository | Return a `*Model` via `toModel()` | DTOs never cross above the repository layer |
| Parse `response.data['fee']` in the provider | Parse via DTO + mapper in the repository | Parsing stays in one typed place |
| `toModel()` inside the DTO class | Separate `dto_<name>_mapper.dart` extension | Matches the project's file layout; keeps the generated-code file pure |
| Hand-edit `dto_*.g.dart` | Change the DTO, rerun build_runner | Generated files are overwritten |
| Non-nullable fields for values the backend may omit | Nullable in the DTO, default in `toModel()` | Prevents `type 'Null' is not a subtype` crashes |
| `'/client/...'` or full `https://...` URLs | `'client/...'` relative path | Base URL comes from the flavor's `.env` |

## Finish

1. build_runner if any DTO changed; `export` new models in `domain.dart`.
2. `flutter analyze` must pass.
3. Report: endpoint path + method, DTO/mapper/model files, repository signature, and any field made nullable because the contract was unclear.
