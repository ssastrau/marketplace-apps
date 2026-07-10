# cPanel & WHM with LiteSpeed Enterprise Quick Deploy App

cPanel & WHM is a widely used Linux server/website administration platform for managing web
hosting, DNS, databases, email, and more through a browser-based interface. This Quick Deploy App
installs cPanel & WHM on Akamai Cloud Compute and layers **LiteSpeed Web Server Enterprise** on
top as the site-serving web server (replacing Apache), giving hosted sites LiteSpeed's
performance and built-in LSCache WordPress acceleration. LiteSpeed Enterprise ships on a
**15-day trial license** (see [Post-Deployment](#post-deployment)); cPanel itself ships unlicensed,
matching how every cPanel one-click across every marketplace works — activation is a manual
step the customer takes after deploy.

This backports the legacy "LiteSpeed cPanel One-Click" StackScript to a modern Ansible playbook,
targeting current cPanel & WHM (11.136+) and the current LiteSpeed WHM plugin, both of which
added AlmaLinux 10 support in 2026.

## Software Included

| Software | Version | Description |
| :---     | :----   | :---        |
| cPanel & WHM | latest (11.136+) | Server/website administration control panel |
| LiteSpeed Web Server | Enterprise, latest (6.3.5 at time of writing) | High-performance web server replacing Apache; ships on a 15-day trial license |

**Supported Distributions:**

- AlmaLinux 10

<!-- REVIEW: confirm whether Ubuntu/Rocky Linux support (offered by the sibling cpanel-almalinux/
cpanel-ubuntu apps) should be added here later — this backport was scoped to AlmaLinux 10 only,
matching the operator's instruction to align with cpanel-almalinux's current CI target. -->

## Post-Deployment

This app has **no operator-facing UDFs** — cPanel and LiteSpeed are administered entirely inside
their own web interfaces after deploy, not through the Ansible playbook (matching how the
existing `cpanel-almalinux`/`cpanel-ubuntu` apps work: no sudo user, no domain/DNS setup, no
firewall management — cPanel self-manages its own security posture, e.g. cPHulk brute-force
protection and an optional Firewall/csf app inside WHM).

When the playbook finishes:

- **Log in to WHM** at `https://<your-server-ip-or-rdns>:2087` as `root`, using the root password
  set when the Linode was created. (SSH in as root and the login banner prints a one-time
  `whmlogin` autologin URL automatically.)
- **Create your first cPanel account** from WHM → *Create a New Account*. Once created, log in to
  cPanel itself at `https://<your-server-ip-or-rdns>:2083` with that account's credentials.
- **Log in to the LiteSpeed WebAdmin console** at `https://<your-server-ip-or-rdns>:7080` with
  username `admin` and the password in `/root/.credentials` (generated fresh per deploy).
- **Activate your licenses.** cPanel ships unlicensed and LiteSpeed ships on a 15-day trial
  (extendable once to 30 days via LiteSpeed support) — both are fully functional during
  evaluation; a production deployment needs a cPanel license and either a purchased LiteSpeed
  Enterprise license or a renewed trial.
- Webmail is available at `https://<your-server-ip-or-rdns>:2096` per cPanel account.

<!-- REVIEW: confirm the post-deploy steps above against a fresh customer-facing deploy — written
from architecture_decisions.md/manual_install.md/e2e_testing.md, not re-verified from a brand new
customer's perspective. -->

## Use our API

Customers can deploy this app through the Akamai Cloud Marketplace or directly using the API.
Before using the commands below, create an [API token](https://www.linode.com/docs/products/tools/linode-api/get-started/#create-an-api-token)
or configure [linode-cli](https://www.linode.com/products/cli/), and substitute your own values
for the defaults. This app has no UDFs, so `stackscript_data` is empty.

SHELL:
```
curl -H "Content-Type: application/json" \
-H "Authorization: Bearer $TOKEN" \
-X POST -d '{
    "image": "linode/almalinux10",
    "region": "us-ord",
    "type": "g6-dedicated-4",
    "label": "openlitespeed-cpanel-occ-us-ord",
    "tags": [],
    "root_pass": "A_Secure_Password",
    "authorized_users": [
        "user1",
        "user2"
    ],
    "booted": true,
    "backups_enabled": false,
    "private_ip": false,
    "stackscript_id": 00000,
    "stackscript_data": {}
}' https://api.linode.com/v4/linode/instances
```

CLI:
```
linode-cli linodes create \
  --image 'linode/almalinux10' \
  --region us-ord \
  --type g6-dedicated-4 \
  --label openlitespeed-cpanel-occ-us-ord \
  --root_pass A_Secure_Password \
  --authorized_users user1 \
  --authorized_users user2 \
  --booted true \
  --backups_enabled false \
  --private_ip false \
  --stackscript_id 000000 \
  --stackscript_data '{}'
```

<!-- REVIEW: fill in the real stackscript_id once this app's production StackScript is created
(this backport used a private test StackScript, id 2161608, during /app-deploy validation). -->

## Resources

- [cPanel & WHM Documentation](https://docs.cpanel.net/)
- [LiteSpeed WHM Plugin Documentation](https://docs.litespeedtech.com/lsws/cp/cpanel/whm-litespeed-plugin/whm-install/)
- [LiteSpeed Trial License](https://docs.litespeedtech.com/lsws/trial/)
- <!-- REVIEW: add the Akamai Marketplace guide URL once /app-docs publishes it -->
