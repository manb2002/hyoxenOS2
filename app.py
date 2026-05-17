"""
Hyoxen Vehicle Technology — Flask Web Application
==================================================
A futuristic EV mobility website with:
- Dynamic product pages
- Lead capture forms (investor, dealer, fleet, rider)
- SQLite database for leads & newsletter subscribers
- Live stats API (vehicles, km, CO2)
- SEO-friendly routing
- Email-ready form handling

Run locally:
    python app.py

Then visit: http://localhost:5000
"""

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash, send_from_directory
)
from datetime import datetime
import sqlite3
import os
import random
from pathlib import Path

# ------------------------------------------------------------
# App Configuration
# ------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hyoxen-dev-key-change-in-production')

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'hyoxen.db'


# ------------------------------------------------------------
# Database Setup
# ------------------------------------------------------------
def get_db():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with all required tables."""
    conn = get_db()
    cur = conn.cursor()

    # Leads table — all form submissions land here
    cur.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audience TEXT NOT NULL,
            name TEXT,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            message TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Newsletter subscribers
    cur.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Live counters — for the homepage intelligence section
    cur.execute('''
        CREATE TABLE IF NOT EXISTS counters (
            key TEXT PRIMARY KEY,
            value INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed initial counter values if empty
    cur.execute('SELECT COUNT(*) FROM counters')
    if cur.fetchone()[0] == 0:
        seed = [
            ('vehicles_streaming', 12847),
            ('battery_cells', 6200000),
            ('km_today', 84310),
            ('co2_avoided', 312),
            ('active_stations', 412),
            ('swaps_this_month', 84210),
        ]
        cur.executemany('INSERT INTO counters (key, value) VALUES (?, ?)', seed)

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# Product Data — central source of truth
# ------------------------------------------------------------
PRODUCTS = {
    'electrax': {
        'slug': 'electrax',
        'name': 'ElectraX',
        'category': 'SCOOTER · URBAN',
        'tagline': 'Built for the daily commute, wired for the city.',
        'description': (
            'A smart electric scooter engineered for India\'s busiest streets. '
            'Real-time GPS, swappable battery, app-paired, and quiet — '
            'ElectraX is the daily companion the city has been waiting for.'
        ),
        'index': '01 / 05',
        'image': 'electrax.webp',
        'specs': [
            {'value': '140', 'unit': 'km', 'label': 'Range'},
            {'value': '85', 'unit': 'kmph', 'label': 'Top Speed'},
            {'value': '90', 'unit': 's', 'label': 'Swap Time'},
        ],
        'features': [
            'GPS Live Tracking', 'Smart BMS', 'Swappable Battery',
            'OTA Updates', 'Anti-theft', 'Mobile App Pairing',
        ],
        'price_from': '₹1,24,999',
        'color': '#00D4FF',
    },
    'voltiva': {
        'slug': 'voltiva',
        'name': 'Voltiva',
        'category': 'COMMUTER · DAILY',
        'tagline': 'Range that respects your routine.',
        'description': (
            'The everyday electric — for the commute that never stops. '
            'Voltiva delivers reliable range, predictable performance, '
            'and the same intelligence stack as the rest of the fleet.'
        ),
        'index': '02 / 05',
        'image': 'voltiva.webp',
        'specs': [
            {'value': '110', 'unit': 'km', 'label': 'Range'},
            {'value': '65', 'unit': 'kmph', 'label': 'Top Speed'},
            {'value': '120', 'unit': 'kg', 'label': 'Payload'},
        ],
        'features': [
            'GPS Live Tracking', 'Smart BMS', 'Swappable Battery',
            'OTA Updates', 'Step-through Frame', 'Mobile App Pairing',
        ],
        'price_from': '₹89,999',
        'color': '#8A6CFF',
    },
    '5e-cargomaster': {
        'slug': '5e-cargomaster',
        'name': '5E CargoMaster',
        'category': 'CARGO · LAST MILE',
        'tagline': 'Last mile, fully telemetered.',
        'description': (
            'Engineered for the route, the driver, and the spreadsheet. '
            'CargoMaster pairs 500kg payload capacity with live diagnostics '
            'and uptime guarantees — purpose-built for delivery fleets.'
        ),
        'index': '03 / 05',
        'image': 'cargomaster.webp',
        'specs': [
            {'value': '180', 'unit': 'km', 'label': 'Range'},
            {'value': '500', 'unit': 'kg', 'label': 'Payload'},
            {'value': 'IP67', 'unit': '', 'label': 'Rating'},
        ],
        'features': [
            'Fleet Telemetry', 'Driver Scoring', 'Geofencing',
            'Route Optimization', 'IP67 Weatherproof', 'Cargo Lock',
        ],
        'price_from': '₹2,49,999',
        'color': '#00D4FF',
    },
    'electra': {
        'slug': 'electra',
        'name': 'Electra',
        'category': 'SCOOTER · CLASSIC',
        'tagline': 'The original ride. Quietly reinvented.',
        'description': (
            'A classic-styled electric scooter for riders who want the silhouette '
            'they grew up with, paired with the intelligence stack of a new generation. '
            'Comfortable seat, generous storage, and a quiet drivetrain.'
        ),
        'index': '04 / 05',
        'image': 'electra.webp',
        'specs': [
            {'value': '120', 'unit': 'km', 'label': 'Range'},
            {'value': '70', 'unit': 'kmph', 'label': 'Top Speed'},
            {'value': '90', 'unit': 's', 'label': 'Swap Time'},
        ],
        'features': [
            'GPS Live Tracking', 'Smart BMS', 'Swappable Battery',
            'Wide Comfort Seat', 'Large Underseat Storage', 'Mobile App Pairing',
        ],
        'price_from': '₹99,999',
        'color': '#8A6CFF',
    },
    'zaptap': {
        'slug': 'zaptap',
        'name': 'ZapTap',
        'category': 'INFRA · CHARGING',
        'tagline': 'Swap in ninety seconds. Anywhere.',
        'description': (
            'India\'s first AI-routed swappable battery network. '
            '90-second swaps. Solar-ready stations. Open to fleets. '
            'The grid that thinks ahead of you.'
        ),
        'index': '05 / 05',
        'image': None,  # ZapTap uses the animated SVG station illustration
        'specs': [
            {'value': '90', 'unit': 's', 'label': 'Swap Time'},
            {'value': '14', 'unit': '', 'label': 'Cities Live'},
            {'value': '24/7', 'unit': '', 'label': 'Uptime'},
        ],
        'features': [
            'AI Route Optimization', 'Solar Compatible', 'Fleet API',
            'Real-time Availability', 'Cashless Swap', 'Climate Controlled',
        ],
        'price_from': 'Subscription',
        'color': '#3AF0B0',
    },
}

# Export markets data
EXPORT_MARKETS = [
    {'idx': '01', 'country': 'Kenya', 'city': 'Nairobi', 'status': 'live'},
    {'idx': '02', 'country': 'Indonesia', 'city': 'Jakarta', 'status': 'live'},
    {'idx': '03', 'country': 'Bangladesh', 'city': 'Dhaka', 'status': 'live'},
    {'idx': '04', 'country': 'Nepal', 'city': 'Kathmandu', 'status': 'live'},
    {'idx': '05', 'country': 'Brazil', 'city': 'São Paulo', 'status': 'pilot'},
    {'idx': '06', 'country': 'Nigeria', 'city': 'Lagos', 'status': 'pilot'},
    {'idx': '07', 'country': 'Vietnam', 'city': 'Hanoi', 'status': 'planned'},
]

# Investor headline numbers
INVESTOR_NUMBERS = [
    {'value': '12', 'sup': 'K+', 'label': 'Vehicles<br>On Road'},
    {'value': '28', 'sup': '', 'label': 'States<br>Served'},
    {'value': '5', 'sup': '', 'label': 'Products<br>Shipping'},
    {'value': '62', 'sup': '%', 'label': 'Women-Led<br>Dealers'},
    {'value': '9.4', 'sup': '★', 'label': 'Customer<br>NPS'},
    {'value': '9', 'sup': '', 'label': 'Countries<br>Targeted'},
]


# ------------------------------------------------------------
# Routes — Public Pages
# ------------------------------------------------------------
@app.route('/')
def home():
    """Homepage — the cinematic 90-second scrolled film."""
    return render_template(
        'index.html',
        products=PRODUCTS,
        markets=EXPORT_MARKETS,
        numbers=INVESTOR_NUMBERS,
    )


@app.route('/vehicles')
def vehicles_index():
    """Listing of all vehicles."""
    return render_template('vehicles.html', products=PRODUCTS)


@app.route('/vehicles/<slug>')
def vehicle_detail(slug):
    """Individual product page."""
    product = PRODUCTS.get(slug)
    if not product:
        return render_template('404.html'), 404
    # Sibling products for the "compare" section
    siblings = {k: v for k, v in PRODUCTS.items() if k != slug}
    return render_template('product.html', product=product, siblings=siblings)


@app.route('/zaptap')
def zaptap():
    """Charging ecosystem page."""
    return render_template('zaptap.html')


@app.route('/os')
def os_page():
    """Hyoxen OS SaaS platform page."""
    return render_template('os.html')


@app.route('/dealers')
def dealers():
    """Become-a-partner page."""
    return render_template('dealers.html')


@app.route('/investors')
def investors():
    """Investor relations page."""
    return render_template('investors.html', numbers=INVESTOR_NUMBERS)


@app.route('/exports')
def exports():
    """Global expansion / export programs."""
    return render_template('exports.html', markets=EXPORT_MARKETS)


@app.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')


# ------------------------------------------------------------
# Routes — Forms
# ------------------------------------------------------------
@app.route('/api/lead', methods=['POST'])
def submit_lead():
    """Universal lead capture — investor, dealer, fleet, rider."""
    data = request.get_json() if request.is_json else request.form

    audience = data.get('audience', 'general')
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    company = data.get('company', '').strip()
    message = data.get('message', '').strip()
    source = data.get('source', 'homepage')

    if not email or '@' not in email:
        return jsonify({'ok': False, 'error': 'Valid email required'}), 400

    conn = get_db()
    conn.execute(
        '''INSERT INTO leads (audience, name, email, phone, company, message, source)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (audience, name, email, phone, company, message, source)
    )
    conn.commit()
    conn.close()

    # In production: send email notification here (see send_lead_email below)
    # send_lead_email(audience, name, email, phone, company, message)

    return jsonify({
        'ok': True,
        'message': f'Thank you. The Hyoxen {audience} team will be in touch within 24 hours.'
    })


@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Newsletter signup."""
    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '').strip().lower()

    if not email or '@' not in email:
        return jsonify({'ok': False, 'error': 'Valid email required'}), 400

    try:
        conn = get_db()
        conn.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        conn.close()
        return jsonify({'ok': True, 'message': 'Subscribed to the Hyoxen Quarterly.'})
    except sqlite3.IntegrityError:
        # Already subscribed — no-op, return success
        return jsonify({'ok': True, 'message': 'You\'re already on the list.'})


