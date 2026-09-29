const body = document.getElementById("releases-body");
const status = document.getElementById("releases-status");

const esc = (value) =>
  String(value ?? "").replace(
    /[&<>'"]/g,
    (char) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#39;",
        '"': "&quot;",
      })[char],
  );

const formatDate = (value) =>
  value
    ? new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(
        new Date(value),
      )
    : "—";

async function loadReleases() {
  try {
    const response = await fetch("/api/releases", {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) throw new Error("Servidor indisponível");

    const payload = await response.json();
    const releases = Array.isArray(payload.releases) ? payload.releases : [];

    if (!releases.length) {
      body.innerHTML =
        '<tr><td colspan="5" class="empty">Nenhuma release publicada foi encontrada.</td></tr>';
      return;
    }

    body.innerHTML = releases
      .map(
        (release) =>
          `<tr><td><a class="release-name" href="${esc(release.url)}" target="_blank" rel="noreferrer">${esc(release.name || release.tagName)} ↗</a></td><td><span class="version">${esc(release.version)}</span></td><td>${esc(formatDate(release.publishedAt))}</td><td><span class="badge ${release.prerelease ? "beta" : ""}">${release.prerelease ? "beta" : "stable"}</span></td><td><a class="download" href="${esc(release.url)}" target="_blank" rel="noreferrer">Ver assets ↗</a></td></tr>`,
      )
      .join("");
    status.textContent = `Sincronizado em ${formatDate(payload.updatedAt)} · ${releases.length} releases disponíveis`;
  } catch (error) {
    body.innerHTML =
      '<tr><td colspan="5" class="error">Não foi possível carregar as versões. Tente novamente mais tarde.</td></tr>';
    status.textContent = "Falha ao consultar o servidor";
  }
}

loadReleases();
