ARG DEBIAN_FRONTEND=noninteractive

FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

WORKDIR /api

ENV FORCE_CUDA="1"

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./model/ ./model/
COPY ./dino/ ./dino/
COPY ./main.py ./

EXPOSE 8111/tcp

CMD ["uvicorn", "main:app", "--host", "localhost", "--port", "8111" ]