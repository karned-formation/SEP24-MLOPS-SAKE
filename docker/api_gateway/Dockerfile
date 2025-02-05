FROM nginx:latest

COPY docker/api_gateway/nginx.conf /etc/nginx/nginx.conf
COPY docker/api_gateway/index.html /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]