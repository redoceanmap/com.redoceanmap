"""허브 소유 인프라의 아웃바운드 어댑터 자리 (ragwatson star_craft 파이프라인 대응).

스포크 도메인 데이터 접속은 여기 두지 않는다 — 그것은 각 스포크의
adapter/outbound/gateways/ 가 허브 포트를 구현해 주입한다(합성 루트 main.py).

여기에는 **어느 스포크의 것도 아닌, 허브 자신이 소유하는 전역 인프라** 접속만 들어온다.
예정(star_craft 파이프라인과 동일 방향):
  - graph/   : Neo4j — 온톨로지 엔티티·관계 (docker-compose에 neo4j 서비스 준비됨)
  - vector/  : pgvector(기존 Postgres 재사용) 또는 Qdrant — 전역 임베딩 검색
구현이 생기기 전까지는 비워 둔다(자리 예약).
"""
