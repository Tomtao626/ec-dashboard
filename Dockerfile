#基础镜像
from python:3.9.6-slim-buster
ENV PROJECT_PROFILE prod
#端口
ARG PORT=8000

#设置时区
ARG TIME_ZONE=Asia/Shanghai

COPY . /app/
WORKDIR /app/
#修改apt镜像源头 参考：https://mirror.tuna.tsinghua.edu.cn/help/debian/
RUN mv sources.list /etc/apt/
RUN apt-get update
RUN python -m pip install -i https://pypi.douban.com/simple --upgrade pip
#pip升级
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential
RUN pip install --no-cache-dir -i https://pypi.douban.com/simple -r requirements_linux.txt
#健康检查
#HEALTHCHECK --interval=5s --timeout=3s  CMD curl -fs http://localhost:8082/health_check || exit 1
EXPOSE ${PORT}
#开机自动启动
#ENTRYPOINT uwsgi --ini start.ini #用这个启动会出现边缘数据无法上报的问题
ENTRYPOINT python manage.py runserver 0.0.0.0:8000