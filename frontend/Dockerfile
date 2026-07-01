FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/default.conf.template /etc/nginx/templates/default.conf.template
COPY frontend/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]