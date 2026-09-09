import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function formatDuration(ms: number | null): string {
  if (ms === null || ms === undefined) return "-";
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(2)} s`;
}

export const CATEGORY_LABELS: Record<string, string> = {
  nic: "NIC Numbers",
  card: "Payment Card Numbers",
  bank_account: "Bank Account Numbers",
  iban: "IBAN Numbers",
  passport: "Passport Numbers",
  email: "Email Addresses",
  telephone: "Telephone Numbers",
  credential: "Credentials",
  api_key: "API Keys & Secrets",
  salary: "Salary Information",
  employee_id: "Employee IDs",
  classification_marker: "Classification Markers",
};

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] || category;
}

export function eventLabel(type: string): string {
  return type
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
