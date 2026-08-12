"""sdv-sim v2 web dashboard server (ASR-014/015/019).

The server embeds the v1 core in-process, exposes the REST API consumed by the
React dashboard, and serves the packaged static assets. It never touches the
filesystem for user files (F-11): the browser sends YAML/JSON content as
strings, and files live on the browser side.
"""

from sdv_sim.server.app import create_app

__all__ = ["create_app"]
