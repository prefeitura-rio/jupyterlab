FROM jupyter/base-notebook:python-3.9.10

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz libpq-dev libgl1 ffmpeg libsm6 libxext6 build-essential nano && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Give jovyan user sudo privileges
RUN echo 'jovyan ALL=(ALL:ALL) ALL' >> /etc/sudoers

# Set a new password for jovyan user (example password: 'emd')
RUN echo 'jovyan:emd' | chpasswd

USER jovyan
RUN python -m pip install --no-cache-dir --upgrade pip setuptools poetry && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyterlab-plotly

WORKDIR /tmp/_create_kernels
COPY ./static /tmp/_static
COPY ./kernels ./kernels
COPY generate_kernels.py .
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install && \
    poetry run python generate_kernels.py

WORKDIR /home/jovyan