# My Catalog 3000

## Introduction

Simple and useful catalog management

# How to use it

- The catalog is visible to any user without an account.
- To be able to create, edit and delete you need an account on Facebook, no need to create a new account on the catalog itself.
- The links to the options create,edit,delete on catalogs and items are available only to currently logged users
- To create an account simple login with your Facebook account and let know the system you are given access to your basic profile in Facebook.

# Installation

# Setting up your Facebook App


1.- Due to the fast changed on technology Facebook uses, these instructions are always update and links are changed very often.

2.- Go to to https://developers.facebook.com/docs/apps/register

3.- Follow all instructions, create your app, update credentials.

4.- You need to get APP ID and SECRET , open the file fb_client_secrets.json and insert accordingly.

5.- On your Facebook app settings, you need to add and callback address, that should be the address of your server, on this case http://localhost:5000



# The server

1.- Server address is 172.245.179.199
2.- To access the server use SSH on port 2200 with the key provided.
3.- To access via browser goto http://172.245.179.199/
4.- If you wish you can populate the database with a basic-sample information with the command : python populatecatalog.py
4.- Up to this point your database is ready to be used run the command : python project.py
5.- You should see the message that your webserver is running under port 5000.
6.- Go to your browser and type : http://localhost:5000.

NOTES:
- Only users signed in are able to do create and make changes on items and catalogs.
- Only owners(creator)of the catalog or items have the right to edit or delete them.
- For a cross site needs, the catalog provides a JSON structure information:

  a) For the Full Catalog on the address http://localhost:5000/catalog/JSON
  b) For the details of the specific category : http://localhost:5000/catalog/[name of the category]>/JSON
  c) For the details of one specific item : http://localhost:5000/item/[name of item]/JSON
  


# Support
- if you have any questions on how to use the blog or with the installation don't doubt to contact us at omarruben@hotmail.com  
"# Udacity-catalog" 
