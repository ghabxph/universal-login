FROM ghabxph/python-common:0.0.1

# Copy project source code
COPY src /app

# Copy HTML / CSS / JS Files
COPY html /html

# WORKDIR to Source Code
WORKDIR /app

# Start the project
ENTRYPOINT '/usr/local/bin/python' 'dev.py'