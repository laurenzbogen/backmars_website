FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash git openssh-client ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global credential.helper \
    '!f() { echo "username=x-access-token"; echo "password=$GITHUB_TOKEN"; }; f'

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY loop.sh /loop.sh
RUN chmod +x /loop.sh

CMD ["/loop.sh"]
