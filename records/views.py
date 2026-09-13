from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import MothSighting
from .forms import MothSightingForm
import csv
from io import TextIOWrapper


def home(request):
    """Homepage"""
    return render(request, 'home.html')


@login_required
def add_sighting(request):
    """Add new sighting"""
    if request.method == 'POST':
        form = MothSightingForm(request.POST)
        if form.is_valid():
            sighting = form.save(commit=False)
            sighting.user = request.user
            sighting.save()
            return redirect('my_records')
    else:
        form = MothSightingForm()
    return render(request, 'add_sighting.html', {'form': form})


@login_required
def my_records(request):
    """Show user's own records"""
    records = MothSighting.objects.filter(user=request.user).order_by('-date')
    return render(request, 'my_records.html', {'records': records})


@login_required
def legacy_import(request):
    """Import MapMate text file"""
    result = {'imported': 0, 'skipped': 0}
    if request.method == 'POST' and request.FILES.get('import_file'):
        f = TextIOWrapper(request.FILES['import_file'].file, encoding='utf-8')
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            try:
                MothSighting.objects.create(
                    user=request.user,
                    taxon=row.get('Taxon', '').strip(),
                    vernacular=row.get('Vernacular', '').strip(),
                    site=row.get('Site', '').strip(),
                    gridref=row.get('Gridref', '').strip(),
                    vice_county=row.get('Vice County', '').strip(),
                    quantity=int(row.get('Quantity') or 1),
                    stage=row.get('Stage', '').strip(),
                    date=row.get('Date', '').strip(),
                    recorder=row.get('Recorder', '').strip(),
                    determiner=row.get('Determiner', '').strip(),
                    method=row.get('Method', '').strip(),
                    comment=row.get('Comment', '').strip(),
                )
                result['imported'] += 1
            except Exception:
                result['skipped'] += 1
    
    return render(request, 'legacy_import.html', {'result': result})