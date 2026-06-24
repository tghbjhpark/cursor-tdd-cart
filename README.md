# Cart Discount TDD Practice

## 목적

이 프로젝트는 **장바구니 할인 계산 로직**을 TDD(Test-Driven Development) 방식으로 구현하는 연습 프로젝트입니다.

도메인 로직은 `src/cart.py`의 Entity 계층에 위치합니다. 모든 테스트와 구현은 **계약 ID**(INV-*, E-*)를 기준으로 작성·추적합니다. 계약 ID는 테스트와 구현을 잇는 **추적의 못**입니다.

상세 요구사항·Discovery 배경은 [docs/PRD.md](docs/PRD.md)를 참고하세요.

**현재 단계:** INV-1 RED 완료 · GREEN 대기 ([테스트 플랜](docs/TEST_PLAN-INV-1-E-1-E-2.md) §7 순서)

## 핵심 원칙

1. **ID에 없는 동작은 만들지 않는다.** 계약표에 없는 할인·예외·기능은 구현하지 않습니다.
2. **테스트가 먼저다.** 구현보다 실패하는 테스트가 항상 앞섭니다.
3. **RED → GREEN → REFACTOR** 순서를 따릅니다.
4. **과잉 구현을 금지한다.** 해당 ID를 통과시키는 최소 코드만 작성합니다.

## 계약 ID 목록

| ID    | 계약(불변식 / 에러)                                                 | 근거 레벨 | 계층        |
| ----- | ------------------------------------------------------------ | ----- | --------- |
| INV-1 | `subtotal(items) == Σ(price × qty)`                          | —     | Entity    |
| INV-2 | `amount ≥ 50000 → round(amount×0.9)` / `< 50000 → 그대로` 경계 포함 | L1    | Entity    |
| INV-3 | `final = 문턱할인 적용 후, VIP면 round(×0.95)`. 순서 문턱→VIP 고정         | L2    | Entity    |
| INV-4 | 모든 입력에서 `0 ≤ final_total ≤ subtotal`. 할인은 금액을 늘리지 않는다        | L3    | Entity    |
| E-1   | `items is None → TypeError`                                  | L0    | Boundary* |
| E-2   | `price` 또는 `qty`가 음수 → `ValueError`, 인덱스 포함                  | L0    | Boundary* |

## 계약 ID 설명

### INV-1

품목 목록에서 소계를 `단가 × 수량`의 합으로 계산합니다. 할인 적용의 전제가 되는 기본 합산 규칙입니다.

### INV-2

문턱 할인 규칙입니다. 금액이 50,000원 이상이면 10% 할인(`round(amount × 0.9)`)을 적용하고, 50,000원 미만이면 원래 금액을 그대로 반환합니다. 경계값 50,000원은 할인 **포함**입니다.

### INV-3

VIP 추가 할인 규칙입니다. 문턱 할인을 먼저 적용한 뒤, VIP 고객이면 그 결과에 5% 할인(`round(× 0.95)`)을 적용합니다. 적용 순서는 **문턱 → VIP**로 고정입니다.

### INV-4

시스템 안전 불변식입니다. 어떤 입력에서도 최종 결제 금액은 0 이상이며 소계를 초과할 수 없습니다. 할인은 금액을 늘리지 않습니다.

### E-1

입력 경계 계약입니다. `items`가 `None`이면 `TypeError`를 발생시킵니다.

### E-2

입력 경계 계약입니다. `price` 또는 `qty`가 음수이면 인덱스 정보를 포함한 `ValueError`를 발생시킵니다.

## 계층 의미

### Entity

`src/cart.py`가 담당합니다. Flask 등 외부 프레임워크에 의존하지 않는 **순수 도메인 계산 로직**(소계·할인·최종 금액)을 구현합니다. INV-1 ~ INV-4가 이 계층의 불변식입니다.

### Boundary*

E-1, E-2는 입력 검증 경계에 가까운 규칙입니다. 본 실습에서는 별도 HTTP/UI 계층 없이 **도메인 함수 진입점**에서 `items`·`price`·`qty`를 검증합니다. 향후 Boundary 계층이 분리되면 동일 ID로 테스트를 이전할 수 있습니다.

## 예상 파일 구조

첫 TDD 사이클(INV-1, E-1, E-2) 기준. 상세는 [docs/TEST_PLAN-INV-1-E-1-E-2.md](docs/TEST_PLAN-INV-1-E-1-E-2.md) §3.

```text
.
├── README.md
├── docs/
│   └── TEST_PLAN-INV-1-E-1-E-2.md
├── src/
│   └── cart.py
└── tests/
    ├── entity/
    │   └── test_subtotal_inv_1.py    # INV-1
    └── boundary/
        └── test_subtotal_e_1_e_2.py  # E-1, E-2
```

