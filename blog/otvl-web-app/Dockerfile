FROM node:16-slim as build-stage

COPY otvl_web/otvl-web-lib/ /build/otvl_web/otvl-web-lib/
WORKDIR /build/otvl_web/otvl-web-lib
RUN yarn global add @vue/cli @vue/cli-service \
  && yarn install \
  && yarn build-lib

COPY otvl-web-app/public /build/otvl-web-app/public
COPY otvl-web-app/src /build/otvl-web-app/src
COPY otvl-web-app/*.js* /build/otvl-web-app/
WORKDIR /build/otvl-web-app
RUN yarn install \
  && yarn build

FROM httpd:2.4
COPY --from=build-stage /build/otvl-web-app/dist /srv/www/site1/web
COPY otvl-web-app/shell /shell
ADD otvl-web-app/shell/entrypoint.sh /

COPY otvl-web-app/apache2/conf /usr/local/apache2/conf
COPY otvl-web-app/apache2/web /srv/www/site1/web
ENV OTVL_WEB_SERVER_NAME demo.otvl.org
ENV OTVL_WEB_APP_PORT 443

ENTRYPOINT /entrypoint.sh /shell/httpd-foreground.sh
