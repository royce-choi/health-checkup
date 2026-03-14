"""
건강검진 병원 대중교통 이동시간 측정 스크립트
TMAP 대중교통 API 사용 (SK Open API)

사용법:
  cd /Users/royce/Project/kimcp
  SK_APP_KEY=l05T3nQpQ17p8vgSeycy549R95yGgfwl2PlB4nwt uv run python /Users/royce/Project/health-checkup/scripts/retry-transit.py

기준시간: 평일 아침 8시 (건강검진 기준)
출발지: 신도림역 (집), 판교역 (회사)
"""

import httpx
import asyncio
import json
import os
import sys

API = 'https://apis.openapi.sk.com/transit/routes'
KEY = os.environ.get('SK_APP_KEY', '')
SEARCH_TIME = '202603120800'  # 평일 아침 8시
RESULTS_PATH = '/Users/royce/Project/health-checkup/results/transit-times.json'

if not KEY:
    print("ERROR: SK_APP_KEY 환경변수를 설정해주세요")
    sys.exit(1)

origins = {
    '집(대림현대3차)': (126.89561060820566, 37.50552097779974),
    '판교역': (127.1118, 37.3948),
}

hospitals = {
    # === 근거리 (무환승) ===
    '필립메디컬센터 서울': (126.8951902, 37.5211719),
    '영등포병원': (126.8958262, 37.5268545),
    '소중한메디케어': (126.8863423, 37.4809848),
    '하나로의료재단 종로센터': (126.9814392, 37.57096),
    '녹십자아이메드 강북': (126.997282, 37.5660776),
    # === 환승 ===
    '강북삼성병원': (126.967750, 37.5684083),
    '라이프케어내과 여의도': (126.9245977, 37.5225179),
    'KMI 여의도': (126.9248449, 37.5243159),
    '한국건강관리협회 서울서부': (126.850910, 37.553847),
    '서울메디케어 공덕': (126.954371, 37.5479194),
    'KMI 광화문': (126.9733018, 37.5718397),
    '메디플라워헬스케어': (127.0144867, 37.4915934),
    '서울센트럴메디케어': (126.8370984, 37.5619101),
    'KMI 강남': (127.0508807, 37.5055012),
    '녹십자아이메드 강남': (127.0059605, 37.490271),
    'HS한신메디피아': (127.0068701, 37.5127259),
    '인터케어검진센터': (127.0465038, 37.5029974),
    '하나로의료재단 강남': (127.0470436, 37.5035425),
    '비에비스나무병원': (127.0324057, 37.5095709),
    # === 판교/분당 ===
    '지앤이알파돔': (127.1121495, 37.3954525),
    '메디피움 판교': (127.1125495, 37.3977124),
    '아폴로헬스케어': (127.0983341, 37.4134038),
    '메디피움 분당': (127.1320504, 37.3786829),
    '필립메디컬 분당': (127.1198192, 37.3852816),
    '분당엠디그린': (127.1230419, 37.3994728),
    '보바스기념병원': (127.098256, 37.3559526),
    '분당제생병원': (127.1217660, 37.3881608),
}

# 판교역에서도 측정할 병원들
pangyo_hospitals = [
    '지앤이알파돔', '메디피움 판교', '아폴로헬스케어', '메디피움 분당',
    '필립메디컬 분당', '분당엠디그린', '보바스기념병원', '분당제생병원'
]


def parse_route(itinerary):
    legs = itinerary.get('legs', [])
    steps = []
    for leg in legs:
        mode = leg.get('mode', '')
        if mode == 'WALK':
            dist = leg.get('distance', 0)
            t = leg.get('sectionTime', 0)
            steps.append(f"도보 {t//60}분({dist}m)")
        elif mode == 'SUBWAY':
            route = leg.get('route', '')
            t = leg.get('sectionTime', 0)
            start_name = leg.get('start', {}).get('name', '')
            end_name = leg.get('end', {}).get('name', '')
            stations = leg.get('passStopList', {}).get('stations', [])
            n_stops = max(0, len(stations) - 1)
            steps.append(f"{route} {start_name}→{end_name} ({n_stops}정거장, {t//60}분)")
        elif mode == 'BUS':
            route = leg.get('route', '')
            t = leg.get('sectionTime', 0)
            start_name = leg.get('start', {}).get('name', '')
            end_name = leg.get('end', {}).get('name', '')
            steps.append(f"버스[{route}] {start_name}→{end_name} ({t//60}분)")
    return steps


