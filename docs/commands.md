# Good Django Commands to know:

`python manage.py runserver`
- command to start the dev server on localhost

`python manage.py makemigrations`
- "commit" database schema changes

`python manage.py migrate`
- apply changes to postgres schema

`python manage.py dbshell`
- opens postgres interactive shell with django specified user

`\conninfo`
- check which user when you are in interactive postgres shell

# custom commands

`python manage.py create_user {--admin}{username} {password} {email}`
- creates a new django user with the specified parameters (--admin flag indicates superuser)