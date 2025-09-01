rm -f /srv/www/site1/web/sitemap.xml.gz
sed -i -e "s=ows_ingress_host=${OWS_INGRESS_HOST}=" /srv/www/site1/web/robots.txt
sed -i -e "s=ows_ingress_host=${OWS_INGRESS_HOST}=" /srv/www/site1/web/sitemap.xml
exec httpd-foreground