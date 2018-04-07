from python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install requirements

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /usr/src/app/

CMD [ "python", "./app.py" ]
