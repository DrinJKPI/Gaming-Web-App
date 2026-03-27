# Deploying to Google Cloud Run

This application runs as a Docker container using **Gunicorn** and reads configuration from environment variables (no secrets baked into the image).

## Prerequisites

- Google Cloud project with **Cloud Run**, **Artifact Registry**, and **Cloud Build** enabled
- **MySQL** reachable from Cloud Run (e.g. Cloud SQL with connector or authorized network)
- **MongoDB Atlas** (or other) URI allowed from Cloud Run egress IPs (or VPC / Private Endpoint)

## Required environment variables

Set these in Cloud Run (or Secret Manager references):

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session signing key (use a long random string) |
| `DATABASE_URL` **or** `MYSQL_*` | SQLAlchemy DB URL **or** `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE` |
| `MONGO_URI` | MongoDB connection string |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | For Google OAuth |
| `GOOGLE_REDIRECT_URI` | Must match your Cloud Run HTTPS URL, e.g. `https://YOUR-SERVICE-XXXX.run.app/auth/google/callback` |

Optional: `WEB_CONCURRENCY`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT`.

## Local Docker

The image does not include `.env` (it is gitignored / dockerignored). Pass variables with **`--env-file`** or **`-e`**.

```bash
docker build -t gaming-web-app:local .
cp .env.example .env   # edit .env with real credentials
docker run --rm -p 8080:8080 --env-file .env gaming-web-app:local
```

Or inline:

```bash
docker run --rm -p 8080:8080 \
  -e SECRET_KEY=dev-only \
  -e DATABASE_URL="mysql+pymysql://USER:PASS@HOST:3306/DB?ssl_disabled=true" \
  -e MONGO_URI="mongodb+srv://..." \
  gaming-web-app:local
```

Open `http://localhost:8080`.

## Artifact Registry and Cloud Build

1. Create a Docker repository (once per project/region):

   ```bash
   gcloud artifacts repositories create gaming-web-app \
     --repository-format=docker \
     --location=us-central1 \
     --description="Gaming web app"
   ```

2. Configure Docker auth for the region:

   ```bash
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

3. Submit a build (from the repo root):

   ```bash
   gcloud builds submit --config=cloudbuild.yaml \
     --substitutions=_REGION=us-central1,_REPO=gaming-web-app,_IMAGE=gaming-web-app
   ```

## Deploy to Cloud Run

Replace placeholders with your project, region, and image path from the build output.

```bash
gcloud run deploy gaming-web-app \
  --image us-central1-docker.pkg.dev/PROJECT_ID/gaming-web-app/gaming-web-app:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-secrets=... \
  --set-env-vars=...
```

For production, prefer **Secret Manager** for `SECRET_KEY`, database passwords, and API keys instead of plain `--set-env-vars`.

## Database URL format

If you use a single `DATABASE_URL`, it should be SQLAlchemy-compatible, for example:

`mysql+pymysql://user:password@host:3306/database_name?ssl_disabled=true`

Some platforms emit `mysql://...`; the app normalizes that to `mysql+pymysql://` when using `DATABASE_URL`.
