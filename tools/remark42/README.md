# Remark42 comments for jonvanlew.com

Self-hosted comments that replace Disqus: no ads, no tracking, and the comments
live on our own VPS. The site already has the comment box wired in
(`themes/clean-blog/templates/comments_remark42.html`); it switches on when
`REMARK42_URL` is set in `publishconf.py`.

VPS: `jon@5.78.83.3` (SSH key login). Docker is already installed and `jon` can
run it without sudo.

## How it's wired

```
visitor ─► Cloudflare ─► tunnel "jvl-hetzner" ─► localhost:8080 ─► Remark42 container
```

No web server config is involved: Apache keeps serving www as before, and
the Cloudflare tunnel (already running for draw / jeannie) carries
`comments.jonvanlew.com` straight to the container. Remark42 only listens on
`127.0.0.1:8080`, so it can't be reached around Cloudflare.

## 1. Start Remark42 on the VPS

Copy `docker-compose.yml` from this folder to `~/remark42/` on the VPS (WinSCP,
or `scp docker-compose.yml jon@5.78.83.3:remark42/` after `ssh jon@5.78.83.3 mkdir -p remark42`), then:

```bash
ssh jon@5.78.83.3
cd ~/remark42
printf 'REMARK42_SECRET=%s\nREMARK42_ADMIN_PASSWD=%s\n' "$(openssl rand -hex 32)" "$(openssl rand -hex 16)" > .env
chmod 600 .env
docker compose up -d
docker compose logs --tail 20
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080/web/
```

The last line should print `200`.

## 2. Cloudflare tunnel route

Cloudflare dashboard → **Networking → Tunnels → jvl-hetzner → Routes → Add route**
(type *Published application*):

- Subdomain `comments`, domain `jonvanlew.com`
- Service `http://localhost:8080`

Cloudflare creates the DNS record itself. **Don't** put an Access login on this
hostname: every visitor's browser has to reach it to load and post comments.

Check https://comments.jonvanlew.com/web/ shows a demo comment box.

## 3. Your admin login (for moderating)

Visitors comment anonymously with a name. To delete or block comments you need
a login Remark42 recognizes. Simplest is GitHub:

1. GitHub → Settings → Developer settings → OAuth Apps → New.
   Homepage `https://www.jonvanlew.com`, callback
   `https://comments.jonvanlew.com/auth/github/callback`.
2. Add `GITHUB_CID=...` and `GITHUB_CSEC=...` lines to `~/remark42/.env`,
   uncomment the two `AUTH_GITHUB_*` lines in `docker-compose.yml`, then
   `docker compose up -d`.
3. Sign in with GitHub in any comment box, click your name to see your user ID
   (`github_...`), put it in `ADMIN_SHARED_ID`, uncomment that line,
   `docker compose up -d`.

## 4. Turn it on in the site

In `publishconf.py` uncomment:

```python
REMARK42_URL = "https://comments.jonvanlew.com"
```

then build and deploy as usual.

## 5. Bring over the old Disqus comments (optional)

1. Disqus admin → *jonnyvlreport* → Moderation → Export comments; Disqus emails
   a `.xml.gz` link.
2. Copy the file to `~/remark42/var/` on the VPS, unzip it (`gunzip`), then:

```bash
cd ~/remark42
docker exec -it remark42 import -p disqus -f /srv/var/disqus-export.xml -s jonvanlew
```

Threads match by page URL, so imported comments land on the same posts.

## Backups

Remark42 writes a daily backup into `~/remark42/var/backup/`. Copying that
folder off the VPS now and then is enough.

## If you ever drop the tunnel

Apache could proxy instead (needs `sudo a2enmod proxy proxy_http` and a
`<VirtualHost *:80>` with `ServerName comments.jonvanlew.com`,
`ProxyPass / http://127.0.0.1:8080/` and `ProxyPassReverse / http://127.0.0.1:8080/`),
but with the tunnel in place there's no reason to.
