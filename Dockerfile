FROM jupyter/datascience-notebook:python-3.9.10

USER root
RUN apt-get update && apt-get install -y --no-install-recommends graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER jovyan
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    apt-get install libpq-dev \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyterlab-plotly
