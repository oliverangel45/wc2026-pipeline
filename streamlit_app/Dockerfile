FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY streamlit_app/ ./streamlit_app/

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app/home.py", "--server.address=0.0.0.0"]