# ------------------------------------------------------------
# Routes — Live Data API
# ------------------------------------------------------------
@app.route('/api/stats')
def stats():
    """
    Live homepage counters.
    In production this would pull from real telemetry.
    For now, base values + small random drift to feel 'live'.
    """
    conn = get_db()
    rows = conn.execute('SELECT key, value FROM counters').fetchall()
    conn.close()

    base = {row['key']: row['value'] for row in rows}

    # Add live drift so numbers feel real
    return jsonify({
        'vehicles_streaming': base['vehicles_streaming'] + random.randint(0, 25),
        'battery_cells': base['battery_cells'] + random.randint(0, 5000),
        'km_today': base['km_today'] + random.randint(50, 200),
        'co2_avoided': base['co2_avoided'],
        'active_stations': base['active_stations'],
        'swaps_this_month': base['swaps_this_month'] + random.randint(10, 80),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
    })


# ------------------------------------------------------------
# Routes — SEO & Utility
# ------------------------------------------------------------
@app.route('/sitemap.xml')
def sitemap():
    """Dynamic XML sitemap for SEO."""
    base_url = request.url_root.rstrip('/')
    pages = [
        '/', '/vehicles', '/zaptap', '/os', '/dealers',
        '/investors', '/exports', '/contact'
    ]
    pages += [f'/vehicles/{slug}' for slug in PRODUCTS.keys()]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += f'  <url><loc>{base_url}{page}</loc></url>\n'
    xml += '</urlset>'

    return xml, 200, {'Content-Type': 'application/xml'}


