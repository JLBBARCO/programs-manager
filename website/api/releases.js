import { getReleases } from './_releases.js';

export default async function handler(request, response) {
  try {
    const data = await getReleases();
    response.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=3600');
    response.setHeader('Access-Control-Allow-Origin', '*');
    return response.status(200).json(data);
  } catch (error) {
    console.error('[releases]', error);
    return response.status(502).json({ error: 'Unable to load releases', releases: [] });
  }
}
