FROM python:3
WORKDIR /dwellings
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3","-u","main.py"]