@app.route('/robots.txt')
def robots():
    base_url = request.url_root.rstrip('/')
    return (
        f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n",
        200,
        {'Content-Type': 'text/plain'}
    )


# ------------------------------------------------------------
# Admin (basic — protect with auth in production)
# ------------------------------------------------------------
from functools import wraps
from flask import Response

def check_admin_auth(username, password):
    """Validate admin credentials against environment variables."""
    expected_user = os.environ.get('ADMIN_USER', 'admin')
    expected_pass = os.environ.get('ADMIN_PASS', 'change-me-in-production')
    return username == expected_user and password == expected_pass


def require_admin(f):
    """Decorator: require HTTP basic auth for admin routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_admin_auth(auth.username, auth.password):
            return Response(
                'Authentication required.',
                401,
                {'WWW-Authenticate': 'Basic realm="Hyoxen Admin"'}
            )
        return f(*args, **kwargs)
    return decorated


@app.route('/admin/leads')
@require_admin
def admin_leads():
    """View all captured leads. Protected by HTTP basic auth."""
    conn = get_db()
    leads = conn.execute(
        'SELECT * FROM leads ORDER BY created_at DESC LIMIT 200'
    ).fetchall()
    subs = conn.execute(
        'SELECT * FROM subscribers ORDER BY created_at DESC LIMIT 200'
    ).fetchall()
    conn.close()
    return render_template('admin.html', leads=leads, subscribers=subs)


# ------------------------------------------------------------
# Error Handlers
# ------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ------------------------------------------------------------
# Optional: Email notification (uncomment + configure SMTP)
# ------------------------------------------------------------
# import smtplib
# from email.mime.text import MIMEText
#
# def send_lead_email(audience, name, email, phone, company, message):
#     smtp_user = os.environ.get('SMTP_USER')
#     smtp_pass = os.environ.get('SMTP_PASS')
#     if not smtp_user:
#         return
#     body = f"""New Hyoxen lead ({audience}):
#     Name: {name}
#     Email: {email}
#     Phone: {phone}
#     Company: {company}
#     Message: {message}
#     """
#     msg = MIMEText(body)
#     msg['Subject'] = f'New {audience} lead — {name or email}'
#     msg['From'] = smtp_user
#     msg['To'] = 'hello@hyoxen.com'
#     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
#         s.login(smtp_user, smtp_pass)
#         s.send_message(msg)


# ------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------
# Initialize database immediately so it works under gunicorn (production) too
init_db()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    print('=' * 60)
    print('  HYOXEN — Mobility, Rewired')
    print(f'  Server running at http://localhost:{port}')
    print(f'  Admin panel:      http://localhost:{port}/admin/leads')
    print('=' * 60)
    app.run(debug=debug, host='0.0.0.0', port=port)
