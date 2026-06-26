import { useCallback, useEffect, useRef, useState } from "react";
import {
  getConfiguredLogServerPort,
  getLogServerDisplay,
  LOG_MONITOR_TIMEOUT_MS,
  getLogServerUrl,
} from "@/constants/app";
import { fetchLogOnce } from "@/lib/logFetcher";
import {
  bucketLogLevel,
  classifyLogSection,
  extractLogLineMetadata,
  parseLogLine,
  type LogLevel,
} from "@/lib/logParser";

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
}

export interface ProgramHistoryGroup {
  programName: string;
  systemName: string | null;
  entries: LogEntry[];
}

export interface LogBuckets {
  info: LogEntry[];
  debug: LogEntry[];
  warning: LogEntry[];
  error: LogEntry[];
  history: ProgramHistoryGroup[];
}

interface UseLogMonitorResult extends LogBuckets {
  isLoading: boolean;
  monitorError: Error | null;
  programName: string | null;
  systemName: string | null;
}

// Intervalo de polling para atualizar o log após a conexão inicial terminar (em ms)
const LOG_POLL_INTERVAL_MS = 5000; // 5 segundos

/**
 * Hook customizado para monitorar logs em tempo real
 *
 * Responsabilidades:
 * - Conectar ao servidor de logs via streaming
 * - Fazer parse das linhas
 * - Classificar e bucketizar os logs
 * - Gerenciar timeout e cancelamento
 * - Fazer polling periódico após a conexão terminar
 * - Retornar estado atualizado
 *
 * @returns Estado dos logs e status do monitoramento
 */
