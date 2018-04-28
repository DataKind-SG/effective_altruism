FROM quay.io/dksg/ea-jupyterlab:1.0.0

# Install python dependencies
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
COPY . /tmp/
