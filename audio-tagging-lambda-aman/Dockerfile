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

# Install Python packages with pip (use prebuilt wheels)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir numpy==1.24.3 && \
    pip install --no-cache-dir llvmlite==0.41.1 && \
    pip install --no-cache-dir numba==0.58.1 && \
    pip install --no-cache-dir soundfile


RUN yum remove -y gcc python3-devel libsndfile-devel && \
    yum clean all

# Set working directory
WORKDIR /var/task/BirdNET-Analyzer

# Copy source code
COPY BirdNET-Analyzer /var/task/BirdNET-Analyzer

# Install BirdNET-Analyzer
RUN pip install .

# RUN cp -r /var/task/BirdNET-Analyzer/birdnet_analyzer/checkpoints \
#          /var/lang/lib/python3.11/site-packages/birdnet_analyzer/

ENV NUMBA_CACHE_DIR=/tmp/numba_cache

# Lambda entry point
CMD ["BirdNET-Analyzer.lambda_handler.lambda_handler"]

