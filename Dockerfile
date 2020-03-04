FROM python:3.8

WORKDIR /home

ENV VK_API_TOKEN="3cfd1b9e48f43434dac264d3f89619a67b74815f10981787e0e2e71102bc9898c27e9cdc2da7009b42c24"
ENV VK_GROUP_ID="192253298"

ENV TZ=Asia/Yekaterinburg
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip vk_api pytz

COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "server_manager.py"]

