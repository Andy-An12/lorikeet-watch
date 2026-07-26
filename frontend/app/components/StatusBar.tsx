export function StatusBar({ hasErrors }: { hasErrors: boolean }) {
  return (
    <span
      className={`inline-block h-4 w-1 ${hasErrors ? "bg-fail" : "bg-pass"}`}
      aria-hidden="true"
    />
  );
}

export function StatusLabel({ hasErrors }: { hasErrors: boolean }) {
  return (
    <span
      className={`font-mono text-sm font-semibold ${
        hasErrors ? "text-fail" : "text-pass"
      }`}
    >
      {hasErrors ? "FAIL" : "PASS"}
    </span>
  );
}
