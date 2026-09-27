# Website do Programs Manager

Site estático servido pela Vercel com funções serverless em `website/api/`.

## Releases diárias

- `GET /api/releases` é chamado pelo navegador a cada carregamento e retorna releases públicas do GitHub.
- `GET /api/cron/releases` atualiza o cache diariamente (`0 6 * * *`, UTC), conforme `website/vercel.json`.
- O cache fica na variável de módulo `releasesCache`, reaproveitada enquanto a instância serverless está aquecida. Uma instância fria repopula o cache automaticamente pelo endpoint público.
- Não há gravação em disco, pois o filesystem de funções Vercel é efêmero.

## Variáveis na Vercel

| Variável            | Obrigatória     | Padrão             | Uso                                                                 |
| ------------------- | --------------- | ------------------ | ------------------------------------------------------------------- |
| `CRON_SECRET`       | Sim em produção | —                  | Autoriza o endpoint diário; a Vercel envia o header correspondente. |
| `GITHUB_OWNER`      | Não             | `JLBBARCO`         | Owner do repositório.                                               |
| `GITHUB_REPOSITORY` | Não             | `programs-manager` | Nome do repositório.                                                |

Defina o Root Directory do projeto Vercel como `website` se ele estiver conectado diretamente ao repositório. Limpe o Build Command antigo (`vite build`) nas configurações do projeto; `website/vercel.json` desativa instalação e build porque o site é estático. O workflow `.github/workflows/deploy-website.yml` já faz deploy de `website`.
