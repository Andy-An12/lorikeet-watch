"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";
import { useSession } from "../../lib/useSession";
import { Nav } from "../components/Nav";
import type { SettingsData } from "../../lib/types";

const EMPTY_FORM = {
  email_enabled: false,
  email_smtp_host: "",
  email_smtp_port: "",
  email_smtp_user: "",
  email_smtp_pass: "",
  email_from: "",
  email_to: "",
  sms_enabled: false,
  twilio_account_sid: "",
  twilio_auth_token: "",
  twilio_from_number: "",
  twilio_to_number: "",
  username: "",
  new_password: "",
};

export default function SettingsPage() {
  const { username, checked } = useSession();
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!checked) return;
    apiFetch("/api/settings")
      .then((res) => res.json())
      .then((data: SettingsData) => {
        setSettings(data);
        setForm((f) => ({
          ...f,
          email_enabled: data.email_enabled === "1",
          email_smtp_host: data.email_smtp_host,
          email_smtp_port: data.email_smtp_port,
          email_smtp_user: data.email_smtp_user,
          email_from: data.email_from,
          email_to: data.email_to,
          sms_enabled: data.sms_enabled === "1",
          twilio_account_sid: data.twilio_account_sid,
          twilio_from_number: data.twilio_from_number,
          twilio_to_number: data.twilio_to_number,
          username: username ?? "admin",
        }));
      })
      .catch(() => setError("Could not load data. Try refreshing the page."));
  }, [checked, username]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setMessage(null);
    try {
      const res = await apiFetch("/api/settings", {
        method: "POST",
        body: JSON.stringify(form),
      });
      if (res.ok) {
        setMessage("Settings saved.");
        setForm((f) => ({
          ...f,
          email_smtp_pass: "",
          twilio_auth_token: "",
          new_password: "",
        }));
      } else {
        setMessage("Could not save settings.");
      }
    } catch {
      setMessage("Could not reach the server. Check your connection and try again.");
    }
  }

  async function regenerateToken() {
    setMessage(null);
    try {
      const res = await apiFetch("/api/settings/regenerate-token", {
        method: "POST",
      });
      if (res.ok) {
        const refreshed = await apiFetch("/api/settings").then((r) => r.json());
        setSettings(refreshed);
        setMessage("Ingest token regenerated.");
      } else {
        setMessage("Could not regenerate the token.");
      }
    } catch {
      setMessage("Could not reach the server. Check your connection and try again.");
    }
  }

  if (!checked) return null;

  return (
    <main>
      <Nav username={username} />
      <div className="mx-auto max-w-2xl px-6 py-8">
        <h1 className="font-display mb-6 text-lg font-semibold text-bone">
          Settings
        </h1>

        <section className="mb-8 border border-panel p-6">
          <h2 className="font-display mb-3 text-sm font-semibold text-accent">
            Ingest token
          </h2>
          <p className="mb-3 break-all font-mono text-xs text-bone/50">
            Use in cron: lorikeet --webhook
            &quot;https://YOUR_HOST/internal/results?token=
            {settings?.ingest_token ?? "…"}&quot; config.yml
          </p>
          <button
            type="button"
            onClick={regenerateToken}
            className="border border-accent px-3 py-1.5 font-mono text-xs text-accent hover:bg-accent/10"
          >
            Regenerate token
          </button>
        </section>

        {error && <p className="mb-4 font-mono text-sm text-fail">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-8">
          <section className="border border-panel p-6">
            <label className="mb-4 flex items-center gap-3 font-mono text-sm text-bone">
              <input
                type="checkbox"
                checked={form.email_enabled}
                onChange={(e) =>
                  setForm((f) => ({ ...f, email_enabled: e.target.checked }))
                }
                className="h-4 w-4 accent-pass"
              />
              Email alerts
            </label>
            <div className="grid grid-cols-2 gap-4">
              <Field
                label="SMTP host"
                value={form.email_smtp_host}
                onChange={(v) => setForm((f) => ({ ...f, email_smtp_host: v }))}
              />
              <Field
                label="SMTP port"
                value={form.email_smtp_port}
                onChange={(v) => setForm((f) => ({ ...f, email_smtp_port: v }))}
              />
              <Field
                label="SMTP user"
                value={form.email_smtp_user}
                onChange={(v) => setForm((f) => ({ ...f, email_smtp_user: v }))}
              />
              <Field
                label="SMTP password"
                type="password"
                value={form.email_smtp_pass}
                onChange={(v) => setForm((f) => ({ ...f, email_smtp_pass: v }))}
                hint="Leave blank to keep the current value."
              />
              <Field
                label="From address"
                value={form.email_from}
                onChange={(v) => setForm((f) => ({ ...f, email_from: v }))}
              />
              <Field
                label="Admin address (to)"
                value={form.email_to}
                onChange={(v) => setForm((f) => ({ ...f, email_to: v }))}
              />
            </div>
          </section>

          <section className="border border-panel p-6">
            <label className="mb-4 flex items-center gap-3 font-mono text-sm text-bone">
              <input
                type="checkbox"
                checked={form.sms_enabled}
                onChange={(e) =>
                  setForm((f) => ({ ...f, sms_enabled: e.target.checked }))
                }
                className="h-4 w-4 accent-pass"
              />
              SMS alerts (Twilio)
            </label>
            <div className="grid grid-cols-2 gap-4">
              <Field
                label="Account SID"
                value={form.twilio_account_sid}
                onChange={(v) =>
                  setForm((f) => ({ ...f, twilio_account_sid: v }))
                }
              />
              <Field
                label="Auth token"
                type="password"
                value={form.twilio_auth_token}
                onChange={(v) =>
                  setForm((f) => ({ ...f, twilio_auth_token: v }))
                }
                hint="Leave blank to keep the current value."
              />
              <Field
                label="From number"
                value={form.twilio_from_number}
                onChange={(v) =>
                  setForm((f) => ({ ...f, twilio_from_number: v }))
                }
              />
              <Field
                label="Admin number (to)"
                value={form.twilio_to_number}
                onChange={(v) =>
                  setForm((f) => ({ ...f, twilio_to_number: v }))
                }
              />
            </div>
          </section>

          <section className="border border-panel p-6">
            <h2 className="font-display mb-4 text-sm font-semibold text-accent">
              Admin login
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <Field
                label="Username"
                value={form.username}
                onChange={(v) => setForm((f) => ({ ...f, username: v }))}
              />
              <Field
                label="New password"
                type="password"
                value={form.new_password}
                onChange={(v) => setForm((f) => ({ ...f, new_password: v }))}
                hint="Leave blank to keep the current password."
              />
            </div>
          </section>

          {message && (
            <p className="font-mono text-sm text-accent">{message}</p>
          )}

          <button
            type="submit"
            className="bg-accent px-4 py-2 font-mono text-sm font-semibold text-ink hover:bg-accent/80"
          >
            Save changes
          </button>
        </form>
      </div>
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  hint,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  hint?: string;
}) {
  return (
    <label className="block font-mono text-xs text-bone/70">
      {label}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 block w-full border border-panel bg-ink px-2 py-1.5 font-mono text-sm text-bone focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
      />
      {hint && <span className="mt-1 block text-bone/40">{hint}</span>}
    </label>
  );
}
