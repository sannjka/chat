server {
        server_name example1.alexandervoloshin.ru;

        location /static {
                alias /home/sannjka/sites/example1.alexandervoloshin.ru/static;
        }

        location / {
                proxy_set_header Host $host;
                proxy_pass http://unix:/tmp/example1.alexandervoloshin.ru.socket;
                proxy_http_version 1.1;
        
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_read_timeout 86400;

                proxy_set_header    X-Real-IP           $remote_addr;
                proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;
                proxy_set_header    X-Forwarded-Proto   $scheme;
        }



    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/alexandervoloshin.ru/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/alexandervoloshin.ru/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

server {
    if ($host = example1.alexandervoloshin.ru) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


        server_name example1.alexandervoloshin.ru;
    listen 80;
    return 404; # managed by Certbot


}
