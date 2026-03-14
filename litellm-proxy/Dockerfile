FROM node:20-slim AS claude-installer
RUN npm install -g @anthropic-ai/claude-code

FROM python:3.11-slim

COPY --from=claude-installer /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=claude-installer /usr/local/bin/node /usr/local/bin/node
RUN ln -sf /usr/local/lib/node_modules/@anthropic-ai/claude-code/cli.js /usr/local/bin/claude \
    && chmod +x /usr/local/bin/claude

RUN pip install uv
WORKDIR /app
COPY pyproject.toml .
RUN uv pip install --system "litellm[proxy]>=1.40" "python-dotenv>=1.0"
COPY custom_handler.py config.yaml ./

EXPOSE 8080
ENV CLAUDE_PATH=claude
CMD ["litellm", "--config", "config.yaml", "--host", "0.0.0.0", "--port", "8080"]
