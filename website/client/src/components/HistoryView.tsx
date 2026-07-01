import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { LOG_LEVEL_STYLES, MESSAGES, TIMESTAMP_COLOR } from "@/constants/app";
import type { ProgramHistoryGroup } from "@/hooks/useLogMonitor";

interface LogEntry {
  timestamp: string;
  level: "INFO" | "DEBUG" | "SUCCESS" | "WARNING" | "ERROR";
  message: string;
}

interface HistoryViewProps {
  historyLogs: ProgramHistoryGroup[];
}

export function HistoryView({ historyLogs }: HistoryViewProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (historyLogs.length === 0) {
    return null;
  }

  function getLevelStyles(level: LogEntry["level"]) {
    return LOG_LEVEL_STYLES[level] || LOG_LEVEL_STYLES.INFO;
  }

  return (
    <div className="mt-8 border-t border-border pt-8">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 bg-muted/50 hover:bg-muted rounded-lg transition-all duration-200"
      >
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-display font-bold text-foreground">
            {MESSAGES.HISTORY_TITLE}
          </h2>
          <span className="text-sm text-muted-foreground">
            ({historyLogs.length} programas)
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-muted-foreground" />
        ) : (
          <ChevronDown className="w-5 h-5 text-muted-foreground" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-4 grid gap-4">
          {historyLogs.map(group => (
            <article
              key={`${group.programName}-${group.systemName ?? "unknown"}`}
              className="border border-border rounded-lg bg-card shadow-sm overflow-hidden"
            >
              <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border/50 px-4 py-3">
                <div>
                  <h3 className="text-base font-display font-semibold text-foreground">
                    {group.programName}
                  </h3>
                  {group.systemName ? (
                    <p className="text-sm text-muted-foreground">
                      Sistema operacional: {group.systemName}
                    </p>
                  ) : null}
                </div>

                <span className="rounded-full bg-muted px-3 py-1 text-xs font-semibold text-foreground">
                  {group.entries.length} registros
                </span>
              </div>

              <div className="max-h-96 overflow-auto">
                <div className="divide-y divide-border/50 min-w-max">
                  {group.entries.map((log, index) => {
                    const styles = getLevelStyles(log.level);
                    return (
                      <div
                        key={`${group.programName}-${log.timestamp}-${index}`}
                        className={`flex items-start gap-3 border-l-4 ${styles.border} px-3 py-2 transition-all duration-200 hover:bg-muted/30`}
                      >
                        <div className="min-w-max">
                          <div className="flex items-center gap-2 whitespace-nowrap text-xs">
                            <time
                              style={{ color: TIMESTAMP_COLOR }}
                              className="font-mono"
                            >
                              {log.timestamp}
                            </time>
                            <span className="text-foreground/50">|</span>
                            <span className={`font-mono ${styles.badge}`}>
                              [{log.level}]
                            </span>
                            <span className="text-foreground">
                              {log.message}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