async def query(client, origin_name, ox, oy, hosp_name, hx, hy):
    try:
        r = await client.post(API, headers={'appKey': KEY},
            json={'startX': ox, 'startY': oy, 'endX': hx, 'endY': hy, 'count': 3,
                  'searchDttm': SEARCH_TIME})
        data = r.json()
        if 'metaData' in data:
            routes = data['metaData']['plan']['itineraries']
            best = min(routes, key=lambda x: x['totalTime'])
            total_min = best['totalTime'] // 60
            walk_min = best['totalWalkTime'] // 60
            transfers = best['transferCount']
            pt = {1: '지하철', 2: '버스', 3: '버스+지하철'}.get(best.get('pathType', 0), '?')
            fare = best['fare']['regular']['totalFare']
            steps = parse_route(best)
            return {
                'origin': origin_name, 'hospital': hosp_name,
                'total_min': total_min, 'walk_min': walk_min,
                'transfers': transfers, 'type': pt, 'fare': fare,
                'route': ' → '.join(steps), 'status': 'ok'
            }
        else:
            err = data.get('error', {}).get('code', 'UNKNOWN')
            return {'origin': origin_name, 'hospital': hosp_name, 'status': f'error:{err}'}
    except Exception as e:
        return {'origin': origin_name, 'hospital': hosp_name, 'status': f'exception:{e}'}


async def main():
    # 기존 결과 로드
    existing = []
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            existing = json.load(f)

    # 이미 성공한 것들 추출
    done = set()
    for r in existing:
        if r['status'] == 'ok':
            done.add((r['origin'], r['hospital']))

    # 실행할 쿼리 목록 구성 (실패한 것만)
    todo = []
    ox, oy = origins['집(대림현대3차)']
    for name, (hx, hy) in hospitals.items():
        if ('집(대림현대3차)', name) not in done:
            todo.append(('집(대림현대3차)', ox, oy, name, hx, hy))

    ox, oy = origins['판교역']
    for name in pangyo_hospitals:
        if ('판교역', name) not in done:
            hx, hy = hospitals[name]
            todo.append(('판교역', ox, oy, name, hx, hy))

    if not todo:
        print("모든 병원 조사 완료! 추가 조회 불필요.")
        return

    print(f"미완료 {len(todo)}건 조회 시작 (2초 간격)...\n")

    new_results = []
    async with httpx.AsyncClient(timeout=30) as client:
        for origin, oxx, oyy, name, hx, hy in todo:
            r = await query(client, origin, oxx, oyy, name, hx, hy)
            new_results.append(r)
            if r['status'] == 'ok':
                print(f"  OK: {origin} → {name} - {r['total_min']}분 | {r['route']}")
            else:
                print(f"  FAIL: {origin} → {name} - {r['status']}")
                if 'QUOTA' in r['status']:
                    print("  ⚠️ 쿼터 초과! 나중에 다시 실행해주세요.")
                    break
            await asyncio.sleep(2)

    # 기존 결과에 새 결과 병합 (실패→성공으로 대체)
    ok_existing = [r for r in existing if r['status'] == 'ok']
    ok_new = [r for r in new_results if r['status'] == 'ok']
    fail_new = [r for r in new_results if r['status'] != 'ok']

    # 기존 ok + 새 ok + 아직 실패한 것들
    merged_done = set()
    merged = []
    for r in ok_existing + ok_new:
        key = (r['origin'], r['hospital'])
        if key not in merged_done:
            merged.append(r)
            merged_done.add(key)
    for r in fail_new:
        key = (r['origin'], r['hospital'])
        if key not in merged_done:
            merged.append(r)
            merged_done.add(key)

    with open(RESULTS_PATH, 'w') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    ok_count = len([r for r in merged if r['status'] == 'ok'])
    fail_count = len([r for r in merged if r['status'] != 'ok'])
    print(f"\n=== 저장 완료: {RESULTS_PATH} ===")
    print(f"성공: {ok_count}건, 실패: {fail_count}건")

    # 전체 요약 출력
    print(f"\n{'출발':>5} → {'병원':<20} | {'시간':>4} | 경로")
    print('-' * 100)
    for r in sorted([x for x in merged if x['status'] == 'ok'], key=lambda x: (x['origin'], x['total_min'])):
        print(f"{r['origin']:>5} → {r['hospital']:<20} | {r['total_min']:>3}분 | {r['route']}")


asyncio.run(main())
