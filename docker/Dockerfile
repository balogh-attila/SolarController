FROM python:3-alpine

WORKDIR /usr/local/

COPY docker/requirements.txt ./share/solar/
RUN pip install --no-cache-dir -r ./share/solar/requirements.txt

COPY src/*.py ./lib/solar/
COPY cfg/config.yaml ./etc/solar/config.yaml

CMD [ "python", "lib/solar/solar_controller.py" ]
