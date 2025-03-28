FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    software-properties-common gcc git jq python3 python3-setuptools python3-pip python3-apt python3-venv

COPY setup.py /setup.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./MarkdownToConfluence /MarkdownToConfluence
RUN pip install -e .

RUN chmod +x /MarkdownToConfluence/convert_all.sh
RUN chmod +x /MarkdownToConfluence/convert.sh
RUN chmod +x /MarkdownToConfluence/entrypoint.sh

ENTRYPOINT [ "bash", "/MarkdownToConfluence/entrypoint.sh" ]

