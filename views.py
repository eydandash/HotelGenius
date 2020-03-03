from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from HotelCleaner.models import DirtyHotel,LanyonHotel,CleanedHotel,UncleanedHotel
from django.db.models import Count
import csv

# All views are created here.

def index(request):
    # handling the case where user enters all details in username and client, and saving the entered data to the
    # session to be rendered easily by other views.
    if request.method == 'POST':

        request.session['client'] = request.POST['client']
        request.session['key'] = request.session._session_key
        return HttpResponseRedirect('upload/')


    return render(request, 'HotelCleaner/index.html', {})

    # handling the case where user uploads a csv file, and saving the uploaded data to the
    # Dirty Hotel Table and increments the no of dirty hotels in the session to be rendered easily by other views and
    # passes them into the corresponding template to be used as template tags.

def upload(request):
    # please note that the file to be uploaded is called TestData and is located in the static files directory.
    sessionClient = request.session.get('client')
    key = request.session.get('key')
    if "GET" == request.method:
        return render(request, 'HotelCleaner/upload.html', {'sessionClient': sessionClient, 'key': key})
    # if not GET, then proceed
    else:
        DirtyHotel.objects.all().delete()     # delete all dirty hotels from previous sessions
        UncleanedHotel.objects.all().delete() # delete all cleaned hotels from previous sessions
        CleanedHotel.objects.all().delete()   # delete all uncleaned hotels from previous sessions
        request.session['dhCount'] = 0
        request.session['chCount'] = 0
        request.session['uchCount'] = 0
        csv_file = request.FILES["csv_file"]  # requests the csv file uploaded.

        file_data = csv_file.read().decode("utf-8",'ignore') # decodes the file and reads it.

        lines = file_data.split("\n")    # splits all data in the csv into lines

        for line in lines:       # loops through lines to dave data to the database
            request.session['dhCount'] = request.session['dhCount']+1
            fields = line.split(",")
            dh = DirtyHotel()
            dh.name = fields[0]
            dh.city = fields[1]
            dh.state = fields[2]
            dh.country = fields[3]
            dh.address = fields[4]
            dh.save()

            if LanyonHotel.objects.filter(name=dh.name, city=dh.city, country=dh.country).exists():
                ch = CleanedHotel()
                ch.dirtyHotel = dh
                ch.lanyonId = LanyonHotel.objects.get(name=dh.name, city=dh.city, country=dh.country).lanyonId
                ch.name = dh.name
                ch.city = dh.city
                ch.country = dh.country
                ch.address = dh.address
                ch.save()
                request.session['chCount'] = request.session['chCount'] + 1

            else:
                uch = UncleanedHotel()
                uch.dirtyHotel = dh
                uch.save()
                request.session['uchCount'] = request.session['uchCount'] + 1
    return HttpResponseRedirect('/cleaning')

    # handling the case cleaning page request
def cleaning(request):
    sessionClient = request.session.get('client')
    key = request.session.get('key')
    return render(request, 'HotelCleaner/cleaning.html',{'sessionClient': sessionClient, 'key' : key})

    # handling the case where user presses the get report, and running queries to obtain
    # different analytical figures, then passing them into the coressponding template to be used as template tags.

def report(request):
    if request.method == 'POST' and 'downloadbtn1' in request.POST:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cleanedDownload.csv"'
        values = CleanedHotel.objects.all().order_by('dirtyHotel__cleanedhotel__country', 'dirtyHotel__cleanedhotel__city','dirtyHotel__cleanedhotel__name')
        writer = csv.writer(response)
        writer.writerow(['LanyonID','Hotel', 'City', 'State','Country','Address'])

        for row in values:
            writer.writerow([row.lanyonId,
                             row.name,
                             row.city,
                             row.state,
                             row.country,
                             row.address])

        return response
    if request.method == 'POST' and 'downloadbtn2' in request.POST:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="uncleanedDownload.csv"'
        values = UncleanedHotel.objects.all().order_by('dirtyHotel__country','dirtyHotel__city','dirtyHotel__cleanedhotel__name')
        writer = csv.writer(response)
        writer.writerow(['Hotel', 'City', 'State', 'Country', 'Address'])

        for row in values:
            writer.writerow([row.dirtyHotel.name,
                             row.dirtyHotel.city,
                             row.dirtyHotel.state,
                             row.dirtyHotel.country,
                             row.dirtyHotel.address])

        return response
    sessionClient = request.session.get('client')
    key = request.session.get('key')
    dhcount = request.session.get('dhCount')
    chcount = request.session.get('chCount')
    uchCount = request.session.get('uchCount')
    lacp = (chcount/dhcount*100)
    cp = round(lacp,2)
    laucp = uchCount/dhcount*100
    ucp = round(laucp,2)
    mcc = CleanedHotel.objects.values("dirtyHotel__cleanedhotel__city").annotate(count=Count('dirtyHotel__cleanedhotel__city')).order_by("-count").first()['dirtyHotel__cleanedhotel__city']
    mcco = CleanedHotel.objects.values("dirtyHotel__cleanedhotel__country").annotate(count=Count('dirtyHotel__cleanedhotel__country')).order_by("-count").first()['dirtyHotel__cleanedhotel__country']
    return render(request, 'HotelCleaner/report.html',{'sessionClient': sessionClient, 'key' : key, 'dhcount':dhcount,'chcount':chcount,'uchCount':uchCount,'ucp':ucp,'cp':cp,'mcc':mcc,'mcco':mcco})