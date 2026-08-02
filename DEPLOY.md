# Deploying TruthLens

**Source repo:** [github.com/swapnilswami332/fake-news-detector](https://github.com/swapnilswami332/fake-news-detector)

TruthLens is two parts in production:

1. **API** — FastAPI + ML model (Docker recommended)
2. **UI** — static React build (Vercel, Netlify, or Cloudflare Pages)

Local dev uses Vite’s proxy. Production needs `VITE_API_URL` on the frontend and `CORS_ORIGINS` on the API.

---

## Recommended layout (portfolio / demo)

| Part | Service | Why |
|------|---------|-----|
| API | [Render](https://render.com) or [Railway](https://railway.app) Docker web service | Fits Python + heavy deps |
| UI | [Vercel](https://vercel.com) or [Netlify](https://netlify.com) | Free static hosting |

**Ollama does not run on these hosts.** Use search + optional hosted LLM later, or set `ENABLE_FACT_CHECKING=false` for ML-only responses (faster, smaller cold starts).

---

## Step 1 — Deploy the API (Docker)

### Render

1. Ensure code is on [swapnilswami332/fake-news-detector](https://github.com/swapnilswami332/fake-news-detector).
2. Render → **New** → **Web Service** → connect that repository.
3. **Environment:** Docker (uses root `Dockerfile`).
4. **Instance type:** at least **Starter** (512MB+). Free tier may OOM or time out on first load because of PyTorch / sentence-transformers.
5. **Environment variables:**

   | Key | Value |
   |-----|--------|
   | `ENABLE_FACT_CHECKING` | `true` (DuckDuckGo + embeddings; no Ollama) or `false` (ML only) |
   | `CORS_ORIGINS` | Your frontend URL, e.g. `https://truthlens.vercel.app` |

6. Deploy. Note the URL, e.g. `https://truthlens-api.onrender.com`.
7. Test: `GET https://YOUR-API/health` → `{"status":"ok"}`.

### Railway

1. **New Project** → **Deploy from GitHub** → select repo.
2. Railway detects the `Dockerfile`. Set the same env vars as above.
3. Generate a public domain in **Settings → Networking**.

### Build note

The Dockerfile runs `python -m backend.train` so `model.pkl` exists in the image. You do not commit `.pkl` files.

---

## Step 2 — Deploy the frontend

### Vercel

1. **Add New Project** → import the GitHub repo.
2. **Root Directory:** `frontend`
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`
5. **Environment variable:**

   | Key | Value |
   |-----|--------|
   | `VITE_API_URL` | `https://YOUR-API.onrender.com` (no trailing slash) |

6. Deploy. Open the Vercel URL and run **Analyze**.

### Netlify

1. **Add site** → import repo.
2. Base directory: `frontend`
3. Build: `npm run build`, publish: `frontend/dist`
4. Set `VITE_API_URL` under **Site settings → Environment variables**.
5. Add `frontend/public/_redirects` or `netlify.toml` for SPA routing:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

(Only needed if client-side routes are added later; this app is a single page.)

---

## Step 3 — Wire CORS

After you know the live frontend URL, update the API:

```text
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

Redeploy or restart the API service. Without this, the browser blocks requests.

---

## Environment reference

### API (`.env` or host dashboard)

```env
ENABLE_FACT_CHECKING=true
CORS_ORIGINS=https://your-frontend.vercel.app
OLLAMA_MODEL=mistral
```

Ollama only works if you run it yourself (same machine or private network). Cloud deploys should not expect `localhost:11434`.

### Frontend (`frontend/.env.production` or Vercel env)

```env
VITE_API_URL=https://your-api.onrender.com
```

---

## Single-server option (VPS)

On a small VPS (DigitalOcean, Hetzner, etc.):

```bash
git clone https://github.com/swapnilswami332/fake-news-detector.git
cd fake-news-detector
docker build -t truthlens-api .
docker run -d -p 8000:8000 \
  -e CORS_ORIGINS=https://yourdomain.com \
  -e ENABLE_FACT_CHECKING=true \
  truthlens-api

cd frontend
npm ci && VITE_API_URL=https://api.yourdomain.com npm run build
# Serve dist/ with nginx or Caddy on your domain
```

---

## Limitations when public

- **Cold starts** on free Render/Railway can take 30–60+ seconds.
- **ML + embeddings** need RAM; undersized plans crash or restart.
- **Fact-check quality** depends on DuckDuckGo and optional LLM; not suitable as a sole arbiter of truth.
- **Costs:** heavy Python images and traffic may exceed free tiers.

---

## Quick checklist

- [ ] API `/health` works in the browser or curl
- [ ] `CORS_ORIGINS` includes the exact frontend origin (scheme + host, no path)
- [ ] `VITE_API_URL` set before frontend build (rebuild after changing it)
- [ ] First `/predict` may be slow while the model loads

For local development, keep using `uvicorn backend.app:app --reload` and `npm run dev` in `frontend/` — no `VITE_API_URL` required.
