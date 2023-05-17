FROM continuumio/miniconda3

WORKDIR /app

COPY env.txt .

RUN conda env create --file env.txt --name gw_bot_env

