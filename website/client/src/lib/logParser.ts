export type LogLevel = "INFO" | "DEBUG" | "SUCCESS" | "WARNING" | "ERROR";

export type LogBucket = "info" | "debug" | "warning" | "error";

export type LogSection = "current" | "history";

const PROGRAM_START_RE = /^Start\s+(.+)$/i;
const OPERATING_SYSTEM_RE = /^Operating System:\s*(.+)$/i;
const SYSTEM_START_RE = /^Start System$/i;
const SYSTEM_END_RE = /^End system$/i;

function parseBrDate(raw: string) {
  const [datePart, timePart] = raw.split(" ");
  const [day, month, year] = datePart.split("/").map(Number);
  const [hour, minute, second] = timePart.split(":").map(Number);

  return new Date(year, month - 1, day, hour, minute, second);
}

/**
 * Formato de cada registro gravado pelo core-app em `historic.json`.
 * Mantém a mesma tipagem de níveis usada anteriormente em `log.log`
 * (INFO, WARNING, ERROR), com timestamp no formato dd/mm/yyyy HH:MM:SS.
 */
export interface HistoricEntry {
  timestamp: string;
  level: string;
  message: string;
}

export interface ParsedLogLine {
  timestamp: Date;
  timestampRaw: string;
  level: LogLevel;
  pid: string | null;
  thread: string | null;
  caller: string | null;
  message: string;
}

export interface LogLineMetadata {
  isSystemStart: boolean;
  isSystemEnd: boolean;
  programName: string | null;
  systemName: string | null;
}

/**
 * Converte um registro bruto de `historic.json` (JSON) em um `ParsedLogLine`
 * normalizado, usado pelo restante do pipeline de exibição.
 */
export function parseHistoricEntry(raw: unknown): ParsedLogLine | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }

  const entry = raw as Partial<HistoricEntry>;

  const timestampRaw =
    typeof entry.timestamp === "string" ? entry.timestamp.trim() : "";
  const level =
    typeof entry.level === "string" ? entry.level.trim().toUpperCase() : "";
  const message =
    typeof entry.message === "string" ? entry.message.trim() : "";

  if (!timestampRaw || !level || !message) {
    return null;
  }

  return {
    timestamp: parseBrDate(timestampRaw),
    timestampRaw,
    level: level as LogLevel,
    pid: null,
    thread: null,
    caller: null,
    message,
  };
}

export function extractLogLineMetadata(message: string): LogLineMetadata {
  const normalizedMessage = message.trim();
  const programMatch = normalizedMessage.match(PROGRAM_START_RE);
  const systemMatch = normalizedMessage.match(OPERATING_SYSTEM_RE);

  return {
    isSystemStart: SYSTEM_START_RE.test(normalizedMessage),
    isSystemEnd: SYSTEM_END_RE.test(normalizedMessage),
    programName: programMatch?.[1]?.trim() ?? null,
    systemName: systemMatch?.[1]?.trim() ?? null,
  };
}

export function classifyLogSection(
  lineTimestamp: Date,
  siteLoadedAt: Date
): LogSection {
  const diffMs = siteLoadedAt.getTime() - lineTimestamp.getTime();
  return diffMs <= 60_000 ? "current" : "history";
}

export function bucketLogLevel(level: LogLevel): LogBucket {
  if (level === "DEBUG") {
    return "debug";
  }

  if (level === "WARNING") {
    return "warning";
  }

  if (level === "ERROR") {
    return "error";
  }

  return "info";
}
