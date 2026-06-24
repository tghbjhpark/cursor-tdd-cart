# PRD — 장바구니 할인 계산기 (cursor-tdd-cart)

| 항목 | 내용 |
|------|------|
| **문서 버전** | 1.0 |
| **작성일** | 2026-06-24 |
| **프로젝트** | cursor-tdd-cart |
| **단계** | Product Discovery 완료 → TDD RED 진입 대기 |
| **근거 문서** | [Report/01](../Report/01.REPORT.md), [Report/02](../Report/02.REPORT.md), [Prompting/01](../Prompting/01.Export-Transcript.md), [Prompting/02](../Prompting/02.Export-Transcript.md) |

---

## 1. 개요

### 1.1 제품 정의

**장바구니 할인 계산기**는 주문 품목(단가·수량)으로 소계를 산출하고, 문턱 할인(5만 원 초과 시 10%) 및 VIP 추가 할인(문턱 할인 후 5%)을 적용해 최종 결제 금액을 계산하는 도메인 로직과 주문 폼(Flask)으로 구성된다.

### 1.2 목적

- MomTest 인터뷰·실주문·CS 사례에서 **테스트 가능한 계약(Contract)** 을 도출하고, 계약 ID로 테스트·구현을 추적한다.
- Dual-Track TDD(RED → GREEN → REFACTOR)로 **Entity(순수 로직)** 와 **Boundary(입력/UI)** 를 분리한다.

### 1.3 범위 구분

| 구분 | 내용 | 본 PRD 범위 |
|------|------|-------------|
| **구현 대상** | 장바구니 소계·문턱 할인·VIP 할인·입력 검증 | ✅ 포함 |
| **Discovery 참고** | 1인 가구 식사·밀키트 구독 MomTest (세션 02) | ❌ 구현 제외, §8 참고 |
| **미확인** | 쿠폰·배송비·`subtotal == 50_000` 경계 | ❌ OOS |

---

## 2. 배경 — MomTest Discovery 요약

[Prompting/02.Export-Transcript.md](../Prompting/02.Export-Transcript.md) 세션에서 두 축의 발견이 있었다.

### 2.1 식사 도메인 (구현 범위 외)

30대 1인 가구 직장인 인터뷰에서 확인된 **실제 행동**:

- 저녁 배달 주 5회+, 월 식비 50만 원 이상 지출
- 메뉴 결정 15분+ → 단골 재주문(회피 전략)
- "바빠서 바꿀 에너지 없음" — 유료 대안(밀키트·구독) 시도 0건

**폐기된 가설:** 요리 독려, 식비 절약 UI, 메뉴 탐색, 냉장고 관리, 건강 니즈 중심 기획.

### 2.2 장바구니 할인 도메인 (본 제품)

[Prompting/02 — Turn 9~10](../Prompting/02.Export-Transcript.md) 인터뷰 메모·실주문·CS 클레임에서 계약이 도출되었다.

**인터뷰·운영 근거:**

| 출처 | 내용 |
|------|------|
| 2024-03-12 | A×3(12,000) + B×1(30,000) = 66,000 → 10% 할인 기대 59,400 |
| VIP 규칙 | 문턱 10% **후** 추가 5%; 순서 고정 |
| 주문 #1107 | 소계 60,000 → 결제 54,000 |
| 주문 #1042 | 소계 48,000 → 할인 없음 |
| 엑셀 검산 | 66,000×0.9=59,400; VIP 59,400×0.95=56,430 |
| CS | `qty=-1` → 화면 합계 0원(버그); items 없이 제출 → HTTP 500 |
| 미확인 | 쿠폰·배송비 없음; 50,000원 **포함** 여부 미확인 |

---

## 3. 사용자·시나리오

### 3.1 사용자

- 주문 담당자·운영자(CS 검산)
- Flask 주문 폼을 통해 품목·수량을 입력하는 Boundary 사용자

### 3.2 핵심 시나리오 (AC)

