# HYOXEN — Python Flask Web App

A full-stack version of the Hyoxen website built with Python (Flask) + SQLite.
Everything the static HTML version has, plus:

- Dynamic product pages for every vehicle
- Working lead-capture forms (investor, dealer, fleet, rider, contact)
- SQLite database that stores every submission
- Live stats API for the homepage counters
- Newsletter signup
- Admin panel to view leads at `/admin/leads`
- Auto-generated `sitemap.xml` and `robots.txt`

---

## 1. Quick Start (5 minutes)

### Step 1 — Install Python
You need Python 3.9 or newer. Check with:
```bash
python3 --version
```
If you don't have it: download from https://python.org

### Step 2 — Install Flask
From inside the `hyoxen-python` folder:
```bash
pip install -r requirements.txt
```
or:
```bash
pip install Flask
```

### Step 3 — Run it
```bash
python app.py
```

You'll see:
```
============================================================
  HYOXEN — Mobility, Rewired
  Server running at http://localhost:5000
  Admin panel:      http://localhost:5000/admin/leads
============================================================
```

Open **http://localhost:5000** in your browser. Done.

---

## 2. What's where

```
hyoxen-python/
├── app.py                        # Flask app — routes, database, forms
├── requirements.txt              # Python dependencies
├── hyoxen.db                     # SQLite database (auto-created on first run)
├── README.md                     # This file
│
├── templates/                    # HTML templates (Jinja2)
│   ├── base.html                 # Shared layout (nav, footer, CSS link)
│   ├── index.html                # Homepage
│   ├── vehicles.html             # Vehicle listing
│   ├── product.html              # Individual product page (used by all 5)
│   ├── zaptap.html               # Charging network page
│   ├── os.html                   # Fleet OS / SaaS page
│   ├── dealers.html              # Dealer application form
│   ├── investors.html            # Investor brief request
│   ├── exports.html              # Global markets
│   ├── contact.html              # Contact page
│   ├── admin.html                # Lead management dashboard
│   ├── 404.html, 500.html        # Error pages
│   └── partials/                 # Reusable components (SVGs)
│
└── static/
    ├── css/hyoxen.css            # All styling
    ├── js/hyoxen.js              # Cursor, animations, form handlers
    └── images/                   # Drop your product photos here
```

---

## 3. URL Routes

| URL | Purpose |
|---|---|
| `/` | Homepage |
| `/vehicles` | Full vehicle lineup |
| `/vehicles/electrax` | Individual product page |
| `/vehicles/voltiva` | etc. |
| `/zaptap` | Charging network |
| `/os` | Hyoxen OS platform |
| `/dealers` | Become a partner form |
| `/investors` | Investor relations |
| `/exports` | Global expansion |
| `/contact` | Contact page |
| `/admin/leads` | Internal lead dashboard ⚠️ add auth before going live |
| `/api/lead` | POST — universal lead submission |
| `/api/subscribe` | POST — newsletter signup |
| `/api/stats` | GET — live counters JSON |
| `/sitemap.xml` | SEO sitemap |
| `/robots.txt` | Robots policy |

---

## 4. Editing content (no Python required for most things)

### Change product specs, names, prices
Open `app.py` and edit the `PRODUCTS` dictionary near the top. Each product has `name`, `tagline`, `specs`, `features`, `price_from`. Save the file — Flask auto-reloads.

### Change investor numbers
Edit the `INVESTOR_NUMBERS` list in `app.py`.

### Change export markets
Edit the `EXPORT_MARKETS` list in `app.py`.

### Change page text
Open the relevant template in `templates/` (e.g., `index.html` for homepage) and edit the text between HTML tags. The base layout (nav, footer) lives in `templates/base.html`.

### Adding real product photos
1. Drop your optimized images into `static/images/` (e.g., `electrax.webp`)
2. Open `templates/partials/product_svg_electrax.html`
3. Replace the entire `<svg>...</svg>` with:
   ```html
   <img src="{{ url_for('static', filename='images/electrax.webp') }}"
        alt="ElectraX" style="max-width:240px; width:100%;" />
   ```
4. Repeat for each vehicle

### Change colors
Open `static/css/hyoxen.css` — first 15 lines define the entire color system. Change `--ion: #00D4FF;` to any hex code and the brand color updates everywhere.

