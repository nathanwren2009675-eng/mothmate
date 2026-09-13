from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from .models import MothSighting
from datetime import datetime
import calendar

# ========== SHARED STYLING ==========
NAVBAR = """
<div class="navbar">
    <a href="/" class="active">🏠 Home</a>
    <a href="/add/" class="add-link">🦋 Add Sighting</a>
    <a href="/records/" class="records-link">📋 My Records</a>
    <a href="/transfer/" class="transfer-link">📥 Legacy Import</a>
    <a href="/stats/" class="stats-link">📊 Statistics</a>
    <a href="/about/" class="about-link">ℹ️ About</a>
    <a href="/logout/" style="float:right">🔓 Log Out</a>
</div>
"""

NAVBAR_GUEST = """
<div class="navbar">
    <a href="/" class="active">🏠 Home</a>
    <a href="/about/">ℹ️ About</a>
    <a href="/login/" style="float:right">🔑 Log In</a>
    <a href="/signup/" style="float:right">✍️ Sign Up</a>
</div>
"""

STYLE = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
    body { background-color: #e8f5e9; min-height: 100vh; }
    .navbar { background-color: #2e7d32; overflow: hidden; padding: 0 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .navbar a { float: left; display: block; color: white; text-align: center; padding: 14px 16px; text-decoration: none; font-size: 15px; transition: background-color 0.3s; }
    .navbar a:hover { background-color: #4caf50; }
    .navbar a.active { background-color: #1b5e20; font-weight: bold; }
    .content { padding: 30px 20px; max-width: 100%; margin: 0 auto; }
    .content h1 { color: #1b5e20; margin-bottom: 15px; font-size: 32px; padding: 0 20px; }
    .search-box { background: white; padding: 20px; margin: 0 20px 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .search-row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    .search-group { flex: 1; min-width: 140px; }
    .search-group label { display: block; color: #2e7d32; font-weight: 600; margin-bottom: 4px; font-size: 13px; }
    .search-group input, .search-group select { width: 100%; padding: 8px; border: 2px solid #a5d6a7; border-radius: 6px; font-size: 14px; outline: none; }
    .search-group input:focus, .search-group select:focus { border-color: #2e7d32; }
    .search-btn { padding: 10px 24px; background-color: #2e7d32; color: white; border: none; border-radius: 6px; font-size: 15px; font-weight: bold; cursor: pointer; margin-top: 18px; }
    .search-btn:hover { background-color: #1b5e20; }
    .clear-btn { padding: 10px 24px; background-color: #757575; color: white; border: none; border-radius: 6px; font-size: 15px; font-weight: bold; cursor: pointer; margin-top: 18px; margin-left: 8px; }
    .clear-btn:hover { background-color: #424242; }
    .result-count { padding: 0 20px 12px; font-size: 16px; color: #2e7d32; }
    .form-box { max-width: 900px; margin: 20px auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
    .form-box h2 { color: #1b5e20; text-align: center; margin-bottom: 25px; }
    .form-row { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 0; }
    .form-group { flex: 1; min-width: 200px; }
    .form-group label { display: block; color: #2e7d32; font-weight: 600; margin-bottom: 6px; font-size: 14px; }
    .form-box input, .form-box textarea { width: 100%; padding: 10px; margin-bottom: 12px; border: 2px solid #a5d6a7; border-radius: 6px; font-size: 14px; outline: none; }
    .form-box input:focus, .form-box textarea:focus { border-color: #2e7d32; }
    .form-box button { width: 100%; padding: 14px; background-color: #2e7d32; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px; }
    .form-box button:hover { background-color: #1b5e20; }
    .error { color: #c62828; margin: 10px 0; text-align: center; }
    .success { color: #2e7d32; margin: 10px 0; text-align: center; font-weight: bold; }
    .info { color: #1565c0; margin: 10px 0; padding: 12px; background: #e3f2fd; border-radius: 6px; line-height: 1.6; font-size: 13px; }
    .skipped { color: #c62828; margin: 10px 0; padding: 12px; background: #ffebee; border-radius: 6px; max-height: 250px; overflow-y: auto; font-family: monospace; font-size: 12px; line-height: 1.4; }
    .table-wrapper { overflow-x: auto; margin: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .records-table { width: 100%; min-width: 1600px; border-collapse: collapse; background: white; }
    .records-table th { background-color: #2e7d32; color: white; padding: 10px 6px; text-align: left; font-size: 12.5px; white-space: nowrap; }
    .records-table td { padding: 8px 6px; border-bottom: 1px solid #e8f5e9; color: #2e7d32; font-size: 12.5px; white-space: nowrap; }
    .records-table tr:hover { background-color: #f1f8e9; }
    .delete-btn { background-color: #c62828; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: bold; }
    .delete-btn:hover { background-color: #b71c1c; }
    .delete-all-btn { background-color: #c62828; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin: 0 20px; }
    .delete-all-btn:hover { background-color: #b71c1c; }
</style>
"""

# ========== MONTH NAME CONVERTER ==========
def parse_month_str(month_text):
    """Convert 'january 2025' or 'jan 2025' or '01/2025' → (start_date, end_date)"""
    month_names = {
        'january':1, 'jan':1, 'february':2, 'feb':2, 'march':3, 'mar':3,
        'april':4, 'apr':4, 'may':5, 'june':6, 'jun':6,
        'july':7, 'jul':7, 'august':8, 'aug':8, 'september':9, 'sep':9, 'sept':9,
        'october':10, 'oct':10, 'november':11, 'nov':11, 'december':12, 'dec':12,
    }
    text = month_text.strip().lower()

    # Format: 01/2025
    if '/' in text and len(text.split('/')) == 2:
        m, y = text.split('/')
        try:
            month = int(m.strip())
            year = int(y.strip())
            if 1 <= month <= 12 and 2000 <= year <= 2100:
                last_day = calendar.monthrange(year, month)[1]
                return f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day}"
        except:
            pass

    # Format: "january 2025" or "jan 2025"
    for name, num in month_names.items():
        if text.startswith(name):
            try:
                year = int(text.replace(name, '').strip())
                if 2000 <= year <= 2100:
                    last_day = calendar.monthrange(year, num)[1]
                    return f"{year}-{num:02d}-01", f"{year}-{num:02d}-{last_day}"
            except:
                pass

    return None, None

# ========== ADVANCED DATE SEARCH PARSER ==========
def parse_date_search(search_text):
    """
    Supports:
    - Single month: '01/2025' or 'jan 2025' → whole month
    - Month range: 'jan 2025-jun 2025' or '01/2025-06/2025' → from start to end month
    Returns: (start_date, end_date) or (None, None)
    """
    search_text = search_text.strip()

    # === MONTH RANGE: jan 2025-jun 2025 or 01/2025-06/2025 ===
    if '-' in search_text:
        part1, part2 = search_text.split('-', 1)
        start_month, _ = parse_month_str(part1)
        _, end_month = parse_month_str(part2)
        if start_month and end_month:
            return start_month, end_month

    # === SINGLE MONTH ===
    start_month, end_month = parse_month_str(search_text)
    if start_month and end_month:
        return start_month, end_month

    # === No special format → do normal search ===
    return None, None

# ========== SIGN UP PAGE ==========
def signup(request):
    error = ""
    csrf_token_value = get_token(request)
    if request.method == 'POST':
        from django.contrib.auth.models import User
        u = request.POST.get('username', '').strip()
        p1 = request.POST.get('password1', '')
        p2 = request.POST.get('password2', '')
        if not u or len(u) < 3:
            error = "❌ Username must be at least 3 characters"
        elif p1 != p2:
            error = "❌ Passwords do not match!"
        elif len(p1) < 6:
            error = "❌ Password must be at least 6 characters"
        else:
            try:
                User.objects.create_user(username=u, password=p1)
                return HttpResponseRedirect('/login/?new=1')
            except:
                error = "❌ Username already taken — try another!"

    return HttpResponse(f"""
    <html><head>{STYLE}</head>
        <body>
            {NAVBAR_GUEST}
            <div class="form-box">
                <h2>✍️ Create Your Account</h2>
                <form method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" placeholder="Choose a username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password1" placeholder="Create a password" required>
                    </div>
                    <div class="form-group">
                        <label>Confirm Password</label>
                        <input type="password" name="password2" placeholder="Type password again" required>
                    </div>
                    <p class="error">{error}</p>
                    <button type="submit">✅ Create Account</button>
                </form>
            </div>
        </body>
    </html>
    """)

# ========== LOGIN PAGE ==========
def login_page(request):
    error = ""
    csrf_token_value = get_token(request)
    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            error = "❌ Wrong username or password!"

    msg = "✅ Account created! Please log in." if request.GET.get('new') else ""
    return HttpResponse(f"""
    <html><head>{STYLE}</head>
        <body>
            {NAVBAR_GUEST}
            <div class="form-box">
                <h2>🔑 Log In to MothMate</h2>
                <form method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" placeholder="Your username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" placeholder="Your password" required>
                    </div>
                    <p class="success">{msg}</p>
                    <p class="error">{error}</p>
                    <button type="submit">🔑 Log In</button>
                </form>
            </div>
        </body>
    </html>
    """)

# ========== LOGOUT ==========
def logout_page(request):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect('/accounts/login/')

# ========== DELETE SINGLE RECORD ==========
def delete_sighting(request, sighting_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    try:
        sighting = MothSighting.objects.get(id=sighting_id, user=request.user)
        sighting.delete()
    except:
        pass
    return HttpResponseRedirect('/records/')

# ========== DELETE ALL RECORDS ==========
def delete_all_records(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    if request.method == 'POST':
        count, _ = MothSighting.objects.filter(user=request.user).delete()
        return HttpResponseRedirect(f'/records/?deleted={count}')
    return HttpResponseRedirect('/records/')

# ========== DATE PARSER — MapMate "DD Mmm YYYY" → Django format ==========
def parse_mapmate_date(date_str):
    date_str = date_str.strip()
    month_map = {'jan':'01','feb':'02','mar':'03','apr':'04','may':'05','jun':'06',
                 'jul':'07','aug':'08','sep':'09','oct':'10','nov':'11','dec':'12'}
    try:
        parts = date_str.split()
        if len(parts) == 3:
            day = parts[0].zfill(2)
            mon = month_map.get(parts[1].lower()[:3], '01')
            yr = parts[2]
            if len(yr) == 2:
                yr = '20' + yr
            return f"{yr}-{mon}-{day}"
    except:
        pass
    return None

# ========== LEGACY IMPORT PAGE ==========
def legacy_transfer(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    
    imported = 0
    skipped = 0
    skipped_lines = []
    error_msg = ""
    
    if request.method == 'POST' and request.FILES.get('mapmate_file'):
        try:
            uploaded_file = request.FILES['mapmate_file']
            content = uploaded_file.read().decode('utf-8-sig', errors='ignore')
            lines = content.splitlines()
            
            header_found = False
            line_number = 0
            
            for line in lines:
                line_number += 1
                original_line = line
                line = line.strip()
                if not line:
                    continue
                
                if not header_found:
                    if 'Code' in line and 'Taxon' in line and 'Date' in line:
                        header_found = True
                    continue
                
                cols = line.split('\t')
                if len(cols) < 9:
                    skipped += 1
                    skipped_lines.append(f"Line {line_number}: Not enough columns → {original_line[:80]}")
                    continue
                
                code = cols[0].strip() if len(cols) > 0 else ''
                taxon = cols[1].strip() if len(cols) > 1 else ''
                vernacular = cols[2].strip() if len(cols) > 2 else ''
                site = cols[3].strip() if len(cols) > 3 else ''
                gridref = cols[4].strip() if len(cols) > 4 else ''
                county = cols[5].strip() if len(cols) > 5 else ''
                qty_str = cols[6].strip() if len(cols) > 6 else '1'
                stage = cols[7].strip() if len(cols) > 7 else ''
                date_str = cols[8].strip() if len(cols) > 8 else ''
                recorder = cols[9].strip() if len(cols) > 9 else ''
                determiner = cols[10].strip() if len(cols) > 10 else ''
                method = cols[11].strip() if len(cols) > 11 else ''
                comment = cols[12].strip() if len(cols) > 12 else ''
                
                if not taxon:
                    skipped += 1
                    skipped_lines.append(f"Line {line_number}: Missing Taxon → {original_line[:80]}")
                    continue
                
                sighting_date = parse_mapmate_date(date_str)
                if not sighting_date:
                    skipped += 1
                    skipped_lines.append(f"Line {line_number}: Bad date '{date_str}' → {original_line[:80]}")
                    continue
                
                qty = 1
                if qty_str and qty_str.isdigit():
                    qty = int(float(qty_str))
                
                MothSighting.objects.create(
                    user=request.user,
                    code=code,
                    taxon=taxon,
                    vernacular=vernacular,
                    location=site,
                    grid_reference=gridref,
                    county=county,
                    quantity=qty,
                    stage=stage,
                    sighting_date=sighting_date,
                    recorder=recorder,
                    determiner=determiner,
                    method=method,
                    comment=comment,
                )
                imported += 1
                    
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
    
    skipped_html = ""
    if skipped_lines:
        skipped_html = f"""
        <div class="skipped">
            <strong>⚠️ Skipped {skipped} lines:</strong><br>
            {('<br>'.join(skipped_lines[:50]))}
            {('<br>... and ' + str(max(0, len(skipped_lines)-50)) + ' more lines') if len(skipped_lines) > 50 else ''}
        </div>"""
    
    return HttpResponse(f"""
    <html><head>{STYLE}</head>
        <body>
            {NAVBAR.replace('class="active"', '').replace('/transfer/', '/transfer/" class="active"')}
            <div class="form-box">
                <h2>📥 Legacy Import — MapMate to MothMate</h2>
                <div class="info">
                    <strong>✅ File format:</strong> Export from MapMate as tab-separated text file with columns:<br>
                    Code | Taxon | Vernacular | Site | Gridref | Vice County | Quantity | Stage | Date | Recorder | Determiner | Method | Comment
                </div>
                <p class="success">✅ IMPORTED: {imported} records | Skipped: {skipped} lines</p>
                {skipped_html}
                <p class="error">{error_msg}</p>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                    <div class="form-group">
                        <label>📁 Select MapMate export file (.txt)</label>
                        <input type="file" name="mapmate_file" accept=".txt,.tsv,.csv" required>
                    </div>
                    <button type="submit">📥 Upload & Import</button>
                </form>
            </div>
        </body>
    </html>
    """)

# ========== HOME PAGE ==========
def home(request):
    if not request.user.is_authenticated:
        return HttpResponse(f"""
        <html><head>{STYLE}</head>
            <body>
                {NAVBAR_GUEST}
                <div class="content">
                    <h1>🦋 Welcome to MothMate</h1>
                    <div class="form-box">
                        <p style="font-size:18px; line-height:1.8; color:#2e7d32; text-align:center;">
                            Your personal moth recording companion<br><br>
                            <a href="/signup/" style="color:#2e7d32; font-weight:bold;">Sign up</a> or 
                            <a href="/login/" style="color:#2e7d32; font-weight:bold;">Log in</a> to start recording
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """)

    total = MothSighting.objects.filter(user=request.user).count()
    return HttpResponse(f"""
    <html><head>{STYLE}</head>
        <body>
            {NAVBAR.replace('class="active"', '').replace('href="/"', 'href="/" class="active"')}
            <div class="content">
                <h1>🦋 Welcome back, {request.user.username}!</h1>
                <div class="form-box">
                    <p style="font-size:20px; line-height:1.8; color:#2e7d32; text-align:center;">
                        You have recorded <strong>{total}</strong> moth sightings so far!<br><br>
                        <a href="/add/" style="color:#2e7d32; font-weight:bold;">→ Add a new sighting</a><br>
                        <a href="/records/" style="color:#2e7d32; font-weight:bold;">→ View & search your records</a><br>
                        <a href="/transfer/" style="color:#2e7d32; font-weight:bold;">→ Import from MapMate</a>
                    </p>
                </div>
            </div>
        </body>
    </html>
    """)

# ========== ADD SIGHTING PAGE ==========
def add_sighting(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    csrf_token_value = get_token(request)
    msg = ""
    if request.method == 'POST':
        MothSighting.objects.create(
            user=request.user,
            code=request.POST.get('code', ''),
            taxon=request.POST.get('taxon', ''),
            vernacular=request.POST.get('vernacular', ''),
            location=request.POST.get('location', ''),
            grid_reference=request.POST.get('grid_reference', ''),
            county=request.POST.get('county', ''),
            quantity=request.POST.get('quantity', 1) or 1,
            stage=request.POST.get('stage', ''),
            sighting_date=request.POST.get('sighting_date', ''),
            recorder=request.POST.get('recorder', ''),
            determiner=request.POST.get('determiner', ''),
            method=request.POST.get('method', ''),
            comment=request.POST.get('comment', ''),
        )
        msg = "✅ Sighting saved successfully!"

    return HttpResponse(f"""
    <html><head>{STYLE}</head>
        <body>
            {NAVBAR.replace('class="active"', '').replace('/add/', '/add/" class="active"')}
            <div class="form-box">
                <h2>🦋 Add New Sighting</h2>
                <form method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Date *</label>
                            <input type="date" name="sighting_date" required>
                        </div>
                        <div class="form-group">
                            <label>Location / Site *</label>
                            <input type="text" name="location" placeholder="Site name" required>
                        </div>
                        <div class="form-group">
                            <label>Grid Reference</label>
                            <input type="text" name="grid_reference" placeholder="e.g. TM534913">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Vice County</label>
                            <input type="text" name="county" placeholder="e.g. 25">
                        </div>
                        <div class="form-group">
                            <label>Code</label>
                            <input type="text" name="code" placeholder="e.g. 45.044">
                        </div>
                        <div class="form-group">
                            <label>Stage</label>
                            <input type="text" name="stage" placeholder="Adult / Larva">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Scientific Name (Taxon) *</label>
                            <input type="text" name="taxon" placeholder="e.g. Emmelina monodactyla" required>
                        </div>
                        <div class="form-group">
                            <label>Common Name</label>
                            <input type="text" name="vernacular" placeholder="e.g. Common Plume">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Quantity</label>
                            <input type="number" name="quantity" value="1" min="1">
                        </div>
                        <div class="form-group">
                            <label>Recorder</label>
                            <input type="text" name="recorder" placeholder="Your name">
                        </div>
                        <div class="form-group">
                            <label>Determiner</label>
                            <input type="text" name="determiner" placeholder="Who identified it">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Method</label>
                            <input type="text" name="method" placeholder="Light trap / Daytime / etc">
                        </div>
                        <div class="form-group">
                            <label>Comment</label>
                            <input type="text" name="comment" placeholder="Any notes">
                        </div>
                    </div>
                    <p class="success">{msg}</p>
                    <button type="submit">💾 Save Sighting</button>
                </form>
            </div>
        </body>
    </html>
    """)

# ========== MY RECORDS — SEARCH + SORT TOGGLE ==========
def records(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    
    deleted_msg = ""
    deleted_count = request.GET.get('deleted')
    if deleted_count:
        deleted_msg = f"✅ DELETED {deleted_count} records successfully!"
    
    remove_filters = request.POST.get('remove_filters', '')
    
    # === Get sort order ===
    sort_order = request.POST.get('sort_order', 'newest')  # default: newest first
    
    if remove_filters:
        search_taxon = search_vernacular = search_location = search_grid = ""
        search_county = search_stage = search_date = search_recorder = ""
        search_determiner = search_method = search_code = ""
        sort_order = 'newest'  # reset sort on clear
    else:
        search_taxon = request.POST.get('search_taxon', '').strip()
        search_vernacular = request.POST.get('search_vernacular', '').strip()
        search_location = request.POST.get('search_location', '').strip()
        search_grid = request.POST.get('search_grid', '').strip()
        search_county = request.POST.get('search_county', '').strip()
        search_stage = request.POST.get('search_stage', '').strip()
        search_date = request.POST.get('search_date', '').strip()
        search_recorder = request.POST.get('search_recorder', '').strip()
        search_determiner = request.POST.get('search_determiner', '').strip()
        search_method = request.POST.get('search_method', '').strip()
        search_code = request.POST.get('search_code', '').strip()

    qs = MothSighting.objects.filter(user=request.user)

    # === DATE SEARCH: Single month OR month range ===
    if search_date:
        start_date, end_date = parse_date_search(search_date)
        if start_date and end_date:
            qs = qs.filter(sighting_date__gte=start_date, sighting_date__lte=end_date)
        else:
            qs = qs.filter(sighting_date__icontains=search_date)

    if search_taxon:
        qs = qs.filter(taxon__icontains=search_taxon)
    if search_vernacular:
        qs = qs.filter(vernacular__icontains=search_vernacular)
    if search_location:
        qs = qs.filter(location__icontains=search_location)
    if search_grid:
        qs = qs.filter(grid_reference__icontains=search_grid)
    if search_county:
        qs = qs.filter(county__icontains=search_county)
    if search_stage:
        qs = qs.filter(stage__icontains=search_stage)
    if search_recorder:
        qs = qs.filter(recorder__icontains=search_recorder)
    if search_determiner:
        qs = qs.filter(determiner__icontains=search_determiner)
    if search_method:
        qs = qs.filter(method__icontains=search_method)
    if search_code:
        qs = qs.filter(code__icontains=search_code)

    # === APPLY SORT ORDER ===
    if sort_order == 'oldest':
        my_sightings = qs.order_by('sighting_date')
    else:
        my_sightings = qs.order_by('-sighting_date')

    total_count = MothSighting.objects.filter(user=request.user).count()
    filtered_count = my_sightings.count()

    rows = ""
    for s in my_sightings:
        # Convert to UK format: DD/MM/YYYY
        try:
            uk_date = s.sighting_date.strftime("%d/%m/%Y") if s.sighting_date else "—"
        except:
            uk_date = str(s.sighting_date)
        
        rows += f"""<tr>
            <td>{s.code or '—'}</td>
            <td>{s.taxon}</td>
            <td>{s.vernacular or '—'}</td>
            <td>{s.location}</td>
            <td>{s.grid_reference or '—'}</td>
            <td>{s.county or '—'}</td>
            <td>{s.stage or '—'}</td>
            <td>{uk_date}</td>
            <td>{s.recorder or '—'}</td>
            <td>{s.determiner or '—'}</td>
            <td>{s.quantity}</td>
            <td>{s.method or '—'}</td>
            <td style="max-width:120px;">{s.comment or '—'}</td>
            <td>
                <form action="/delete/{s.id}/" method="post" style="display:inline;" onsubmit="return confirm('Delete this record? Cannot undo!');">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                    <button type="submit" class="delete-btn">🗑️</button>
                </form>
            </td>
        </tr>"""

    # === SELECTED OPTION HTML ===
    newest_sel = 'selected' if sort_order == 'newest' else ''
    oldest_sel = 'selected' if sort_order == 'oldest' else ''

    return HttpResponse(f"""
    <html><head>{STYLE}</head>
        <body>
            {NAVBAR.replace('class="active"', '').replace('/records/', '/records/" class="active"')}
            <div class="content">
                <h1>📋 My Records</h1>
                <p class="success">{deleted_msg}</p>

                <div class="search-box">
                    <form method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        <div class="search-row">
                            <div class="search-group">
                                <label>Code</label>
                                <input type="text" name="search_code" placeholder="Code" value="{search_code}">
                            </div>
                            <div class="search-group">
                                <label>Taxon</label>
                                <input type="text" name="search_taxon" placeholder="Scientific name" value="{search_taxon}">
                            </div>
                            <div class="search-group">
                                <label>Vernacular</label>
                                <input type="text" name="search_vernacular" placeholder="Common name" value="{search_vernacular}">
                            </div>
                            <div class="search-group">
                                <label>Location</label>
                                <input type="text" name="search_location" placeholder="Site name" value="{search_location}">
                            </div>
                            <div class="search-group">
                                <label>Grid Ref</label>
                                <input type="text" name="search_grid" placeholder="Grid ref" value="{search_grid}">
                            </div>
                            <div class="search-group">
                                <label>Vice County</label>
                                <input type="text" name="search_county" placeholder="County" value="{search_county}">
                            </div>
                        </div>
                        <div class="search-row">
                            <div class="search-group">
                                <label>Stage</label>
                                <input type="text" name="search_stage" placeholder="Adult/Larva" value="{search_stage}">
                            </div>
                            <div class="search-group">
                                <label>Date Search</label>
                                <input type="text" name="search_date" placeholder="e.g. 01/2025 or jan-jun 2025" value="{search_date}">
                            </div>
                            <div class="search-group">
                                <label>Recorder</label>
                                <input type="text" name="search_recorder" placeholder="Name" value="{search_recorder}">
                            </div>
                            <div class="search-group">
                                <label>Determiner</label>
                                <input type="text" name="search_determiner" placeholder="Name" value="{search_determiner}">
                            </div>
                            <div class="search-group">
                                <label>Method</label>
                                <input type="text" name="search_method" placeholder="Trap/Observation" value="{search_method}">
                            </div>
                            <div class="search-group">
                                <label>Sort By Date</label>
                                <select name="sort_order" onchange="this.form.submit()">
                                    <option value="newest" {newest_sel}>📅 Newest First</option>
                                    <option value="oldest" {oldest_sel}>📅 Oldest First</option>
                                </select>
                            </div>
                            <div class="search-group">
                                <label style="visibility:hidden;">Actions</label>
                                <input type="submit" value="🔍 Search" class="search-btn">
                                <button type="submit" name="remove_filters" value="1" class="clear-btn">❌ Remove</button>
                            </div>
                        </div>
                    </form>
                </div>

                <div class="result-count">
                    <strong>Showing {filtered_count} of {total_count} total records</strong>
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    <form action="/delete-all/" method="post" style="display:inline;" onsubmit="return confirm('⚠️ DELETE ALL {total_count} RECORDS? This CANNOT be undone! Are you SURE?');">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        <button type="submit" class="delete-all-btn">🗑️ DELETE ALL RECORDS</button>
                    </form>
                </div>

                <div class="table-wrapper">
                    <table class="records-table">
                        <tr>
                            <th>Code</th>
                            <th>Taxon</th>
                            <th>Vernacular</th>
                            <th>Location</th>
                            <th>Grid</th>
                            <th>Vice County</th>
                            <th>Stage</th>
                            <th>Date</th>
                            <th>Recorder</th>
                            <th>Determiner</th>
                            <th>Qty</th>
                            <th>Method</th>
                            <th>Comment</th>
                            <th>Del</th>
                        </tr>
                        {rows or "<tr><td colspan='14' style='text-align:center;padding:30px;color:#666;'>No matching records. Try a different search term.</td></tr>"}
                    </table>
                </div>
            </div>
        </body>
    </html>
    """)

# ========== STATISTICS PAGE ==========
def stats(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    total = MothSighting.objects.filter(user=request.user).count()
    return HttpResponse(f"""
    <html><head>{STYLE}</head>
        <body>
            {NAVBAR.replace('class="active"', '').replace('/stats/', '/stats/" class="active"')}
            <div class="content">
                <h1>📊 Statistics</h1>
                <div class="form-box">
                    <p style="font-size:20px; line-height:1.8; color:#2e7d32; text-align:center;">
                        Total Sightings Recorded: <strong>{total}</strong>
                    </p>
                </div>
            </div>
        </body>
    </html>
    """)

# ========== ABOUT PAGE ==========
def about(request):
    nav = NAVBAR_GUEST if not request.user.is_authenticated else NAVBAR.replace('class="active"', '').replace('/about/', '/about/" class="active"')
    return HttpResponse(f"""
    <html><head>{STYLE}</head>
        <body>
            {nav}
            <div class="content">
                <h1>ℹ️ About MothMate</h1>
                <div class="form-box">
                    <p style="font-size:16px; line-height:1.8; color:#2e7d32;">
                        MothMate — Your personal moth biological recording platform.<br><br>
                        Built for recording, storing, and importing moth sightings with full MapMate compatibility.
                    </p>
                </div>
            </div>
        </body>
    </html>
    """)