## TDD 진행 순서

[docs/TEST_PLAN-INV-1-E-1-E-2.md](docs/TEST_PLAN-INV-1-E-1-E-2.md) §7 권장 순서. **한 번에 하나의 실패 테스트**만 추가하고 GREEN으로 통과시킨 뒤 다음으로 넘깁니다.

- RED: `tests/` 만 수정 · `src/` 건드리지 않음
- GREEN: `src/cart.py`에 최소 구현 · 충족한 계약 ID를 구현 줄 주석으로 표기
- REFACTOR: T1–T8 전부 통과 후 구조 정리 · 전후 `pytest -q` 동작 불변

### RED 체크리스트

`tests/` 만 수정. 각 항목은 **의도적으로 실패**하는 테스트가 추가된 상태여야 합니다.

| # | 계약 | 작업 | 파일 | 상태 |
|---|------|------|------|------|
| T1 | INV-1 | `test_inv_1_single_item` — `[(10_000, 2)]` → `20_000` | `tests/entity/test_subtotal_inv_1.py` | [x] |
| T2 | INV-1 | `test_inv_1_multiple_items_ac3_subtotal` — AC-3 소계 `66_000` | 동일 | [x] |
| T3 | INV-1 | `test_inv_1_empty_items` — `[]` → `0` | 동일 | [x] |
| T4 | E-1 | `test_e_1_items_none_raises_type_error` — `subtotal(None)` → `TypeError` | `tests/boundary/test_subtotal_e_1_e_2.py` | [ ] |
| T5 | E-2 | `test_e_2_negative_qty_includes_index` — 음수 qty, 메시지에 `0` | 동일 | [ ] |
| T6 | E-2 | `test_e_2_negative_price_includes_index` — 음수 price, 메시지에 `0` | 동일 | [ ] |
| T7 | E-2 | `test_e_2_violation_at_second_item` — 두 번째 품목 위반, 메시지에 `1` | 동일 | [ ] |
| T8 | E-2 | price·qty 모두 음수 — `[(-1, -1)]`, 메시지에 `0` | 동일 | [ ] |

RED 완료 확인:

```bash
pytest tests/entity/test_subtotal_inv_1.py -q    # INV-1 — import/ assertion 실패 기대
pytest tests/boundary/test_subtotal_e_1_e_2.py -q  # E-1, E-2 — 파일·테스트 추가 후
```

### GREEN 체크리스트

`src/cart.py` 만 수정. **해당 RED 묶음을 통과시키는 최소 코드**만 추가합니다.

| 순서 | 충족 ID | 작업 | 통과 테스트 | 상태 |
|------|---------|------|-------------|------|
| 1 | INV-1 | `subtotal` 구현 — `Σ(price × qty)` 루프·곱셈 | T1–T3 | [ ] |
| 2 | E-1 | `items is None` → `TypeError` (합산 **전** 검사) | T4 | [ ] |
| 3 | E-2 | `price < 0` 또는 `qty < 0` → `ValueError` (0-based 인덱스 포함) | T5–T8 | [ ] |

GREEN 구현 시 주석 예:

```python
total += price * qty  # INV-1
raise TypeError("items must not be None")  # E-1
raise ValueError(f"invalid item at index {i}")  # E-2
```

GREEN 완료 확인:

```bash
pytest -q   # T1–T8 전부 통과 (실패 0)
```

**주의:** INV-1 GREEN만으로는 E-1·E-2 테스트가 통과하면 안 됩니다. E 검증은 각각 별도 GREEN 사이클에서 추가합니다.

### REFACTOR

- [ ] T1–T8 통과 상태에서 중복 검증 로직 등 구조만 정리
- [ ] 리팩터 전후 `pytest -q` 결과 동일

**커밋 분리 예:** `test(RED)` → `feat(GREEN)` → `refactor` — [테스트 플랜 §7](docs/TEST_PLAN-INV-1-E-1-E-2.md) 참고

## 테스트 실행

```bash
pytest tests/entity/test_subtotal_inv_1.py -q   # INV-1
pytest tests/boundary/test_subtotal_e_1_e_2.py -q  # E-1, E-2
pytest -q                                        # 전체
```

`-q`는 quiet mode로, 테스트 결과를 간략하게 출력합니다.

## 구현 금지 사항

- 할인 정책 추가 금지
- 쿠폰, 세금, 배송비, 포인트 기능 추가 금지
- ID에 없는 예외 처리 추가 금지
- UI, CLI, DB, API 코드 추가 금지
