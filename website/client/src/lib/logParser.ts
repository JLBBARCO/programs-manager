export type LogLevel = "INFO" | "DEBUG" | "SUCCESS" | "WARNING" | "ERROR";

export type LogBucket = "info" | "debug" | "warning" | "error";

export type LogSection = "current" | "history";

const LINE_RE =
  /^\[(\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2})\] \[(\w+)\](?: \[pid:(\d+)\])?(?: \[thread:([^\]]+)\])?(?: \[caller:([^\]]+)\])? ?(.*)$/;
const SYSTEM_START_RE = /^Start System$/i;
const PROGRAM_START_RE = /^Start\s+(.+)$/i;
const OPERATING_SYSTEM_RE = /^Operating System:\s*(.+)$/i;
const SYSTEM_END_RE = /^End system$/i;

function parseBrDate(raw: string) {
  const [datePart, timePart] = raw.split(" ");
  const [day, month, year] = datePart.split("/").map(Number);
  const [hour, minute, second] = timePart.split(":").map(Number);

  return new Date(year, month - 1, day, hour, minute, second);
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

export function parseLogLine(raw: string): ParsedLogLine | null {
  const line = raw.trim();
  if (!line) {
    return null;
  }

  const match = line.match(LINE_RE);
  if (!match) {
    return null;
  }

  const [, dateRaw, level, pid, thread, caller, message] = match;

  return {
    timestamp: parseBrDate(dateRaw),
    timestampRaw: dateRaw,
    level: level.toUpperCase() as LogLevel,
    pid: pid ?? null,
    thread: thread ?? null,
    caller: caller ?? null,
    message: message.trim(),
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