| ID | 시나리오 | 입력 | 기대 결과 |
|----|----------|------|-----------|
| AC-1 | 주문 #1107 | `subtotal=60_000`, `is_vip=False` | `total=54_000` |
| AC-2 | 주문 #1042 | `subtotal=48_000`, `is_vip=False` | `total=48_000` |
| AC-3 | 2024-03-12 (일반) | A×3(12,000)+B×1(30,000) | `subtotal=66_000`, `total=59_400` |
| AC-4 | 2024-03-12 (VIP) | 동일 품목, `is_vip=True` | `total=56_430` |

---

## 4. 기능 요구사항 — 계약표

모든 구현·테스트는 **계약 ID**를 참조한다. ID가 없는 동작은 구현하지 않는다.

### 4.1 불변식 (Invariant) — Entity (`src/cart.py`)

| ID | 계약 | 테스트 가능 문장 |
|----|------|------------------|
| INV-1 | 소계 합산 | `subtotal == sum(item.price * item.qty for item in items)` |
| INV-2 | 문턱 할인 적용 | `subtotal > 50_000`이면 `total == round(subtotal * 0.9)` |
| INV-3 | 문턱 미달 | `subtotal <= 50_000`이면 `total == subtotal` |
| INV-4 | VIP 추가 할인 | 문턱 적용 후 금액 `t1`에 대해 `is_vip=True`이면 `total == round(t1 * 0.95)` |
| INV-5 | VIP 단독 할인 없음 | `is_vip=True`이고 `subtotal <= 50_000`이면 `total == subtotal` |
| INV-6 | 할인 적용 순서 | 항상 **문턱 10% → VIP 5%** (순서 변경 금지) |

### 4.2 에러 계약 — Entity

| ID | 계약 | 테스트 가능 문장 |
|----|------|------------------|
| E-1 | 음수 수량 | `qty < 0`이면 `ValueError` (인덱스 포함 메시지) |
| E-2 | 음수 단가 | `price < 0`이면 `ValueError` |
| E-3 | None 입력 | `items is None`이면 `TypeError` |
| E-4 | 빈 장바구니 | `len(items) == 0`이면 `ValueError` |

### 4.3 에러 계약 — Boundary (`src/app.py`)

| ID | 계약 | 테스트 가능 문장 |
|----|------|------------------|
| E-5 | 음수 수량 UI | `qty < 0` 제출 시 응답 합계가 `0`이면 안 됨; 검증 오류 또는 E-1 위임 |
| E-6 | 빈 제출 | `items` 없이 POST 시 HTTP **500이 아님** → `400` 또는 `422` + 검증 메시지 |

### 4.4 구현 범위 제외 (OOS)

| OOS ID | 제외 항목 | 사유 |
|--------|-----------|------|
| OOS-1 | 쿠폰 할인 | 인터뷰 언급 없음 |
| OOS-2 | 배송비 | 인터뷰 언급 없음 |
| OOS-3 | `subtotal == 50_000` 시 10% 여부 | "넘으면"만 확인; 동점 주문·사례 없음 |
| OOS-4 | 소수 원 `ROUND` 방식 | 모든 검산 예가 정수; 분수 사례 없음 |
| OOS-5 | VIP 5%를 문턱 전 적용 | "문턱 → VIP 고정"만 확인 |
| OOS-6 | 문턱 미달 VIP 5% 단독 | 실주문·명시 규칙 없음 (INV-5는 추론) |
| OOS-7 | 포인트·등급·세그먼트 | 근거 없음 |
| OOS-8 | `qty == 0` 처리 | CS 사례는 `-1`만 |
| OOS-9 | 품목 카탈로그·카테고리 할인 | 단일 사례만 존재 |
| OOS-10 | 할인 캡·최대 할인 한도 | 언급 없음 |

---

## 5. 비기능 요구사항

### 5.1 아키텍처 (ECB)

| 계층 | 경로 | 책임 |
|------|------|------|
| Entity | `src/cart.py` | 소계·할인 순수 로직; Flask import 금지 |
| Boundary | `src/app.py` | Flask 주문 폼; `cart.py` 재사용 |
| Entity 테스트 | `tests/entity/` | INV-*, E-1~E-4, AC-* |
| Boundary 테스트 | `tests/boundary/` | E-5, E-6 |

### 5.2 개발 워크플로

```
RED (tests/ 만) → GREEN (src/ 최소 구현) → REFACTOR (구조 정리)
```

