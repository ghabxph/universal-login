FROM python:3.9.0a2-alpine3.10

# Install essential dependencies
RUN apk --no-cache --virtual build-dependencies add build-base libffi-dev openssl-dev \
  && pip install pip==20.0.1 \
  && pip install Flask==1.1.1 \
  && pip install bcrypt==3.1.7 \
  && pip install jwcrypto==0.6.0 \
  && pip install pymongo==3.10.1 \
  && apk del build-dependencies

# Other dependencies
RUN pip install requests==2.22.0

# Copy project source code
COPY src /app

# WORKDIR to Source Code
WORKDIR /app

# Start the project
ENTRYPOINT '/usr/local/bin/python' 'dev.py'