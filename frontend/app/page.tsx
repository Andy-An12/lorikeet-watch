"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { useSession } from "../lib/useSession";
import { Nav } from "./components/Nav";
import { StatusBar, StatusLabel } from "./components/StatusBar";
import type { DashboardRun } from "../lib/types";

export default function DashboardPage() {
  const { username, checked } = useSession();
  const [runs, setRuns] = useState<DashboardRun[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!checked) return;
    apiFetch("/api/dashboard")
      .then((res) => res.json())
      .then((data) => setRuns(data.runs))
      .catch(() => setError("Could not load data. Try refreshing the page."));
  }, [checked]);

  if (!checked) return null;

  return (
    <main>
      <Nav username={username} />
      <div className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="font-display mb-6 text-lg font-semibold text-bone">
          Hosts
        </h1>
        {error && <p className="font-mono text-sm text-fail">{error}</p>}
        {!error && runs === null && (
          <p className="font-mono text-sm text-bone/50">Loading…</p>
        )}
        {runs !== null && runs.length === 0 && (
          <p className="font-mono text-sm text-bone/50">
            No runs yet. Once lorikeet&apos;s cron posts a result, it shows up
            here.
          </p>
        )}
        <ul className="divide-y divide-panel border-t border-panel">
          {runs?.map((run) => (
            <li key={run.hostname}>
              <Link
                href={`/host?name=${encodeURIComponent(run.hostname)}`}
                className="flex items-center gap-4 py-3 hover:bg-panel/40"
              >
                <StatusBar hasErrors={run.has_errors} />
                <span className="flex-1 font-mono text-sm text-bone">
                  {run.hostname}
                </span>
                <StatusLabel hasErrors={run.has_errors} />
                <span className="w-40 text-right font-mono text-xs text-bone/50">
                  {run.created_at}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