export function useLogMonitor(): UseLogMonitorResult {
  const logServerPort = getConfiguredLogServerPort();
  const logServerUrl = getLogServerUrl(logServerPort);
  const logServerDisplay = getLogServerDisplay(logServerPort);
  const [info, setInfo] = useState<LogEntry[]>([]);
  const [debug, setDebug] = useState<LogEntry[]>([]);
  const [warning, setWarning] = useState<LogEntry[]>([]);
  const [error, setError] = useState<LogEntry[]>([]);
  const [history, setHistory] = useState<ProgramHistoryGroup[]>([]);
  const [programName, setProgramName] = useState<string | null>(null);
  const [systemName, setSystemName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [monitorError, setMonitorError] = useState<Error | null>(null);

  // Refs para lifecycle seguro
  const controllerRef = useRef<AbortController | null>(null);
  const timeoutIdRef = useRef<number | null>(null);
  const pollIntervalRef = useRef<number | null>(null);
  const loadTimeRef = useRef(new Date());
  const processedLinesRef = useRef<Set<string>>(new Set());
  const isPollingRef = useRef(false);
  const historyGroupsRef = useRef<Map<string, ProgramHistoryGroup>>(new Map());
  const currentProgramNameRef = useRef<string | null>(null);
  const currentSystemNameRef = useRef<string | null>(null);

  // Função pura para bucketizar log
  const appendLog = useCallback(
    (entry: LogEntry, section: "current" | "history") => {
      if (section === "history") {
        const groupName =
          currentProgramNameRef.current ?? "Programa desconhecido";
        const groupKey = groupName;
        const existingGroup = historyGroupsRef.current.get(groupKey);

        const nextGroup: ProgramHistoryGroup = existingGroup
          ? {
              ...existingGroup,
              systemName:
                currentSystemNameRef.current ?? existingGroup.systemName,
              entries: [...existingGroup.entries, entry],
            }
          : {
              programName: groupName,
              systemName: currentSystemNameRef.current,
              entries: [entry],
            };

        historyGroupsRef.current.set(groupKey, nextGroup);
        setHistory(Array.from(historyGroupsRef.current.values()));
      }

      const bucket = bucketLogLevel(entry.level);

      if (bucket === "debug") {
        setDebug(prev => [...prev, entry]);
        return;
      }

      if (bucket === "warning") {
        setWarning(prev => [...prev, entry]);
        return;
      }

      if (bucket === "error") {
        setError(prev => [...prev, entry]);
        return;
      }

      setInfo(prev => [...prev, entry]);
    },
    []
  );

  // Função para processar linhas (usada tanto no streaming quanto no polling)
  const processLogLine = useCallback(
    (rawLine: string): boolean => {
      const lineKey = rawLine.trim();
      if (processedLinesRef.current.has(lineKey)) {
        return false; // Já foi processada
      }

      const parsed = parseLogLine(rawLine);
      if (!parsed) {
        return false;
      }

      processedLinesRef.current.add(lineKey);

      const metadata = extractLogLineMetadata(parsed.message);

      if (metadata.isSystemStart) {
        currentProgramNameRef.current = null;
        currentSystemNameRef.current = null;
        setProgramName(null);
        setSystemName(null);
        return false;
      }

      if (metadata.programName) {
        currentProgramNameRef.current = metadata.programName;
        setProgramName(metadata.programName);
        return false;
      }

      if (metadata.systemName) {
        currentSystemNameRef.current = metadata.systemName;
        setSystemName(metadata.systemName);
        return false;
      }

      if (metadata.isSystemEnd) {
        return true;
      }

      const section = classifyLogSection(parsed.timestamp, loadTimeRef.current);
      const entry: LogEntry = {
        timestamp: parsed.timestampRaw,
        level: parsed.level,
        message: parsed.message,
      };

      appendLog(entry, section);
      return parsed.message.trim().toLowerCase() === "end system";
    },
    [appendLog]
  );

  const processLogBatch = useCallback(
    (lines: string[]) => {
      let systemEnded = false;

      for (const line of lines) {
        if (processLogLine(line)) {
          systemEnded = true;
        }
      }

      return systemEnded;
    },
    [processLogLine]
  );

  // Função para fazer polling periódico
  const startPolling = useCallback(() => {
    if (isPollingRef.current) return;
    isPollingRef.current = true;

    const poll = async () => {
      try {
        const lines = await fetchLogOnce(
          logServerUrl,
          controllerRef.current?.signal
        );

        const systemEnded = processLogBatch(lines);

        // Se encontrou "End system", parar de fazer polling
        if (systemEnded) {
          isPollingRef.current = false;
          if (pollIntervalRef.current) {
            window.clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
        }
      } catch (err) {
        // Erro ao fazer polling, mas não marca como erro fatal
        // Continua tentando
      }
    };

    pollIntervalRef.current = window.setInterval(poll, LOG_POLL_INTERVAL_MS);
  }, [processLogBatch]);

  useEffect(() => {
    const controller = new AbortController();
    controllerRef.current = controller;

    let didTimeout = false;

    const timeoutId = window.setTimeout(() => {
      didTimeout = true;
      setIsLoading(false);
      setMonitorError(new Error(logServerDisplay.timeout));
      controller.abort();
      // Iniciar polling após timeout
      startPolling();
    }, LOG_MONITOR_TIMEOUT_MS);

    timeoutIdRef.current = timeoutId;

    const monitorLogs = async () => {
      try {
        const initialLines = await fetchLogOnce(
          logServerUrl,
          controller.signal
        );

        setIsLoading(false);

        if (processLogBatch(initialLines)) {
          controller.abort();
          window.clearTimeout(timeoutId);
          return;
        }
        startPolling();
      } catch (err) {
        if (!controller.signal.aborted && !didTimeout) {
          setMonitorError(
            err instanceof Error
              ? err
              : new Error("Erro desconhecido ao monitorar logs")
          );
          setIsLoading(false);
          // Iniciar polling mesmo com erro
          startPolling();
        }
      }
    };

    void monitorLogs();

    // Cleanup
    return () => {
      window.clearTimeout(timeoutId);
      if (pollIntervalRef.current) {
        window.clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      controller.abort();
      controllerRef.current = null;
      timeoutIdRef.current = null;
      isPollingRef.current = false;
    };
  }, [processLogLine, startPolling]);

  return {
    info,
    debug,
    warning,
    error,
    history,
    isLoading,
    monitorError,
    programName,
    systemName,
  };
}