---

## 5. Viewing captured leads

Visit **http://localhost:5000/admin/leads** to see every form submission and newsletter signup, newest first.

⚠️ **Before going live:** the admin page has no password. Add Flask-Login or HTTP basic auth before deploying publicly.

---

## 6. Sending email notifications when a lead arrives

Open `app.py`, scroll to the `send_lead_email` function (commented out at the bottom). Uncomment it. Set these environment variables before running:

```bash
export SMTP_USER="youremail@gmail.com"
export SMTP_PASS="your-app-password"   # Gmail → Settings → App Passwords
python app.py
```

Then uncomment the line `# send_lead_email(...)` inside the `submit_lead` route.

---

## 7. Going to production

This Flask app is built to deploy on any Python host. Here are the easiest options:

### Option A — Render.com (recommended, free tier available)
1. Push code to GitHub
2. Sign up at render.com → New → Web Service → connect GitHub
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add `gunicorn==21.2.0` to `requirements.txt` first
6. Render gives you a free `*.onrender.com` URL — point your domain to it

### Option B — Railway.app
1. Push to GitHub
2. railway.app → New Project → Deploy from GitHub
3. Add `Procfile` containing: `web: gunicorn app:app`
4. Auto-detects Python, deploys in 90 seconds

### Option C — PythonAnywhere (easiest, no GitHub needed)
1. pythonanywhere.com → free account
2. Upload the entire `hyoxen-python` folder
3. Web tab → Add new web app → Flask → point to `app.py`

### Option D — Fly.io (developer-friendly, free tier)
```bash
brew install flyctl
fly launch
fly deploy
```

### For all production deployments:
1. Set `app.config['SECRET_KEY']` via environment variable, not hardcoded
2. Set `debug=False` in `app.py`
3. Use PostgreSQL instead of SQLite if expecting heavy traffic
4. Add HTTPS (automatic on Render/Railway/Fly)
5. Add authentication to `/admin/leads`

---

## 8. Troubleshooting

**`ModuleNotFoundError: No module named 'flask'`**
→ Run `pip install Flask`

**`Address already in use`**
→ Port 5000 is taken. Run `python app.py` after changing the port at the bottom of `app.py` to e.g. `port=8000`

**Browser shows "This site can't be reached"**
→ Make sure `python app.py` is still running in your terminal. Don't close it.

**Forms submit but nothing happens visually**
→ Open browser dev tools (F12) → Console tab — JavaScript errors will show here. Network tab shows whether `/api/lead` is being called.

**Database errors**
→ Delete `hyoxen.db` and restart `python app.py` — it'll re-create the schema.

---

## 9. Common changes — recipe book

### Add a new product
1. In `app.py`, add a new entry to the `PRODUCTS` dictionary following the same format
2. Create `templates/partials/product_svg_yournewslug.html` with an SVG illustration
3. Done — the page auto-generates at `/vehicles/yournewslug`

### Add a new page
1. Create `templates/yourpage.html`
2. In `app.py`, add:
   ```python
   @app.route('/yourpage')
   def yourpage():
       return render_template('yourpage.html')
   ```

### Get a CSV export of leads
Add to `app.py`:
```python
import csv
from flask import Response

@app.route('/admin/leads.csv')
def export_leads():
    conn = get_db()
    leads = conn.execute('SELECT * FROM leads ORDER BY created_at DESC').fetchall()
    conn.close()

    def generate():
        yield 'id,audience,name,email,phone,company,message,source,created_at\n'
        for r in leads:
            yield f'{r["id"]},{r["audience"]},"{r["name"] or ""}","{r["email"]}","{r["phone"] or ""}","{r["company"] or ""}","{(r["message"] or "").replace(chr(34), "")}","{r["source"] or ""}",{r["created_at"]}\n'

    return Response(generate(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=hyoxen-leads.csv'})
```

Then visit `/admin/leads.csv` to download.

---

## 10. Need help?

This is a complete, working application. If you want changes:
- New page → tell me what it should contain
- Real photos → drop them into `static/images/`, tell me which file to swap
- Custom features → describe what you need

— Built for Hyoxen Vehicle Technology Pvt. Ltd. · Mobility, Rewired.
