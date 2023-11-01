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
   a. linux: `python3 manage.py makemigrations`\
   b. Windows: `python manage.py makemigrations`\
   c. MacOs: `Mali ka ada han im nakadian`
6. Migrate\
   a. linux: `python3 manage.py migrate`\
   b. Windows: `python manage.py migrate`\
   c. MacOs: `Ano nga yadi ka pa???`
7. Run the server\
   a. linux: `python3 manage.py runserver`\
   b. Windows: `python3 manage.py runserver`\
   c. MacOs: `Wara didi kanan Mac. Uli nala!`
