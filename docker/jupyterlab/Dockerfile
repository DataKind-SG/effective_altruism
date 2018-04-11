# minimal-notebook image as of 20180402
FROM jupyter/minimal-notebook:8d9388cac562

# make sure apt is up to date
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libssl-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

ENV NVM_DIR $HOME/.nvm
ENV NODE_VERSION 8.11.1

# Install nvm with node and npm
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.33.8/install.sh | /bin/bash \
     && /bin/bash -c "source $NVM_DIR/nvm.sh && nvm install $NODE_VERSION && nvm use --delete-prefix $NODE_VERSION"

# Install python dependencies
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
RUN jupyter labextension install @jupyterlab/plotly-extension
RUN jupyter labextension install jupyterlab_bokeh
RUN jupyter labextension install @jupyterlab/geojson-extension
COPY . /tmp/
