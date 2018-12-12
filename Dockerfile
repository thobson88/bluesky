
FROM python:3.6

ENV PYTHONUNBUFFERED=1

RUN apt-get update -y \
	&& apt-get install -y python3-opengl

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "BlueSky.py", "--headless"]