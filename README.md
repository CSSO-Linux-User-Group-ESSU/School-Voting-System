# CCS-Voting
A voting system for CCS.

# Setting up github in terminal 
[Setting up your account](https://docs.github.com/en/get-started/quickstart/set-up-git)

# Cloning
1. Run `git clone --branch contrib https://github.com/Linux-User-Group-ESSU/CCS-Voting.git`

# After cloning the repo run on terminal:
1. `cd CCS-Voting`
2. Create a virtual environment
     `pip install venv`
     `python3 -m venv .venv`
3. Activate Virtual environment
     `source .venv/bin/activate`
4. Install requirements.txt
     `pip install -r requirements.txt`
5. Create the migration\
    `python3 manage.py makemigrations`\
6. Migrate\
    `python3 manage.py migrate`\
7. Run the server\
    `python3 manage.py runserver`\

# Deployment
1. Set the DEBUG to `False` in e_votinh/settings.py
2. Add your IP Address to `ALLOWED_HOST` in e_voting/settings/py
3. run `python manage.py collectstatic`
4. run `python3 manage.py runserver IP_ADDRESS:PORT`
