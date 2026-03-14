# 건강검진 추적 관리

회사 지원 건강검진 병원 조사 및 개인 건강검진 결과를 추적 관리하는 저장소입니다.

## 프로젝트 배경

- 회사 지원 건강검진 패키지 활용 (30만원 기준)
- 집(현대3차아이파크, 영등포구) + 회사(카카오 판교아지트) 기준 접근성 조사
- 매년 검진 결과를 추적하여 건강 변화를 모니터링

## 디렉토리 구조

```
health-checkup/
├── README.md
├── CHANGELOG.md                       # 작업 이력
├── reports/
│   ├── 2026-final-recommendation.md   # 최종 추천 및 병원별 최적 조합
│   ├── 2026-health-analysis.md        # 개인 검진결과 분석 및 2026 추천
│   ├── 2026-nearby-hospitals.md       # 집 근거리 병원 (30분 이내)
│   ├── 2026-transfer-hospitals.md     # 서울 원거리 병원 (30~50분)
│   └── 2026-pangyo-hospitals.md       # 판교/분당 병원 + 아폴로 피부시술
├── results/
│   ├── naver-transit-times.md         # 이동시간 실측 (교통수단별 비교)
│   ├── 2024-검진결과.pdf
│   ├── 2025-검진결과.pdf
│   └── *.xlsx                         # 병원 리스트 원본 데이터
└── scripts/
    └── retry-transit.py               # TMAP API 자동 측정 스크립트
```

## 리포트 읽는 순서

1. **[건강 분석](reports/2026-health-analysis.md)** - 내 건강 상태와 올해 받아야 할 검사 확인
2. **[최종 추천](reports/2026-final-recommendation.md)** - TOP 5 병원 + 병원별 최적 조합
3. **[이동시간 비교](results/naver-transit-times.md)** - 교통수단별(지하철/버스/도보) 시간 비교
4. 병원 상세가 궁금하면: [근거리](reports/2026-nearby-hospitals.md) | [원거리](reports/2026-transfer-hospitals.md) | [판교](reports/2026-pangyo-hospitals.md)

## 향후 계획

- [ ] 2026년 검진 병원 최종 선택 및 예약
- [ ] 2026년 검진 완료 후 결과 업로드 및 연도별 비교 업데이트
- [ ] 매년 검진결과 추적하여 건강 트렌드 관리
