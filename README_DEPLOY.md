# CORTEX Deployment Notes

## Local Deployment

```powershell
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

Open `http://localhost:8501`.

## Streamlit Community Cloud

1. Push this `source_code` folder to a GitHub repository.
2. In Streamlit Community Cloud, choose `app.py` as the entry point.
3. The platform will install `requirements.txt`.

## Render

Use these settings:

- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Docker

```powershell
docker build -t cortex-health .
docker run -p 8501:8501 cortex-health
```
