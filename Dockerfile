FROM python:3.6

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements_headless.txt ./
RUN pip install --no-cache-dir -r requirements_headless.txt

COPY . .

CMD ["python", "BlueSky.py", "--headless"]
