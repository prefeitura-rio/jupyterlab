FROM jupyter/datascience-notebook:python-3.9.10

USER root
RUN apt-get update && apt-get install -y --no-install-recommends graphviz libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


USER jovyan
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade setuptools && \
    python -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyterlab-plotly
