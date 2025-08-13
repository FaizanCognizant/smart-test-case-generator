## Deploying to Azure App Service

- Linux App Service:
  - Stack: Python 3.12+ (or a custom container with curl)
  - Startup Command: `bash startup.sh`
  - App settings:
    - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
    - `WEBSITES_PORT` = `8000` (optional; app reads `PORT`)

- Windows App Service:
  - Stack: Python 3.12+
  - Startup Command: `powershell -ExecutionPolicy Bypass -File startup.ps1`
  - App settings:
    - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`

This will:
1) Install `uv` if missing
2) Run `uv tool install "browser-use[cli]"`
3) Start the app with `uv run python app.py` (binding to `$PORT`)
