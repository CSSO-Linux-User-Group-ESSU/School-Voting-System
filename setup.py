import os
import subprocess

# os.system("python3 -m venv .venv")
curren_dir = os.path.dirname(os.path.abspath(__file__))
virtual_env = os.path.join(curren_dir, ".venv/bin/activate")
subprocess.run(f"""
                bash -c 'source {virtual_env} &&
                pip install -r requirements.txt &&
                python manage.py makemigrations account &&
                python manage.py makemigrations administrator &&
                python manage.py makemigrations voting && 
                python manage.py migrate
                '""", shell=True)   
