"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { apiFetch } from "../../lib/api";
import { useSession } from "../../lib/useSession";
import { Nav } from "../components/Nav";
import { StatusBar, StatusLabel } from "../components/StatusBar";
import type { HostRun } from "../../lib/types";

function HostHistory() {
  const { username, checked } = useSession();
  const searchParams = useSearchParams();
  const hostname = searchParams.get("name") ?? "";
  const [runs, setRuns] = useState<HostRun[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!checked || !hostname) return;
    apiFetch(`/api/hosts/${encodeURIComponent(hostname)}`)
      .then((res) => res.json())
      .then((data) => setRuns(data.runs))
      .catch(() => setError("Could not load data. Try refreshing the page."));
  }, [checked, hostname]);

  if (!checked) return null;

  return (
    <main>
      <Nav username={username} />
      <div className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="font-display mb-6 text-lg font-semibold text-bone">
          {hostname || "Unknown host"}
        </h1>
        {error && <p className="font-mono text-sm text-fail">{error}</p>}
        {!error && runs === null && (
          <p className="font-mono text-sm text-bone/50">Loading…</p>
        )}
        <div className="space-y-6">
          {runs?.map((run) => (
            <details key={run.id} className="border border-panel">
              <summary className="flex cursor-pointer items-center gap-4 bg-panel/40 px-4 py-3">
                <StatusBar hasErrors={run.has_errors} />
                <StatusLabel hasErrors={run.has_errors} />
                <span className="font-mono text-xs text-bone/50">
                  {run.created_at}
                </span>
              </summary>
              <ul className="divide-y divide-panel">
                {run.steps.map((step) => (
                  <li key={step.name} className="flex gap-4 px-4 py-2 pl-8">
                    <StatusBar hasErrors={!step.pass} />
                    <span className="flex-1 font-mono text-sm text-bone">
                      {step.name}
                    </span>
                    <span className="font-mono text-xs text-bone/50">
                      {step.error || step.output}
                    </span>
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </div>
      </div>
    </main>
  );
}

export default function HostPage() {
  return (
    <Suspense fallback={null}>
      <HostHistory />
    </Suspense>
  );
}
