FROM python:3.13 AS build-stage
COPY . /ows/
WORKDIR /ows
RUN pip install -r requirements.txt \
    && mkdocs build

FROM httpd:2.4
COPY --from=build-stage /ows/site /srv/www/site1/web
COPY apache2/conf /usr/local/apache2/conf
COPY apache2/shell /shell

ENV OWS_INGRESS_HOST ows_ingress_host.otvl.org
CMD /shell/launcher.sh
