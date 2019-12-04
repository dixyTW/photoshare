# PhotoShare
WebApp that behaves similar to Tumblr

![Home Page](https://github.com/dixyTW/photoshare/blob/master/Screen%20Shot%202019-12-03%20at%2010.58.03%20PM.png)
![Photos](https://github.com/dixyTW/photoshare/blob/master/Screen%20Shot%202019-12-04%20at%202.01.03%20AM.png)

Guests may:
Browse photos

Users may:
Register for an account
Upload photos, add taggs to photos
Create Albums to store photos
Like/Comment other users photos
Add/Remove Friends
Look up photos by their hashtags

## Setup
First download required files with: 
```bash
pip install -r requirements.txt
```


MySQL
```bash
export PATH=${PATH}:/usr/local/mysql/bin #path is the path to your local MySQL file, lets cmd able to call mysql by using the command below:
```
Open a MySQL window:
```bash
mysql -u root -h 127.0.0.1 -p
```
In the MySQL window, use
```MySQL
source /Users/kangtungho/desktop/pa1_tunghokang/schema.sql;
```
to choose the database you want for PhotoShare and 
```MySQL
DROP DATABASE pa1;
```
to drop the database, make sure the name of the tables/filename is consistent with the one in app.py

Starting PhotoShare
Inside the directory where all files are located, run command: 
```bash
export FLASK_APP=app.py 
```
to compile the code and type in: 
```bash
flask run 
```
to start the application
