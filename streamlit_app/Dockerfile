FROM python:3.11-slim
 
WORKDIR /app
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY streamlit_app/ ./streamlit_app/
 
ENV PYTHONUNBUFFERED=1
 
CMD ["streamlit", "run", "streamlit_app/Home.py", "--server.address=0.0.0.0", "--server.port=8501"]