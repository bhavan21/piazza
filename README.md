# Piazza like application for Database and Informatics Lab Project
![Python](https://img.shields.io/badge/Python-3.5.2-brightgreen.svg)
![Django](https://img.shields.io/badge/Django-1.11.6-brightgreen.svg)

## About
> This project aims at creating a piazza like application using django backend server

## Creating environment
> It is always preferable to use virtual environments when doing proects based on python
```
pip3 install virtualenv
virtualenv fordis
cd fordis/bin
source activate
```

## Installations

Install django 1.11.6 from terminal :
```
pip3 install django=1.11.6
```
Install django_extensions:
```
pip install django_extensions
```
## Directory Structure
```
|--class
    |--static           # contains all static files like js and css 
    |--templates/class  # contains all html templates for application class
    |--admin.py         # admin configuration
    |--apps.py          # app configuration
    |--models.py        # models is the schema of database
    |--tests.py         # this can be used for automatic testing
    |--urls.py          # url redirection which came into app 'class' are handled here
    |--views.py         # views are the functions which handle logic for all urls
|--piazza
    |--settings.py      # app settings are handled here
    |--urls.py          # url entering the host address are first captured here and redirected
    |--wsgi.py          # starting point of the website is here for server
|--manage.py            # it sets all variables required like middleware, allowed_hosts etc..
|--dbsqlite.3           # The very own database of he project  
```

### Starting address of project
Try accessing 'hostaddress:port/class'
