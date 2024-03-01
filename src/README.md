# cdd-backend-benin

Run the App
`cd cdd-backend-benin/src`

## Setup

Set Python environment (use python 3)
`python3 -m venv venv`

Activate Python Environment
`source venv/bin/activate`

Upgrade pip
`pip install --upgrade pip`

Install application

- `pip install -r requirements.txt`
- `pip install -r requirements.dev.txt`

Start Application

- Create a local environment file (customize according to your needs) from the provided template: `cp cdd/example.env cdd/.env`. For example fill database credentials
- Do the same for `local_settings.py`: `cp cdd/local_settings_template.py cdd/local_settings.py` and update if needed.
- `python3 manage.py migrate`
- `python3 manage.py runserver`

Fist steps:

- Using the user interface, create the different project, phases, activities and tasks

- You can create agents using the interface too or use `save_agents_sc_csv_datas_to_db` and `save_agents_fc_csv_datas_to_db` from `authentication/functions.py`
