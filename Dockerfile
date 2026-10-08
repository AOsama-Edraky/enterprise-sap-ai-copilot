FROM python:3.12-slim
WORKDIR /app
RUN useradd --uid 10001 --create-home demo
COPY --chown=demo:demo copilot ./copilot
COPY --chown=demo:demo data ./data
COPY --chown=demo:demo evals ./evals
RUN mkdir .runtime && chown demo:demo .runtime
USER demo
CMD ["python", "-m", "copilot", "demo"]
