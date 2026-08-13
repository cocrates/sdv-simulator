/**
 * Hash routing (F-10 — spec/sdv-sim-v2.md Constraints): client routing uses
 * the URL hash, so the server only serves static assets and no non-API GET
 * fallback policy is needed.
 *
 * Routes: `#/editor` (default), `#/replay`, `#/report`. An unknown hash falls
 * back to `editor`.
 */

import { useEffect, useState } from "react";

export type Route = "editor" | "replay" | "report";

function parseHash(): Route {
  const raw = window.location.hash.replace(/^#\/?/, "").split("?")[0];
  if (raw === "replay" || raw === "report") return raw;
  return "editor";
}

function useHashRoute(): Route {
  const [route, setRoute] = useState<Route>(() => parseHash());

  useEffect(() => {
    const onChange = () => setRoute(parseHash());
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  return route;
}

export function navigate(route: Route): void {
  window.location.hash = `/${route}`;
}

export default useHashRoute;
