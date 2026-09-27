const OWNER = process.env.GITHUB_OWNER || 'JLBBARCO';
const REPOSITORY = process.env.GITHUB_REPOSITORY || 'programs-manager';
const API_URL = `https://api.github.com/repos/${OWNER}/${REPOSITORY}/releases?per_page=100`;
let releasesCache = { releases: [], updatedAt: null };

function normalizeRelease(release) {
  const version = String(release.tag_name || '').replace(/^v/i, '');
  return {
    id: release.id,
    name: release.name || release.tag_name,
    tagName: release.tag_name,
    version,
    url: release.html_url,
    publishedAt: release.published_at || release.created_at,
    prerelease: Boolean(release.prerelease),
    draft: Boolean(release.draft),
    installCommands: {
      windows: `$env:AIP_VERSION = '${version}'; irm https://raw.githubusercontent.com/${OWNER}/${REPOSITORY}/main/core-app/run.ps1 | iex`,
      linux: `AIP_VERSION=${version} curl -fsSL https://raw.githubusercontent.com/${OWNER}/${REPOSITORY}/main/core-app/run.sh | AIP_VERSION=${version} bash`,
    },
  };
}

export async function refreshReleases() {
  const response = await fetch(API_URL, {
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'programs-manager-vercel',
    },
  });
  if (!response.ok) throw new Error(`GitHub releases request failed: ${response.status}`);
  const releases = (await response.json())
    .filter((release) => !release.draft)
    .map(normalizeRelease)
    .sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
  releasesCache = { releases, updatedAt: new Date().toISOString() };
  return releasesCache;
}

export async function getReleases() {
  if (!releasesCache.updatedAt) return refreshReleases();
  return releasesCache;
}
