# My Catalog 3000

## Introduction

Simple and useful catalog management

# How to use it

- The catalog is visible to any user without an account.
- To be able to create, edit and delete you need an account on Facebook, no need to create a new account on the catalog itself.
- The links to the options create,edit,delete on catalogs and items are available only to currently logged users
- To create an account simple login with your Facebook account and let know the system you are given access to your basic profile in Facebook.

# The server

1. Server address is 172.245.179.199
2. To access the server use SSH on port 2200 with the key provided.
3. To access via browser goto http://172.245.179.199/
4. After the server was deployed , we need to make a few changes to update an secure it:
  a) Update system packages
  b) Activate and configure UFW (firewall) 
  c) Change default SSH port
  d) Configure port 80 to server our catalog
  e) Activate port NTP
  f) Deactivate root access
  g) Deactiveate password access, enforcing key-based authentication
  h) Give user(not root) access to run the server
  
4. Our server uses Apache, WSGI, Python, Flask, SQLAlchemy and Postgress as database engine

NOTES:
- To run the python server, apache must not be running
- To run the catalog server use the command : sudo python project.py
- Only users signed in are able to do create and make changes on items and catalogs.
- Only owners(creator)of the catalog or items have the right to edit or delete them.
- For a cross site needs, the catalog provides a JSON structure information:

# Support
- if you have any questions on how to use the blog or with the installation don't doubt to contact us at omarruben@hotmail.com  

"# Udacity-catalog" 
