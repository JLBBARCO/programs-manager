import { getLogServerDisplay, getLogServerPortFromUrl } from "@/constants/app";
import type { HistoricEntry } from "@/lib/logParser";

/**
 * Busca o conteúdo completo de `historic.json`, servido pelo core-app na
 * porta local, e retorna a lista de registros já desserializada.
 * Útil tanto para a carga inicial quanto para o polling periódico.
 */
export async function fetchHistoricOnce(
  url: string,
  signal?: AbortSignal
): Promise<HistoricEntry[]> {
  const portDisplay = getLogServerDisplay(getLogServerPortFromUrl(url));
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
    signal,
  });

  if (!res.ok) {
    throw new Error(
      `Servidor na porta ${portDisplay.port} respondeu ${res.status}`
    );
  }

  const text = await res.text();
  const trimmed = text.trim();
  if (!trimmed) {
    return [];
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(trimmed);
  } catch {
    throw new Error(
      "Não foi possível interpretar historic.json - conteúdo inválido."
    );
  }

  if (Array.isArray(parsed)) {
    return parsed as HistoricEntry[];
  }

  if (parsed && typeof parsed === "object" && Array.isArray((parsed as { data?: unknown }).data)) {
    return (parsed as { data: HistoricEntry[] }).data;
  }

  return [];
}
