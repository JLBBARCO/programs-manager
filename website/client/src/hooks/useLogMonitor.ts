import { useCallback, useEffect, useRef, useState } from "react";
import {
  getConfiguredLogServerPort,
  getLogServerDisplay,
  LOG_MONITOR_TIMEOUT_MS,
  getLogServerUrl,
} from "@/constants/app";
import { fetchHistoricOnce } from "@/lib/logFetcher";
import {
  bucketLogLevel,
  classifyLogSection,
  extractLogLineMetadata,
  parseHistoricEntry,
  type HistoricEntry,
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

// Intervalo de polling para atualizar o historic.json após a conexão inicial terminar (em ms)
const LOG_POLL_INTERVAL_MS = 5000; // 5 segundos

/**
 * Hook customizado para monitorar o histórico de execução (historic.json)
 *
 * Responsabilidades:
 * - Buscar o historic.json exposto pelo core-app via servidor local
 * - Fazer parse dos registros
 * - Classificar e bucketizar os logs
 * - Gerenciar timeout e cancelamento
 * - Fazer polling periódico após a conexão inicial terminar
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
  const processedEntriesRef = useRef<Set<string>>(new Set());
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

  // Função para processar um registro individual (usada tanto na carga inicial quanto no polling)
  const processHistoricEntry = useCallback(
    (rawEntry: HistoricEntry): boolean => {
      const parsed = parseHistoricEntry(rawEntry);
      if (!parsed) {
        return false;
      }

      const entryKey = `${parsed.timestampRaw}|${parsed.level}|${parsed.message}`;
      if (processedEntriesRef.current.has(entryKey)) {
        return false; // Já foi processado
      }

      processedEntriesRef.current.add(entryKey);

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

  const processHistoricBatch = useCallback(
    (entries: HistoricEntry[]) => {
      let systemEnded = false;

      for (const entry of entries) {
        if (processHistoricEntry(entry)) {
          systemEnded = true;
        }
      }

      return systemEnded;
    },
    [processHistoricEntry]
  );

  // Função para fazer polling periódico
  const startPolling = useCallback(() => {
    if (isPollingRef.current) return;
    isPollingRef.current = true;

    const poll = async () => {
      try {
        const entries = await fetchHistoricOnce(
          logServerUrl,
          controllerRef.current?.signal
        );

        const systemEnded = processHistoricBatch(entries);

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
  }, [processHistoricBatch]);

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
        const initialEntries = await fetchHistoricOnce(
          logServerUrl,
          controller.signal
        );

        setIsLoading(false);

        if (processHistoricBatch(initialEntries)) {
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
              : new Error("Erro desconhecido ao monitorar o histórico")
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
  }, [processHistoricEntry, startPolling]);

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
