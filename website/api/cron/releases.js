import { refreshReleases } from '../_releases.js';

export default async function handler(request, response) {
  const configuredSecret = process.env.CRON_SECRET;
  const authorization = request.headers.authorization || '';
  const isVercelCron = configuredSecret && authorization === `Bearer ${configuredSecret}`;
  const isLocalDevelopment = process.env.NODE_ENV !== 'production' && !configuredSecret;

  if (!isVercelCron && !isLocalDevelopment) return response.status(401).json({ error: 'Unauthorized' });

  try {
    const data = await refreshReleases();
    return response.status(200).json({ ok: true, updatedAt: data.updatedAt, count: data.releases.length });
  } catch (error) {
    console.error('[cron/releases]', error);
    return response.status(502).json({ ok: false, error: 'Unable to refresh releases' });
  }
}
