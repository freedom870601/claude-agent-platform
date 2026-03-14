FROM python:3.11-slim
RUN pip install uv
WORKDIR /app
COPY pyproject.toml .
RUN uv pip install --system fastapi "uvicorn[standard]" openai playwright pydantic
RUN playwright install chromium --with-deps
COPY app/ ./app/
EXPOSE 8000
ENV LITELLM_URL=""
ENV LITELLM_MASTER_KEY=""
ENV LITELLM_MODEL="claude-cli"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
