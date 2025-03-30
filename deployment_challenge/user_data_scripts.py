user_data_lam = """#!/bin/bash

# Update the system packages
sudo yum update -y

# Install httpd and mariadb (MySQL) server
sudo yum install -y httpd mariadb105-server

# Start the httpd service
sudo systemctl start httpd

# Start the mariadb service
sudo systemctl start mariadb

# Enable the services to start on boot
sudo systemctl enable httpd
sudo systemctl enable mariadb

# Set basic permissions for /var/www directory
sudo chown -R apache:apache /var/www
sudo chmod -R 0770 /var/www
"""

user_data_lap = """#!/bin/bash

# Update the system packages
sudo yum update -y

# Install httpd and php
sudo yum install -y httpd php php-mbstring php-xml php-mysqlnd wget

# Download phpmyadmin
cd /var/www/html
sudo wget https://files.phpmyadmin.net/phpMyAdmin/5.2.2/phpMyAdmin-5.2.2-all-languages.tar.gz
sudo tar -xvzf phpMyAdmin-5.2.2-all-languages.tar.gz
sudo rm -f phpMyAdmin-5.2.2-all-languages.tar.gz
sudo mv phpMyAdmin-* phpmyadmin
cd /var/www/html/phpmyadmin
sudo cp config.sample.inc.php config.inc.php

# Modify the phpMyAdmin config file to connect to RDS MySQL
sudo sed -i "s/\$cfg\['Servers'\]\[\$i\]\['host'\] = 'localhost';/\$cfg\['Servers'\]\[\$i\]\['host'\] = 'RDS_ENDPOINT_ID';/" /var/www/html/phpmyadmin/config.inc.php
sudo sed -i "s/\$cfg\['Servers'\]\[\$i\]\['auth_type'\] = 'cookie';/\$cfg\['Servers'\]\[\$i\]\['auth_type'\] = 'http';/" /var/www/html/phpmyadmin/config.inc.php

# Start the httpd service
sudo systemctl start httpd

# Enable the services to start on boot
sudo systemctl enable httpd

# Set basic permissions for /var/www directory
sudo chown -R apache:apache /var/www
sudo chmod -R 0770 /var/www
"""
