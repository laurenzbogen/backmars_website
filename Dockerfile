FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash git openssh-client \
    && rm -rf /var/lib/apt/lists/*
# If compress_image.sh uses imagemagick/ffmpeg/etc., add them to the apt-get line

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Allow git to operate on the bind-mounted repo regardless of file ownership
RUN git config --global --add safe.directory '*'

COPY loop.sh /loop.sh
RUN chmod +x /loop.sh

CMD ["/loop.sh"]
