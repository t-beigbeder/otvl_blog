sed -i -e "s=default_api_server_url=https://${OTVL_WEB_SERVER_NAME}:${OTVL_WEB_APP_PORT}/api/v2=" /srv/www/site1/web/index.html
sed -i -e "s=default_web_server_url=https://${OTVL_WEB_SERVER_NAME}:${OTVL_WEB_APP_PORT}=" /srv/www/site1/web/index.html
sed -i -e "s=@@otvl_web_server_name@@=${OTVL_WEB_SERVER_NAME}=" /srv/www/site1/web/robots.txt
sed -i -e "s=@@otvl_web_server_name@@=${OTVL_WEB_SERVER_NAME}=" /srv/www/site1/web/robots-allow.txt
if [ "${OTVL_WEB_ENABLE_BOTS}" ] ; then cp -p /srv/www/site1/web/robots-allow.txt /srv/www/site1/web/robots.txt ; fi
exec httpd-foreground
