FROM python:3.10.7-slim-bullseye
ENV PYTHONIOENCODING=utf-8

RUN pip install virtualenv
ENV VIRTUAL_ENV=/venv
RUN virtualenv venv -p python3
ENV PATH="VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt . 
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN rm -rf requirements.txt && \
    rm -rf /var/cache/apt/* && \
    rm -rf /root/.cache/pip