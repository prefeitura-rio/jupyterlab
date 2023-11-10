FROM jupyter/base-notebook:python-3.9.10

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz libpq-dev libgl1 ffmpeg libsm6 libxext6 build-essential nano zsh git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Oh My Zsh and automatically change the default shell to zsh
RUN sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

# Install Antigen for Zsh plugin management
RUN curl -L git.io/antigen > .antigen.zsh

# Give jovyan user sudo privileges
RUN echo 'jovyan ALL=(ALL:ALL) ALL' >> /etc/sudoers

# Set a new password for jovyan user (example password: 'emd')
RUN echo 'jovyan:emd' | chpasswd

USER jovyan

# Copy .zsh_custom file as .zshrc in the home directory of jovyan
COPY .zshrc /home/jovyan/.zshrc

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

# Switch to Zsh as default shell
SHELL ["/bin/zsh", "-c"]

WORKDIR /home/jovyan