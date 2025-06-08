FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies (no unnecessary tools)
RUN yum install -y \
    tar \
    xz \
    curl \
    gcc \
    gcc-c++ \
    make \
    python3-devel \
    ncurses-compat-libs \
    libsndfile \
    libsndfile-devel \
    && yum clean all

# Install ffmpeg (static binary for x86_64)
RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz && \
    tar -xJf ffmpeg.tar.xz && \
    mv ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
    chmod +x /usr/local/bin/ffmpeg && \
    rm -rf ffmpeg.tar.xz ffmpeg-*-static

# Copy requirements.txt before installing dependencies (better caching)
COPY requirements.txt .

# Upgrade pip and install Python packages from requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to keep image lean
RUN yum remove -y gcc python3-devel libsndfile-devel && \
    yum clean all

# Set working directory
WORKDIR /var/task/BirdNET-Analyzer

# Copy source code
COPY BirdNET-Analyzer /var/task/BirdNET-Analyzer

# Install BirdNET-Analyzer package
RUN pip install .

ENV NUMBA_CACHE_DIR=/tmp/numba_cache

# Lambda entry point
CMD ["BirdNET-Analyzer.lambda_handler.lambda_handler"]
