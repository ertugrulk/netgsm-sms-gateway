# netgsm-sms-gateway
NetGSM SMS Gateway is a WSGI application written in Python that sends e-mail once it receives API call from NetGSM's Servers. 

### Requirements:
* Python 2.7
* mod_wsgi
* Apache (or nginx)
* A functioning NetGSM account

### 
### How to install on Apache:
1 -  Set up your site like so;

>    vim /etc/apache2/sites-available/smssubdomain-yourdomain-com.conf


And copy the following into the file and then make the changes such as /var/www/path-to-your-application
```
<VirtualHost *:80>
	ServerName smssubdomain.yourdomain.com
	ServerAdmin info@yourdomain.com
	DocumentRoot /var/www/path-to-your-application
  ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined
  WSGIScriptAlias / /var/www/path-to-your-application/smsgateway.wsgi
  <Directory /var/www/sms.ertugrulk.me/>
    Order deny,allow
    Allow from all
  </Directory>
</VirtualHost>
```
2 -  Clone the git repository to the application path
```
cd /var/www/path-to-your-application/
git clone https://github.com/ertugrulk/netgsm-sms-gateway/
cp netgsm-sms-gateway/* ./
```
3 -  Configuration. Edit the configuration file:

>   vim config.cfg


```
[SMTP]
username = test@gmail.com
password = MySuperSecretPass55
host = smtp.gmail.com
port = 465
usessl = 1
[Prefs]
destinationemail = test@gmail.com
emailsubject = SMS FROM $sender
emailtext = Received from $sender at $datetime: $message
```

* If the SMTP Server does not support SSL, change usessl to "0" (zero without quotes). 
* Variables that you can use in "emailsubject" and "emailtext" include: $sender, $datetime and $message. 
You may change it how you wish.

4 - Enter the application path to the script.

>	vim smsgateway.wsgi

After the ```def application(environ, start_response):``` line, change the variable appath to the script's path
```
	apppath = "/var/www/path-to-your-application/"
```
5 - Reload apache
```
sudo a2ensite smssubdomain-yourdomain-com
sudo service apache2 reload
```
6 -  Set up your NetGSM account so as to forward incoming SMS to your web server
 In the API settings pane, click Forward incoming SMS (Gelen SMS'i Yonlendir), enter your URL and then click Save.



