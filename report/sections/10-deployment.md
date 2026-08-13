# 10. 배포

배포는 **하나의 Python 패키지**가 **하나의 서버 프로세스**로 실행되는 구조이다.
프런트엔드 정적 자산이 패키지에 포함되어 별도 정적 서버가 필요 없다.

## 10.1 패키징

- 빌드 백엔드는 **hatchling**이며, `uv build`(또는 `python -m build`)로 wheel을 만든다.
- 프런트엔드 빌드 결과(`frontend/dist/`)는 `sdv_sim/server/static/`으로 복사되고,
  wheel 빌드 시 **강제 포함**(force-include)된다 — 정적 자산이 누락되면 빌드가 실패하도록
  구성되어, "서버는 있으나 UI가 없는" 패키지가 나오지 않는다.
- 정적 자산이 없는 상태로 `serve`를 실행하면 `/` 요청에
  `{"message": "static not built"}`를 반환해 상태를 명확히 알린다 (11.2절의 check-files 검증과 연동).
- 패키지 이름은 `sdv-sim`, 진입점은 `sdv-sim = sdv_sim.cli.main:main`이다.

## 10.2 serve 실행 모델

`sdv-sim serve`는 **단일 프로세스**로 전체 서비스를 제공한다.

| 항목 | 동작 |
|------|------|
| 프로세스 | FastAPI 앱 + 정적 자산을 하나의 uvicorn 프로세스로 실행 |
| 포트 | `--port` (기본 `8888`) — 바인딩 전에 **점유 여부 확인**, 사용 중이면 종료 코드 2로 즉시 실패 |
| 호스트 | `--host` (기본 `127.0.0.1`). `0.0.0.0` 지정 시 외부 노출 경고 출력 (9.3절 ②) |
| 개발 모드 | `--dev`: 정적 마운트 대신 **Vite 개발 서버**가 `/api`를 이 서버로 프록시 (6.1절) |
| 로그 | uvicorn 로그를 **stdout**으로 출력 (spec 요구) — systemd journal에서 확인 |

## 10.3 systemd 서비스

`deploy/`에는 systemd **user unit**과 설치 스크립트가 포함되어 있다.

```ini
[Service]
Type=simple
WorkingDirectory=%h/work/sdv-simulator
Environment=SDV_SIM_LANG=ko
ExecStart=%h/work/sdv-simulator/.venv/bin/sdv-sim serve --port 8888 --host 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

- **user unit**: 시스템 서비스가 아니라 로그인 사용자 단위로 동작한다 (`WantedBy=default.target`).
  부팅 시 자동 시작이 필요하면 `loginctl enable-linger`를 사용하며 `install.sh`가 자동 처리한다.
- `Restart=always`로 프로세스가 죽으면 5초 후 재시작한다.
- `--host 0.0.0.0`은 **인증 없이 네트워크에 대시보드를 노출**하므로, 방화벽에서 소스 IP를
  제한하는 것을 전제로 한다 (spec 제약).
- `install.sh` / `uninstall.sh`가 서비스 설치·제거를 수행한다.
- **실제 설치는 보류** 상태이다 — 개발 머신에서는 개발 모드로만 검증되었으며,
  시스템 서비스로의 설치 여부는 별도 결정으로 남겨 두었다 (부록 C.4).
