[![forthebadge](https://forthebadge.com/images/badges/cc-0.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
# SoftDesk

(This is an exercize project for OpenClassRooms)

SoftDest is an API Restfull to manage Project grouping Issue, where User can post Comments on these Issue.

## Local installation
You will need Python and Git installed on your device.
1. Import the SoftDest API sources  
`git clone https://github.com/firgon/P10`


2. Install requirements  
From your installation folder (P10):   
`pip install -r requirements.txt`

3. Add your Django Secret Key   
In your installation folder (P10) add a file named .env
with one line :   
SECRET_KEY = '<your_django_secret_key>'   
(you can generate a django secret key with tools like : https://miniwebtool.com/fr/django-secret-key-generator/)

## Tests
You can check everything is ok by :
1. Launching tests  
From your installation folder (P10):  
`python manage.py test`


## Usage
1. Launch Server
From your installation folder (P10):  
`python manage.py runserver`
   

2. Enjoy the API !   
You can access the complete URIs documentation on Postman: 
[here](https://documenter.getpostman.com/view/21659102/2s8YY9wScu)


## Technologies
- Python

## Authors

Our code squad : Firgon
