# CORTEX Personalized Health Intelligence - Source Code

This folder contains the runnable MVP for the CORTEX prototype. The UI is a Streamlit implementation rebuilt around the Stitch prototype screens: dashboard, intelligence hub, upload validation, profile baseline, patient alerts, and clinician portal.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app automatically loads `sample_health_data.csv`. You can also upload another CSV with the same schema.

## Required CSV Columns

```text
user_id,date,heart_rate,resting_heart_rate,hrv,sleep_hours,sleep_score,steps,active_minutes,calories_burned,spo2,respiratory_rate,stress_level,body_temperature
```

Optional target columns for training/evaluation:

```text
recovery_score,health_state
```

## Files

- `app.py` - Streamlit dashboard and report interface.
- `components.py` - Reusable Streamlit HTML/CSS cards, gauge, chips, charts, and validation components.
- `styles.py` - CORTEX clinical UI theme.
- `pages/` - Dashboard, intelligence hub, upload validation, profile baseline, patient alerts, and clinician portal screens.
- `model.py` - CORTEX personalized baseline, scoring, anomaly, and recommendation engine.
- `utils.py` - CSV validation, column normalization, data cleaning, and dataset summary helpers.
- `reporting.py` - Downloadable PDF health report generation.
- `generate_sample_data.py` - Rebuilds the included multi-user demonstration dataset.
- `train_model.py` - Optional train/test script. Uses scikit-learn if installed and falls back to the deterministic CORTEX rule engine if not.
- `run_smoke_tests.py` - Local logic test for data cleaning and health intelligence output.
- `sample_health_data.csv` - Demo dataset for the prototype.

## Test

```powershell
python run_smoke_tests.py
python train_model.py
```

Generated metrics are written to `model_artifacts/training_metrics.json`.

## Deploy Locally

```powershell
streamlit run app.py --server.port 8501
```

Then open `http://localhost:8501`.

## Public Deployment

For the fastest public deployment, use Streamlit Community Cloud:

- Repository: `Shalinijha0701/CORTEX`
- Branch: `main`
- Main file path: `app.py`

The repository also includes `render.yaml`, `Dockerfile`, `Procfile`, and `runtime.txt` for Render or Docker-based deployment.

## Deploy On Render Or Streamlit Community Cloud

Use `app.py` as the entry point and install packages from `requirements.txt`. The app does not require a database for the MVP; uploaded CSV data is processed in-session.
