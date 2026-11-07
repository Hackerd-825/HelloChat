# HelloChat (Vercel)

> Projet original créé par [devffin](https://github.com/devffin) et repris et adapté pour fonctionner avec Vercel.

Vercel est serverless : pas de WebSocket ni de mémoire partagée. Le chat utilise donc
du polling HTTP (toutes les 2 s) et Redis pour stocker les messages.

## Déploiement
1. Pousse le projet sur GitHub, puis importe-le dans Vercel (ou `vercel` en CLI).
2. Dans le projet Vercel : **Storage → Marketplace → Upstash Redis** → connecte-le au projet
   (ça ajoute `KV_REST_API_URL` / `KV_REST_API_TOKEN` ou `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN`).
3. Redéploie.

Sans Redis, l'app marche en local (mémoire), mais pas de façon fiable sur Vercel.

## Local
```bash
pip install -r requirements.txt
python app.py
