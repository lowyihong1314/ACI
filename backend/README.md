# ACI Backend

## Runtime

- Debug API: `0.0.0.0:5011`
- Production API: `0.0.0.0:5012`
- Database: MariaDB `aci_db`

## Database config

Current connection is defined in [`backend/.env`](/home/utba/flaskapp/ACI/backend/.env):

```env
DATABASE_URL=mysql+pymysql://yukang:Lowyihong123@127.0.0.1:3306/aci_db?charset=utf8mb4
```

If MariaDB is on another host or port, update `DATABASE_URL` in `.env`.

## Setup

```bash
cd /home/utba/flaskapp/ACI/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Alembic

Migration config lives in:

- [`backend/alembic.ini`](/home/utba/flaskapp/ACI/backend/alembic.ini)
- [`backend/migrations/env.py`](/home/utba/flaskapp/ACI/backend/migrations/env.py)
- [`backend/migrations/versions/20260310_0001_create_user_data.py`](/home/utba/flaskapp/ACI/backend/migrations/versions/20260310_0001_create_user_data.py)

Run migrations:

```bash
cd /home/utba/flaskapp/ACI/backend
. .venv/bin/activate
alembic upgrade head
```

Create a new migration after model changes:

```bash
cd /home/utba/flaskapp/ACI/backend
. .venv/bin/activate
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
```

## Run

Debug:

```bash
cd /home/utba/flaskapp/ACI/backend
source .venv/bin/activate
python run.py
```

Production with Gunicorn:

```bash
cd /home/utba/flaskapp/ACI/backend
source .venv/bin/activate
gunicorn -w 2 -b 0.0.0.0:5012 gunicorn_run:app
```

## Default admin

- Username: `admin`
- Password: `admin123`

The default admin is inserted by the app on startup if it does not already exist.

## Profile API

- `GET /api/auth/profile`
  Returns the current logged-in user's `user_data`
- `PATCH /api/auth/profile`
  Updates `username`, `full_name`, `email`
- Password change is also handled by `PATCH /api/auth/profile`
  Send `current_password` and `new_password` together
