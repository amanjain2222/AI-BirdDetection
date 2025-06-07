FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies
RUN yum update -y && yum install -y mesa-libGL && yum clean all

COPY requirements.txt  ${LAMBDA_TASK_ROOT} 

# Install function dependencies
RUN pip install --no-cache-dir torch==2.0.1+cpu torchvision==0.15.2+cpu --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Pre-create config directories and set permissions
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV YOLO_CONFIG_DIR=/tmp/ultralytics

RUN mkdir -p /tmp/matplotlib /tmp/ultralytics && \
    chmod -R 755 /tmp/matplotlib /tmp/ultralytics

# Copy function code
COPY query-by-video.py ${LAMBDA_TASK_ROOT}

# Set environment variables to force headless mode
ENV DISPLAY=""
ENV MPLBACKEND=Agg

# Set default environment variables (can be overridden at runtime)
ENV MODEL_BUCKET_NAME=birdstore
ENV MODEL_KEY=models/model.pt
ENV CONFIDENCE_THRESHOLD=0.5
ENV FRAME_SKIP=1

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "query-by-video.lambda_handler" ]