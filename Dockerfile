FROM python:3.14.3-slim

ENV APP_HOME=/home/app/
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR $APP_HOME

RUN pip install --no-cache-dir uv

COPY ./pyproject.toml $APP_HOME
COPY ./src/ $APP_HOME/src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e . --system
