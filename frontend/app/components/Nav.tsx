"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "../../lib/api";

export function Nav({ username }: { username: string | null }) {
  const router = useRouter();

  async function logout() {
    await apiFetch("/api/logout", { method: "POST" });
    router.replace("/login");
  }

  return (
    <nav className="flex items-center justify-between border-b border-panel px-6 py-4">
      <Link
        href="/"
        className="font-display text-lg font-semibold tracking-tight text-bone"
      >
        lorikeet-watch
      </Link>
      <div className="flex items-center gap-4 font-mono text-sm text-bone/70">
        {username && <span>{username}</span>}
        <Link href="/settings" className="hover:text-accent">
          Settings
        </Link>
        <button onClick={logout} className="hover:text-fail">
          Log out
        </button>
      </div>
    </nav>
  );
}
