# coolmod_crawler

## Running locally

Set environment variable `TELEGRAM_TOKEN`

### PyCharm

Create a run configuration that points to: `coolmod_crawler/main.py`

### CLI

Run:

```
scrapy crawl graphic_cards
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

2. Copy files to server:

```
scp -r PythonProjects/coolmod_crawler <user>@<ip>:/home/<user>/scrapy-projects
```

3. Install dependencies:

```
Cd ~/scrapy-projects/coolmod_crawler
pip3 install -r requirements.txt
```

4. Create script (`~/crawl.sh`):

```sh
#!/bin/sh
# go to the spider directory
cd /home/<user>/scrapy-projects/coolmod_crawler
# run the spider
/usr/local/bin/scrapy crawl graphic_cards
```

5. Make the script executable:

```
chmod +x ~/crawl.sh
```

6. Create cron job:

```
crontab -e
```

```
*/2 * * * * /home/pi/crawl.sh
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
