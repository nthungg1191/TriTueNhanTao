FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libopenblas-dev \
        liblapack-dev \
        libatlas3-base \
        libx11-dev \
        libgtk-3-dev \
        libsm6 \
        libxrender1 \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
ENV CMAKE_ARGS="-DCMAKE_POLICY_VERSION_MINIMUM=3.5"
RUN pip install --upgrade pip setuptools wheel

RUN pip install cmake==3.27.7

RUN pip install --no-build-isolation dlib==19.24.2

RUN pip install -r requirements.txt
COPY . ./

EXPOSE 5555
CMD ["python", "run.py"]
