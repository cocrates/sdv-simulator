"""SDV 시뮬레이터 커스텀 컴포넌트 예제.

YAML만으로는 발생할 수 없는 ``log`` 이벤트와 라이브러리 API를 보여줍니다:

- ``load(arch, scenario, components={...})`` — 컴포넌트 클래스 등록
- ``Component.on_message`` / ``TaskContext.send`` / ``TaskContext.log``
- 클래스 키 매칭: 컴포넌트 정의의 ``class`` 필드, 없으면 컴포넌트 name
  (예: ``samples/vehicle/architecture.yaml``의 ``door_act``는
  ``class: DoorActuator``로 정의되어 있어 등록 키는 ``DoorActuator``)

기본 샘플(``samples/basic/``)과 함께 실행하는 데모:
문이 열리면(door_cmd 수신) 상태를 로그로 남기고 door_state를 다시 전송합니다.

실행::

    python samples/vehicle/components.py

기대: door_cmd 수신마다 ``log`` 이벤트 발생, exit 0 (assertion 모두 pass)
"""

from __future__ import annotations

from sdv_sim.core.component import Component, Message, TaskContext
from sdv_sim.core.engine import load

# samples/basic/architecture.yaml 의 door_ecu.door_act (class 미지정 → name 매칭)
class door_act(Component):
    """도어 액추에이터: door_cmd를 받으면 상태를 기록하고 door_state로 응답."""

    def on_message(self, ctx: TaskContext, message: Message) -> None:
        if message.name != "door_cmd":
            return
        ctx.log(f"door_cmd received at t={ctx.now_ms()}, data={message.data}")
        # body_can의 door_state 프레임(메시지 매핑)으로 응답 전송
        ctx.send("door_state", {"state": "open"})


def main() -> int:
    sim = load(
        "samples/basic/architecture.yaml",
        "samples/basic/scenario.yaml",
        components={"door_act": door_act},
    )
    result = sim.run()

    logs = [e for e in result.events if e.type == "log"]
    print(f"simulation: {'pass' if result.report.simulation.result == 'pass' else 'fail'}")
    print(f"log events: {len(logs)} (door_cmd rx마다 1건)")
    for e in logs[:3]:
        print(f"  t={e.t_ms} data={e.data!r}")

    passed = all(a.status == "pass" for a in result.assertions)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
