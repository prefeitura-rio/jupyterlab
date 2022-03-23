FROM jupyter/datascience-notebook:python-3.9.10

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyterlab-plotly