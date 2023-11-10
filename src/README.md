# cdd-backend-benin

Run the App
`cd cdd-backend-benin/src`

## Setup

Set Python environment (use python 3)
`python3 -m venv venv`

Activate Python Environment
`source venv/bin/activate`

Install application

- `pip install -r requirements.txt`
- `pip install -r requirements.dev.txt`

Start Application

- Create a local environment file (customize according to your needs) from the provided template: `cp cdd/example.env cdd/.env`. For example fill database credentials
- `python3 manage.py migrate`
- `python3 manage.py runserver`
