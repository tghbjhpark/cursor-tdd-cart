# export — 세션 보고서 + Transcript Export (`/export-session` 별칭)

**추가 입력 없이 즉시 실행.** 사용자가 `/export` 만 입력했다. 세션 주제·산출물·대화 내용은 **현재 채팅 전체**에서 자동 추출한다. 추가 질문·확인 요청 금지.

## 자동 추출 (사용자에게 묻지 말 것)
- **세션 주제**: 이번 대화의 핵심 작업 (예: TDD RED, Command 작성, pytest 실행)
- **산출물**: 생성·수정된 파일 목록
- **Transcript**: User/Cursor 턴 전체

## 번호 규칙
1. `Report/`·`Prompting/`의 기존 `NN.*` 파일을 확인한다.
2. 가장 큰 번호 + 1을 다음 번호로 쓴다. (예: 04까지 있으면 → 05)
3. 번호는 **2자리** (`01`, `02`, … `05`).

## 생성 파일 (반드시 2개)

| 파일 | 설명 |
|------|------|
| `Report/NN.REPORT.md` | 세션 요약 보고서 |
| `Prompting/NN.Export-Transcript.md` | 대화 전문 Export |

## 보고서 형식 (`Report/NN.REPORT.md`)
- 제목: `# MagicSquare_1004 — {자동 추출한 세션 주제}`
- 상단 메타 표: 프로젝트, 단계, 보고서 생성일, 목적
- 섹션: 1. 요약 / 2. 핵심 결정·산출물 / 3. 다음 단계
- 관련 Transcript 링크: `Prompting/NN.Export-Transcript.md`
- 마지막 줄: `*본 문서는 Report/NN.REPORT.md — …입니다.*`
