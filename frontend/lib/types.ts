export interface Step {
  name: string;
  pass: boolean;
  output: string | null;
  error: string | null;
  duration: number | null;
}

export interface DashboardRun {
  hostname: string;
  has_errors: boolean;
  created_at: string;
}

export interface HostRun {
  id: number;
  has_errors: boolean;
  created_at: string;
  steps: Step[];
}

export interface SettingsData {
  email_enabled: string;
  email_smtp_host: string;
  email_smtp_port: string;
  email_smtp_user: string;
  email_from: string;
  email_to: string;
  sms_enabled: string;
  twilio_account_sid: string;
  twilio_from_number: string;
  twilio_to_number: string;
  ingest_token: string;
}
