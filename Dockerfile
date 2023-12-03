FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

COPY . .

ENV ENV prod

CMD ["python", "index.py"]
