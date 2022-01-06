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
export PAPERTRAIL_URL=<papertrail_url>
export PAPERTRAIL_PORT=<papertrail_port>
```

### PyCharm

Create a run configuration that points to: `graphic_cards_stock_crawler/main.py`

### CLI

Run:

```
scrapy crawl graphic_cards_stock`
```

### Telegram Configuration

1. Create bot with the **BotFather** and type `/newbot`.
2. Create a Telegram channel and add the bot to the channel.
3. Retrieve the channel ID: 
   1. Make the channel public.
   2. Make a request to the Telegram API with the Telegram API key and the channel name:
      ```
      curl -X POST 'https://api.telegram.org/bot<API_KEY>/sendMessage?chat_id=@<CHANNEL_NAME>&text=123'
      ```
   3. The response includes a chat ID.
   4. Make the channel private again.

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