- 구현 줄에 충족 계약 ID 주석 필수 (예: `# INV-2`)
- 구조 변경과 동작 변경은 커밋 분리
- 작업 종료 시 `pytest -q` 전체 통과

### 5.3 기술 스택

- Python 3.12
- pytest
- Flask (Boundary)

---

## 6. MVP 범위

### 6.1 포함 (RED 우선순위)

| 순서 | 계약 ID | 내용 |
|------|---------|------|
| 1 | INV-1, AC-3 | 소계 합산 |
| 2 | INV-2, INV-3, AC-1, AC-2 | 문턱 10% 할인 |
| 3 | E-1, E-5 | 음수 수량 거부 |
| 4 | E-4, E-6 | 빈 장바구니·빈 제출 |
| 5 | INV-4, INV-6, AC-4 | VIP 2단계 할인 |

### 6.2 제외

- OOS-1 ~ OOS-10 전항
- 밀키트·식사 도메인 전체 (Discovery 참고만)

---

## 7. 검증·테스트 계획

### 7.1 명령

```bash
pytest -q                  # 전체
pytest tests/entity -q     # Entity (INV, E-1~4, AC)
pytest tests/boundary -q   # Boundary (E-5, E-6)
```

### 7.2 Entity 테스트 예시

```python
# AC-1 — INV-2
assert calc_total(60_000, is_vip=False) == 54_000

# AC-2 — INV-3
assert calc_total(48_000, is_vip=False) == 48_000

# AC-3 — INV-1, INV-2
assert calc_subtotal([(12_000, 3), (30_000, 1)]) == 66_000
assert calc_total(66_000, is_vip=False) == 59_400

# AC-4 — INV-4, INV-6
assert calc_total(66_000, is_vip=True) == 56_430

# E-1
with pytest.raises(ValueError, match="qty"):
    calc_subtotal([(12_000, -1)])
```

### 7.3 Boundary 테스트 예시

```python
# E-6
resp = client.post("/order", data={})
assert resp.status_code in (400, 422)
assert resp.status_code != 500
```

---

## 8. Discovery 부록 — 밀키트 구독 (구현 범위 외)

[Report/02](../Report/02.REPORT.md) 및 [Prompting/02](../Prompting/02.Export-Transcript.md) Turn 5~8에서 도출된 계약은 **별도 제품 가설**이며 본 코드베이스 MVP에 포함하지 않는다.

**핵심 발견 (참고):**

- Job-to-be-done: "추가 에너지 없이 저녁 끝내기"
- 밀키트·구독 과거 시도 0건
- "프리미엄·정기구독"은 미입증 가정

향후 식사 도메인 제품을 기획할 경우 `Prompting/02` Turn 6·8의 INV/E/MVP/OOS 표를 별도 PRD로 분리하는 것을 권장한다.

---

## 9. 미해결 질문 (MomTest 보강)

구현 전 또는 OOS 해제 전에 확인할 항목 ([Report/02 §3](../Report/02.REPORT.md)):

1. `subtotal == 50_000`일 때 10% 할인 적용 여부
2. VIP 고객 **실주문** 번호·금액 (엑셀 검산만 존재)
3. 중간 `round()` 적용 시점 (문턱 후 / VIP 후 / 최종 1회)
4. `qty == 0` 입력 시 기대 동작
5. `price` 음수 실제 CS 사례 유무

---

## 10. 문서 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| 1.0 | 2026-06-24 | Report/01·02, Prompting/01·02 기반 초안 작성 |

---

## 11. 관련 링크

| 문서 | 설명 |
|------|------|
| [AGENTS.md](../AGENTS.md) | 저장소 워크플로·ECB 지도 |
| [Report/01.REPORT.md](../Report/01.REPORT.md) | Export 워크플로 세션 |
| [Report/02.REPORT.md](../Report/02.REPORT.md) | MomTest·계약 도출 세션 요약 |
| [Prompting/01.Export-Transcript.md](../Prompting/01.Export-Transcript.md) | Export 세션 Transcript |
| [Prompting/02.Export-Transcript.md](../Prompting/02.Export-Transcript.md) | Discovery·계약 도출 Transcript |

*본 문서는 docs/PRD.md — 장바구니 할인 계산기 제품 요구사항 정의서입니다.*
