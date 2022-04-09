### Initial Server Setup Cheat Sheet
#### Using Ubuntu Linux Distro As Server

always update the server packages in the case you login first time
`sudo apt update && sudo apt upgrade -y`


configure ssh login for root user
`paste .pub file from local pc to ~/.ssh/authorized_keys`


add new user and add the user to the sudo group
`sudo adduser sammy`
`sudo usermod -aG sudo sammy`


login as the created user and configure ssh login for sammy user
`ssh sammy@64.277.12.78`
`mkdir .ssh && cd .ssh && touch authorized_keys`
`paste .pub file from local pc to ~/.ssh/authorized_keys`


as root user disable password authentication
`nano /etc/ssh/ssd_config`
`set PasswordAuthentication no`


setup firewall for the server
`sudo ufw app list`
`sudo ufw allow openssh`
`sudo ufw enable`


check for activate fireware
`sudo ufw status`


install the latest version of python (3.10)
`sudo apt install python3.10`


change the priority of python to be 3.10 by default
`sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 2`
`sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1`
`sudo update-alternatives --config python`


install pip
`sudo apt-get install -y python3-pip`


upgrade pip
`sudo -H pip3 install --upgrade pip`


install virtualenv
`sudo -H pip3 install virtualenv`



#### Deploying Django Project Cheat Sheet

installing postgres and libraries
`sudo apt install python-dev libpq-dev postgresql postgresql-contrib`

creating postgres database and user
`sudo su - postgres psql`
`alter user postgres with password 'rootpassword' `
`create database djangodb;`
`create user djangouser with create db login with password 'password' `


change to sammy user home dir create apps folder
`cd /home/sammy && mkdir apps`

`cd apps && git clone git@github.com:kkthecompguy/assetisha.git`


change project permission to read, write and execute rights by user
`chmod -R 755 assetisha`


create a virtualenv inside assetisha project
`cd assetisha && virtualenv venv`


activate virtualenv
`source venv/bin/activate`


install gunicorn and dependencies for the project
`pip3 install gunicorn`
`pip3 install -r requirements.txt`


add sever ip address to allowed host and configure db dict
`nano assetisha/settings.py`
`set ALLOWED_HOST=['64.277.12.78', '127.0.0.1', 'localhost']`
`set DATABASES = { \
  default: {
    'ENGINE': 'django.db.backend.postgresql_psycopg2',
    'NAME': 'djangodb',
    'USER': 'djangouser',
    'PASSWORD': 'password',
    'HOST': 'localhost',
    'PORT': 5432
  }
}
`


allow firewall to allow port 8000
`sudo ufw allow 8000`


test applications to make sure it runs with no error
`python3 manage.py runserver 0.0.0.0:8000`


if it runs with no errors we are good to go

we can also test gunicorn if it cann run the project
`guniorn --bind 0.0.0.0:8000 assetisha.wsgi`


deactivate virtualenv
`deactivate`


set up socket to the project to run on startup
`sudo nano /etc/systemd/system/assetisha.socket`
past the following
`
[Unit]
Description=assetisha gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
`


set up service file for the socket to run
`sudo nano /etc/systemd/system/assetisha.service`
paste the following
`
[Unit]
Description=gunicorn daemon
Requires=assetisha.socket
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/home/sammy/apps/assetisha
ExecStart=/home/sammy/assetisha/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          assetisha.wsgi:application

[Install]
WantedBy=multi-user.target
`


We can now start and enable the Gunicorn socket. This will create the socket file at /run/gunicorn.sock now and at boot. When a connection is made to that socket, systemd will automatically start the gunicorn.service to handle it
`sudo systemctl start assetisha.socket`
`sudo systemctl enable assetisha.socket`

Check the status of the process to find out whether it was able to start
`sudo systemctl status gunicorn.socket`


Next, check for the existence of the gunicorn.sock file within the /run directory:
`file /run/gunicorn.sock`

check for socket logs
`sudo journalctl -u assetisha.socket`


Testing Socket Activation
`curl --unix-socket /run/gunicorn.sock localhost`
You should receive the HTML output from your application in the terminal. This indicates that Gunicorn was started and was able to serve your Django application.


You can verify that the Gunicorn service is running by typing
`sudo systemctl status gunicorn`

If the output from curl or the output of systemctl status indicates that a problem occurred, check the logs for additional details:
`sudo journalctl -u gunicorn`

restart the service
`sudo systemctl daemon-reload`
`sudo systemctl restart assetisha`


install nginx as load balancer
`sudo apt install nginx`


Configure Nginx to Proxy Pass to Gunicorn
`sudo nano /etc/nginx/sites-available/assetisha`
paste the following
`
server {
    listen 80;
    server_name 64.277.12.78;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/sammy/assetisha;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
`


Save and close the file when you are finished. Now, we can enable the file by linking it to the sites-enabled directory:
`sudo ln -s /etc/nginx/sites-available/assetisha /etc/nginx/sites-enabled`

Test your Nginx configuration for syntax errors by typing:
`sudo nginx -t`

If no errors are reported, go ahead and restart Nginx by typing:
`sudo systemctl restart nginx`

Finally, we need to open up our firewall to normal traffic on port 80. Since we no longer need access to the development server, we can remove the rule to open port 8000 as well:
`sudo ufw delete allow 8000`
`sudo ufw allow 'Nginx Full'`