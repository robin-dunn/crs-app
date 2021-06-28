# FROM ubuntu:18.04 as builder

# ARG DESTDIR="/build"

# # Setup build env
# RUN apt-get update -y \
#     && apt-get install -y --fix-missing --no-install-recommends \
#             software-properties-common build-essential ca-certificates \
#             make cmake wget unzip libtool automake \
#             zlib1g-dev libsqlite3-dev pkg-config sqlite3 libcurl4-gnutls-dev \
#             libtiff5-dev

# COPY . /PROJ

# RUN cd /PROJ \
#     && ./autogen.sh \
#     && ./configure --prefix=/usr \
#     && make -j$(nproc) \
#     && make install


# FROM ubuntu:18.04 as runner

# RUN date

# RUN apt-get update; \
#     DEBIAN_FRONTEND=noninteractive apt-get install -y \
#         libsqlite3-0 libtiff5 libcurl4 libcurl3-gnutls \
#         wget ca-certificates

# # Put this first as this is rarely changing
# RUN \
#     mkdir -p /usr/share/proj; \
#     wget --no-verbose --mirror https://cdn.proj.org/; \
#     rm -f cdn.proj.org/*.js; \
#     rm -f cdn.proj.org/*.css; \
#     mv cdn.proj.org/* /usr/share/proj/; \
#     rmdir cdn.proj.org

# COPY --from=builder  /build/usr/share/proj/ /usr/share/proj/
# COPY --from=builder  /build/usr/include/ /usr/include/
# COPY --from=builder  /build/usr/bin/ /usr/bin/
# COPY --from=builder  /build/usr/lib/ /usr/lib/

##################################################################
# The above commmented out code is intended to setup the PROJ
# dependencies, however this fails with an auto.sh file not found.
# The docker image may still run without the above, so not sure
# if it's really necessary.
##################################################################

FROM python:3.9.4 as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM node:11.4.0-alpine as builder
COPY . /app
WORKDIR /app/ui
RUN npm install
RUN npm run build -- --output-path=./dist/crs-app

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
# RUN useradd --create-home appuser
# WORKDIR /home/appuser
# USER appuser

WORKDIR /app
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "app/app.py" ]