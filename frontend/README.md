# ACI Frontend

## What is included

- A login page in Vite + React
- A logged-in dashboard shell
- A top navbar with 3 placeholder entries: `Option 1`, `Option 2`, `Option 3`
- A logout button with a Font Awesome icon
- A profile interface for editing `user_data`
- Font Awesome installed through `@fortawesome/fontawesome-free`

## Login behavior

- The login form now calls the Flask backend endpoint `/api/auth/login`
- Vite dev server proxies `/api/*` requests to `http://127.0.0.1:5011`
- Login state is stored in `localStorage` as `aci-access-token` and `aci-user`
- On page load, the app calls `/api/auth/me` to restore the session
- Clicking logout clears the stored session and returns to the login page
- Profile updates are sent to `PATCH /api/auth/profile`
- Password changes require both `current_password` and `new_password`

## Main files

- [`src/App.jsx`](/home/utba/flaskapp/ACI/frontend/src/App.jsx)
- [`src/App.css`](/home/utba/flaskapp/ACI/frontend/src/App.css)
- [`src/index.css`](/home/utba/flaskapp/ACI/frontend/src/index.css)
- [`src/main.jsx`](/home/utba/flaskapp/ACI/frontend/src/main.jsx)

## Run locally

```bash
cd /home/utba/flaskapp/ACI/frontend
npm install
npm run dev
```

Backend must be running at the same time:

```bash
cd /home/utba/flaskapp/ACI/backend
. .venv/bin/activate
python run.py
```

## Build

```bash
cd /home/utba/flaskapp/ACI/frontend
npm run build
```

## Notes

- The current navbar icons are placeholders and can be replaced with your real menu items later
- Default backend login is `admin / admin123` unless you changed it in the backend
