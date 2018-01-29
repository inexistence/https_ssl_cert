# HTTPS SSL CERT

Let's Encrypt 免费 SSL 证书生成脚本。

在 Mac 和 Ubuntu 上试过 shell 脚本。Win 上没试过不知道能不能，如果不能可能是有些脚本命令不兼容吧。

Python 脚本还没试过。

## 使用说明
`Let's Encrypt` 生成的证书只有90天有效期。

目录下 `multissl.sh` 和 `siglessl.sh` 是多域名shell脚本和单域名shell脚本。python脚本是根据这两个的方案写的。

### 简易使用
若首次运行，会自动生成 `account.key`（你的账号key）, `domain.key`（域名key）, `domain.csr`（使用域名key和域名列表生成的域名csr）, `intermediate.pem`（Let's Encrypt的中间证书） 文件，保留以上这些文件可以复用于下次更新证书。

#### 以使用 python 脚本创建 `a.com` 和 `b.com` 域名的 ssl 证书为例：
1. 编写 `domains` 文件，每行输入一个域名。
2. 配置服务端环境，使得能够访问 `http://a.com/.well-known/acme-challenge/` 和 `http://b.com/.well-known/acme-challenge/` 来获得本目录下的文件。用于 `Let's Encrypt` 验证域名是否属于你。
3. 在本目录下运行 `python letsencrypt.py --domains ./domains`。若原本已经有了 `a.com` 和 `b.com` 生成的 `domain.csr` 在本目录下，可以通过增加参数 `--update` 来只进行更新证书操作。（PS：更新证书即是使用原本的 `account.key` 和 `domain.csr` 重新生成新证书）
4. `signed.cert` 是未整合 `Let's Encrypt` 中间证书前的证书。生成的 `chained.pem` 就是最终的整合了 `Let's Encrypt` 中间证书的最终证书。一般我们使用的是 `chained.pem` 。
5. 配置服务端环境的证书key为 `domain.key` ,证书为 `chained.pem`。

#### 以使用 shell 脚本创建 `a.com` 和 `b.com` 域名的 ssl 证书为例：
1. 配置服务端环境，使得能够访问 `http://a.com/.well-known/acme-challenge/` 和 `http://b.com/.well-known/acme-challenge/` 来获得本目录下的文件。用于 `Let's Encrypt` 验证域名是否属于你。
2. 因为是多域名，选择使用 `multissl.sh`
3. 修改 `multissl.sh` 中 domaincn 的值为你的域名，如下：`domaincn="[SAN]\nsubjectAltName=DNS:a.com,DNS:b.com"`
4. MAC 下，先运行 `chmod -x ./multissl.sh` 设置权限
5. 运行 `./multissl.sh`，生成 `account.key`，`domain.key`，`signed.cert`，`chained.pem` 等文件。
6. `signed.cert` 是未整合 `Let's Encrypt` 中间证书前的证书。生成的 `chained.pem` 就是最终的整合了 `Let's Encrypt` 中间证书的最终证书。一般我们使用的是 `chained.pem` 。
7. 配置服务端环境的证书key为 `domain.key` ,证书为 `chained.pem`。

### NGINX 配置参考

`API_BASE_URL` 替换成你的域名，多域名以空格分开。如 `a.com b.com`。
`location /.well-known/acme-challenge/` 下的 `alias` 是本目录所在位置。

#### http
```
server {
    listen              80;
    server_name  API_BASE_URL;
    root         /usr/share/nginx/node/public;
    index        index.html;

    gzip on;
    gzip_disable "msie6";

    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_min_length 256;
    gzip_types text/plain text/css application/json application/x-javascript application/javascript text/xml application/xml application/xml+rss text/javascript application/vnd.ms-fontobject application/x-font-ttf font/opentype image/svg+xml image/x-icon;

    # Proxy To Backend
    location /api {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_set_header X-NginX-Proxy true;
      proxy_pass http://127.0.0.1:8000;
      proxy_redirect default;
    }
    location /v0 {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_set_header X-NginX-Proxy true;
      proxy_pass http://127.0.0.1:8000;
      proxy_redirect default;
    }
    location / {
        try_files $uri $uri/ /index.html =404;
    }
    location /.well-known/acme-challenge/ {
        alias /etc/nginx/ssl/;
        try_files $uri =404;
    }
}
server_names_hash_bucket_size 128;
client_max_body_size 16M;

```

在证书生成完成后配置，配置完可能需要重启 nginx, 运行 `service nginx reload`。
#### https
```
server {
    listen  443 ssl;

    server_name  API_BASE_URL;
    ssl_certificate     /etc/nginx/ssl/chained.pem;
    ssl_certificate_key /etc/nginx/ssl/domain.key;
    root         /usr/share/nginx/node/public;
    index        index.html;

    gzip on;
    gzip_disable "msie6";

    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_min_length 256;
    gzip_types text/plain text/css application/json application/x-javascript application/javascript text/xml application/xml application/xml+rss text/javascript application/vnd.ms-fontobject application/x-font-ttf font/opentype image/svg+xml image/x-icon;

    # Proxy To Backend
    location / {
        proxy_pass http://127.0.0.1:8000/;
    }
}
```
