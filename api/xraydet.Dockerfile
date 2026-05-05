ARG DEBIAN_FRONTEND=noninteractive

# ARG PYTORCH="2.1.2"
# Host has 12.2, maybe it works this way
# ARG CUDA="12.1"
# ARG CUDNN="8"

# ARG MMCV="2.1.0"
# ARG MMDET="3.3.0"

# Takes way too long
# FROM nvidia/cuda:12.2.2-devel-ubuntu22.04

FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

# # TODO: Which Python version is installed here? Is this going to be a problem?
# RUN apt-get update && \
#   apt-get install -y \
#   python3-pip \
#   python3-opencv \
#   libglib2.0-0

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
  ca-certificates \
  g++ \
  openjdk-11-jre-headless \
  # MMDet Requirements
  ffmpeg libsm6 libxext6 git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 \
  && rm -rf /var/lib/apt/lists/*

# Installing MMDetection packages
RUN pip install openmim && \
  mim install "mmengine" "mmcv==2.1.0"
# RUN pip install mmengine
# RUN ["/bin/bash", "-c", "pip install mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cu122/torch2.1.2/index.html"]
# RUN pip install mmdet==3.3.0

WORKDIR /api

ENV FORCE_CUDA="1"
ENV MMCV_WITH_OPS=1
# COPY ./mmdet_setup.sh ./mmdet_setup.sh
# RUN bash ./mmdet_setup.sh
# RUN pip install openmim && \
#   mim install mmengine mmpretrain timm mmdet \
#   mim install "mmcv==2.1.0"

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# cv2 & mmdet container dependencies 
# RUN apt-get update && apt-get install -y \
#   ffmpeg libsm6 libxext6 git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6

COPY ./model/ ./model/
COPY ./pydantic_models/ ./pydantic_models/
COPY ./utils/ ./utils/
COPY ./main.py ./

EXPOSE 8110/tcp

CMD ["uvicorn", "main:app", "--host", "localhost", "--port", "8110" ]