"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await apiFetch("/api/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      if (res.ok) {
        router.replace("/");
        return;
      }
      setError("Wrong username or password.");
    } catch {
      setError("Could not reach the server. Check your connection and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm border border-panel bg-panel/40 p-8"
      >
        <h1 className="font-display mb-6 text-xl font-semibold text-bone">
          lorikeet-watch
        </h1>
        <label className="mb-4 block font-mono text-sm text-bone/70">
          username
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoFocus
            className="mt-1 block w-full border border-panel bg-ink px-3 py-2 font-mono text-bone focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </label>
        <label className="mb-6 block font-mono text-sm text-bone/70">
          password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1 block w-full border border-panel bg-ink px-3 py-2 font-mono text-bone focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </label>
        {error && <p className="mb-4 font-mono text-sm text-fail">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-accent px-4 py-2 font-mono text-sm font-semibold text-ink transition-colors hover:bg-accent/80 disabled:opacity-50"
        >
          {submitting ? "Logging in…" : "Log in"}
        </button>
      </form>
    </main>
  );
}
