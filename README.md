# graphic_cards_stock_crawler

## Running locally

Set environment variables:

```
export TELEGRAM_TOKEN=<TOKEN>
export TELEGRAM_CHAT_ID=<CHAT_ID>
export MARIADB_USER=pi
export MARIADB_PASSWORD=<PASSWORD>
export MARIADB_HOST=localhost
export MARIADB_PORT=3306
export MARIADB_SCHEMA=graphic_cards_stock_crawler
```

### PyCharm

Create a run configuration that points to: `graphic_cards_stock_crawler/main.py`

### CLI

Run:

```
scrapy crawl graphic_cards_stock`
```

## Raspberry Setup

1. Install and configure MariaDB:

Install:

```
sudo apt update
sudo apt upgrade
sudo apt install mariadb-server
```

Configure:

```
sudo mysql_secure_installation
```

Create user:

```
sudo mysql -uroot -p
CREATE USER 'pi'@'%' IDENTIFIED BY '<PASSWORD>';
GRANT ALL PRIVILEGES ON *.* TO 'pi'@'%';
FLUSH PRIVILEGES;
exit;
```

Configure remote access:

```
nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

```
bind-address            = 0.0.0.0
```

From your local machine:

```
mysql -upi -p -h <RASPBERYPI_IP>
```

2. Install dependencies:

```
cd ~/scrapy-projects/graphic_cards_stock_crawler
pip3 install -r requirements.txt
```

3. Copy `crawl.sh` to the home directory (`~/`):

4. Make the script executable:

```
chmod +x ~/crawl.sh
```

5. Create cron job:

```
crontab -e
```

```
*/2 * * * * MARIADB_USER=pi MARIADB_PASSWORD=<PASSWORD> MARIADB_HOST=localhost MARIADB_PORT=3306 MARIADB_SCHEMA=graphic_cards_stock_crawler TELEGRAM_TOKEN=<TOKEN> TELEGRAM_CHAT_ID=<CHAT_ID> /home/pi/crawl.sh
```

It will run every 2 minutes.

7. Check cron jobs:

```
crontab -l
```

8. Check logs:

```
grep CRON /var/log/syslog
```

If the mail service is installed you can also see the logs with `sudo tail -f /var/mail/pi`
