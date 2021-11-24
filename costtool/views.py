from datetime import datetime, timedelta
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect,render
from django.db import IntegrityError
from django.template import Context, loader, RequestContext
#from django.contrib.auth import authenticate, login as auth_login
#from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
#from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q,Max, Min, Count
from costtool import models as m
from costtool.forms import ShareProjForm,DistForm,VideoForm,FileUploadForm,AboutForm, AdminForm,TransfersForm, AgenciesForm,RegisterForm,License,ForgotForm, LoginForm, PricesForm, PricesSearchForm, PriceIndicesForm, NonPerIndicesForm, WageDefaults, WageConverter,UMConverter, PriceBenefits, PriceSummary,MultipleSummary, UserForm, UserProfileForm, ProjectsForm, ProgramsForm, ProgramDescForm, ParticipantsForm, EffectForm,SettingsForm, GeographicalForm, GeographicalForm_orig, InflationForm, InflationForm_orig, IngredientsForm,IngredientsFullForm
from costtool.functions import calculations2, calculations, updateDate, updateProj
from dateutil.relativedelta import relativedelta
from django.contrib.humanize.templatetags.humanize import intcomma
#from django.core.mail import send_mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from email.MIMEImage import MIMEImage
#from django.contrib import messages
from datetime import *
from django.views.decorators.cache import cache_page

import datetime, time
import xlrd
import xlwt
import MySQLdb
import math
import csv
#import random
#import os
#import warnings

def videos(request):
    videoList = []

    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')
       else:
          # Handle file upload
          if request.method == 'POST':
             form = VideoForm(request.POST, request.FILES)
             if form.is_valid():
                video = form.save(commit=False)
                if video.videoName is not None and video.videoName != '' and video.link is not None and video.link != '':
                   video.save()
          else:
             form = VideoForm() # A empty, unbound form

          # Load documents for the list page
          database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
          cursor = database.cursor ()
          mysql = """SELECT videoName, MAX(CONVERT_TZ(vDate,'GMT','EST')) from costtool_videos group by videoName"""
          try:
             cursor.execute(mysql)
             results = cursor.fetchall()
             for row in results:
                ret = {}
                ret['Name'] = row[0]
                ret['Date'] = row[1]
                videoList.append(ret)
          except:
             print("Error: unable to fetch data")

          # disconnect from server
          database.close()

          # Render list page with the documents and the form
          return render(
          'admin/videos.html',
          {'form': form, 'videoList':videoList},
          context_instance=RequestContext(request)
          )

def tour(request):
   video = m.Videos.objects.filter(videoName = 'Full Tour').order_by('-id')[0]
   #return HttpResponseRedirect('https://www.youtube.com/watch?v=8jIlU9Ebb8o')
   return HttpResponseRedirect(video.link)

def tutorial1(request):
   video = m.Videos.objects.filter(videoName = 'Tutorial 1').order_by('-id')[0]
   #return HttpResponseRedirect('http://www.screencast.com/t/YnjycwrBj')
   return HttpResponseRedirect(video.link)

def tutorial2(request):
   video = m.Videos.objects.filter(videoName = 'Tutorial 2').order_by('-id')[0]
   #return HttpResponseRedirect('http://www.screencast.com/t/DTllm2cb')
   return HttpResponseRedirect(video.link)

def tutorial3(request):
   video = m.Videos.objects.filter(videoName = 'Tutorial 3').order_by('-id')[0]
   #return HttpResponseRedirect('http://www.screencast.com/t/Z1E2fyjWUB9')
   return HttpResponseRedirect(video.link)

def tutorial4(request):
   video = m.Videos.objects.filter(videoName = 'Tutorial 4').order_by('-id')[0]
   #return HttpResponseRedirect('https://drive.google.com/open?id=0Bwor6cRBC4CrZHRZaEFZWXBLbkE&authuser=0')
   return HttpResponseRedirect(video.link)

def tutorial5(request):
   video = m.Videos.objects.filter(videoName = 'Tutorial 5').order_by('-id')[0]
   #return HttpResponseRedirect('https://drive.google.com/open?id=0Bwor6cRBC4CrNl9WaWNFcFlCejg&authuser=0')
   return HttpResponseRedirect(video.link)

def upload(request):
    DocList = []
    if 'user' not in request.session: 
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')                                                                                   
       else: 
       # Handle file upload
          if request.method == 'POST':
             form = FileUploadForm(request.POST, request.FILES)
             if form.is_valid():
                newdoc = m.FileUpload(docfile = request.FILES['docfile'])
                newdoc.docName = request.FILES['docfile']  
                newdoc.docfile = '/home/amritha/costtool/documents/' + request.FILES['docfile'].name
                handle_uploaded_file(request.FILES['docfile'], request.FILES['docfile'].name)
                newdoc.save()

               # Redirect to the document list after POST
               #return HttpResponseRedirect('/admin/options.html')
          else:
             form = FileUploadForm() # A empty, unbound form

          # Load documents for the list page
          database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
          cursor = database.cursor ()
          mysql = """SELECT docName, MAX(CONVERT_TZ(docDate,'GMT','EST')) from costtool_fileupload group by docName"""

          try:
             cursor.execute(mysql)
             results = cursor.fetchall()
             for row in results:
                ret = {}
                ret['Name'] = row[0]
                ret['Date'] = row[1]
                DocList.append(ret)
          except:
             print("Error: unable to fetch data")

          # disconnect from server
          database.close()

          # Render list page with the documents and the form
          return render(
             'admin/upload.html',
              {'form': form, 'DocList':DocList},
              context_instance=RequestContext(request)
              )

def handle_uploaded_file(f, fname):
    loc = '/home/amritha/costtool/documents/' + fname
    with open(loc, 'wb+') as destination:
        for chunk in f.chunks():
           destination.write(chunk)
    
def add_program(request):
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    context = RequestContext(request)

    if request.method == 'POST':
        programform = ProgramsForm(request.POST)

        if programform.is_valid():
            progname = programform.save(commit=False)
            progname.projectId = project_id
            progname.save()
            upd = updateDate(project_id, None)
            return HttpResponseRedirect('/project/programs/'+project_id+'/program_list.html')
        else:
            print(programform.errors)

    else:
        programform = ProgramsForm()

    return render(request,
            'project/programs/add_program.html',
            {'programform': programform,'project_id':project_id})


def indices(request):
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    return render(request,'project/indices.html',{'project_id':project_id})

'''def about2(request):
    #if 'user' in request.session:
        #del request.session['user']
    #if 'password' in request.session:
       #del request.session['password']
    template = loader.get_template('about.html')
    about = m.About.objects.get(id = 1)
    context = Context({'web':about.web, 'email':about.email})
    return HttpResponse(template.render(context))
'''
def about(request):                                                                                                                       
    about = m.About.objects.get(id = 1)
    #return HttpResponse("Hello, world. You're at the costout about page.")
    return render(request, 'about.html', {'web':about.web, 'email':about.email})

def contact(request):
    context = RequestContext(request)
    if 'user' not in request.session: 
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')                                                                                   
       else: 
          arec = m.About.objects.get(id = 1)
          if request.method == 'POST':
             aboutform = AboutForm(request.POST)
             if aboutform.is_valid():
                a = aboutform.save(commit=False)
                if a.web == '' and a.email == '' and a.sendemail == '':
                   return render('admin/contact.html',{'aboutform':aboutform,'err':'Enter Web, Email and/or Password to Save'}, context)
                elif a.web != '' and a.web[:4] != 'www.':
                   return render('admin/contact.html',{'aboutform':aboutform,'err':'The first four letters should be www.'}, context)
                if a.web != '' and a.email != '' and a.sendemail != '':
                   arec.web = a.web
                   arec.email = a.email
                   arec.sendemail = a.sendemail
                   arec.save(update_fields=['web','email', 'sendemail'])
                elif a.web != '':
                   arec.web = a.web
                   arec.save(update_fields=['web'])
                elif a.email != '':
                   arec.email = a.email
                   arec.save(update_fields=['email'])
                elif a.sendemail != '':
                   arec.sendemail = a.sendemail
                   arec.save(update_fields=['sendemail'])
                return HttpResponseRedirect('/project/project_list.html')
             else:
                print(aboutform.errors)
          else:
             aboutform = AboutForm()

          return render(
            'admin/contact.html',
            {'aboutform': aboutform}, context)

def logout(request):
    if 'user' in request.session:
        del request.session['user']
    if 'password' in request.session:
       del request.session['password']
    return render(request,'about.html')

def settings(request):
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    return render(request, 'project/settings.html',{'project_id':project_id})

def prices(request):
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'ccc'
    try:
       login = m.Login.objects.filter(user=loggedinuser).latest('startDate')
       return render(request,'prices/prices.html')
    except ObjectDoesNotExist:
       return render(request,'prices/message.html')

def reports(request,project_id):                                                                                                                 
    project = m.Projects.objects.get(pk=project_id)
    request.session['project_id'] = project_id
    if project.typeanalysis == 'Cost-Effectiveness Analysis':
       return render(request,'reports/reports_eff.html', {'project_id':project_id})
    else:
       return render(request,'reports/reports.html', {'project_id':project_id})

def noofreg(request):
    RegList = []
    prevDate = ''
    count = 0
    if 'user' not in request.session: 
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')                                                                                   
       else:
           #f = open( '/home/amritha/costtool/documents/filename.txt', 'w+' )
           for l in  m.Login.objects.all():
              ret = {}
              count = 0
              for l2 in m.Login.objects.filter(startDate = l.startDate):
                 count = count + 1
              if prevDate != l.startDate:
                 ret['startdate'] = time.mktime(l.startDate.timetuple()) * 1000
                 ret['countondate'] = count
                 RegList.append(ret)
              prevDate = l.startDate
           return render(request,'reports/noofreg.html',{'RegList':RegList})

def cumulreg(request):
    if 'user' not in request.session: 
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')                                                                                   
       else:
          #f = open( '/home/amritha/costtool/documents/filename.txt', 'w+' ) 
          RegList = []
          firstDate = datetime.date(2015, 5, 17)
          fifteenth = datetime.date(2015, 5, 17) + timedelta(days=15)
          latest = m.Login.objects.latest('startDate')
          count = 0
          while fifteenth < latest.startDate + timedelta(days=15):
             ret = {}
             for l in m.Login.objects.filter(startDate__gte=firstDate,startDate__lt=fifteenth):
                count = count + 1
             ret['startdate'] = time.mktime(fifteenth.timetuple()) * 1000
             ret['countondate'] = count
             RegList.append(ret)
             firstDate = fifteenth
             fifteenth = fifteenth + timedelta(days=15)
          return render(request,'reports/cumulreg.html',{'RegList':RegList})

def costeff(request):
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    project = m.Projects.objects.get(pk=project_id)
    ProgList = []
    program = m.Programs.objects.filter(projectId=project_id)
    for p in program:
       ret = {}
       try:
          programdesc = m.ProgramDesc.objects.get(programId_id=p.id)
          ret['lengthofprogram'] = programdesc.numberofyears
          ret['num_participants'] = programdesc.numberofparticipants
       except:
          ret['lengthofprogram'] = 'n/a'
          ret['num_participants'] = 'n/a'

       try:
          eff = m.Effectiveness.objects.get(programId_id = p.id)
          ret['average_effect'] = eff.avgeffectperparticipant
          ret['unitmeasureeffect'] = eff.unitmeasureeffect
          ret['sigeffect'] = eff.sigeffect
       except:
          ret['average_effect'] = 'n/a'
          ret['unitmeasureeffect'] = 'n/a'
          ret['sigeffect'] = 'n/a'

       try:
          ingredients = m.Ingredients.objects.filter(programId = p.id)
          ret['average_cost'] = ingredients[0].averageCost
          ret['total_cost'] = ingredients[0].totalCost
          ret['effRatio'] =  ingredients[0].effRatio
       except:
          ret['average_cost'] = 'n/a'
          ret['total_cost'] = 'n/a'
          ret['effRatio'] = 'n/a'

       ret['short_name'] = p.progshortname

       database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
       cursor = database.cursor ()
       sql = """SELECT MAX(ABS(averageCost)) FROM costtool_ingredients WHERE programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s)"""
       try:
          cursor.execute(sql,{'projectId' : project_id})
          row = cursor.fetchone()
          ret['Max'] = row[0]
       except:
          print("Error: unable to fetch data")
          ret['Max'] = 'n/a'

       cursor3 = database.cursor ()
       sql3 = """SELECT MAX(ABS(avgeffectperparticipant)) FROM costtool_effectiveness WHERE programId_id IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s)"""
       try:
          cursor3.execute(sql3,{'projectId' : project_id})
          row3 = cursor3.fetchone()
          ret['MaxEff'] = row3[0]
       except:
          print("Error: unable to fetch data")
          ret['MaxEff'] = 'n/a'

       ProgList.append(ret)
    return render(request,'reports/costeff.html', {'ProjectName': project.projectname,'ProgList':ProgList,'x1':-100000,'x2':120000})

def costeff_table(request):
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    project = m.Projects.objects.get(pk=project_id)
    ProgList = []
    program = m.Programs.objects.filter(projectId=project_id)
    for p in program:
       ret = {}
       try:
          programdesc = m.ProgramDesc.objects.get(programId_id=p.id)
          if programdesc.lengthofprogram == 'One year or less':
             ret['lengthofprogram'] = programdesc.lengthofprogram
          else:
             ret['lengthofprogram'] = programdesc.numberofyears
          ret['num_participants'] = programdesc.numberofparticipants
       except:
          ret['lengthofprogram'] = 'n/a'
          ret['num_participants'] = 'n/a'

       try:
          eff = m.Effectiveness.objects.get(programId_id = p.id)
          if eff.avgeffectperparticipant is None or eff.avgeffectperparticipant == '':
             ret['average_effect'] = 'n/a'
          else:   
             ret['average_effect'] = eff.avgeffectperparticipant
          if eff.unitmeasureeffect is None or eff.unitmeasureeffect == '':
             ret['unitmeasureeffect'] = 'n/a'
          else:   
             ret['unitmeasureeffect'] = eff.unitmeasureeffect
          ret['sigeffect'] = eff.sigeffect
       except:
          ret['average_effect'] = 'n/a'
          ret['unitmeasureeffect'] = 'n/a'
          ret['sigeffect'] = 'n/a'
       try:
          ingredients = m.Ingredients.objects.filter(programId = p.id)
          avgcost = str(intcomma(round(float(ingredients[0].averageCost),2)))
          if ingredients[0].effRatio == 'NULL' or ingredients[0].effRatio is None:
             ret['effRatio'] = 'None'
          else:
             ret['effRatio'] = str(intcomma(round(float(ingredients[0].effRatio),2)))
          ret['average_cost'] = avgcost
          ret['total_cost'] = ingredients[0].totalCost
          if ingredients[0].averageCost >= 0:
             ret['greater'] = ''.join(('Compared to BAU, you will be spending $', avgcost, ' per participant in order to obtain this effect: ', ret['average_effect'], '.'))
          else:
              ret['greater'] = ''.join(('Compared to BAU, you will be saving $', avgcost, ' per participant in order to obtain this effect: ', ret['average_effect'], '.'))
       except:
          ret['average_cost'] = 0
          ret['total_cost'] = 0
          ret['greater'] = 'n/a'
          ret['effRatio'] = 'n/a'

       ret['short_name'] = p.progshortname

       ProgList.append(ret)
    return render(request,'reports/costeff_table.html', {'ProjectName': project.projectname,'ProgList':ProgList})

def export_cea(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=cea_analysis.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Cost-effectiveness analysis")

    row_num = 0

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    if 'project_id' in request.session:
       projectId = request.session['project_id']                                                                                                                                                                
    else:
       projectId = 0 

    project = m.Projects.objects.get(pk = projectId)
    sett = m.Settings.objects.get(projectId = projectId)
    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2

    font_style3 = xlwt.XFStyle()
    font_style3.pattern = pattern
    font_style3.num_format_str = '$#,##0.00'

    font_style5 = xlwt.XFStyle()
    font_style5.font.bold = True
    font_style5.pattern = pattern

    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
    money_xf.pattern = pattern3
    money_xf_22 = xlwt.XFStyle()
    money_xf_22.num_format_str = '$#,##0.00'
    money_xf_22.pattern = pattern

    money_xf2 = xlwt.XFStyle()
    money_xf2.num_format_str = '$#,##0.00'
    money_xf3 = xlwt.XFStyle()
    money_xf3.num_format_str = '#,##0.00'
    money_xf2.pattern = pattern2
    money_xf3.pattern = pattern2

    money_xf4 = xlwt.XFStyle()
    money_xf4.num_format_str = '#,##0.00'
    money_xf4.pattern = pattern3

    money_p = xlwt.XFStyle()
    money_p.num_format_str = '0.0\\%'
    money_p.pattern = pattern3
    money_p_22 = xlwt.XFStyle()
    money_p_22.num_format_str = '0.0\\%'
    money_p_22.pattern = pattern

    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    aL.wrap = True
    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3
    font_style4.alignment = aL
    font_style4.num_format_str = '$#,##0.00'

    ab = xlwt.Alignment()
    ab.vert = a.VERT_CENTER
    ab.horz = a.HORZ_CENTER
    font_cent = xlwt.XFStyle()
    font_cent.alignment = ab
    font_cent.pattern = pattern3
    font_cent_22 = xlwt.XFStyle()
    font_cent_22.alignment = ab
    font_cent_22.pattern = pattern

    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT
    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern
    money_str_22.alignment = aR
    ws.col(2).width = 8000
    ws.col(3).width = 50000

    ws.write(0, 0, "Project", font_style5)
    ws.write(0, 1, "", font_style5)
    ws.write(0, 2, "", font_style5)
    ws.write(0, 3, project.projectname, font_style4)
    ws.write(0, 4, "", font_style4)

    ws.write(1, 0, "Type of Analysis", font_style3)
    ws.write(1, 1, "", font_style5)
    ws.write(1, 2, "", font_style5)
    ws.write(1, 3, project.typeanalysis, font_style4)
    ws.write(1, 4, "", font_style4)

    ws.write(2, 0, "Type of Cost", font_style3)
    ws.write(2, 1, "", font_style5)
    ws.write(2, 2, "", font_style5)
    ws.write(2, 3, project.typeofcost, font_style4)
    ws.write(2, 4, "", font_style4)

    ws.write(3, 0, "Geographical location in which you are expressing costs", font_style3)
    ws.write(3, 1, "", font_style5)
    ws.write(3, 2, "", font_style5)
    ws.write(3, 3, sett.stateEstimates + ' ' + sett.areaEstimates, font_style4)
    ws.write(3, 4, "", font_style4)

    ws.write(4, 0, "Year in which you are expressing costs", font_style3)
    ws.write(4, 1, "", font_style5)
    ws.write(4, 2, "", font_style5)
    ws.write(4, 3, str(sett.yearEstimates), font_style4)
    ws.write(4, 4, "", font_style4)

    ws.write(5, 0, "Discount Rate", font_style3)
    ws.write(5, 1, "", font_style5)
    ws.write(5, 2, "", font_style5)
    ws.write(5, 3, str(sett.discountRateEstimates), font_style4)
    ws.write(5, 4, "", font_style4)

    cursor = database.cursor ()
    sql = """SELECT DISTINCT p.progname, if(pp.lengthofprogram = 'One year or less',pp.lengthofprogram, pp.numberofyears), e.avgeffectperparticipant, e.unitmeasureeffect, e.sigeffect, i.totalCost, pp.numberofparticipants, i.averagecost, i.effRatio, case when i.averagecost >= 0 then concat('Compared to BAU, you will be spending $',FORMAT(CONVERT(i.averagecost, DECIMAL(10,2)),2),' per participant in order to obtain this effect: ', e.avgeffectperparticipant, '.') else concat('Compared to BAU, you will be saving $', FORMAT(CONVERT(i.averagecost, DECIMAL(10,2)),2), ' per participant in order to obtain this effect: ', e.avgeffectperparticipant, '.') end as interpret from costtool_programs p Left join costtool_programdesc pp On p.id = pp.programId_id Left join costtool_effectiveness e On p.id = e.programId_id Left join costtool_ingredients i On p.id = i.programId Where p.projectid = %(projectId)s"""

    row_num = 8

    columns = [
          (u"Program", 12000),
          (u"Length of the program", 7000),
          (u"Average effect per participant", 5000),
          (u"Unit of measure of effectiveness", 10000),
          (u"Sig./ Non-sig", 5000),
          (u"Total gross cost", 5000),
          (u"Number of participants", 5000),
          (u"Avg. cost per participant", 5000),
          (u"Cost-effectiveness ratio", 5000),
          (u"Interpretation of CE ratio (BAU=Business as usual)", 25000)
    ]

    try:
       cursor.execute(sql,{'projectId' : projectId})
       results = cursor.fetchall()
       if results != ():
          for col_num in xrange(len(columns)):
             ws.write(row_num, col_num, columns[col_num][0], font_style)
             # set column width
             ws.col(col_num).width = columns[col_num][1]

       for row in results:
          row_num += 1
          progname = row[0]
          lengthofprogram = row[1]
          avgeffectperparticipant = row[2]
          unitmeasureeffect = row[3]
          sigeffect = row[4]
          totalCost = row[5]
          numberofparticipants = row[6]
          averagecost = row[7]
          effRatio = row[8]
          interpret = row[9]
          for col_num in xrange(len(row)):
             if row_num % 2 == 0:
                if col_num == 5 or  col_num == 7 or  col_num == 8:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
                elif col_num == 1 or col_num == 2 or col_num == 6:
                   ws.write(row_num, col_num, row[col_num],font_cent_22)
                else:
                   ws.write(row_num, col_num, row[col_num],font_style3)
             else:
                if col_num == 5 or  col_num == 7 or  col_num == 8:
                   ws.write(row_num, col_num, row[col_num], money_xf)
                elif col_num == 1 or col_num == 2 or col_num == 6:
                   ws.write(row_num, col_num, row[col_num],font_cent)
                else:
                   ws.write(row_num, col_num, row[col_num], font_style4)

    except:
       print("Error: unable to fetch data")

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def ca_table(request):
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0

    project = m.Projects.objects.get(pk=project_id)
    ProgList = []
    program = m.Programs.objects.filter(projectId=project_id)
    for p in program:
       ret = {}
       try:
          programdesc = m.ProgramDesc.objects.get(programId_id=p.id)
          if programdesc.lengthofprogram == 'One year or less':
             ret['lengthofprogram'] = programdesc.lengthofprogram
          else:
             ret['lengthofprogram'] = programdesc.numberofyears
          ret['num_participants'] = programdesc.numberofparticipants
       except:
          ret['lengthofprogram'] = 'n/a'
          ret['num_participants'] = 'n/a'

       try:
          ingredients = m.Ingredients.objects.filter(programId = p.id)
          avgcost = str(intcomma(round(float(ingredients[0].averageCost),2)))
          ret['average_cost'] = avgcost
          ret['total_cost'] = ingredients[0].totalCost
       except:
          ret['average_cost'] = 'n/a'
          ret['total_cost'] = 'n/a'

       ret['short_name'] = p.progshortname

       ProgList.append(ret)
    return render(request,'reports/ca_table.html', {'ProjectName': project.projectname,'ProgList':ProgList})

def export_ca(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=ca_analysis.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Cost analysis")

    row_num = 0

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool") 
    if 'project_id' in request.session:
       projectId = request.session['project_id']                                                                                                                                                                
    else:
       projectId = 0

    project = m.Projects.objects.get(pk = projectId)
    sett = m.Settings.objects.get(projectId = projectId)
    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2

    font_style3 = xlwt.XFStyle()
    font_style3.pattern = pattern
    font_style3.num_format_str = '$#,##0.00'

    font_style5 = xlwt.XFStyle()
    font_style5.font.bold = True
    font_style5.pattern = pattern

    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
    money_xf.pattern = pattern3
    money_xf_22 = xlwt.XFStyle()
    money_xf_22.num_format_str = '$#,##0.00'
    money_xf_22.pattern = pattern

    money_xf2 = xlwt.XFStyle()
    money_xf2.num_format_str = '$#,##0.00'
    money_xf3 = xlwt.XFStyle()
    money_xf3.num_format_str = '#,##0.00'
    money_xf2.pattern = pattern2
    money_xf3.pattern = pattern2

    money_xf4 = xlwt.XFStyle()
    money_xf4.num_format_str = '#,##0.00'
    money_xf4.pattern = pattern3

    money_p = xlwt.XFStyle()
    money_p.num_format_str = '0.0\\%'
    money_p.pattern = pattern3
    money_p_22 = xlwt.XFStyle()
    money_p_22.num_format_str = '0.0\\%'
    money_p_22.pattern = pattern

    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    aL.wrap = True
    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3
    font_style4.alignment = aL
    font_style4.num_format_str = '$#,##0.00'

    ab = xlwt.Alignment()
    ab.vert = a.VERT_CENTER
    ab.horz = a.HORZ_CENTER
    font_cent = xlwt.XFStyle()
    font_cent.alignment = ab
    font_cent.pattern = pattern3
    font_cent_22 = xlwt.XFStyle()
    font_cent_22.alignment = ab
    font_cent_22.pattern = pattern

    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT
    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern
    money_str_22.alignment = aR
    ws.col(2).width = 8000
    ws.col(3).width = 50000

    ws.write(0, 0, "Project", font_style5)
    ws.write(0, 1, "", font_style5)
    ws.write(0, 2, "", font_style5)
    ws.write(0, 3, project.projectname, font_style4)
    ws.write(0, 4, "", font_style4)

    ws.write(1, 0, "Type of Analysis", font_style3)
    ws.write(1, 1, "", font_style5)
    ws.write(1, 2, "", font_style5)
    ws.write(1, 3, project.typeanalysis, font_style4)
    ws.write(1, 4, "", font_style4)

    ws.write(2, 0, "Type of Cost", font_style3)
    ws.write(2, 1, "", font_style5)
    ws.write(2, 2, "", font_style5)
    ws.write(2, 3, project.typeofcost, font_style4)
    ws.write(2, 4, "", font_style4)

    ws.write(3, 0, "Geographical location in which you are expressing costs", font_style3)
    ws.write(3, 1, "", font_style5)
    ws.write(3, 2, "", font_style5)
    ws.write(3, 3, sett.stateEstimates + ' ' + sett.areaEstimates, font_style4)
    ws.write(3, 4, "", font_style4)

    ws.write(4, 0, "Year in which you are expressing costs", font_style3)
    ws.write(4, 1, "", font_style5)
    ws.write(4, 2, "", font_style5)
    ws.write(4, 3, str(sett.yearEstimates), font_style4)
    ws.write(4, 4, "", font_style4)

    ws.write(5, 0, "Discount Rate", font_style3)
    ws.write(5, 1, "", font_style5)
    ws.write(5, 2, "", font_style5)
    ws.write(5, 3, str(sett.discountRateEstimates), font_style4)
    ws.write(5, 4, "", font_style4)

    cursor = database.cursor ()
    sql = """SELECT DISTINCT p.progname, if(pp.lengthofprogram = 'One year or less',pp.lengthofprogram, pp.numberofyears), i.totalCost, pp.numberofparticipants, i.averagecost from costtool_programs p Left join costtool_programdesc pp On p.id = pp.programId_id Left join costtool_ingredients i On p.id = i.programId Where p.projectid = %(projectId)s """
    row_num = 8

    columns = [
          (u"Program", 12000),
          (u"Length of the program", 7000),
          (u"Total gross cost", 7000),
          (u"Number of participants", 7000),
          (u"Avg. cost per participant", 7000),
    ]

    try:
       cursor.execute(sql,{'projectId' : projectId})
       results = cursor.fetchall()
       if results != ():
          for col_num in xrange(len(columns)):
             ws.write(row_num, col_num, columns[col_num][0], font_style)
             # set column width
             ws.col(col_num).width = columns[col_num][1]

       for row in results:
          row_num += 1
          progname = row[0]
          lengthofprogram = row[1]
          totalCost = row[2]
          numberofparticipants = row[3]
          averagecost = row[4]
          for col_num in xrange(len(row)):
             if row_num % 2 == 0:
                if col_num == 2 or  col_num == 4:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
                elif col_num == 1 or col_num == 3:
                   ws.write(row_num, col_num, row[col_num],font_cent_22)
                else:
                   ws.write(row_num, col_num, row[col_num],font_style3)
             else:
                if col_num == 2 or  col_num == 4:
                   ws.write(row_num, col_num, row[col_num], money_xf)
                elif col_num == 1 or col_num == 3:
                   ws.write(row_num, col_num, row[col_num],font_cent)
                else:
                   ws.write(row_num, col_num, row[col_num], font_style4)

    except:
       print("Error: unable to fetch data")

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def costanal(request):                                                                                                                
   return render(request,'reports/costanal.html')

def costanalbyyear(request):                                                                                                               
   return render(request,'reports/costanalbyyear.html')   

def compcostanal(request):
   if 'project_id' in request.session:
      project_id = request.session['project_id']                                                                                                                                                                
   else:
      project_id = 0
   project = m.Projects.objects.get(pk=project_id)
   ProgList = []
   MaxTotal = []
   try:
      program = m.Programs.objects.filter(projectId=project_id)
      for p in program:
         ret = {}
         fixtot = 0
         for i in m.Ingredients.objects.filter(programId = p.id).filter(variableFixed = 'Fixed'):
            if i.costPerIngredient is not None:
               fixtot = fixtot + i.costPerIngredient
            else:
               fixtot = fixtot
         ret['fixtot'] = fixtot

         ltot = 0
         for i in m.Ingredients.objects.filter(programId = p.id).filter(variableFixed = 'Lumpy'):
            if i.costPerIngredient is not None:
               ltot = ltot + i.costPerIngredient
            else:
               ltot = ltot
         ret['ltot'] = ltot

         vartot = 0
         for i in m.Ingredients.objects.filter(programId = p.id).filter(variableFixed = 'Variable'):
            if i.costPerIngredient is not None:
               vartot = vartot + i.costPerIngredient
            else:
               vartot = vartot
         ret['vartot'] = vartot

         pertot = 0
         for i in m.Ingredients.objects.filter(programId = p.id).filter(category = 'Personnel'):
            if i.costPerIngredient is not None:
               pertot = pertot + i.costPerIngredient
            else:
               pertot = pertot
         ret['pertot'] = pertot

         mattot = 0
         for i in m.Ingredients.objects.filter(programId = p.id).filter(category = 'Material/Equipment'):
            if i.costPerIngredient is not None:
               mattot = mattot + i.costPerIngredient
            else:
               mattot = mattot
         ret['mattot'] = mattot

         factot = 0
         for i in m.Ingredients.objects.filter(programId = p.id).filter(category = 'Facilities'):
            if i.costPerIngredient is not None:
               factot = factot + i.costPerIngredient
            else:
               factot = factot
         ret['factot'] = factot

         inptot = 0
         for i in m.Ingredients.objects.filter(programId = p.id).filter(category = 'Other Inputs'):
            if i.costPerIngredient is not None:
               inptot = inptot + i.costPerIngredient
            else:
               inptot = inptot
         ret['inptot'] = inptot

         ingredients = m.Ingredients.objects.filter(programId = p.id)
         try:
            ret['total_cost'] = ingredients[0].totalCost
            ret['avg_cost'] = ingredients[0].averageCost
         except:
            ret['total_cost'] = 'n/a'
            ret['avg_cost'] = 'n/a'

         ret['short_name'] = p.progshortname

         database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
         cursor = database.cursor ()
         sql = """SELECT MAX(totalCost) FROM costtool_ingredients WHERE programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s)"""
         try:
            cursor.execute(sql,{'projectId' : project_id})
            row = cursor.fetchone()
            ret['Max'] = row[0]
         except:
            print("Error: unable to fetch data")
            ret['Max'] = 'n/a'

         cursor2 = database.cursor ()
         sql2 = """SELECT MIN(totalCost) FROM costtool_ingredients WHERE programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s)"""
         try:
            cursor2.execute(sql2,{'projectId' : project_id})
            row2 = cursor2.fetchone()
            if row2[0] > 0:
               ret['Min'] = 0
            else:
               ret['Min'] = row2[0]

         except:
            print("Error: unable to fetch data")
            ret['Min'] = 'n/a'

         cursor3 = database.cursor ()
         sql3 = """SELECT MAX(averageCost) FROM costtool_ingredients WHERE programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s)"""
         try:
            cursor3.execute(sql3,{'projectId' : project_id})
            row3 = cursor3.fetchone()
            ret['Maxavg'] = row3[0]
         except:
            print("Error: unable to fetch data")
            ret['Maxavg'] = 'n/a'

         cursor4 = database.cursor ()
         sql4 = """SELECT MIN(averageCost) FROM costtool_ingredients WHERE programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s)"""
         try:
            cursor4.execute(sql4,{'projectId' : project_id})
            row4 = cursor4.fetchone()
            if row4[0] > 0:
               ret['Minavg'] = 0
            else:
               ret['Minavg'] = row4[0]
         except:
            print("Error: unable to fetch data")
            ret['Minavg'] = 'n/a'

         cursor5 = database.cursor ()
         sql5 = """SELECT SUM(costperingredient),programid FROM costtool_ingredients WHERE category = 'Personnel' AND programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s) group by programid order by sum(costperingredient) desc"""
         try:
            cursor5.execute(sql5,{'projectId' : project_id})
            row5 = cursor5.fetchone()
            ret['MaxPer'] = row5[0]
         except:
            print("Error: unable to fetch data")
            ret['MaxPer'] = ret['Max']

         cursor9 = database.cursor ()
         sql9 = """SELECT SUM(costperingredient),programid FROM costtool_ingredients WHERE category = 'Personnel' AND programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s) group by programid order by sum(costperingredient) asc"""
         try:
            cursor9.execute(sql9,{'projectId' : project_id})
            row9 = cursor9.fetchone()
            if row9[0] > 0:
               ret['MinPer'] = 0
            else:
               ret['MinPer'] = row9[0]
         except:
            print("Error: unable to fetch data")
            ret['MinPer'] = ret['Min']

         cursor6 = database.cursor ()
         sql6 = """SELECT SUM(costperingredient),programid FROM costtool_ingredients WHERE category = 'Material/Equipment' AND programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s) group by programid order by sum(costperingredient) desc"""
         try:
            cursor6.execute(sql6,{'projectId' : project_id})
            row6 = cursor6.fetchone()
            ret['MaxMat'] = row6[0]
         except:
            print("Error: unable to fetch data6")
            ret['MaxMat'] = ret['Max']

         cursor10 = database.cursor ()
         sql10 = """SELECT SUM(costperingredient),programid FROM costtool_ingredients WHERE category = 'Material/Equipment' AND programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s) group by programid order by sum(costperingredient) asc"""
         try:
            cursor10.execute(sql10,{'projectId' : project_id})
            row10 = cursor10.fetchone()
            if row10[0] > 0:
               ret['MinMat'] = 0
            else:
               ret['MinMat'] = row10[0]

         except:
            print("Error: unable to fetch data10")
            ret['MinMat'] = ret['Min']

         cursor7 = database.cursor ()
         sql7 = """SELECT SUM(costperingredient),programid FROM costtool_ingredients WHERE category = 'Facilities' AND programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s) group by programid order by sum(costperingredient) desc"""
         try:
            cursor7.execute(sql7,{'projectId' : project_id})
            row7 = cursor7.fetchone()
            ret['MaxFac'] = row7[0]
         except:
            print("Error: unable to fetch data7")
            ret['MaxFac'] = ret['Max']

         cursor8 = database.cursor ()
         sql8 = """SELECT SUM(costperingredient),programid FROM costtool_ingredients WHERE category = 'Other Inputs' AND programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s) group by programid order by sum(costperingredient) desc"""
         try:
            cursor8.execute(sql8,{'projectId' : project_id})
            row8 = cursor8.fetchone()
            ret['MaxInp'] = row8[0]
         except:
            print("Error: unable to fetch data8")
            ret['MaxInp'] = ret['Max']

         cursor11 = database.cursor ()         
         sql11 = """SELECT SUM(costperingredient),programid FROM costtool_ingredients WHERE category = 'Facilities' AND programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s) group by programid order by sum(costperingredient) asc"""          
         try:
            cursor11.execute(sql11,{'projectId' : project_id})
            row11 = cursor11.fetchone()
            if row11[0] > 0:
               ret['MinFac'] = 0
            else:
               ret['MinFac'] = row11[0]
         except: 
            print("Error: unable to fetch data11")
            ret['MinFac'] = ret['Min']

         cursor12 = database.cursor ()
         sql12 = """SELECT SUM(costperingredient),programid FROM costtool_ingredients WHERE category = 'Other Inputs' AND programId IN (SELECT id FROM costtool_programs WHERE projectid = %(projectId)s) group by programid order by sum(costperingredient) asc"""
         try:
            cursor12.execute(sql12,{'projectId' : project_id})
            row12 = cursor12.fetchone()
            if row12[0] > 0:
               ret['MinInp'] = 0
            else:
               ret['MinInp'] = row12[0]

         except:
            print("Error: unable to fetch data8")
            ret['MinInp'] = ret['Min']

         ProgList.append(ret)
   except ObjectDoesNotExist:
      return HttpResponse('A Project and/or Program does not exist! Cannot proceed further.')
   return render(request,'reports/compcostanal.html', {'ProjectName': project.projectname, 'ProgList':ProgList})

def options(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')
       else:
          return render(request,'admin/options.html')

def userreports(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')
       else:
          return render(request,'admin/userreports.html')

def tech(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')
       else:
          return render(request,'admin/tech.html')

def proj_table(request):
    ProjList = []
    demoList = []
    panal = 0
    peff = 0
    prog = 0
    if 'user' not in request.session: 
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')                                                                                   
       else: 
           try:
              project = m.Projects.objects.filter(created_at__gte = datetime.date(2015, 9, 1))
              proj = m.Projects.objects.filter(user = 'Demo admin')
              for pp in proj:
                 demoList.append(pp.projectname)
              for p in project:
                 ret = {}
                 if p.projectname not in demoList:
                   ret['id'] = p.id
                   ret['projectname'] = p.projectname
                   ret['typeanalysis'] = p.typeanalysis
                   if p.typeanalysis == 'Cost Analysis':
                     panal = panal + 1
                   else:
                      peff = peff + 1
                   ret['user'] = p.user
                   ret['created_at'] = p.created_at
                   prog = prog + m.Programs.objects.filter(projectId = p.id).count()
 
                   ProjList.append(ret)
           except ObjectDoesNotExist:
              return HttpResponse('Projects do not exist! Cannot proceed further.')
           return render(request,'reports/proj_table.html', {'ProjList': ProjList, 'panal':panal, 'peff':peff, 'prog':prog})

def users_table(request):
    UsersList = []
    demoList = []
    prcount = 0
    logincount = 0
    #f = open( '/home/amritha/costtool/documents/filename.txt', 'w+' )
    if 'user' not in request.session: 
       return render(request,'prices/message.html')
    else:
       if request.session['user'] != 'Demo admin':
          return render(request,'prices/message.html')
       else: 
          try:
             proj = m.Projects.objects.filter(user = 'Demo admin')
             for pp in proj:
                demoList.append(pp.projectname)
          except ObjectDoesNotExist:
             print('Projects do not exist!')

          try:
             pricesm = m.Prices.objects.exclude(priceProvider = 'cbcse')
             prices = m.Prices.objects.filter(priceProvider = 'Demo admin')
             for pp in prices:
                demoList.append(pp.ingredient)
             for p in pricesm:
                if p.ingredient not in demoList:
             #f.write(p.ingredient)
             #f.write('\n')
             #f.write(p.priceProvider)
             #f.write('\n')
                   prcount = prcount + 1
          except ObjectDoesNotExist:
             print('Prices do not exist!')
       #f.close()
          try:
             users = m.Login.objects.all()
             uscount = m.Login.objects.all().count() 
             for u in users:
                #f.write(str(u.startDate)) 
                ret = {}
                ret['id'] = u.id
                ret['user'] = u.user
                ret['email'] = u.email
                ret['firstName'] = u.firstName
                ret['lastName'] = u.lastName
                ret['addressline1'] = u.addressline1
                ret['addressline2'] = u.addressline2
                ret['city'] = u.city
                ret['state'] = u.state
                ret['zip'] = u.zip
                ret['country'] = u.country
                ret['phone'] = u.phone
                ret['organisation'] = u.organisation
                ret['type_of_org'] = u.type_of_org
                ret['other_org'] = u.other_org
                ret['position'] = u.position
                ret['other_pos'] = u.other_pos
                ret['publicOrPrivate'] = u.publicOrPrivate
                ret['startDate'] = str(u.startDate)
                ret['endDate'] = str(u.endDate)
                ret['lastLogin'] = str(u.lastLogin)
                ret['timesLoggedin'] = u.timesLoggedin
                if u.timesLoggedin is not None:
                   logincount = logincount + int(u.timesLoggedin)

                projcount = 0
                for proj in m.Projects.objects.filter(user = u.user).filter(created_at__gte = datetime.date(2015, 9, 1)):
                   if proj.projectname not in demoList:
                     projcount = projcount + 1
                ret['projcount'] = projcount
                UsersList.append(ret)
          except ObjectDoesNotExist:
             return HttpResponse('Users do not exist! Cannot proceed further.')
          #f.close()
          return render(request,'reports/users_table.html', {'UsersList': UsersList,'uscount':uscount,'prcount':prcount, 'logincount':logincount})

def export_proj(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=projects.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Projects")

    row_num = 0
    panal = 0
    peff = 0
    prog = 0
    demoList = []

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    try:
       project = m.Projects.objects.filter(created_at__gte = datetime.date(2015, 9, 1))
       proj = m.Projects.objects.filter(user = 'Demo admin')
       for pp in proj:
          demoList.append(pp.projectname)
       for p in project:
          ret = {}
          if p.projectname not in demoList: 
             if p.typeanalysis == 'Cost Analysis':
                panal = panal + 1
             else:
                peff = peff + 1
             prog = prog + m.Programs.objects.filter(projectId = p.id).count() 
    except ObjectDoesNotExist:
       return HttpResponse('Projects do not exist! Cannot proceed further.')

    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2
    pattern3 = xlwt.Pattern()
    pattern3.pattern_fore_colour = 1
    font_style3 = xlwt.XFStyle()
    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    aL.wrap = True
    font_style3.alignment = aL
    font_style3.pattern = pattern2

    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3
    font_style4.alignment = aL
    date_style4 = xlwt.XFStyle()
    date_style4.pattern = pattern3
    date_style4.num_format_str = 'mm/dd/yyyy hh:mm'

    date_style3 = xlwt.XFStyle()
    date_style3.pattern = pattern2
    date_style3.num_format_str = 'mm/dd/yyyy hh:mm'

    font_style5 = xlwt.XFStyle()
    font_style5.font.bold = True
    font_style5.pattern = pattern

    ws.write(0, 0, "Number of Programs:", font_style5)
    ws.write(0, 1, "", font_style5)
    ws.write(0, 2, "", font_style5)
    ws.write(0, 3, prog, font_style4)
    ws.write(0, 4, "", font_style4)

    ws.write(1, 0, "Number of Cost Analysis done:", font_style5)
    ws.write(1, 1, "", font_style5)
    ws.write(1, 2, "", font_style5)
    ws.write(1, 3, panal, font_style4)
    ws.write(1, 4, "", font_style4)

    ws.write(2, 0, "Number of Cost-Effectiveness Analysis done:", font_style5)
    ws.write(2, 1, "", font_style5)
    ws.write(2, 2, "", font_style5)
    ws.write(2, 3, peff, font_style4)
    ws.write(2, 4, "", font_style4)

    cursor = database.cursor ()
    sql = """SELECT id, projectname, typeanalysis, user, CONVERT_TZ(created_at,'GMT','EST') FROM costtool_projects where projectname NOT IN (SELECT projectname FROM costtool_projects WHERE user = 'Demo Admin') and created_at >= '2015-09-01'"""

    row_num = 5

    columns = [
          (u"Id", 2000),
          (u"Name of the Project", 7000),
          (u"Type of Analysis", 7000),
          (u"User Name", 7000),
          (u"Date of creation", 7000),
    ]

    try:
       cursor.execute(sql)
       results = cursor.fetchall()
       if results != ():
          for col_num in xrange(len(columns)):
             ws.write(row_num, col_num, columns[col_num][0], font_style)
             # set column width
             ws.col(col_num).width = columns[col_num][1]

       for row in results:
          row_num += 1
          id = row[0]
          projectname = row[1]
          typeanalysis = row[2]
          user = row[3]
          created_at = row[4]
          for col_num in xrange(len(row)):
             if col_num == 4:
                ws.write(row_num, col_num, row[col_num],date_style4)
             else:
                ws.write(row_num, col_num, row[col_num],font_style4)

    except:
       print("Error: unable to fetch data")

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_users(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=users.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Users")

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
 
    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2
    pattern3 = xlwt.Pattern()
    pattern3.pattern_fore_colour = 1
    font_style3 = xlwt.XFStyle()
    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    aL.wrap = True
    font_style3.alignment = aL
    font_style3.pattern = pattern2

    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3
    font_style4.alignment = aL
    date_style4 = xlwt.XFStyle()
    date_style4.pattern = pattern3
    date_style4.num_format_str = 'mm/dd/yyyy'

    date_style3 = xlwt.XFStyle()
    date_style3.pattern = pattern2
    date_style3.num_format_str = 'mm/dd/yyyy'

    font_style5 = xlwt.XFStyle()
    font_style5.font.bold = True
    font_style5.pattern = pattern

    cursor = database.cursor ()
    sql = """SELECT id, user, email, firstName, lastName, addressline1, addressline2, city, state, zip, country, phone, organisation, type_of_org, other_org, position, other_pos, publicOrPrivate, startDate, endDate, lastLogin, timesLoggedin, (SELECT count(*) from costtool_projects where user =  l.user and projectname NOT IN (SELECT projectname FROM costtool_projects WHERE user = 'Demo Admin') and created_at >= '2015-09-01') as projcount  FROM costtool_login l"""

    demoList = []
    prcount = 0
    logincount = 0

    try:
       pricesm = m.Prices.objects.exclude(priceProvider = 'cbcse')
       prices = m.Prices.objects.filter(priceProvider = 'Demo admin')
       for pp in prices:
          demoList.append(pp.ingredient)
       for p in pricesm:
          if p.ingredient not in demoList:
             prcount = prcount + 1
    except ObjectDoesNotExist:
       print('Prices do not exist!')

    try:
       for u in m.Login.objects.all():
          if u.timesLoggedin is not None:
             logincount = logincount + int(u.timesLoggedin)
    except ObjectDoesNotExist:
       print('Users do not exist!') 

    uscount = m.Login.objects.all().count()
    
    ws.write(0, 0, "Number of Users:", font_style5)
    ws.write(0, 1, "", font_style5)
    ws.write(0, 2, "", font_style5)
    ws.write(0, 3, uscount, font_style4)
    ws.write(0, 4, "", font_style4)

    ws.write(1, 0, "Number of times Users logged in:", font_style5)
    ws.write(1, 1, "", font_style5)
    ws.write(1, 2, "", font_style5)
    ws.write(1, 3, logincount, font_style4)
    ws.write(1, 4, "", font_style4)

    ws.write(2, 0, "Number of Prices created by Users:", font_style5)
    ws.write(2, 1, "", font_style5)
    ws.write(2, 2, "", font_style5)
    ws.write(2, 3, prcount, font_style4)
    ws.write(2, 4, "", font_style4)

    row_num = 5

    columns = [
          (u"Id", 2000),
          (u"User Name", 7000),
          (u"Email", 7000),
          (u"First Name", 7000),
          (u"Last Name", 7000),
          (u"Address Line1", 7000),
          (u"Address Line2", 7000),
          (u"City", 7000),
          (u"State", 7000),
          (u"Zip", 7000),
          (u"Country", 7000),
          (u"Phone", 7000),
          (u"Organization", 7000),
          (u"Type of Organization", 7000),
          (u"Other Organization", 7000),
          (u"Position", 7000),
          (u"Other Position", 7000),
          (u"Public or Private", 7000),
          (u"Start Date of Licence", 7000),
          (u"Licence Expiry Date", 7000),
          (u"Date Last Logged in", 7000),
          (u"Number of times Logged in", 7000),
          (u"Number of Projects", 7000)
    ]

    try:
       cursor.execute(sql)
       results = cursor.fetchall()
       if results != ():
          for col_num in xrange(len(columns)):
             ws.write(row_num, col_num, columns[col_num][0], font_style)
             # set column width
             ws.col(col_num).width = columns[col_num][1]

       for row in results:
          row_num += 1
          id = row[0]
          user = row[1]
          email = row[2]
          firstName = row[3]
          lastName = row[4]
          addressline1 = row[5]
          addressline2 = row[6]
          city = row[7]
          state = row[8]
          zip = row[9]
          country = row[10]
          phone = row[11]
          organisation = row[12]
          type_of_org = row[13]
          other_org = row[14]
          position = row[15]
          organisation = row[16]
          publicOrPrivate = row[17]
          startDate = row[18]
          endDate = row[19]
          lastLogin = row[20]
          timesLoggedin = row[21]
          projcount = row[22]
          for col_num in xrange(len(row)):
              if col_num == 18 or col_num == 19 or col_num == 20:
                ws.write(row_num, col_num, row[col_num],date_style4)
              else:
                ws.write(row_num, col_num, row[col_num],font_style4)

    except:
       print("Error: unable to fetch data")

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def del_user(request, user_id):
    context = RequestContext(request)
    user = m.Login.objects.get(pk=user_id)

    for pr in m.Projects.objects.filter(user = user.user):
       for p in m.Programs.objects.filter(projectId = pr.id):
          try:
             m.Distribution.objects.filter(programId=p.id).delete()
          except ObjectDoesNotExist:
             print('distribution do not exist')

          try:
             m.Agencies.objects.filter(programId=p.id).delete()
          except ObjectDoesNotExist:
             print('agencies do not exist')

          try:
             m.Transfers.objects.filter(programId=p.id).delete()
          except ObjectDoesNotExist:
             print('transfers do not exist')

          try:
             m.Ingredients.objects.filter(programId=p.id).delete()
          except ObjectDoesNotExist:
             print('ingredients do not exist')

          try:
             m.Effectiveness.objects.get(programId_id = p.id).delete()
          except ObjectDoesNotExist:
             print('effectiveness does not exist')

          try:
             progdesc = m.ProgramDesc.objects.get(programId_id = p.id)
             m.ParticipantsPerYear.objects.filter(programdescId_id = progdesc.id).delete()
             m.ProgramDesc.objects.get(programId_id = p.id).delete()
          except ObjectDoesNotExist:
             print('program desc does not exist')

          m.Programs.objects.get(pk = p.id).delete()

       m.InflationIndices.objects.filter(projectId=pr.id).delete()
       m.GeographicalIndices.objects.filter(projectId=pr.id).delete()
       m.Settings.objects.get(projectId=pr.id).delete()
       m.Projects.objects.get(pk=pr.id).delete()

    m.Prices.objects.filter(priceProvider = user.user).delete()   
    m.Login.objects.get(pk=user_id).delete()
    return HttpResponseRedirect('/reports/users_table.html')

def login(request):
   context = RequestContext(request)
   if 'user' in request.session:
      del request.session['user']
   if 'password' in request.session:   
      del request.session['password']

   if request.method == 'POST':
      loginform = LoginForm(request.POST)
      if loginform.is_valid():
         login = loginform.save(commit=False)
         request.session['user'] = login.user
         request.session['password'] = login.password
         try:
            login2 = m.Login.objects.filter(user=login.user).latest('startDate')
            if login.password == login2.password:
               if login2.user not in ('Additional projects', 'Demo admin', 'cbcse', 'teaching account') and login2.endDate <= date.today():
                  return render('login/login.html',{'loginform': loginform, 'err': 'Your license agreement has expired.  Please re-register from the Home page. If you wish to continue using your existing account, re-register with the same User name. You may change your password and any other information that needs updating.'}, context)
               else: 
                  login2.lastLogin = datetime.datetime.now()
                  if login2.timesLoggedin is None:
                     login2.timesLoggedin = 1
                  else:
                     login2.timesLoggedin = login2.timesLoggedin + 1
                  login2.save(update_fields=['lastLogin', 'timesLoggedin']) 
                  return HttpResponseRedirect('/project/project_list.html')
            else:
               return render('login/login.html',{'loginform': loginform, 'err': 'Invalid user or password'}, context)
         except ObjectDoesNotExist:
            return render('login/login.html',{'loginform': loginform, 'err': 'Invalid user or password'}, context)
 
      else:
         form_errors = 'Yes'
         print(form_errors)
   else:
      loginform = LoginForm()

   return render('login/login.html',{'loginform': loginform}, context)

def myaccount(request):
    context = RequestContext(request)
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'ccc'
    try:
       login = m.Login.objects.filter(user=loggedinuser).latest('startDate')
       if request.method == 'POST':
          adminform = AdminForm(request.POST)
          if adminform.is_valid():
             a = adminform.save(commit=False)
             if a.oldemail  == '' and a.email == '' and a.emailagain == '' and a.oldpassword  == '' and a.password == '' and a.passwordagain == '':
                return render('admin/myaccount.html',{'adminform':adminform,'err':'Enter either the email or the password to Save'}, context)
             else:
                if a.oldemail != '' or a.email != '' or a.emailagain != '':
                   try:
                      l = m.Login.objects.filter(user=loggedinuser, email=a.oldemail).latest('startDate')
                      if (a.oldemail is not None and (a.email == '' or a.emailagain == '')) or (a.email is not None and (a.oldemail == '' or a.emailagain == '')) or (a.emailagain is not None and (a.email == '' or a.oldemail == '')):
                         return render('admin/myaccount.html',{'adminform':adminform,'err':'Enter the old email, new email and new email again to Save'}, context)
                      elif a.email != a.emailagain:
                         return render('admin/myaccount.html',{'adminform':adminform,'err':'The new email does not match the email entered again'}, context)
                   except:
                      return render('admin/myaccount.html',{'adminform':adminform,'err':'The old email you have entered does not match the email we have in our records. '}, context)
                else:
                   try:
                      p = m.Login.objects.filter(user=loggedinuser, password=a.oldpassword).latest('startDate')
                      if (a.oldpassword is not None and (a.password == '' or a.passwordagain == '')) or (a.password is not None and (a.oldpassword == '' or a.passwordagain == '')) or (a.passwordagain is not None and (a.password == '' or a.oldpassword == '')):
                         return render('admin/myaccount.html',{'adminform':adminform,'err':'Enter the old password, new password and new password again to Save'}, context)
                      elif a.password != a.passwordagain:
                         return render('admin/myaccount.html',{'adminform':adminform,'err':'The new password does not match the password entered again'}, context)
                   except:
                      return render('admin/myaccount.html',{'adminform':adminform,'err':'The old password you have entered does not match the password we have in our records. '}, context)
                if a.email != '' and a.password != '':
                   l.email = a.email
                   l.password = a.password
                   l.save(update_fields=['email','password'])
                   return HttpResponseRedirect('/project/project_list.html')
                elif a.email != '':
                   l.email = a.email
                   l.save(update_fields=['email'])
                   return HttpResponseRedirect('/project/project_list.html')
                elif a.password != '':
                   p.password = a.password
                   p.save(update_fields=['password'])
                   return HttpResponseRedirect('/project/project_list.html')
          else:
             print(adminform.errors)
       else:
          adminform = AdminForm()

       return render(
            'admin/myaccount.html',
            {'adminform': adminform}, context)
    except ObjectDoesNotExist:
       return render(request,'prices/message.html')

def forgot(request):
    context = RequestContext(request)
    message = ""

    if request.method == 'POST':
       registerform = ForgotForm(request.POST)
       if registerform.is_valid():
          register = registerform.save(commit=False)
          r2 = m.Login.objects.filter(email = register.email)
          if len(r2) == 0:
             return render('login/forgot.html',{'registerform':registerform,'err':'The email address you have entered does not match what we have in our records. Please enter again.'}, context)
          for r in r2:
             today = date.today()
             if r.endDate > today:
                # Define these once; use them twice!
                strFrom = 'cbcsecosttoolkit@gmail.com'
                #strFrom = 'fmh7@tc.columbia.edu'
                strTo = r.email

                # Create the root message and fill in the from, to, and subject headers
                msgRoot = MIMEMultipart('related')
                msgRoot['Subject'] = 'Login details to CostOut'
                msgRoot['From'] = strFrom
                msgRoot['To'] = strTo
                msgRoot.preamble = 'This is a multi-part message in MIME format.'
                # Encapsulate the plain and HTML versions of the message body in an
                # 'alternative' part, so message agents can decide which they want to display.
                msgAlternative = MIMEMultipart('alternative')
                msgRoot.attach(msgAlternative)

                msgText = MIMEText('This is the alternative plain text message.')
                msgAlternative.attach(msgText)

                # We reference the image in the IMG SRC attribute by the ID we give it below
                msgText = MIMEText('The User Name you used to log in to <i> CostOut</i> is: <br><b>' + r.user + '</b><br>Your Password is: <br><b>' + r.password + '</b><br><br>If you need to contact the <i>CostOut</i> team, please email fmh7@tc.columbia.edu.', 'html')
                msgAlternative.attach(msgText)

                # Send the email (this example assumes SMTP authentication is required)
                try:
                   import smtplib
                   smtp = smtplib.SMTP()
                   smtp = smtplib.SMTP('smtp.gmail.com:587')
                   smtp.ehlo()
                   smtp.starttls()
                   about = m.About.objects.get(id = 1)
                   smtp.login('cbcsecosttoolkit@gmail.com', about.sendemail)
                   #smtp.login('fmh7@tc.columbia.edu', about.sendemail)
                   smtp.sendmail(strFrom, strTo, msgRoot.as_string())
                   smtp.quit()
                #changed   
                except:
                   return render('login/forgot.html',{'registerform':registerform,'err':str(error)}, context) 
             #else:
                 #mesg = 'Your license agreement has expired.  Please re-register from the Home page.'
                 #return render('login/forgot.html',{'registerform':registerform,'err':mesg}, context)  
          return HttpResponseRedirect('/login/login.html')
       else:
             print(registerform.errors)
             return render('login/forgot.html',{'registerform':registerform,'err':registerform.errors}, context)
    else:
       registerform = ForgotForm()

    return render(
            'login/forgot.html',
            {'registerform': registerform}, context)

def register(request):
   context = RequestContext(request)
   if request.method == 'POST':
      registerform = RegisterForm(request.POST)
      if registerform.is_valid():
         register = registerform.save(commit=False)
         try:
            login = m.Login.objects.filter(user=register.user).latest('startDate')
            if login.endDate > date.today():
               return render('register/register.html',{'registerform': registerform, 'err': 'The User Name you have entered already exists. Please select another one.'}, context)  
         except ObjectDoesNotExist:
            print ('xyz')   
         if register.password != register.passwordagain:                                                                              
            return render('register/register.html',{'registerform': registerform, 'err': 'The password does not match the confirm password.'}, context)         
         if register.email != register.emailagain:
            return render('register/register.html',{'registerform': registerform, 'err': 'The email does not match the confirm email.'}, context)
         request.session['userR'] = register.user
         request.session['email'] = register.email
         request.session['passwordR'] = register.password
         request.session['firstName'] = register.firstName
         request.session['lastName'] = register.lastName
         #request.session['addressline1'] = register.addressline1
         #request.session['addressline2'] = register.addressline2
         #request.session['city'] = register.city
         request.session['state'] = register.state
         #request.session['zip'] = register.zip
         request.session['country'] = register.country
         #request.session['phone'] = register.phone
         request.session['organisation'] = register.organisation
         request.session['type_of_org'] = register.type_of_org
         request.session['other_org'] = register.other_org
         request.session['position'] = register.position
         request.session['other_pos'] = register.other_pos
         request.session['publicOrPrivate'] = register.publicOrPrivate 
         return HttpResponseRedirect('/register/license.html') 
      else:
         print(registerform.errors)
          
   else:                                                                                                                            
      registerform = RegisterForm()
                                                             
   return render('register/register.html',{'registerform': registerform}, context)

def license(request):
   context = RequestContext(request)

   if 'publicOrPrivate' in request.session:
      publicOrPrivate = request.session['publicOrPrivate']
   else:
      publicOrPrivate = 'Public' 

   temp_var = 'a'
 
   if request.method == 'POST':
      licenseform = License(request.POST)
      if licenseform.is_valid():
         license = licenseform.save(commit=False)
         if license.licenseSigned == 'Yes':
            #if request.session['phone'] is not None and request.session['phone'] != '':
               #m.Login.objects.create(user=request.session['userR'], email=request.session['email'],password=request.session['passwordR'],firstName=request.session['firstName'],lastName=request.session['lastName'],addressline1=request.session['addressline1'],addressline2=request.session['addressline2'],city=request.session['city'],state=request.session['state'],zip=request.session['zip'],country=request.session['country'],phone=request.session['phone'],organisation=request.session['organisation'],position=request.session['position'],publicOrPrivate=request.session['publicOrPrivate'], licenseSigned ='Yes',endDate= datetime.datetime.now() + relativedelta(years=2)) 
            #else:
            m.Login.objects.create(user=request.session['userR'], email=request.session['email'],password=request.session['passwordR'],firstName=request.session['firstName'],lastName=request.session['lastName'],state=request.session['state'],country=request.session['country'],organisation=request.session['organisation'],type_of_org=request.session['type_of_org'],other_org=request.session['other_org'],position=request.session['position'],other_pos=request.session['other_pos'],publicOrPrivate=request.session['publicOrPrivate'], licenseSigned ='Yes',endDate= datetime.datetime.now() + relativedelta(years=2))
            try:
               existing = m.Login.objects.get(user=request.session['userR'])                                                                                                                                              
               temp_var = 'b'
            except MultipleObjectsReturned:
               print('there is more than one login with same user name')
            except ObjectDoesNotExist:   
               temp_var = 'b'
               print('object does not exist')

            if temp_var == 'b': 
               for p1 in m.Prices.objects.filter(priceProvider = 'Demo admin'):
                  pr = m.Prices.objects.get(pk=p1.id)
                  pr.priceProvider = request.session['userR']
                  pr.pk = None
                  pr.save()

               for p in m.Projects.objects.filter(user = 'Demo admin'):
                  obj = m.Projects.objects.get(pk=p.id)
                  obj.user = request.session['userR'] 
                  obj.created_at = datetime.datetime.now()
                  obj.pk = None
                  obj.save()
               
                  for i in m.InflationIndices.objects.filter(projectId=p.id):
                     inf = m.InflationIndices.objects.get(pk=i.id)
                     inf.projectId = obj.id
                     inf.pk = None
                     inf.save()

                  for g in  m.GeographicalIndices.objects.filter(projectId=p.id):
                     geo = m.GeographicalIndices.objects.get(pk=g.id)
                     geo.projectId = obj.id
                     geo.pk = None
                     geo.save()

                  sett = m.Settings.objects.get(projectId=p.id)
                  sett.projectId = obj.id
                  sett.pk = None
                  sett.save()
 
                  for pr in m.Programs.objects.filter(projectId = p.id): 
                     prog = m.Programs.objects.get(pk = pr.id)
                     prog.projectId = obj.id
                     prog.pk = None
                     prog.save()

                     try:
                        progdesc = m.ProgramDesc.objects.get(programId_id = pr.id)
                        progdesc.programId_id = prog.id
                        old_progdesc_id = progdesc.pk
                        progdesc.pk = None
                        progdesc.save()
                        for part in m.ParticipantsPerYear.objects.filter(programdescId_id = old_progdesc_id):
                           ppy = m.ParticipantsPerYear.objects.get(pk = part.id)
                           ppy.programdescId_id = progdesc.id
                           ppy.pk = None
                           ppy.save()
                     except ObjectDoesNotExist:
                        print('program desc does not exist')

                     try:
                        eff = m.Effectiveness.objects.get(programId_id = pr.id)
                        eff.programId_id = prog.id
                        eff.pk = None
                        eff.save()
                     except ObjectDoesNotExist:
                        print('effectiveness does not exist')

                     try:
                        for i in  m.Ingredients.objects.filter(programId=pr.id):
                           ing = m.Ingredients.objects.get(pk = i.id)
                           ing.programId = prog.id 
                           ing.pk = None
                           ing.save()
                           try:
                              dis = m.Distribution.objects.get(ingredientId = i.id)
                              dis.programId = prog.id
                              dis.ingredientId = ing.id 
                              dis.pk = None
                              dis.save()
                           except ObjectDoesNotExist:
                              print('distribution do not exist')
                     except ObjectDoesNotExist:
                        print('ingredients do not exist')

                     try:
                        ag = m.Agencies.objects.get(programId=pr.id)
                        ag.programId = prog.id
                        ag.pk = None
                        ag.save()
                     except ObjectDoesNotExist:
                        print('agencies do not exist')

                     try:
                        for t in m.Transfers.objects.filter(programId=pr.id):
                           trans = m.Transfers.objects.get(pk=t.id)
                           trans.programId = prog.id 
                           trans.pk = None
                           trans.save()
                     except ObjectDoesNotExist:
                        print('transfers do not exist')

            return HttpResponseRedirect('/login/login.html')
         else:        
            return HttpResponseRedirect('/about.html')
      else:
         form_errors = 'Select Yes or No to proceed'
         return render('register/license.html',{'licenseform': licenseform, 'form_errors':form_errors, 'publicOrPrivate':'publicOrPrivate'}, context)
   else:                                                                                                                            
      licenseform = License()
   return render('register/license.html',{'licenseform': licenseform, 'publicOrPrivate':'publicOrPrivate'}, context)

def return_pdf(request):
   publicOrPrivate=request.session['publicOrPrivate']
   if publicOrPrivate == 'Public':
      with open('/home/amritha/costtool/documents/Online Public Institution Tool Kit License.pdf', 'r') as pdf:
         response = HttpResponse(pdf.read(), content_type='application/pdf')
         response['Content-Disposition'] = 'inline;filename=Online Public Institution Tool Kit License.pdf'
         return response
      pdf.closed
   else:
      with open('/home/amritha/costtool/documents/Online Private Institution Tool Kit License.pdf', 'r') as pdf:
         response = HttpResponse(pdf.read(), content_type='application/pdf')
         response['Content-Disposition'] = 'inline;filename=Online Private Institution Tool Kit License.pdf'
         return response
      pdf.closed

def quickstart(request):
   with open('/home/amritha/costtool/documents/Quickstart.docx', 'r') as docx:
      response = HttpResponse(docx.read(), content_type='application/docx')
      response['Content-Disposition'] = 'inline;filename=Quickstart.docx'
      return response
   docx.closed

def tutorial1_pdf(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Tutorial 1 Add personnel ingredient.pdf', 'r') as pdf:                             
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Tutorial 1 Add personnel ingredient.pdf'
          return response
       pdf.closed

def tutorial2_pdf(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Tutorial 2 Adding a new ingredient.pdf', 'r') as pdf:     
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Tutorial 2 Adding a new ingredient.pdf'
          return response
       pdf.closed

def tutorial3_pdf(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Tutorial 3 How to choose a price.pdf', 'r') as pdf:
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Tutorial 3 How to choose a price.pdf'
          return response
       pdf.closed
   
def tutorial4_pdf(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Tutorial 4 Project Settings.pdf', 'r') as pdf:
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Tutorial 4 Project Settings.pdf'                                          
          return response                                                                                                                    
       pdf.closed

def tutorial5_pdf(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Tutorial 5 Adding facilities prices.pdf', 'r') as pdf:
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Tutorial 5 Adding facilities prices.pdf'                                       
          return response
       pdf.closed

def tutorials(request):
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'ccc'
    try:
       login = m.Login.objects.filter(user=loggedinuser).latest('startDate')
       return render(request,'tutorials.html')
    except ObjectDoesNotExist:
       return render(request,'prices/message.html')

def imports(request):
    return render(request,'prices/imports.html')

def license2(request):
    return render(request,'license2.html')

def private_pdf(request):
   with open('/home/amritha/costtool/documents/Online Private Institution Tool Kit License.pdf', 'r') as pdf:
      response = HttpResponse(pdf.read(), content_type='application/pdf')
      response['Content-Disposition'] = 'inline;filename=Online Private Institution Tool Kit License.pdf'
      return response
   pdf.closed

def public_pdf(request):
   with open('/home/amritha/costtool/documents/Online Public Institution Tool Kit License.pdf', 'r') as pdf:
      response = HttpResponse(pdf.read(), content_type='application/pdf')
      response['Content-Disposition'] = 'inline;filename=Online Public Institution Tool Kit License.pdf'
      return response
   pdf.closed

'''def tech1(request):
   with open('/home/amritha/costtool/documents/Internal_Updating the CostOut Database Handbook.docx', 'r') as docx:
      response = HttpResponse(docx.read(), content_type='application/docx')
      response['Content-Disposition'] = 'inline;filename=Internal_Updating the CostOut Database Handbook.docx'
      return response
   docx.closed
'''
def tech2(request):
   with open('/home/amritha/costtool/documents/Developer Instructions.docx', 'r') as docx:
      response = HttpResponse(docx.read(), content_type='application/docx')
      response['Content-Disposition'] = 'inline;filename=Developer Instructions.docx'
      return response
   docx.closed

def additional(request):
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'ccc'
    try:
       login = m.Login.objects.filter(user=loggedinuser).latest('startDate')
       return render(request,'additional.html')
    except ObjectDoesNotExist:
       return render(request,'prices/message.html')

def xl1(request):
   with open('/home/amritha/costtool/documents/DBofPrices.xlsx', 'r') as xlsx:
      response = HttpResponse(xlsx.read(), content_type='application/xlsx')
      response['Content-Disposition'] = 'inline;filename=DBofPrices.xlsx'
      return response
   xlsx.closed

def xl2(request):
   with open('/home/amritha/costtool/documents/InflationIndex.xlsx', 'r') as xlsx:
      response = HttpResponse(xlsx.read(), content_type='application/xlsx')
      response['Content-Disposition'] = 'inline;filename=InflationIndex.xlsx'
      return response
   xlsx.closed

def xl3(request):
   with open('/home/amritha/costtool/documents/GeographicalIndex.xlsx', 'r') as xlsx:
      response = HttpResponse(xlsx.read(), content_type='application/xlsx')
      response['Content-Disposition'] = 'inline;filename=GeographicalIndex.xlsx'
      return response
   xlsx.closed

def doc1(request):
   with open('/home/amritha/costtool/documents/Internal_Updating the CostOut Database Handbook.docx', 'r') as docx:
      response = HttpResponse(docx.read(), content_type='application/docx')
      response['Content-Disposition'] = 'inline;filename=Internal_Updating the CostOut Database Handbook.docx'
      return response
   docx.closed

def doc2(request):
   with open('/home/amritha/costtool/documents/Tutorial template.docx', 'r') as docx:
      response = HttpResponse(docx.read(), content_type='application/docx')
      response['Content-Disposition'] = 'inline;filename=Tutorial template.docx'
      return response
   docx.closed

def doc3(request):
   with open('/home/amritha/costtool/documents/Developer Instructions.docx', 'r') as docx:
      response = HttpResponse(docx.read(), content_type='application/docx')
      response['Content-Disposition'] = 'inline;filename=Developer Instructions.docx'
      return response
   docx.closed

def add1(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Average Size of Educational Facilities.xlsx', 'r') as xlsx:
          response = HttpResponse(xlsx.read(), content_type='application/xlsx')
          response['Content-Disposition'] = 'inline;filename=Average Size of Educational Facilities.xlsx'
          return response
       xlsx.closed

def add2(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Calculating Cost Differences Between Programs.pdf', 'r') as pdf:
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Calculating Cost Differences Between Programs.pdf'
          return response
       pdf.closed

def add3(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/CostOut Feedback Form.docx', 'r') as docx:
          response = HttpResponse(docx.read(), content_type='application/docx')
          response['Content-Disposition'] = 'inline;filename=CostOut Feedback Form.docx'
          return response
       docx.closed

def add4(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Database of Benefits Rates.xls', 'r') as xlsx:
          response = HttpResponse(xlsx.read(), content_type='application/xls')
          response['Content-Disposition'] = 'inline;filename=Database of Benefits Rates.xls'
          return response
       xlsx.closed

def add5(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Example Interview Protocol.pdf', 'r') as pdf:
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Example Interview Protocol.pdf'
          return response
       pdf.closed

def add6(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Formulas used in CostOut.pdf', 'r') as pdf:
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Formulas used in CostOut.pdf'
          return response
       pdf.closed

def add7(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Sources of Prices and Benefits.pdf', 'r') as pdf:
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Sources of Prices and Benefits.pdf'
          return response
       pdf.closed

def add8(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/Finding National Prices.pdf', 'r') as pdf:
          response = HttpResponse(pdf.read(), content_type='application/pdf')
          response['Content-Disposition'] = 'inline;filename=Finding National Prices.pdf'
          return response
       pdf.closed

def manual(request):
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'ccc'
    try:
       login = m.Login.objects.filter(user=loggedinuser).latest('startDate')
       return render(request,'manual.html')
    except ObjectDoesNotExist:
       return render(request,'prices/message.html')

def manual1(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/CostOut Manual 2015.docx', 'r') as docx:
          response = HttpResponse(docx.read(), content_type='application/docx')
          response['Content-Disposition'] = 'inline;filename=CostOut Manual 2015.docx'
          return response
       docx.closed

def manual2(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       with open('/home/amritha/costtool/documents/CostOut Screenshots.docx', 'r') as docx:
          response = HttpResponse(docx.read(), content_type='application/docx')
          response['Content-Disposition'] = 'inline;filename=CostOut Screenshots.docx'
          return response
       docx.closed

def full_table(request):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    if 'projectname' in request.session:
       projectname = request.session['projectname']
    else:
       projectname = 'ccc'
    if 'programname' in request.session:
       progname = request.session['programname']
    else:
       progname = 'ccc'
    result = 0
    upd = 0
    total_cost = 0
    avg_cost = ''
    avg_eff = None
    eff_ratio = None

    try:
       sett = m.Settings.objects.get(projectId=request.session['project_id'])
       discountRateEstimates = sett.discountRateEstimates
       try:
          infEstimate = m.InflationIndices.objects.get(projectId=request.session['project_id'],yearCPI=sett.yearEstimates)
       except ObjectDoesNotExist:
          infEstimate = 'No inflation index available' 

       try:    
          geoEstimate = m.GeographicalIndices.objects.get(projectId=request.session['project_id'],stateIndex=sett.stateEstimates,areaIndex=sett.areaEstimates)
       except ObjectDoesNotExist:
          geoEstimate = 'No geographical index available'

    except ObjectDoesNotExist:
       discountRateEstimates = 'No discount rate' 

    try:
       ingredients = m.Ingredients.objects.filter(programId = program_id)
       for i in ingredients:
          total_cost = i.totalCost
          avg_cost = i.averageCost
          eff_ratio = i.effRatio
    except ObjectDoesNotExist:
       total_cost = 0                                                                                                                
       avg_cost = ''
       eff_ratio = None

    if request.method == 'POST' and request.is_ajax():
       if 'id' in request.POST:
          changed = False
          i = m.Ingredients.objects.get(pk=request.POST.get('id'))
          if i.ingredient != request.POST.get('ingredient'):
             i.ingredient = request.POST.get('ingredient')
             changed = True
          if i.notes != request.POST.get('notes'):
             i.notes = request.POST.get('notes')
             changed = True
          if i.category != request.POST.get('category'):
             i.category = request.POST.get('category')
             changed = True
          if str(i.yearQtyUsed) != str(request.POST.get('yearQtyUsed')):
             i.yearQtyUsed = request.POST.get('yearQtyUsed')
             changed = True
          if i.variableFixed != request.POST.get('variableFixed'):
             i.variableFixed = request.POST.get('variableFixed')
             changed = True
          if i.quantityUsed != request.POST.get('quantityUsed'):
             i.quantityUsed = request.POST.get('quantityUsed')
             changed = True
          if i.quantityUsed is None:
             i.quantityUsed = 1
          if i.lifetimeAsset != request.POST.get('lifetimeAsset'):
             i.lifetimeAsset = request.POST.get('lifetimeAsset')
             changed = True
          if i.interestRate != request.POST.get('interestRate'):
             i.interestRate = request.POST.get('interestRate')
             changed = True
          if i.benefitRate != request.POST.get('benefitRate'):
             i.benefitRate = request.POST.get('benefitRate')
             changed = True
          if str(i.percentageofUsage) != str(request.POST.get('percentageofUsage')):
             i.percentageofUsage = request.POST.get('percentageofUsage')
             changed = True
          #if changed == True:   
          if i.lifetimeAsset == 1 or i.lifetimeAsset == '1':
             i.priceAdjAmortization = float(i.convertedPrice)
          else:
             if i.interestRate == '0.0' or i.interestRate == 0.0 or i.interestRate == '0':
                i.priceAdjAmortization = float(i.convertedPrice) / float(i.lifetimeAsset)
             else:
                i.priceAdjAmortization = float(i.convertedPrice) * ((float(i.interestRate)/100)*math.pow((1+(float(i.interestRate)/100)),float(i.lifetimeAsset)))/ (math.pow((1+(float(i.interestRate)/100)),float(i.lifetimeAsset))-1)
          if i.category == 'Personnel':
             if i.benefitRate is None or i.benefitRate == 'None':
                i.priceAdjBenefits = i.priceAdjAmortization
             else:
                i.priceAdjBenefits = float(i.priceAdjAmortization) * (1 + float(i.benefitRate)/float(100))
          else:
             i.priceAdjBenefits = i.priceAdjAmortization

          i.save(update_fields=['ingredient','notes','category','yearQtyUsed','variableFixed','quantityUsed','lifetimeAsset','interestRate','benefitRate', 'percentageofUsage','priceAdjAmortization','priceAdjBenefits'])
          result = calculations2(project_id, program_id)
          upd = updateDate(project_id, program_id)
       else:
          print('no id given')
    return render('project/programs/costs/full_table.html',{'ingredients':ingredients,'project_id':project_id, 'program_id':program_id,'total_cost':round(total_cost,3),'avg_cost':avg_cost,'eff_ratio':eff_ratio,'projectname':projectname, 'programname':progname, 'discountRateEstimates':discountRateEstimates, 'infEstimate':infEstimate,'geoEstimate':geoEstimate, 'geoArea':'' },context)

def tabbedlayout(request,project_id,program_id):
    project = m.Projects.objects.get(pk=project_id)
    program = m.Programs.objects.get(pk=program_id)

    request.session['program_id'] = program_id
    request.session['projectname'] = project.projectname
    request.session['programname'] = program.progname
    loggedinuser = request.session['user']

    effectform = EffectForm()
    total_cost = 0                                                                                                                                    
    avg_cost = ''
    upd = 0
    avg_eff = None
    eff_ratio = None
    noofyears = ''
    total_agency1 = 0.0
    total_agency2 = 0.0
    total_agency3 = 0.0
    total_agency4 = 0.0
    total_other = 0.0
    net_agency1 = 0.0
    net_agency2 = 0.0
    net_agency3 = 0.0
    net_agency4 = 0.0
    net_other = 0.0
    agcount = 0
    noofpart = 0
    IngFormSet = modelformset_factory(m.Ingredients,extra=20)
    ingform = IngFormSet(queryset = m.Ingredients.objects.filter(programId = program_id),prefix="ingform")
    try:
        programdesc = m.ProgramDesc.objects.get(programId=program_id)
        form1 = ProgramDescForm(request.POST, instance=programdesc)
        numberofparticipants = programdesc.numberofparticipants
        noofyears = programdesc.numberofyears
        progid = programdesc.id
        objectexists = True
        recordExists = True
        if numberofparticipants is None:
           noofpart = 0
        else:
           noofpart = numberofparticipants
        old_total = 0
        for q in m.ParticipantsPerYear.objects.filter(programdescId=programdesc.id):
           old_total = old_total + q.noofparticipants

    except ObjectDoesNotExist:
        form1 = ProgramDescForm(request.POST)
        numberofparticipants = 1
        noofyears = 1
        progid = 0
        old_total = 0
        objectexists = False
        recordExists = False
        noofpart = 0
    
    try:
       effect = m.Effectiveness.objects.get(programId_id=program_id)
       effectform = EffectForm(request.POST, instance=effect)
       avgeff = effect.avgeffectperparticipant
       effobjexists = True
    except ObjectDoesNotExist:
       effectform = EffectForm(request.POST)
       effobjexists = False
       avgeff = None    

    try:
        ing = m.Ingredients.objects.filter(programId = program_id)
        for i in ing:
           total_cost = i.totalCost
           avg_cost = i.averageCost
           eff_ratio = i.effRatio
    except ObjectDoesNotExist:
       total_cost = 0
       avg_cost = ''
       eff_ratio = None    
    
    try:
       ing2 = m.Ingredients.objects.get(programId = program_id)
       recordExists = True
       ingRecordExists = 'True'
    except MultipleObjectsReturned:
       recordExists = True
       ingRecordExists = 'True'
    except ObjectDoesNotExist:
       recordExists = False
       ingRecordExists = 'False' 

    DistFormSet = modelformset_factory(m.Distribution,form=DistForm,extra=20)
    distform = DistFormSet(prefix="distform")

    try:
       ag = m.Agencies.objects.get(programId = program_id)
       agcount = 0
       agency1 = ag.agency1
       agency2 = ag.agency2
       agency3 = ag.agency3
       agency4 = ag.agency4
       if ag.agency1 is not None and ag.agency1 != '':
          agcount = agcount + 1
       if ag.agency2 is not None and ag.agency2 != '':
          agcount = agcount + 1
       if ag.agency3 is not None and ag.agency3 != '':
          agcount = agcount + 1
       if ag.agency4 is not None and ag.agency4 != '':
          agcount = agcount + 1
    except ObjectDoesNotExist:
       agency1 = 'Program Sponsor' 
       agency2 = 'Government Agencies'
       agency3 = 'Private Organizations'
       agency4 = 'Students/Parents'
    
    PartFormSet = inlineformset_factory(m.ProgramDesc,m.ParticipantsPerYear,form=ParticipantsForm,extra=10)
    if objectexists:
        try:
            partform = PartFormSet(request.POST,request.FILES, instance=programdesc,prefix="partform" )
            partobjexists = True
        except ObjectDoesNotExist:
            partform = PartFormSet(request.POST, request.FILES,prefix="partform")
            partobjexists = False
    else:
        partform = PartFormSet(request.POST, request.FILES,prefix="partform")
        partobjexists = False

    if partobjexists:
        partform = PartFormSet( instance=programdesc,prefix="partform")
    else:
        partform = PartFormSet(prefix="partform")   

    TransFormSet = modelformset_factory(m.Transfers,extra=20)
    try:
        ag = m.Agencies.objects.get(programId = program_id)
        trans = m.Transfers.objects.filter(programId = program_id) 
        transform = TransFormSet(queryset = trans,prefix="transform")
    except ObjectDoesNotExist:
        transform = TransFormSet(prefix="transform")

    if request.method == 'POST':
        if 'submit1' in request.POST:
            if form1.is_valid():
               id = form1.save(commit=False)
               id.numberofyears = 1
               id.programId = program
               id.save()
               upd = updateDate(project_id, program_id)
               programdesc = m.ProgramDesc.objects.get(pk=id.id)
               partform = PartFormSet(request.POST,request.FILES, instance=programdesc,prefix="partform" )
               if partform.is_valid():
                  partform.save()
                  upd = updateDate(project_id, program_id)
                  m.ParticipantsPerYear.objects.filter(noofparticipants__isnull=True).delete()
                  queryset = m.ParticipantsPerYear.objects.filter(programdescId=id.id)
                  programdesc.numberofyears=queryset.count()
                  total = 0
                  if (m.ParticipantsPerYear.objects.filter(programdescId=id.id).count() == 0) and programdesc.lengthofprogram == 'More than one year':
                     errtext = 'You have selected the length of the program as More than one year but have not entered the number of participants per year.'
                     return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart, 'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'errtext':errtext,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'form1','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'partform.errors':partform.errors,'frm2':effectform,'frm4':distform, 'frm5':transform, 'loggedinuser':loggedinuser})

                  else:
                     for q in queryset:
                        total = float(total) + float(q.noofparticipants) 
                     #if (numberofparticipants == programdesc.numberofparticipants or programdesc.numberofparticipants is None) and total != 0:
                     if total != old_total: 
                        programdesc.numberofparticipants = total / programdesc.numberofyears   
                  if programdesc.lengthofprogram == 'One year or less':
                     programdesc.numberofyears = 1 
                     m.ParticipantsPerYear.objects.filter(programdescId=id.id).delete()
                  programdesc.save()
                  upd = updateDate(project_id, program_id)
                  ing = m.Ingredients.objects.filter(programId = program_id)
                  for i in ing:
                     if programdesc.numberofparticipants is not None:
                        if programdesc.numberofparticipants == 0:
                           i.averageCost = float(i.totalCost) / float("inf")
                        else:
                           i.averageCost = float(i.totalCost) / float(programdesc.numberofparticipants)
                        avg_cost = round(i.averageCost,2)
                     else:
                        i.averageCost = None 
                     if avgeff is not None  and i.averageCost is not None:
                         if avgeff == '0':
                            i.effRatio = None                                                                                                
                            eff_ratio = None
                         else:   
                            i.effRatio = float(i.averageCost) / float(avgeff)
                            eff_ratio = round(i.effRatio,2)
                     else:   
                        i.effRatio = None 
                     try:
                        partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=programdesc.id, yearnumber=i.yearQtyUsed)                 
                        if i.costPerIngredient is not None:
                           i.costPerParticipant = float(i.costPerIngredient) / float(partperyear.noofparticipants)
                     except ObjectDoesNotExist:
                        if i.costPerIngredient is not None:
                           if numberofparticipants == 0:
                              i.costPerParticipant = float(i.costPerIngredient) / float("inf")
                           else:
                              if programdesc.numberofparticipants is not None:
                                 i.costPerParticipant = float(i.costPerIngredient) / float(programdesc.numberofparticipants)
                              else:
                                 i.costPerParticipant = float(i.costPerIngredient) / float(numberofparticipants) 
                     i.save(update_fields=['averageCost','effRatio','costPerParticipant'])
                     upd = updateDate(project_id, program_id)
                  try:
                     trans = m.Transfers.objects.filter(programId = program_id)
                      
                     for transfer1 in trans:
                        if transfer1.perparticipantOrTotal == 'Participant':
                           try:
                              partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=programdesc.id, yearnumber=transfer1.grantYear)
                              transfer1.total_amount =  float(transfer1.grantAmount) * float(partperyear.noofparticipants)
                              pe = True
                           except ObjectDoesNotExist:
                              transfer1.total_amount = transfer1.grantAmount 
                              pe = False

                           if programdesc.numberofparticipants is not None and pe == False:
                              transfer1.total_amount = transfer1.grantAmount * programdesc.numberofparticipants

                           if transfer1.grantFrom == agency1:
                              transfer1.cost_agency1 = transfer1.total_amount
                           elif transfer1.grantFrom == agency2:
                              transfer1.cost_agency2 = transfer1.total_amount
                           elif transfer1.grantFrom == agency3:
                              transfer1.cost_agency3 = transfer1.total_amount
                           elif transfer1.grantFrom == agency4:
                              transfer1.cost_agency4 = transfer1.total_amount

                           if transfer1.grantTo == agency1:
                              transfer1.cost_agency1 = -transfer1.total_amount
                           elif transfer1.grantTo == agency2:
                              transfer1.cost_agency2 = -transfer1.total_amount
                           elif transfer1.grantTo == agency3:
                              transfer1.cost_agency3 = -transfer1.total_amount
                           elif transfer1.grantTo == agency4:
                              transfer1.cost_agency4 = -transfer1.total_amount
                           transfer1.save(update_fields=['total_amount','cost_agency1','cost_agency2', 'cost_agency3','cost_agency4'])
                           upd = updateDate(project_id, program_id)
                  except ObjectDoesNotExist:
                     print('no transfer records')

                  request.session['programdescId'] = programdesc.id
                  if project.typeanalysis == 'Cost Analysis':
                     return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')
                  else:
                     return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=effform')
               else:
                  print(partform.errors)
                  return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart,'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'form1','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'partform.errors':partform.errors,'frm2':effectform,'frm4':distform, 'frm5':transform, 'loggedinuser':loggedinuser})

            else:
               print(form1.errors)
               return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart,'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'form1','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'errtext':form1.errors,'frm2':effectform,'frm4':distform, 'frm5':transform, 'loggedinuser':loggedinuser})

    else:
       if objectexists:
          form1 = ProgramDescForm(instance=programdesc)
          oldvalue = programdesc.numberofparticipants
       else:
          form1 = ProgramDescForm()
        
       if partobjexists: 
          partform = PartFormSet( instance=programdesc, prefix="partform",initial=[{'yearnumber': "%d" % (i+1)} for i in range(programdesc.numberofyears,programdesc.numberofyears+10)])

       else:
          partform = PartFormSet(prefix="partform",initial=[{'yearnumber': "%d" % (i+1)} for i in range(10)])
       for form in partform:
          instance = getattr(form, 'instance', None)
          if instance and partobjexists and not instance.pk:
             form.fields['noofparticipants'].widget.attrs['readonly'] = True

    if request.method == 'POST':
       if 'submit2' in request.POST:
          if effectform.is_valid():
             sourceeffectdata = effectform.save(commit=False)
             sourceeffectdata.programId = program
             sourceeffectdata.save()
             upd = updateDate(project_id, program_id)
             ing = m.Ingredients.objects.filter(programId = program_id)
             for i in ing:
                if sourceeffectdata.avgeffectperparticipant is not None  and i.averageCost is not None:
                   if sourceeffectdata.avgeffectperparticipant == '0':
                      i.effRatio = None                                                                                                
                      eff_ratio = None
                   else:   
                      i.effRatio = float(i.averageCost) / float(sourceeffectdata.avgeffectperparticipant)
                      eff_ratio = round(i.effRatio,2)
                else:
                   i.effRatio = None 
                i.save(update_fields=['effRatio'])
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')
          else:
             print(effectform.errors)
             return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart,'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'effform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm2':effectform, 'frm3':ingform,'effectform.errors':effectform.errors,'frm4':distform, 'frm5':transform, 'loggedinuser':loggedinuser})

    else:
       if effobjexists:                                                                                                            
          effectform = EffectForm(instance=effect)
       else:
          effectform = EffectForm()   


    if request.method == 'POST':
       if 'editIng' in request.POST:
          ingform = IngFormSet(request.POST,request.FILES,queryset = ing,prefix="ingform")
          if ingform.is_valid():
             f = ingform.save(commit=False)
             for ing in f:
                if ing.priceAdjInflation != 'No index' and ing.priceAdjGeographicalArea != 'No index':
                   perc = m.Ingredients.objects.get(pk = ing.id)
                   ing.percentageofUsage = perc.percentageofUsage
                   if ing.percentageofUsage is None:
                      ing.percentageofUsage = 100     
                   if ing.adjPricePerIngredient != 'No geographical index available' and ing.adjPricePerIngredient != 'No inflation index available' and ing.adjPricePerIngredient != '':
                      if ing.percentageofUsage == 100:
                         if ing.adjPricePerIngredient is not None and ing.quantityUsed is not None and ing.quantityUsed != '': 
                            ing.costPerIngredient = round(float(ing.adjPricePerIngredient) * float(ing.quantityUsed),3)
                      else:
                         if ing.adjPricePerIngredient is not None and ing.quantityUsed is not None and ing.quantityUsed != '':  
                            ing.costPerIngredient = round(float(ing.adjPricePerIngredient) * float(ing.quantityUsed) * float(ing.percentageofUsage) / 100,3) 
                   try:
                      partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=progid, yearnumber=ing.yearQtyUsed)
                      if ing.costPerIngredient is not None: 
                         ing.costPerParticipant = round(float(ing.costPerIngredient) / float(partperyear.noofparticipants),3)
                      ing.save(update_fields=['ingredient', 'quantityUsed','variableFixed','costPerIngredient','costPerParticipant','notes']) 
                   except ObjectDoesNotExist:
                      if ing.costPerIngredient is not None:
                          if numberofparticipants == 0:
                             ing.costPerParticipant = float(ing.costPerIngredient) / float("inf")
                          else:
                             if numberofparticipants is not None:
                                ing.costPerParticipant = float(ing.costPerIngredient) / float(numberofparticipants)
                             else:
                                if numberofparticipants is None:
                                   ing.costPerParticipant = float(ing.costPerIngredient)
                                else:
                                   ing.costPerParticipant = float(ing.costPerIngredient) / float(numberofparticipants)

                      ing.save(update_fields=['ingredient', 'quantityUsed','variableFixed','costPerIngredient','costPerParticipant','notes'])
                   upd = updateDate(project_id, program_id)
             ing1 = m.Ingredients.objects.filter(programId = program_id)
             total_cost = 0
             for i in ing1:
                if i.costPerIngredient is not None:  
                   total_cost = total_cost + i.costPerIngredient
                else:
                   total_cost = total_cost 
             for i in ing1:
                i.totalCost = total_cost
                total_cost = round(total_cost,2)
                if i.costPerIngredient is not None and i.totalCost is not None and  float(i.totalCost) != 0.000: 
                   i.percentageCost = float(i.costPerIngredient) * (100 / float(i.totalCost))
                else:
                   i.percentageCost = 0  
                if numberofparticipants is not None:
                   if numberofparticipants == 0:
                      i.averageCost = float(i.totalCost) / float("inf")
                   else:
                      i.averageCost = float(i.totalCost) / float(numberofparticipants)
                   avg_cost = i.averageCost
                   avg_cost = round(avg_cost,2)
                else:
                   i.averageCost = None 
                   avg_cost = None

                if avgeff is not None  and i.averageCost is not None:
                   if avgeff == '0':
                      i.effRatio = None                                                                                                
                      eff_ratio = None
                   else:   
                      i.effRatio = float(i.averageCost) / float(avgeff)
                      eff_ratio = round(i.effRatio,2)
                else:
                   i.effRatio = None
                   eff_ratio = None

                i.save(update_fields=['totalCost','averageCost','percentageCost','effRatio'])
                upd = updateDate(project_id, program_id)
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')
          else:
             print(ingform.errors)
             return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart,'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'costform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'ingform.errors':ingform.errors,'frm2':effectform,'frm4':distform,'frm5':transform})
    else:
       ing = m.Ingredients.objects.filter(programId = program_id)
       for i in ing:
          total_cost = i.totalCost
          avg_cost = i.averageCost
          if avgeff is not None  and i.averageCost is not None:
             if avgeff == '0':
                i.effRatio = None                                                                                                
                eff_ratio = None
             else:   
                i.effRatio = float(i.averageCost) / float(avgeff)
                eff_ratio = round(i.effRatio,2)
          else:
             i.effRatio = None
             eff_ratio = None
       ingform = IngFormSet(queryset = ing,prefix="ingform")
       for form in ingform:
          form.fields['newMeasure'].widget.attrs['readonly'] = True 
          form.fields['yearQtyUsed'].widget.attrs['readonly'] = True
          form.fields['totalCost'].widget.attrs['readonly'] = True 
          form.fields['adjPricePerIngredient'].widget.attrs['readonly'] = True
          form.fields['costPerIngredient'].widget.attrs['readonly'] = True
          form.fields['percentageCost'].widget.attrs['readonly'] = True
          form.fields['costPerParticipant'].widget.attrs['readonly'] = True
          instance = getattr(form, 'instance', None)
          if instance and not instance.pk:
             form.fields['ingredient'].widget.attrs['readonly'] = True
             form.fields['notes'].widget.attrs['readonly'] = True
             form.fields['quantityUsed'].widget.attrs['readonly'] = True
    
    if request.method == 'POST':
       if 'editDist' in request.POST:
          distform = DistFormSet(request.POST,request.FILES,prefix="distform")
          ag = m.Agencies.objects.get(programId = program_id)
          if distform.is_valid():
             f = distform.save(commit=False)
             for dist in f:
                if dist.cost_agency1_percent is None:
                   dist.cost_agency1_percent = 0
                   dist.cost_agency1 = 0
                else:
                   dist.cost_agency1 = float(dist.cost) * float(dist.cost_agency1_percent / 100)

                if dist.cost_agency2_percent is None:
                   dist.cost_agency2_percent = 0
                   dist.cost_agency2 = 0
                else:
                   dist.cost_agency2 = float(dist.cost) * float(dist.cost_agency2_percent / 100)

                if dist.cost_agency3_percent is None:
                   dist.cost_agency3_percent = 0
                   dist.cost_agency3 = 0
                else:
                   dist.cost_agency3 = float(dist.cost) * float(dist.cost_agency3_percent / 100)

                if dist.cost_agency4_percent is None:
                   dist.cost_agency4_percent = 0
                   dist.cost_agency4 = 0
                else:
                   dist.cost_agency4 = float(dist.cost) * float(dist.cost_agency4_percent / 100)

                dist.cost_other_percent = 100 - (dist.cost_agency1_percent + dist.cost_agency2_percent + dist.cost_agency3_percent + dist.cost_agency4_percent)
                if dist.cost is not None:
                   dist.cost_other = float(dist.cost) * float(dist.cost_other_percent / 100)

                total_agency1 = round(total_agency1 + dist.cost_agency1,3)
                total_agency2 = round(total_agency2 + dist.cost_agency2,3)
                total_agency3 = round(total_agency3 + dist.cost_agency3,3)
                total_agency4 = round(total_agency4 + dist.cost_agency4,3)

                if dist.cost_other is not None:
                   total_other = round(total_other + dist.cost_other,3)
                ag.total_agency1 = total_agency1
                ag.total_agency2 = total_agency2
                ag.total_agency3 = total_agency3
                ag.total_agency4 = total_agency4
                ag.total_other = total_other
                ag.total_cost = total_cost
                ag.save(update_fields=['total_agency1','total_agency2','total_agency3','total_agency4','total_other','total_cost'])
                upd = updateDate(project_id, program_id)

                if dist.cost_other_percent < 0:
                    return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart, 'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'distform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'distform_errors':'The percentage cost spread between the different agencies cannot be greater than 100.','frm2':effectform,'frm4':distform, 'frm5':transform, 'loggedinuser':loggedinuser})
                else:
                   dist.save(update_fields=['cost_agency1','cost_agency1_percent','cost_agency2','cost_agency2_percent','cost_agency3','cost_agency3_percent','cost_agency4','cost_agency4_percent','cost_other','cost_other_percent'])
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=distform')

          else:
             print(distform.errors)
             return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart,'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'effform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm2':effectform, 'frm3':ingform,'distform.errors':distform.errors,'frm4':distform,'frm5':transform})       
    else:
       try:
          inglist = m.Ingredients.objects.filter(programId = program_id)
          try:
             ag = m.Agencies.objects.get(programId = program_id)
          except ObjectDoesNotExist:
             m.Agencies.objects.create(agency1 = 'Program Sponsor', agency2 = 'Government Agencies', agency3 = 'Private Organizations', agency4 = 'Students/Parents', programId = program_id)
             ag = m.Agencies.objects.get(programId = program_id)
             print('agencies do not exist')
          for ing in inglist: 
              try:
                 dist = m.Distribution.objects.get(ingredientId = ing.id)
              except ObjectDoesNotExist:
                 m.Distribution.objects.create(ingredient = ing.ingredient,cost = ing.costPerIngredient, yearQtyUsed = ing.yearQtyUsed, programId = ing.programId, ingredientId = ing.id)
                 dist = m.Distribution.objects.get(ingredientId = ing.id)
                 recordExists = True
    
              dist.cost = ing.costPerIngredient
              dist.ingredient = ing.ingredient
              dist.yearQtyUsed = ing.yearQtyUsed
              ag.total_cost = ing.totalCost

              if dist.cost_agency1_percent is not None:
                 dist.cost_agency1 = float(dist.cost) * float(dist.cost_agency1_percent / 100)
              else:
                 dist.cost_agency1_percent = 0
              if dist.cost_agency2_percent is not None:
                 dist.cost_agency2 = float(dist.cost) * float(dist.cost_agency2_percent / 100)
              else:
                 dist.cost_agency2_percent = 0
              if dist.cost_agency3_percent is not None:
                 dist.cost_agency3 = float(dist.cost) * float(dist.cost_agency3_percent / 100)
              else:
                 dist.cost_agency3_percent = 0
              if dist.cost_agency4_percent is not None:
                 dist.cost_agency4 = float(dist.cost) * float(dist.cost_agency4_percent / 100)
              else:
                 dist.cost_agency4_percent = 0
              dist.cost_other_percent = 100 - (dist.cost_agency1_percent + dist.cost_agency2_percent + dist.cost_agency3_percent + dist.cost_agency4_percent)
              if dist.cost is not None:
                 dist.cost_other = float(dist.cost) * float(dist.cost_other_percent / 100)

              if dist.cost_agency1 is not None:
                 total_agency1 = round(float(total_agency1) + float(dist.cost_agency1),3)
              if dist.cost_agency2 is not None:
                 total_agency2 = round(float(total_agency2) + float(dist.cost_agency2),3)
              if dist.cost_agency3 is not None:
                 total_agency3 = round(float(total_agency3) + float(dist.cost_agency3),3)
              if dist.cost_agency4 is not None:
                 total_agency4 = round(float(total_agency4) + float(dist.cost_agency4),3)
              if dist.cost_other is not None:
                 total_other = round(float(total_other) + float(dist.cost_other),3)
              dist.save(update_fields=['cost', 'ingredient','yearQtyUsed','cost_agency1','cost_agency2','cost_agency3','cost_agency4','cost_other','cost_other_percent'])
              #upd = updateDate(project_id, program_id)

          ag.total_agency1 = total_agency1
          ag.total_agency2 = total_agency2
          ag.total_agency3 = total_agency3
          ag.total_agency4 = total_agency4
          ag.total_other = total_other
          ag.save(update_fields=['total_agency1','total_agency2','total_agency3','total_agency4','total_other','total_cost'])
       except ObjectDoesNotExist:
          print('no point in doing anything if no records in Ingredients')
   
       distform = DistFormSet(queryset = m.Distribution.objects.filter(programId = program_id),prefix="distform")
       for form in distform:
          form.fields['ingredient'].widget.attrs['readonly'] = True
          form.fields['yearQtyUsed'].widget.attrs['readonly'] = True
          form.fields['cost'].widget.attrs['readonly'] = True
          form.fields['cost_agency1'].widget.attrs['readonly'] = True
          form.fields['cost_agency2'].widget.attrs['readonly'] = True
          form.fields['cost_agency3'].widget.attrs['readonly'] = True
          form.fields['cost_agency4'].widget.attrs['readonly'] = True
          form.fields['cost_other_percent'].widget.attrs['readonly'] = True  
          form.fields['cost_other'].widget.attrs['readonly'] = True
    
    if request.method == 'POST':
       if 'editTrans' in request.POST:
          transform = TransFormSet(request.POST,request.FILES,prefix="transform")
          if transform.is_valid():
             f = transform.save(commit=False)
             for t in f:
                t.save(update_fields=['grantName'])
                upd = updateDate(project_id, program_id)
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=transform')
 
          else:
             print(transform.errors)
             return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart,'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'effform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm2':effectform, 'frm3':ingform,'distform.errors':distform.errors,'frm4':distform,'frm5':transform, 'transform.errors':transform.errors, 'loggedinuser':loggedinuser})

    else:
       try:
          ag = m.Agencies.objects.get(programId = program_id)
          trans = m.Transfers.objects.filter(programId = program_id)

          for t in trans:
             if t.cost_agency1 is not None:
                net_agency1 = net_agency1 + float(t.cost_agency1)
             if t.cost_agency2 is not None:
                net_agency2 = net_agency2 + float(t.cost_agency2)
             if t.cost_agency3 is not None:
                net_agency3 = net_agency3 + float(t.cost_agency3)
             if t.cost_agency4 is not None:
                net_agency4 = net_agency4 + float(t.cost_agency4)
             if t.cost_other is not None:
                net_other = net_other + float(t.cost_other)
          
          net_agency1 = net_agency1 + float(ag.total_agency1)
          net_agency2 = net_agency2 + float(ag.total_agency2)
          net_agency3 = net_agency3 + float(ag.total_agency3)
          net_agency4 = net_agency4 + float(ag.total_agency4)
          net_other = net_other + float(ag.total_other)

          ag.net_agency1 = net_agency1
          ag.net_agency2 = net_agency2
          ag.net_agency3 = net_agency3
          ag.net_agency4 = net_agency4
          ag.net_other = net_other
          ag.save(update_fields=['net_agency1','net_agency2','net_agency3','net_agency4','net_other'])
          #upd = updateDate(project_id, program_id)
       except ObjectDoesNotExist:
          print('agencies do not exist')
 
       transform = TransFormSet(queryset = trans,prefix="transform")
       for form in transform:
          form.fields['grantName'].widget.attrs['readonly'] = True
          form.fields['grantYear'].widget.attrs['readonly'] = True
          form.fields['cost_agency1'].widget.attrs['readonly'] = True
          form.fields['cost_agency2'].widget.attrs['readonly'] = True
          form.fields['cost_agency3'].widget.attrs['readonly'] = True
          form.fields['cost_agency4'].widget.attrs['readonly'] = True
          form.fields['cost_other'].widget.attrs['readonly'] = True             

    return render (request,'project/programs/effect/tabbedview.html',{'ingRecordExists':ingRecordExists, 'noofpart' : noofpart,'agcount': agcount,'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'eff_ratio':eff_ratio,'project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'frm2':effectform, 'frm4':distform, 'frm5':transform, 'loggedinuser':loggedinuser})

def add_agency(request):
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    context = RequestContext(request)
    try:
       agency = m.Agencies.objects.get(programId=program_id)
    except ObjectDoesNotExist:
       print('object does not exist')

    if request.method == 'POST':
        agencyform = AgenciesForm(request.POST,instance=agency)

        if agencyform.is_valid():
            agency1 = agencyform.save(commit=False)
            distrib = m.Distribution.objects.filter(programId=program_id)
            for dist in distrib:
               if agency1.agency2 is None or agency1.agency2 == '':
                  dist.cost_agency2 = 0.0
                  dist.cost_agency2_percent = 0.0
                  agency1.total_agency2 = 0.0
                  agency1.net_agency2 = 0.0
                  try:
                     m.Transfers.objects.exclude(cost_agency2__isnull=True).delete()
                  except ObjectDoesNotExist:
                     print('no idea what was here') 
               if agency1.agency3 is None or agency1.agency3 == '':
                  dist.cost_agency3 = 0.0
                  dist.cost_agency3_percent = 0.0
                  agency1.total_agency3 = 0.0
                  agency1.net_agency3 = 0.0
                  try:
                     m.Transfers.objects.exclude(cost_agency3__isnull=True).delete()
                  except ObjectDoesNotExist:
                     print('3')
               if agency1.agency4 is None or agency1.agency4 == '':
                  dist.cost_agency4 = 0.0
                  dist.cost_agency4_percent = 0.0
                  agency1.total_agency4 = 0.0
                  agency1.net_agency4 = 0.0
                  try:
                     m.Transfers.objects.exclude(cost_agency4__isnull=True).delete()
                  except ObjectDoesNotExist:
                     print('4') 
               if  dist.cost_agency1_percent is not None and dist.cost_agency2_percent is not None and dist.cost_agency3_percent is not None and dist.cost_agency4_percent is not None:
                   dist.cost_other_percent = float(100) - (float(dist.cost_agency1_percent) + float(dist.cost_agency2_percent) + float(dist.cost_agency3_percent) + float(dist.cost_agency4_percent))
               if dist.cost is not None and dist.cost_other_percent is not None:
                  dist.cost_other = float(dist.cost) * float(dist.cost_other_percent / 100)
                              
               dist.save(update_fields=['cost_other_percent','cost_other','cost_agency2','cost_agency2_percent','cost_agency3','cost_agency3_percent','cost_agency4','cost_agency4_percent'])
            else:
               print('not None')
            agency1.save(update_fields=['agency1','agency2','agency3','agency4','total_agency2','net_agency2','total_agency3','net_agency3','total_agency4','net_agency4'])
            upd = updateDate(project_id, program_id)
            return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=distform')
        else:
            print(agencyform.errors)

    else:
        agencyform = AgenciesForm(instance=agency)

    return render(request,
            'project/programs/dist/add_agency.html',
            {'project_id':project_id,'program_id':program_id,'agencyform': agencyform})

def add_transfer(request):
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    context = RequestContext(request)
    ptext = ' ' 
    pcount = 0
    try:
       progdesc = m.ProgramDesc.objects.get(programId_id = program_id)
       try: 
          part = m.ParticipantsPerYear.objects.filter(programdescId_id=progdesc.id)
          pcount = part.count()
          for p in part:
             ptext = ptext + str(p.noofparticipants) + ' for Year ' + str(p.yearnumber) +', '   
       except ObjectDoesNotExist:
          pcount = 0
       avgno = progdesc.numberofparticipants
    except ObjectDoesNotExist:
       avgno = 1
    
    try:
       agency = m.Agencies.objects.get(programId=program_id)
       ag1 = agency.agency1
       ag2 = agency.agency2
       ag3 = agency.agency3
       ag4 = agency.agency4
    except ObjectDoesNotExist:
       print('object does not exist')
       ag1 = ''
       ag2 = ''
       ag3 = ''
       ag4 = ''

    if pcount > 0:
       MFormSet = modelformset_factory(m.Transfers, form=TransfersForm, extra=pcount)
       if request.method == 'POST':
          transferform = MFormSet(request.POST, request.FILES)
          if transferform.is_valid():
             transfers = transferform.save(commit=False)
             tamountNone = True
             tName = True

             for transfer1 in transfers:
                if transfer1.grantAmount is not None:
                   tamountNone = False

             if tamountNone == True:
                err = 'Enter an  amount for atleast one year'
                return render ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)  
 
             for transfer1 in transfers:
                transfer1.programId = program_id
                transfer1.grantFrom = request.POST.get('grantFrom')
                transfer1.grantTo = request.POST.get('grantTo')
                transfer1.grantName = request.POST.get('desc')
                transfer1.perparticipantOrTotal = request.POST.get('pOrTotal')
                if transfer1.grantName == '' or transfer1.grantName is None:
                   err = 'Enter the name of the transfer/subsidy/fee'
                   return render ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)  

                if transfer1.grantFrom == transfer1.grantTo:
                   err = 'From and To cannot be the same agency'
                   transfer1.grantName = request.POST.get('desc')
                   return render ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)

                if transfer1.perparticipantOrTotal == 'Total':
                   transfer1.total_amount = transfer1.grantAmount
                else:
                   try:
                      partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=progdesc.id, yearnumber=transfer1.grantYear)
                      if transfer1.grantAmount is not None: 
                         transfer1.total_amount =  float(transfer1.grantAmount) * float(partperyear.noofparticipants)
                   except ObjectDoesNotExist:
                      transfer1.total_amount = transfer1.grantAmount

                if transfer1.total_amount is not None:
                   if transfer1.grantFrom == ag1.strip():
                      transfer1.cost_agency1 = transfer1.total_amount
                   elif transfer1.grantFrom == ag2.strip():
                      transfer1.cost_agency2 = transfer1.total_amount
                   elif transfer1.grantFrom == ag3.strip():
                      transfer1.cost_agency3 = transfer1.total_amount
                   elif transfer1.grantFrom == ag4.strip():
                      transfer1.cost_agency4 = transfer1.total_amount
                   elif transfer1.grantFrom == 'Other':
                      transfer1.cost_other = transfer1.total_amount
                   
                   if transfer1.grantTo == ag1.strip():
                      transfer1.cost_agency1 = -transfer1.total_amount
                   elif transfer1.grantTo == ag2.strip():
                      transfer1.cost_agency2 = -transfer1.total_amount
                   elif transfer1.grantTo == ag3.strip():
                      transfer1.cost_agency3 = -transfer1.total_amount
                   elif transfer1.grantTo == ag4.strip():
                      transfer1.cost_agency4 = -transfer1.total_amount
                   elif transfer1.grantTo == 'Other':
                      transfer1.cost_other = -transfer1.total_amount

                   transfer1.save()
                   upd = updateDate(project_id, program_id)
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=transform')
          else:
             print(transferform.errors)
             return render ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors},context)

       else:
          transferform = MFormSet(queryset=m.Transfers.objects.none(),initial=[{'grantYear': "%d" % (i+1)} for i in range(10)])
    else:
       if request.method == 'POST':
          transferform = TransfersForm(request.POST)
          if transferform.is_valid():
             transfer1 = transferform.save(commit=False)
             transfer1.programId = program_id
             transfer1.grantYear = 1
             
             if transfer1.grantAmount is None:
                err = 'Enter an  amount'
                return render ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)

             if transfer1.grantName == '' or transfer1.grantName is None:
                   err = 'Enter the name of the transfer/subsidy/fee'
                   return render ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)

             if transfer1.grantFrom == transfer1.grantTo:
                err = 'From and To cannot be the same agency'
                return render ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'err': err},context)

             if transfer1.perparticipantOrTotal == 'Total':
                transfer1.total_amount = transfer1.grantAmount
             else:
                if transfer1.averageno is None:
                   transfer1.total_amount = transfer1.grantAmount * avgno
                else:
                   transfer1.total_amount = transfer1.grantAmount * transfer1.averageno

             if transfer1.grantFrom == ag1.strip():
                transfer1.cost_agency1 = transfer1.total_amount
             elif transfer1.grantFrom == ag2.strip():
                transfer1.cost_agency2 = transfer1.total_amount
             elif transfer1.grantFrom == ag3.strip():
                transfer1.cost_agency3 = transfer1.total_amount
             elif transfer1.grantFrom == ag4.strip():
                transfer1.cost_agency4 = transfer1.total_amount
             elif transfer1.grantFrom == 'Other':
                transfer1.cost_other = transfer1.total_amount

             if transfer1.grantTo == ag1.strip():
                transfer1.cost_agency1 = -transfer1.total_amount
             elif transfer1.grantTo == ag2.strip():
                transfer1.cost_agency2 = -transfer1.total_amount
             elif transfer1.grantTo == ag3.strip():
                transfer1.cost_agency3 = -transfer1.total_amount
             elif transfer1.grantTo == ag4.strip():
                transfer1.cost_agency4 = -transfer1.total_amount
             elif transfer1.grantTo == 'Other':
                transfer1.cost_other = -transfer1.total_amount

             transfer1.save() 
             upd = updateDate(project_id, program_id)
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=transform')
          else:
              print(transferform.errors)
              return render ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors},context)
       else:
           transferform = TransfersForm()

    return render(request,
            'project/programs/transfer/add_transfer.html',
            {'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform})

def del_transfer(request, trans_id):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   

    m.Transfers.objects.get(pk=trans_id).delete()
    upd = updateDate(project_id, program_id)
    return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=transform')

def del_ingredient(request, ing_id):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    avg_eff = None
    eff_Ratio = None

    try:
       programdesc = m.ProgramDesc.objects.get(programId = program_id)
       numberofparticipants = programdesc.numberofparticipants
    except ObjectDoesNotExist:
       numberofparticipants = 1

    try:
       eff = m.Effectiveness.objects.get(programId_id = request.session['program_id'])
       avgeff = eff.avgeffectperparticipant                  
    except ObjectDoesNotExist:
       avgeff = None

    if (m.Distribution.objects.filter(programId=program_id).count()== 1):
       m.Agencies.objects.get(programId=program_id).delete()
    m.Distribution.objects.get(ingredientId=ing_id).delete()
    m.Ingredients.objects.get(pk=ing_id).delete()
    total_cost = 0
    ing = m.Ingredients.objects.filter(programId = program_id)
    for i in ing:
        if i.costPerIngredient is not None: 
           total_cost = total_cost + i.costPerIngredient
        else:   
           total_cost = total_cost 
    for i in ing:
        i.totalCost = total_cost
        if i.costPerIngredient is not None and i.totalCost is not None and  float(i.totalCost) != 0.000: 
           i.percentageCost = i.costPerIngredient * 100 /i.totalCost
        else:
           i.percentageCost = 0 
        if numberofparticipants is not None:
           if numberofparticipants == 0:
              i.averageCost = float(i.totalCost) / float("inf")
           else:
              i.averageCost = float(i.totalCost) / float(numberofparticipants)
           avg_cost = i.averageCost
        else:
           i.averageCost = None
           avg_cost = None

        if avgeff is not None and i.averageCost is not None:
           if avgeff == '0':
              i.effRatio = None                                                                                               
              eff_ratio = None
           else:   
              i.effRatio = float(i.averageCost) / float(avgeff)
              eff_ratio = round(i.effRatio,2)
        else:
           i.effRatio = None
           eff_ratio = None
        i.save(update_fields=['totalCost','averageCost','percentageCost','effRatio'])        
        upd = updateDate(project_id, program_id)
    return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')

def dupl_ingredient(request, ing_id):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    avgeff = None
    eff_Ratio = None

    try:
       programdesc = m.ProgramDesc.objects.get(programId = program_id)
       numberofparticipants = programdesc.numberofparticipants
    except ObjectDoesNotExist:
       numberofparticipants = 1

    try:
       eff = m.Effectiveness.objects.get(programId_id = request.session['program_id'])
       avgeff = eff.avgeffectperparticipant
    except ObjectDoesNotExist:
       avgeff = None

    ingredient = m.Ingredients.objects.get(pk=ing_id)
    if ingredient.yearQtyUsed is None:
       ingredient.yearQtyUsed = 1

    m.Ingredients.objects.create(SourceBenefitData = ingredient.SourceBenefitData, notes = ingredient.notes, category = ingredient.category, ingredient = ingredient.ingredient, edLevel = ingredient.edLevel, sector = ingredient.sector, unitMeasurePrice = ingredient.unitMeasurePrice, price =  ingredient.price, sourcePriceData = ingredient.sourcePriceData, urlPrice = ingredient.urlPrice, newMeasure = ingredient.newMeasure, convertedPrice = ingredient.convertedPrice, yearPrice = ingredient.yearPrice, statePrice = ingredient.statePrice, areaPrice = ingredient.areaPrice, programId = ingredient.programId, lifetimeAsset = ingredient.lifetimeAsset, interestRate = ingredient.interestRate, benefitRate = ingredient.benefitRate, indexCPI = ingredient.indexCPI, geoIndex = ingredient.geoIndex, quantityUsed = ingredient.quantityUsed, variableFixed = ingredient.variableFixed, yearQtyUsed = ingredient.yearQtyUsed, priceAdjAmortization = ingredient.priceAdjAmortization, percentageofUsage = ingredient.percentageofUsage, adjPricePerIngredient = ingredient.adjPricePerIngredient, priceAdjInflation = ingredient.priceAdjInflation, priceAdjBenefits = ingredient.priceAdjBenefits,priceAdjGeographicalArea = ingredient.priceAdjGeographicalArea, priceNetPresentValue = ingredient.priceNetPresentValue, costPerIngredient = ingredient.costPerIngredient, costPerParticipant = ingredient.costPerParticipant )

    total_cost = 0
    ing = m.Ingredients.objects.filter(programId = program_id)
    for i in ing:
        if i.costPerIngredient is not None: 
           total_cost = total_cost + i.costPerIngredient
        else:   
           total_cost = total_cost 
    for i in ing:
        i.totalCost = total_cost
        if i.costPerIngredient is not None and i.totalCost is not None and  float(i.totalCost) != 0.000: 
           i.percentageCost = i.costPerIngredient * 100 /i.totalCost
        else:
           i.percentageCost = 0 
        if numberofparticipants is not None:
           if numberofparticipants == 0:
              i.averageCost = float(i.totalCost) / float("inf")
           else:
              i.averageCost = float(i.totalCost) / float(numberofparticipants)
           avg_cost = i.averageCost
        else:
           i.averageCost = None
           avg_cost = None
                
        if avgeff is not None and i.averageCost is not None:
           if avgeff == '0': 
              i.effRatio = None
              eff_ratio = None
           else:   
              i.effRatio = float(i.averageCost) / float(avgeff)
              eff_ratio = round(i.effRatio,2)
        else:
           i.effRatio = None
           eff_ratio = None
                              
        i.save(update_fields=['totalCost','averageCost','percentageCost','effRatio'])        
        upd = updateDate(project_id, program_id)
    return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')

def search_costs(request):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0

    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   

    if 'projectname' in request.session:
       projectname = request.session['projectname']
    else:
       projectname = 'ccc'

    if 'programname' in request.session:
       progname = request.session['programname']
    else:
       progname = 'ccc'

    try:
       sett = m.Settings.objects.get(projectId = project_id)
       choicesEdn = ''
       choicesSec = ''
       if 'Select' in sett.limitEdn:
          choicesEdn = 'All,General,Grades PK,Grades K-6,Grades 6-8,Grades 9-12,Grades K-12,PostSecondary'
       else:
          if 'General' in sett.limitEdn:
             choicesEdn = choicesEdn + ',General'
          if 'Grades PK' in sett.limitEdn:
             choicesEdn = choicesEdn + ',Grades PK'
          if 'Grades K-6' in sett.limitEdn:
             choicesEdn = choicesEdn + ',Grades K-6'
          if 'Grades 6-8' in sett.limitEdn:
             choicesEdn = choicesEdn + ',Grades 6-8'
          if 'Grades 9-12' in sett.limitEdn:
             choicesEdn = choicesEdn + ',Grades 9-12'
          if 'Grades K-12' in sett.limitEdn:
             choicesEdn = choicesEdn + ',Grades K-12'
          if 'PostSecondary' in sett.limitEdn:
             choicesEdn = choicesEdn + ',PostSecondary'
       if choicesEdn.startswith(','):
          choicesEdn = choicesEdn[1:len(choicesEdn)] 
       if 'Select' in sett.limitSector:
          choicesSec = 'Any,Private,Public'
       else:
          if 'Any' in sett.limitSector:
             choicesSec = choicesSec + ',Any'
          if 'Private' in sett.limitSector:
             choicesSec = choicesSec + ',Private'
          if 'Public' in sett.limitSector:
             choicesSec = choicesSec + ',Public'
       if choicesSec.startswith(','):
          choicesSec = choicesSec[1:len(choicesSec)]         
    except ObjectDoesNotExist:
       choicesEdn = 'All,General,Grades PK,Grades K-6,Grades 6-8,Grades 9-12,Grades K-12,PostSecondary'
       choicesSec = 'All,Any,Private,Public'
  
    if 'hrsCalendarYr' in request.session:
        del request.session['hrsCalendarYr']

    if 'hrsAcademicYr' in request.session:
        del request.session['hrsAcademicYr']

    if 'hrsHigherEdn' in request.session:
        del request.session['hrsHigherEdn']

    if 'price' in request.session:
        del request.session['price']

    if 'measure' in request.session:
        del request.session['measure']

    #if 'price_id' in request.session:
        #del request.session['price_id']

    if 'Rate' in request.session:
        del request.session['Rate']

    if 'benefit_id' in request.session:
        del request.session['benefit_id']

    if 'search_cat' in request.session:
       del request.session['search_cat']

    if 'search_edLevel' in request.session:
       del request.session['search_edLevel']

    if 'search_sector' in request.session:
       del request.session['search_sector']
    
    if 'search_ingredient' in request.session:
       del request.session['search_ingredient']

    if 'lifetimeAsset' in request.session:
       del request.session['lifetimeAsset']

    if 'interestRate' in request.session:
       del request.session['interestRate']

    if request.method == 'POST':
        costform = PricesSearchForm(data=request.POST)
        if costform.is_valid():
            priceProvider = costform.save(commit=False)
            return HttpResponseRedirect('/project/programs/costs/price_search_results.html')
        else:
            print(costform.errors)
            return HttpResponse(costform.errors)
    else:
       costform = PricesSearchForm()
    return render('project/programs/costs/search_costs.html',{'costform':costform,'choicesEdn':choicesEdn,'choicesSec':choicesSec,'project_id':project_id, 'program_id':program_id,'projectname':projectname, 'programname':progname},context)

def price_search2(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    projectname = request.session['projectname']
    progname = request.session['programname']  
    prices = m.Prices.objects.all()
    pcount = prices.count()
    cat = request.GET['category']
    request.session['search_cat'] = cat
    edLevel = request.GET['edLevel']
    request.session['search_edLevel'] = edLevel
    sector = request.GET['sector']
    request.session['search_sector'] = sector
    ingredient = request.GET['ingredient']
    request.session['search_ingredient'] = ingredient
    template = loader.get_template('project/programs/costs/price_search_results.html')
    context = Context({'projectname':projectname, 'programname':progname,'prices' : prices, 'pcount':pcount, 'cat': cat, 'edLevel':edLevel, 'sector':sector, 'ingredient':ingredient, 'project_id':project_id, 'program_id':program_id})
    return HttpResponse(template.render(context))
 
def price_search(request):
    context = RequestContext(request)

    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    if 'projectname' in request.session:
       projectname = request.session['projectname']
    else:
       projectname = 'ccc'
    if 'programname' in request.session:
       progname = request.session['programname']
    else:
       progname = 'ccc'

    if 'new_price' in request.session:
        del request.session['new_price']

    if 'new_measure' in request.session:
        del request.session['new_measure']

    try:
       sett = m.Settings.objects.get(projectId = project_id)
       if 'CBCSE' in sett.selectDatabase and 'My' in sett.selectDatabase:
          prices = m.Prices.objects.filter(priceProvider = 'CBCSE') | m.Prices.objects.filter(priceProvider = request.session['user'])
          #prices = m.Prices.objects.raw("SELECT * from costtool_prices WHERE priceProvider = 'CBCSE' or priceProvider = %s", [request.session['user']])
          prices2 = prices
       elif 'CBCSE' in sett.selectDatabase:
          prices = m.Prices.objects.filter(priceProvider = 'CBCSE')
       elif 'My' in sett.selectDatabase:
          prices = m.Prices.objects.filter(priceProvider = request.session['user'])

    except ObjectDoesNotExist:
       prices = m.Prices.objects.all()
 
    if 'category' in request.GET or 'edlevel' in request.GET or 'sector' in request.GET or 'ingredient' in request.GET:
       cat = request.GET['category']
       request.session['search_cat'] = cat
       edLevel = request.GET['edLevel']
       request.session['search_edLevel'] = edLevel 
       sector = request.GET['sector']
       request.session['search_sector'] = sector
       ingredient = request.GET['ingredient']
       request.session['search_ingredient'] = ingredient
       kwargs = { }
       if cat:
          if cat != 'All': 
             kwargs['category'] = cat
             
       prices = prices.filter(**kwargs)
       if edLevel:
          if edLevel == 'All':
             edLevellist = ['','General','Grades PK','Grades K-6','Grades 6-8','Grades 9-12','Grades K-12','PostSecondary'] 
          elif edLevel == 'General': 
             edLevellist = ['All','General']
             prices = prices.filter(edLevel__in=edLevellist)
          elif edLevel == 'Grades PK': 
             edLevellist = ['All','Grades PK']
             prices = prices.filter(edLevel__in=edLevellist)
          elif edLevel == 'Grades 6-8': 
             edLevellist = ['All','Grades 6-8']
             prices = prices.filter(edLevel__in=edLevellist)
          elif edLevel == 'Grades 9-12': 
             edLevellist = ['All','Grades 9-12']
             prices = prices.filter(edLevel__in=edLevellist)
          elif edLevel == 'Grades K-12': 
             edLevellist = ['All','Grades K-6','Grades 9-12', 'Grades 6-8','Grades K-12']
             prices = prices.filter(edLevel__in=edLevellist)
          elif edLevel == 'Grades K-6': 
             edLevellist = ['All','Grades K-6']
             prices = prices.filter(edLevel__in=edLevellist)
          elif edLevel == 'PostSecondary': 
             edLevellist = ['All','PostSecondary']
             prices = prices.filter(edLevel__in=edLevellist)
          else:
             prices = prices.filter(edLevel = edLevel)
       if sector:
          if sector == 'Any':
             sectorList = ['','Any','Public','Private']
             prices = prices.filter(sector__in=sectorList)
          elif sector == 'Public':
             sectorList = ['Any','Public']
             prices = prices.filter(sector__in=sectorList)
          elif sector == 'Private':
             sectorList = ['Any','Private']
             prices = prices.filter(sector__in=sectorList)
          else:
             prices = prices.filter(sector = sector)
       if ingredient:
          buildlist = ['building','residence','classroom','auditorium', 'construction', 'house']
          teachlist = ['teacher', 'professor', 'faculty', 'instructor', 'coach', 'educator', 'lecturer', 'scholar', 'tutor']
          faclist = ['research', 'faculty', 'professor', 'investigation', 'experiment', 'doctorate', 'curator', 'lab', 'librarian', 'library', 'engineer', 'college', 'university', 'data']
          techlist = ['technology', 'telecommunications', 'multimedia', 'digital', 'information', 'data', 'software', 'programmer', 'system', 'technical', 'network']
          complist = ['computer', 'laptop', 'notebook', 'cpu', 'monitor', 'mac', 'pc', 'desktop']
          airlist = ['airfare', 'plane', 'ticket', 'fare', 'air fare']

          if ingredient in buildlist:
             prices = prices.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in buildlist]))
          elif ingredient in teachlist:
             prices = prices.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in teachlist]))
          elif ingredient in faclist:
             prices = prices.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in faclist]))
          elif ingredient in techlist:
             prices = prices.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in techlist]))
          elif ingredient in complist:             
             prices = prices.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in complist]))
          elif ingredient in airlist:
             prices = prices.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in airlist]))   
          else:
             prices = prices.filter(ingredient__icontains = ingredient)
       if 'recent' in sett.limitYear:
          if not ingredient:
             ingredients = prices2
          else:
             if ingredient in buildlist:
                ingredients = prices2.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in buildlist]))
             elif ingredient in teachlist:
                ingredients = prices2.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in teachlist]))
             elif ingredient in faclist:
                ingredients = prices2.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in faclist]))
             elif ingredient in techlist:
                ingredients = prices2.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in techlist]))
             elif ingredient in complist:
                ingredients = prices2.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in complist]))
             elif ingredient in airlist:
                ingredients = prices2.filter(reduce(lambda x, y: x | y, [Q(ingredient__icontains=word) for word in airlist]))

             else:
                ingredients = prices2.filter(ingredient__icontains = ingredient)
                   #this should give us a list of all ingredients
          price_pks = []                                                                                                       
          for ingredient in ingredients:
             price = prices2.filter(ingredient=ingredient.ingredient,category=ingredient.category,edLevel=ingredient.edLevel,sector=ingredient.sector).order_by('-yearPrice')[0] 
             price_pks.append(price.pk)
          prices = prices.filter(pk__in=price_pks)
       prices = prices.order_by('ingredient')   
       pcount = prices.count()
       template = loader.get_template('project/programs/costs/price_search_results.html')
       context = Context({'projectname':projectname, 'programname':progname,'prices' : prices, 'pcount':pcount, 'cat': cat, 'edLevel':edLevel, 'sector':sector, 'ingredient':ingredient, 'project_id':project_id, 'program_id':program_id})
       return HttpResponse(template.render(context))
    else:
        return HttpResponse('Please enter some criteria to do a search')

def decideCat(request,price_id):
    context = RequestContext(request)
    price = m.Prices.objects.get(pk=price_id)
    try:
       request.session['price_id'] = price_id 
       inf = m.InflationIndices.objects.get(projectId=request.session['project_id'],yearCPI=price.yearPrice)
       request.session['priceExists'] = True
       if price.category == 'Personnel':
          return HttpResponseRedirect('/project/programs/costs/'+ price_id +'/price_indices.html')
       else:
          return HttpResponseRedirect('/project/programs/costs/'+ price_id +'/nonper_indices.html')
    except ObjectDoesNotExist:
       request.session['priceExists'] = False 
       return render('project/programs/costs/gotoinf.html',{'yearPrice':price.yearPrice},context)

def gotoinf(request):
   return render(request,'project/programs/costs/gotoinf.html')
    
def price_indices(request,price_id):
    price = m.Prices.objects.get(pk=price_id)

    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    if 'projectname' in request.session:
       projectname = request.session['projectname']
    else:
       projectname = 'ccc'
    if 'programname' in request.session:
       progname = request.session['programname']
    else:
       progname = 'ccc'


    if 'search_cat' in request.session:
       cat = request.session['search_cat']
    else:
       cat = 'vvv'
    if 'search_edLevel' in request.session:
       edLevel = request.session['search_edLevel']
    else:
       edLevel = 'vvv'
    if 'search_sector' in request.session:
       sector = request.session['search_sector']
    else:
       sector = 'ccc'
    if 'search_ingredient' in request.session:
       ingredient = request.session['search_ingredient']
    else:
       ingredient = 'ccc'

    #cat =  request.session['search_cat']
    #edLevel =  request.session['search_edLevel']
    #sector =  request.session['search_sector']
    #ingredient = request.session['search_ingredient']

    if 'new_price' in request.session:
       new_price = request.session['new_price']
    else:
       new_price = price.price
       request.session['new_price'] = price.price

    if 'new_measure' in request.session:
       new_measure = request.session['new_measure']
    else:
       new_measure = price.unitMeasurePrice
       request.session['new_measure'] = price.unitMeasurePrice
 
    request.session['price_id'] = price_id
    request.session['price'] = price.price
    request.session['measure'] = price.unitMeasurePrice
    template = loader.get_template('project/programs/costs/price_indices.html')
    context = Context({
        'price' : price,
        'new_price' : new_price,
        'new_measure' : new_measure,
        'cat' : cat, 'edLevel':  edLevel, 'sector': sector,'ingredient' : ingredient, 
        'project_id':project_id, 'program_id':program_id, 'projectname':projectname, 'programname':progname 
    })
    return HttpResponse(template.render(context))

def nonper_indices(request,price_id):
    context = RequestContext(request)
    price = m.Prices.objects.get(pk=price_id)

    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    if 'projectname' in request.session:
       projectname = request.session['projectname']
    else:
       projectname = 'ccc'
    if 'programname' in request.session:
       progname = request.session['programname']
    else:
       progname = 'ccc'

    if 'search_cat' in request.session:
       cat = request.session['search_cat']
    else:
       cat = 'vvv'
    if 'search_edLevel' in request.session:
       edLevel = request.session['search_edLevel']
    else:
       edLevel = 'vvv'
    if 'search_sector' in request.session:
       sector = request.session['search_sector']
    else:
       sector = 'ccc'
    if 'search_ingredient' in request.session:
       ingredient = request.session['search_ingredient']
    else:
       ingredient = 'ccc'
    #cat =  request.session['search_cat']
    #edLevel =  request.session['search_edLevel']
    #sector =  request.session['search_sector']
    #ingredient = request.session['search_ingredient']

    if 'new_price' in request.session:
       new_price = request.session['new_price']
    else:
       new_price = price.price
       request.session['new_price'] = price.price

    if 'new_measure' in request.session:
       new_measure = request.session['new_measure']
    else:
       new_measure = price.unitMeasurePrice
       request.session['new_measure'] = price.unitMeasurePrice

    request.session['price_id'] = price_id
    request.session['price'] = price.price
    request.session['measure'] = price.unitMeasurePrice

    if request.method == 'POST':
        form = NonPerIndicesForm(request.POST)
        if form.is_valid():
            lifetimeAsset = form.save(commit=False)
            request.session['lifetimeAsset'] = lifetimeAsset.lifetimeAsset
            request.session['interestRate'] = lifetimeAsset.interestRate
            return HttpResponseRedirect('/project/programs/costs/summary.html')
        else:
            print(form.errors)
            return render('project/programs/costs/nonper_indices.html',{'form':form, 'price':price, 'new_price' : new_price, 'new_measure' : new_measure, 'cat' : cat, 'edLevel':  edLevel, 'sector': sector,'ingredient' : ingredient,'project_id':project_id, 'program_id':program_id,'form.errors':form.errors,'projectname':projectname, 'programname':progname},context)
    else:
        form = NonPerIndicesForm()

    return render('project/programs/costs/nonper_indices.html',{'form':form, 'price':price, 'new_price' : new_price, 'new_measure' : new_measure, 'cat' : cat, 'edLevel':  edLevel, 'sector': sector,'ingredient' : ingredient,'project_id':project_id, 'program_id':program_id, 'projectname':projectname, 'programname':progname},context)

def um_converter(request):
    context = RequestContext(request)

    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = 0   

    try:
       sett = m.Settings.objects.get(projectId=project_id)
       hrsCalendarYr = float(sett.hrsCalendarYr)
       hrsAcademicYr = float(sett.hrsAcademicYr)
       hrsHigherEdn = float(sett.hrsHigherEdn)
    except ObjectDoesNotExist:
       hrsCalendarYr = float(2080)
       hrsAcademicYr = float(1440)
       hrsHigherEdn = float(1560)

    if 'price' in request.session:
       price = float(request.session['price'])
    else:
       price = 0.0
       request.session['price'] = 0.0

    if 'measure' in request.session:
       measure = request.session['measure']
    else:
       measure = ''
       request.session['measure'] = ''

    if 'new_price' in request.session:
        new_price = request.session['new_price']
    else: 
        new_price = price
        request.session['new_price'] = price

    if 'new_measure' in request.session:
        new_measure = request.session['new_measure']
    else: 
        new_measure = measure
        request.session['new_measure'] = measure
    mylist = ['Sq. Inch', 'Sq. Foot','Sq. Yard','Acre','Sq. Mile','Sq. Meter','Sq. Kilometer','Hectare']
    listVol=['Fluid Ounces','Cups','Pints','Quarts','Gallons','Liters']
    listLen=['Inches','Feet','Yards','Miles','Millimeter','Centimeter','Kilometer','Mile']
    listTime=['Hour', 'Day', 'Week', 'K-12 Academic Year','Higher Ed Academic Year','Calendar Year']
    allList = ['Sq. Inch', 'Sq. Foot','Sq. Yard','Acre','Sq. Mile','Sq. Meter','Sq. Kilometer','Hectare','Ounces','Cups','Pints','Quarts','Gallons','Liters','Inches','Feet','Yards','Miles','Millimeter','Centimeter','Kilometer','Minutes','Hours','Days','Weeks','Years']
    measureType = 'mylist'

    if measure == 'Other':
       measureType = 'allList'
    elif measure in mylist:
       measureType = 'mylist'
    elif measure in listVol:
       measureType = 'listVol'
    elif measure in listLen:
       measureType = 'listLen'
    elif measure in listTime:
       measureType = 'listTime'

    if request.method == 'POST':
        if 'compute' in request.POST:
            form = UMConverter(data=request.POST)
            if form.is_valid():
                newMeasure = form.save(commit=False)
                if measureType == 'mylist':
                    # done on May 7 
                    if measure == 'Sq. Inch':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price * 12 * 12
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price * 36 * 36
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price / 0.0000001594
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price * 4014489600
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price * 1550.003
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price / 0.00000000064516
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price / 0.000000064516

                    if measure == 'Sq. Foot' or measure == 'Sq. Ft.':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price / 144
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price / 0.111111
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price / 0.0000229568
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price / 0.0000000358701
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price / 0.092903
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price / 0.000000092903
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price / 0.0000092903

                    if measure == 'Sq. Yard':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price / 1296
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price / 9
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price / 0.000206612
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price / 0.000000322831
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price / 0.836127
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price / 0.000000836127
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price / 0.0000836127

                    if measure == 'Acre':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price / 0.000006273
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price / 4840
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price / 43560
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price / 0.0015625
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price / 4046.86
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price / 0.00404686
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price / 0.404686

                    if measure == 'Sq. Mile':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price / 0.000000004014
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price / 0.000003098
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price / 0.0000002788
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price / 640
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price / 0.00000259
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price / 2.5899
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price / 258.999

                    if measure == 'Sq. Meter':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price / 1550
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price / 1.19599
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price / 10.7639
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price / 0.000247105
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price / 0.000000386102
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price / 0.000001
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price / 0.0001

                    if measure == 'Sq. Kilometer':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price / 0.00000000155
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price / 0.000001196
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price / 0.0000001076
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price / 247.105
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price / 0.386102
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price / 1000000
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price / 100

                    if measure == 'Hectare':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price / 0.000000155
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price / 11959.9
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price / 107639
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price / 2.47105
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price / 0.00386102
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price / 10000
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price / 0.01

                    request.session['new_measure'] = newMeasure.newMeasure
                    new_measure = newMeasure.newMeasure
                if measureType == 'listVol':
                    if measure == 'Fluid Ounces':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price / 0.125
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price / 0.0625
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price / 0.03125
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price / 0.0078125
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price / 0.0295735

                    if measure == 'Cups':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price / 8
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price / 0.5
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price / 0.25
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price / 0.0625
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price / 0.236588

                    if measure == 'Pints':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price / 2
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price / 16
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price / 0.5
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price / 0.125
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price / 0.473176

                    if measure == 'Quarts':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price / 4
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price / 2
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price / 32
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price / 0.25
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price / 0.946353

                    if measure == 'Gallons':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price / 16
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price / 8
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price / 4
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price / 128
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price / 3.78541

                    if measure == 'Liters':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price / 4.22675
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price / 2.11338
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price / 1.05669
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price / 0.264172
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price / 33.814

                    request.session['new_measure'] = newMeasure.newMeasureVol
                    new_measure = newMeasure.newMeasureVol

                if measureType == 'listLen':
                    if measure == 'Inches':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price / 0.0833333
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price / 0.0277778
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price / 0.0000157828
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price / 25.4
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price / 2.54
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price / 0.0000254

                    if measure == 'Feet':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price / 12
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price / 0.333333
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price / 0.00018
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price / 304.8
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price / 30.48
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price / 0.0003048

                    if measure == 'Yards':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price / 36
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price / 3
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price / 0.000568182
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price / 914.4
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price / 91.44
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price / 0.0009144

                    if measure == 'Miles' or measure == 'Mile':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price / 63360
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price / 5280
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price / 1760
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price / 0.00000160934
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price / 160934
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price / 1.609

                    if measure == 'Millimeter':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price / 0.0393701
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price / 0.00328084
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price / 0.00109361
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price / 0.00000062137
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price / 0.1
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price / 0.000001

                    if measure == 'Centimeter':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price / 0.393701
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price / 0.0328084
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price / 0.0109361
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price / 0.0000062137
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price / 10
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price / 0.00001

                    if measure == 'Kilometer':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price / 39370.1
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price / 3280.84
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price / 1093.61
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price / 0.621371
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price / 100000
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price / 1000000

                    request.session['new_measure'] = newMeasure.newMeasureLen
                    new_measure = newMeasure.newMeasureLen

                if measureType == 'listTime':
                   if measure == 'Hour':
                      newMeasure.convertedPrice = price
                      if newMeasure.newMeasureTime == 'Day':
                         newMeasure.convertedPrice = price * 8
                      if newMeasure.newMeasureTime == 'Week':
                         newMeasure.convertedPrice = price * 40
                      if newMeasure.newMeasureTime == 'Calendar Year':
                         newMeasure.convertedPrice = price * hrsCalendarYr
                      if newMeasure.newMeasureTime == 'K-12 Academic Year':
                         newMeasure.convertedPrice = price * hrsAcademicYr
                      if newMeasure.newMeasureTime == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                         newMeasure.convertedPrice = price * hrsHigherEdn
                      
                   if measure == 'Day': 
                      newMeasure.convertedPrice = price
                      if newMeasure.newMeasureTime == 'Hour':
                         newMeasure.convertedPrice = price /  8
                      if newMeasure.newMeasureTime == 'Week':
                         newMeasure.convertedPrice = price *  5
                      if newMeasure.newMeasureTime == 'Calendar Year':
                         newMeasure.convertedPrice = price * (hrsCalendarYr / 8)
                      if newMeasure.newMeasureTime == 'K-12 Academic Year':
                         newMeasure.convertedPrice = price * (hrsAcademicYr / 8)
                      if newMeasure.newMeasureTime == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                         newMeasure.convertedPrice = price * (hrsHigherEdn / 8)

                   if measure == 'Week': 
                      newMeasure.convertedPrice = price
                      if newMeasure.newMeasureTime == 'Hour':
                         newMeasure.convertedPrice = price / 40
                      if newMeasure.newMeasureTime == 'Day':
                         newMeasure.convertedPrice = price /  5
                      if newMeasure.newMeasureTime == 'Calendar Year':
                         newMeasure.convertedPrice = price * 52
                      if newMeasure.newMeasureTime == 'K-12 Academic Year':
                         newMeasure.convertedPrice = price * 36                                                                            
                      if newMeasure.newMeasureTime == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                         newMeasure.convertedPrice = price * 39

                   if measure == 'Calendar Year':
                      newMeasure.convertedPrice = price
                      if newMeasure.newMeasureTime == 'Hour':
                         newMeasure.convertedPrice = price / hrsCalendarYr
                      if newMeasure.newMeasureTime == 'Day':
                         newMeasure.convertedPrice = price / (hrsCalendarYr / 8)
                      if newMeasure.newMeasureTime == 'Week':
                         newMeasure.convertedPrice = price / 52
                      if newMeasure.newMeasureTime == 'K-12 Academic Year':
                         newMeasure.convertedPrice = price * (hrsAcademicYr / hrsCalendarYr)
                      if newMeasure.newMeasureTime == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                         newMeasure.convertedPrice = price * (hrsHigherEdn / hrsCalendarYr)
                                         
                   if measure == 'K-12 Academic Year':
                      newMeasure.convertedPrice = price
                      if newMeasure.newMeasureTime == 'Hour':
                         newMeasure.convertedPrice = price / hrsAcademicYr
                      if newMeasure.newMeasureTime == 'Day':
                         newMeasure.convertedPrice = price / (hrsAcademicYr / 8)
                      if newMeasure.newMeasureTime == 'Week':
                         newMeasure.convertedPrice = price / 36
                      if newMeasure.newMeasureTime == 'Calendar Year':
                         newMeasure.convertedPrice = price * (hrsCalendarYr / hrsAcademicYr)
                      if newMeasure.newMeasureTime == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                         newMeasure.convertedPrice = price * (hrsHigherEdn / hrsAcademicYr)

                   if measure == 'Higher Ed Academic Year' or measure == 'Higher Education Academic Year':
                      newMeasure.convertedPrice = price
                      if newMeasure.newMeasureTime == 'Hour':
                         newMeasure.convertedPrice = price / hrsHigherEdn
                      if newMeasure.newMeasureTime == 'Day':
                         newMeasure.convertedPrice = price / (hrsHigherEdn / 8)
                      if newMeasure.newMeasureTime == 'Week':
                         newMeasure.convertedPrice = price / 39
                      if newMeasure.newMeasureTime == 'Calendar Year':
                         newMeasure.convertedPrice = price * (hrsCalendarYr / hrsHigherEdn)
                      if newMeasure.newMeasureTime == 'K-12 Academic Year':
                         newMeasure.convertedPrice = price * (hrsAcademicYr / hrsHigherEdn)

                   request.session['new_measure'] = newMeasure.newMeasureTime
                   new_measure = newMeasure.newMeasureTime

                request.session['new_price'] = newMeasure.convertedPrice
                return HttpResponseRedirect('/project/programs/costs/umconverter.html')
            else:
                print(form.errors)

        if 'use' in request.POST:
            price_id = request.session['price_id']
            return HttpResponseRedirect('/project/programs/costs/'+ price_id + '/nonper_indices.html')

    else:
        if measure == 'Other' or measureType == 'mylist':
           form = UMConverter(initial={'convertedPrice':new_price,'newMeasure':new_measure})
        elif measureType == 'listVol':
           form = UMConverter(initial={'convertedPrice':new_price,'newMeasureVol':new_measure})
        elif measureType == 'listLen':
           form = UMConverter(initial={'convertedPrice':new_price,'newMeasureLen':new_measure})
        elif measureType == 'listTime':
           form = UMConverter(initial={'convertedPrice':new_price,'newMeasureTime':new_measure})

    return render('project/programs/costs/umconverter.html',{'form':form, 'price':price,'measure':measure,'measureType':measureType, 'new_price' : new_price, 'new_measure' : new_measure, 'price_id':price_id},context)

def wage_converter(request):
    context = RequestContext(request)
    price_id = request.session['price_id']

    if 'price' in request.session:
       price = float(request.session['price'])
    else:
       price = 0.0
       request.session['price'] = 0.0

    if 'measure' in request.session:
       measure = request.session['measure'] 
    else:
       measure = ''
       request.session['measure'] = ''
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'hrsCalendarYr' in request.session:
       hrsCalendarYr = request.session['hrsCalendarYr']
    else:
        try:
            sett = m.Settings.objects.get(projectId=project_id)
            hrsCalendarYr = sett.hrsCalendarYr
            request.session['hrsCalendarYr'] = hrsCalendarYr
            objExists = True
        except ObjectDoesNotExist:
            hrsCalendarYr = 2080
            request.session['hrsCalendarYr'] = hrsCalendarYr
            objExists = False

    if 'hrsAcademicYr' in request.session:
       hrsAcademicYr = request.session['hrsAcademicYr']
    else:
        if objExists:
            hrsAcademicYr = sett.hrsAcademicYr
            request.session['hrsAcademicYr'] = hrsAcademicYr
        else:
            hrsAcademicYr = 1440
            request.session['hrsAcademicYr'] = hrsAcademicYr

    if 'hrsHigherEdn' in request.session:
       hrsHigherEdn = request.session['hrsHigherEdn']
    else:
        if objExists:
            hrsHigherEdn = sett.hrsHigherEdn
            request.session['hrsHigherEdn'] = hrsHigherEdn
        else:
            hrsHigherEdn = 1560
            request.session['hrsHigherEdn'] = hrsHigherEdn

    hrsCalendarYr = float(hrsCalendarYr)
    hrsAcademicYr = float(hrsAcademicYr)
    hrsHigherEdn = float(hrsHigherEdn)

    if 'new_price' in request.session:
        new_price = request.session['new_price']
    else:  
        new_price = round(float(price),3)
        request.session['new_price'] = new_price

    if 'new_measure' in request.session:
        new_measure = request.session['new_measure']
    else:  
        new_measure = measure
        request.session['new_measure'] = measure

    if request.method == 'POST':
        if 'compute' in request.POST:
            form = WageConverter(data=request.POST)
            if form.is_valid():
                newMeasure = form.save(commit=False)
                if measure.strip() == 'Hour':
                    newMeasure.convertedPrice = price 
                    if newMeasure.newMeasure.strip() == 'Day':
                        newMeasure.convertedPrice = price * 8
                    if newMeasure.newMeasure.strip() == 'Week':
                        newMeasure.convertedPrice = price * 40
                    if newMeasure.newMeasure.strip() == 'Calendar Year':
                        newMeasure.convertedPrice = price * hrsCalendarYr
                    if newMeasure.newMeasure.strip() == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * hrsAcademicYr
                    if newMeasure.newMeasure.strip() == 'Higher Ed Academic Year' or newMeasure.newMeasure.strip() == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * hrsHigherEdn

                if measure.strip() == 'Day': 
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure.strip() == 'Hour':
                        newMeasure.convertedPrice = price /  8
                    if newMeasure.newMeasure.strip() == 'Week':
                        newMeasure.convertedPrice = price *  5
                    if newMeasure.newMeasure.strip() == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / 8)
                    if newMeasure.newMeasure.strip() == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / 8)
                    if newMeasure.newMeasure.strip() == 'Higher Ed Academic Year' or newMeasure.newMeasure.strip() == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / 8)

                if measure.strip() == 'Week': 
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure.strip() == 'Hour':
                        newMeasure.convertedPrice = price / 40
                    if newMeasure.newMeasure.strip() == 'Day':
                        newMeasure.convertedPrice = price /  5
                    if newMeasure.newMeasure.strip() == 'Calendar Year':
                        newMeasure.convertedPrice = price * 52
                    if newMeasure.newMeasure.strip() == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * 36
                    if newMeasure.newMeasure.strip() == 'Higher Ed Academic Year' or newMeasure.newMeasure.strip() == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * 39

                if measure.strip() == 'Calendar Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure.strip() == 'Hour':
                        newMeasure.convertedPrice = price / hrsCalendarYr
                    if newMeasure.newMeasure.strip() == 'Day':
                        newMeasure.convertedPrice = price / (hrsCalendarYr / 8)
                    if newMeasure.newMeasure.strip() == 'Week':
                        newMeasure.convertedPrice = price / 52
                    if newMeasure.newMeasure.strip() == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / hrsCalendarYr)
                    if newMeasure.newMeasure.strip() == 'Higher Ed Academic Year' or newMeasure.newMeasure.strip() == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / hrsCalendarYr)

                if measure.strip() == 'K-12 Academic Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure.strip() == 'Hour':
                        newMeasure.convertedPrice = price / hrsAcademicYr
                    if newMeasure.newMeasure.strip() == 'Day':
                        newMeasure.convertedPrice = price / (hrsAcademicYr / 8)
                    if newMeasure.newMeasure.strip() == 'Week':
                        newMeasure.convertedPrice = price / 36
                    if newMeasure.newMeasure.strip() == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / hrsAcademicYr)
                    if newMeasure.newMeasure.strip() == 'Higher Ed Academic Year' or newMeasure.newMeasure.strip() == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / hrsAcademicYr)

                if measure.strip() == 'Higher Ed Academic Year' or measure.strip() == 'Higher Education Academic Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure.strip() == 'Hour':
                        newMeasure.convertedPrice = price / hrsHigherEdn
                    if newMeasure.newMeasure.strip() == 'Day':
                        newMeasure.convertedPrice = price / (hrsHigherEdn / 8)
                    if newMeasure.newMeasure.strip() == 'Week':
                        newMeasure.convertedPrice = price / 39
                    if newMeasure.newMeasure.strip() == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / hrsHigherEdn)
                    if newMeasure.newMeasure.strip() == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / hrsHigherEdn)
                if newMeasure.convertedPrice is not None:
                   request.session['new_price'] = round(float(newMeasure.convertedPrice),3)
                request.session['new_measure'] = newMeasure.newMeasure 
                return HttpResponseRedirect('/project/programs/costs/wage_converter.html')
            else:
                print(form.errors)

        if 'use' in request.POST:
            price_id = request.session['price_id']
            return HttpResponseRedirect('/project/programs/costs/'+ price_id + '/price_indices.html')

    else:
        form = WageConverter(initial={'convertedPrice':new_price,'newMeasure':new_measure})

    return render('project/programs/costs/wage_converter.html',{'form':form, 'convertedPrice':new_price,'newMeasure':new_measure,'price':price, 'price_id':price_id,'measure':measure, 'hrsCalendarYr': hrsCalendarYr, 'hrsAcademicYr':hrsAcademicYr, 'hrsHigherEdn':hrsHigherEdn},context)
 
def wage_defaults(request):
    context = RequestContext(request)

    if 'hrsCalendarYr' in request.session:
       hrsCalendarYr = request.session['hrsCalendarYr']
    else:   
        try:
            sett = m.Settings.objects.get(projectId=project_id)
            hrsCalendarYr = sett.hrsCalendarYr
            objExists = True 
        except ObjectDoesNotExist:
            hrsCalendarYr = 2080
            objExists = False

    if 'hrsAcademicYr' in request.session:
       hrsAcademicYr = request.session['hrsAcademicYr']
    else:
        if objExists:
            hrsAcademicYr = sett.hrsAcademicYr
        else:
            hrsAcademicYr = 1440

    if 'hrsHigherEdn' in request.session:
       hrsHigherEdn = request.session['hrsHigherEdn']
    else:
        if objExists:
            hrsHigherEdn = sett.hrsHigherEdn
        else:
            hrsHigherEdn = 1560
 
    if request.method == 'POST':
        form = WageDefaults(data=request.POST)
        if form.is_valid():
            benefitRate = form.save(commit=False)
            request.session['hrsCalendarYr'] = benefitRate.hrsCalendarYr
            request.session['hrsAcademicYr'] = benefitRate.hrsAcademicYr
            request.session['hrsHigherEdn'] = benefitRate.hrsHigherEdn
            return HttpResponseRedirect('/project/programs/costs/wage_converter.html')
        else:
            print(form.errors)
    else:
       form = WageDefaults(initial={'hrsCalendarYr': hrsCalendarYr, 'hrsAcademicYr':hrsAcademicYr, 'hrsHigherEdn':hrsHigherEdn}) 

    return render('project/programs/costs/wage_defaults.html',{'form':form},context)

def price_benefits(request,price_id):
    context = RequestContext(request)

    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    if 'projectname' in request.session:
       projectname = request.session['projectname']
    else:
       projectname = 'ccc'
    if 'programname' in request.session:
       progname = request.session['programname']
    else:
       progname = 'ccc'

    request.session['price_id'] = price_id
    price = m.Prices.objects.get(pk=price_id)

    if 'Rate' in request.session:
        benefitRate = request.session['Rate']
    else:
        if 'benefit_id' in request.session:
            benefit_id = request.session['benefit_id']
            benefit = m.Benefits.objects.get(pk=benefit_id)
            benefitRate = benefit.BenefitRate
        else:
            benefitRate = 0

    if request.method == 'POST':
        form = PriceBenefits(request.POST)
        if form.is_valid():
            benefitRate = form.save(commit=False)
            request.session['Rate'] = benefitRate.benefitRate
            return HttpResponseRedirect('/project/programs/costs/summary.html')
        else:
            print(form.errors)
            return render('project/programs/costs/price_benefits.html',{'form':form, 'benefitRate':benefitRate,'price':price, 'project_id':project_id, 'program_id':program_id,'projectname':projectname, 'programname':progname,'form.errors':form.errors},context)
    else:
        form = PriceBenefits()
    return render('project/programs/costs/price_benefits.html',{'form':form, 'benefitRate':benefitRate,'price':price, 'project_id':project_id, 'program_id':program_id,'projectname':projectname, 'programname':progname},context)

def benefits(request):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = ''
    allbenefits = m.Benefits.objects.all()
    return render(request,'project/programs/costs/benefits.html', {'project_id':project_id, 'program_id':program_id, 'allbenefits' : allbenefits, 'price_id':price_id})

def save_benefit(request,ben_id):
    context = RequestContext(request)
    request.session['benefit_id'] = ben_id
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = ''
    return HttpResponseRedirect('/project/programs/costs/'+ price_id +'/price_benefits.html')

def price_summary(request):
    context = RequestContext(request)
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = ''
    price = m.Prices.objects.get(pk=price_id)
    
    if 'Rate' in request.session:
       Rate = request.session['Rate']
    else:
       Rate = None

    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    if 'program_id' in request.session:
       program_id = request.session['program_id']
    else:
       program_id = 0   
    if 'projectname' in request.session:
       projectname = request.session['projectname']
    else:
       projectname = 'ccc'
    if 'programname' in request.session:
       progname = request.session['programname']
    else:
       progname = 'ccc'

    pcount = 0

    if 'new_price' in request.session:
       new_price = request.session['new_price']
    else:
       new_price = price.price

    if 'new_measure' in request.session:
       new_measure = request.session['new_measure']
    else:
       new_measure = price.unitMeasurePrice

    if 'benefit_id' in request.session:
        benefit = m.Benefits.objects.get(pk=request.session['benefit_id'])
        SourceBenefitData = benefit.SourceBenefitData
        YearBenefit = benefit.YearBenefit
    else:
        SourceBenefitData = ''
        YearBenefit = ''
    
    if 'lifetimeAsset' in request.session:
       lifetimeAsset = request.session['lifetimeAsset']
    else:
       lifetimeAsset = 1.0
            
    if 'interestRate' in request.session:
       interestRate = request.session['interestRate']
    else:
       interestRate = 0.0

    try:
       sett = m.Settings.objects.get(projectId=request.session['project_id'])
       discountRateEstimates = sett.discountRateEstimates
       try:
          infEstimate = m.InflationIndices.objects.get(projectId=request.session['project_id'],yearCPI=sett.yearEstimates)
       except ObjectDoesNotExist:
          infEstimate = 'No inflation index available'
       try:
          geoEstimate = m.GeographicalIndices.objects.get(projectId=request.session['project_id'],stateIndex=sett.stateEstimates,areaIndex=sett.areaEstimates)
          geoEst = geoEstimate.geoIndex
       except ObjectDoesNotExist:
          geoEst = 'No geographical index available'
    except ObjectDoesNotExist:
       discountRateEstimates = 'No discount rate'

    try:
       inf = m.InflationIndices.objects.get(projectId=request.session['project_id'],yearCPI=price.yearPrice)
       infinf = inf.indexCPI
    except ObjectDoesNotExist:
       infinf = 'No inflation index available'

    try:
       geo = m.GeographicalIndices.objects.get(projectId=request.session['project_id'],stateIndex=price.statePrice,areaIndex=price.areaPrice)
       geoIndex = geo.geoIndex
    except ObjectDoesNotExist:
       geoIndex = 'No geographical index available'

    try:
       programdesc = m.ProgramDesc.objects.get(programId = request.session['program_id'])
       progid = programdesc.id
       if programdesc.numberofparticipants is None:
          numberofparticipants = 1
       else:
          numberofparticipants = programdesc.numberofparticipants 
    except ObjectDoesNotExist:
       numberofparticipants = 1
       progid = 0
   
    try:
       pcount = m.ParticipantsPerYear.objects.filter(programdescId_id=progid).count()
    except ObjectDoesNotExist:
       pcount = 0
 
    try:
       eff = m.Effectiveness.objects.get(programId_id = request.session['program_id'])
       avgeff = eff.avgeffectperparticipant
    except ObjectDoesNotExist:
       avgeff = None

    if pcount > 0:
       MFormSet = modelformset_factory(m.Ingredients, form=PriceSummary, extra=pcount)
       if request.method == 'POST':
          form = MFormSet(request.POST, request.FILES)
          if form.is_valid():
             ingredients = form.save(commit=False)
             qtyNone = True
             percNone = True
             for ingredient in ingredients:
                if ingredient.quantityUsed is not None:
                   qtyNone = False
                if ingredient.percentageofUsage is not None:
                   percNone = False

             if qtyNone == True:
                err = 'Enter a Quantity for at least one year'
                return render('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'new_measure':new_measure,'projectname':projectname, 'programname':progname,'form.errors':form.errors,'err': err},context)
             if percNone == True:
                err = 'Enter % of time used for at least one year'
                return render('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'new_measure':new_measure,'projectname':projectname, 'programname':progname,'form.errors':form.errors,'err': err},context)


             for ingredient in ingredients:
                 if ingredient.quantityUsed is not None and ingredient.percentageofUsage is not None:
                    ingredient.variableFixed = request.POST.get('variableFixed2')
                    if ingredient.notes is None:
                       ingredient.notes = ''
                    else:
                       ingredient.notes = request.POST.get('notes2')
                    ingredient.category = price.category
                    ingredient.ingredient = price.ingredient
                    ingredient.edLevel = price.edLevel
                    ingredient.sector = price.sector
                    ingredient.unitMeasurePrice = price.unitMeasurePrice
                    ingredient.price = price.price
                    ingredient.sourcePriceData = price.sourcePriceData
                    ingredient.urlPrice = price.urlPrice
                    ingredient.newMeasure = new_measure
                    ingredient.convertedPrice = new_price
                    if Rate is not None:
                       ingredient.benefitRate = round(float(Rate.strip('"')),2)
                    ingredient.SourceBenefitData = SourceBenefitData
                    ingredient.YearBenefit = YearBenefit
                    ingredient.yearPrice = price.yearPrice
                    ingredient.statePrice = price.statePrice
                    ingredient.areaPrice = price.areaPrice
                    if ingredient.category != 'Personnel':
                       ingredient.lifetimeAsset = lifetimeAsset
                       ingredient.interestRate = interestRate
                    else:  
                       ingredient.lifetimeAsset = request.POST.get('lifetimeAsset')
                       ingredient.interestRate = request.POST.get('interestRate')
                    ingredient.indexCPI = infinf
                    ingredient.geoIndex = geoIndex
                    ingredient.programId = request.session['program_id']
                    if ingredient.lifetimeAsset is None:
                       ingredient.lifetimeAsset = 1
                    if ingredient.interestRate is None or ingredient.interestRate == '0':
                       ingredient.interestRate = 0.0
                    if ingredient.lifetimeAsset == 1 or ingredient.lifetimeAsset == '1':
                       ingredient.priceAdjAmortization = round(float(ingredient.convertedPrice),3)
                    else:  
                       if ingredient.interestRate == '0.0' or ingredient.interestRate == 0.0 or ingredient.interestRate == '0':
                          ingredient.priceAdjAmortization = round(float(ingredient.convertedPrice),3) / float(ingredient.lifetimeAsset)
                       else:
                          ingredient.priceAdjAmortization = round(float(ingredient.convertedPrice),3) * ((float(ingredient.interestRate)/100)*math.pow((1+(float(ingredient.interestRate)/100)),float(ingredient.lifetimeAsset)))/ (math.pow((1+(float(ingredient.interestRate)/100)),float(ingredient.lifetimeAsset))-1)
                    if ingredient.category == 'Personnel':
                       ingredient.priceAdjBenefits = round(round(ingredient.priceAdjAmortization,3) * (1 + float(ingredient.benefitRate)/100),3)
                    else:
                       ingredient.priceAdjBenefits = round(ingredient.priceAdjAmortization,3)
                    if infinf == 'No inflation index available' or infEstimate.indexCPI == 'No inflation index available':
                       ingredient.priceAdjInflation = 'No index'
                    else:
                       ingredient.priceAdjInflation = round(round(ingredient.priceAdjBenefits,3) * round((float(infEstimate.indexCPI) / float(infinf)),3),3)
                    if ingredient.priceAdjInflation == 'No index':
                       ingredient.indexCPI = 'No inflation index available'
                       ingredient.priceAdjGeographicalArea = None
                       ingredient.priceNetPresentValue = None
                       ingredient.adjPricePerIngredient = 'No inflation index available'
                       ingredient.costPerIngredient = None
                       ingredient.costPerParticipant = None
                    else:
                       if geoIndex == 'No geographical index available' or geoEst == 'No geographical index available':
                          ingredient.priceAdjGeographicalArea = 'No index'
                       else:
                          ingredient.priceAdjGeographicalArea = round(ingredient.priceAdjInflation,3) * (float(geoEst) / float(geoIndex))
                       if ingredient.priceAdjGeographicalArea == 'No index':
                          ingredient.priceNetPresentValue = None
                          ingredient.adjPricePerIngredient = 'No geographical index available'
                          ingredient.costPerIngredient = None
                          ingredient.costPerParticipant = None
                       else:  
                          ingredient.priceNetPresentValue = round(ingredient.priceAdjGeographicalArea,3) * math.exp((1- ingredient.yearQtyUsed) * (discountRateEstimates/100))
                          ingredient.adjPricePerIngredient = round(ingredient.priceNetPresentValue,3)
                          if ingredient.quantityUsed is None and ingredient.percentageofUsage is None:
                             ingredient.costPerIngredient = 0.0
                          else:
                             if ingredient.percentageofUsage == 100:
                                ingredient.costPerIngredient = round(ingredient.adjPricePerIngredient,3) * float(ingredient.quantityUsed)
                             else:
                                ingredient.costPerIngredient = round(round(ingredient.adjPricePerIngredient,3) * float(ingredient.quantityUsed) * (float(ingredient.percentageofUsage)/100),3)
                             try:
                                partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=programdesc.id, yearnumber=ingredient.yearQtyUsed)
                                ingredient.costPerParticipant = round(round(float(ingredient.costPerIngredient),3) / float(partperyear.noofparticipants),3)
                             except ObjectDoesNotExist:
                                ingredient.costPerParticipant = round(round(float(ingredient.costPerIngredient),3) / float(numberofparticipants),3)
                    ingredient.save()

             total_cost = 0
             ing =  m.Ingredients.objects.filter(programId = request.session['program_id'])
             for i in ing:
                 if i.costPerIngredient is not None:
                    total_cost = total_cost + i.costPerIngredient
                 else:
                    total_cost = total_cost
             for i in ing:
                i.totalCost = total_cost
                if i.costPerIngredient is not None:
                   i.percentageCost = i.costPerIngredient * 100 / i.totalCost
                else:
                   i.percentageCost = 0  

                if numberofparticipants is not None:
                   if numberofparticipants == 0:
                      i.averageCost = float(i.totalCost) / float("inf")
                   else:
                      i.averageCost = float(i.totalCost) / float(numberofparticipants)
                else:
                   i.averageCost = None
                if avgeff is not None and avgeff != '0' and i.averageCost is not None:
                   i.effRatio = float(i.averageCost) / float(avgeff)
                else:
                   i.effRatio = None

                i.save(update_fields=['totalCost','averageCost','percentageCost','effRatio'])
                upd = updateDate(project_id, program_id)
             return HttpResponseRedirect('/project/programs/effect/'+ project_id + '/' + program_id + '/tabbedview.html?activeform=costform')
             
          else:
             print(form.errors)
             return render('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'new_measure':new_measure,'projectname':projectname, 'programname':progname,'form.errors':form.errors},context)
       else:
          form = MFormSet(queryset=m.Ingredients.objects.none(),initial=[{'yearQtyUsed': "%d" % (i+1)} for i in range(10)])
    else:
       if request.method == 'POST':
          form = PriceSummary(request.POST)
          if form.is_valid():
             ingredient = form.save(commit=False)
             if ingredient.quantityUsed is None:
                err = 'Enter Quantity'
                return render('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'new_measure':new_measure,'projectname':projectname, 'programname':progname,'form.errors':form.errors,'err': err},context)
             if ingredient.percentageofUsage is None:
                err = 'Enter % of time used'
                return render('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'new_measure':new_measure,'projectname':projectname, 'programname':progname,'form.errors':form.errors,'err': err},context)
             ingredient.category = price.category
             ingredient.ingredient = price.ingredient
             ingredient.edLevel = price.edLevel
             ingredient.sector = price.sector
             ingredient.unitMeasurePrice = price.unitMeasurePrice
             ingredient.price = price.price
             ingredient.sourcePriceData = price.sourcePriceData
             ingredient.urlPrice = price.urlPrice
             ingredient.newMeasure = new_measure
             ingredient.convertedPrice = float(new_price)
             if Rate is not None:
                ingredient.benefitRate = round(float(Rate.strip('"')),2)
             ingredient.SourceBenefitData = SourceBenefitData
             ingredient.YearBenefit = YearBenefit
             ingredient.yearPrice = price.yearPrice
             ingredient.statePrice = price.statePrice
             ingredient.areaPrice = price.areaPrice
             if ingredient.category != 'Personnel':
                ingredient.lifetimeAsset = lifetimeAsset
                ingredient.interestRate = interestRate
             ingredient.yearQtyUsed = 1      
             ingredient.indexCPI = infinf
             ingredient.geoIndex = geoIndex
             ingredient.programId = request.session['program_id']
             if ingredient.lifetimeAsset is None:
                ingredient.lifetimeAsset = 1
             if ingredient.interestRate is None or ingredient.interestRate == '0':
                ingredient.interestRate = 0.0
             if ingredient.lifetimeAsset == 1 or ingredient.lifetimeAsset == '1':
                ingredient.priceAdjAmortization = round(float(ingredient.convertedPrice),3) 
             else:   
                if ingredient.interestRate == '0.0' or ingredient.interestRate == 0.0 or ingredient.interestRate == '0':   
                   ingredient.priceAdjAmortization = round(ingredient.convertedPrice,3) / float(ingredient.lifetimeAsset)
                else:
                   ingredient.priceAdjAmortization = round(ingredient.convertedPrice,3) * ((float(ingredient.interestRate)/100)*math.pow((1+(float(ingredient.interestRate)/100)),float(ingredient.lifetimeAsset)))/ (math.pow((1+(float(ingredient.interestRate)/100)),float(ingredient.lifetimeAsset))-1)
             if ingredient.category == 'Personnel':
                ingredient.priceAdjBenefits = round(ingredient.priceAdjAmortization,3) * round((1 + float(ingredient.benefitRate)/100),3)
             else:
                ingredient.priceAdjBenefits = round(ingredient.priceAdjAmortization,3)
             if infinf == 'No inflation index available' or infEstimate.indexCPI == 'No inflation index available':
                ingredient.priceAdjInflation = 'No index'
             else:
                ingredient.priceAdjInflation = round(round(ingredient.priceAdjBenefits,3) * round(float(infEstimate.indexCPI),3) / round(float(infinf),3),3) 
             if ingredient.priceAdjInflation == 'No index':
                ingredient.indexCPI = 'No inflation index available' 
                ingredient.priceAdjGeographicalArea = None 
                ingredient.priceNetPresentValue = None
                ingredient.adjPricePerIngredient = 'No inflation index available'
                ingredient.costPerIngredient = None
                ingredient.costPerParticipant = None
             else:
                if geoIndex == 'No geographical index available' or geoEst == 'No geographical index available':
                   ingredient.priceAdjGeographicalArea = 'No index'
                else:
                   ingredient.priceAdjGeographicalArea = round(ingredient.priceAdjInflation,3) * (float(geoEst) / float(geoIndex))    
                if ingredient.priceAdjGeographicalArea == 'No index':
                   ingredient.priceNetPresentValue = None
                   ingredient.adjPricePerIngredient = 'No geographical index available'
                   ingredient.costPerIngredient = None                                                                           
                   ingredient.costPerParticipant = None
                else:
                   ingredient.priceNetPresentValue = round(ingredient.priceAdjGeographicalArea,3) * math.exp((1-ingredient.yearQtyUsed) *(discountRateEstimates/100))
                   ingredient.adjPricePerIngredient = round(ingredient.priceNetPresentValue,3)
                   if ingredient.percentageofUsage == 100:
                      ingredient.costPerIngredient = round(ingredient.adjPricePerIngredient,3) * float(ingredient.quantityUsed)
                   else:
                      ingredient.costPerIngredient = round(round(ingredient.adjPricePerIngredient,3) * float(ingredient.quantityUsed) * (float(ingredient.percentageofUsage)/100),3)
                   if numberofparticipants is not None:
                      ingredient.costPerParticipant = round(float(ingredient.costPerIngredient),3) / float(numberofparticipants)
             #print(ingredient.priceAdjAmortization
             #print(ingredient.priceAdjBenefits
             #print(ingredient.priceAdjInflation
             #print(ingredient.priceAdjGeographicalArea
             #print(ingredient.priceNetPresentValue
             #print(ingredient.adjPricePerIngredient
             #print(ingredient.costPerIngredient
             #print(ingredient.costPerParticipant
             ingredient.save()

             total_cost = 0
             ing = m.Ingredients.objects.filter(programId = request.session['program_id'])
             for i in ing:
                if i.costPerIngredient is not None:
                   total_cost = total_cost + i.costPerIngredient
                else:
                   total_cost = total_cost
             for i in ing:
                i.totalCost = total_cost
                if i.costPerIngredient is not None and i.totalCost is not None and  float(i.totalCost) != 0.000:
                   i.percentageCost = i.costPerIngredient * 100 / i.totalCost
                else:
                   i.percentageCost = 0
                if numberofparticipants is not None:
                   i.averageCost = float(i.totalCost) / float(numberofparticipants)
                if avgeff is not None and i.averageCost is not None:
                   i.effRatio = float(i.averageCost) / float(avgeff)
                else:
                   i.effRatio = None
                if numberofparticipants is not None:
                   i.save(update_fields=['totalCost','averageCost','percentageCost','effRatio'])
                else:
                   i.save(update_fields=['totalCost','percentageCost','effRatio']) 
                upd = updateDate(project_id, program_id)
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/' + program_id + '/tabbedview.html?activeform=costform')
          else:
             print(form.errors)

       else:
          form = PriceSummary()
    return render('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'projectname':projectname, 'programname':progname,'new_measure':new_measure},context)

def program_list(request,project_id):
    request.session['project_id'] = project_id
    loggedinuser = request.session['user']
    sharList = [] 
    try:
        project = m.Projects.objects.get(pk=project_id)
        program = m.Programs.objects.filter(projectId=project_id)
        if project.shared == 'Y':
            try:
               qset = m.SharedProj.objects.filter(projectid=project_id)
               for q in qset:
                   sharList.append(q.shared_user)
                   sharList.append(', ')
            except MultipleObjectsReturned: 
               qset  = m.SharedProj.objects.get(projectid=project_id)
               sharList.append(q.shared_user)
        sharList = ''.join(sharList)
        if sharList[-2:] == ", ":
           sharList = sharList[:-2]
    except ObjectDoesNotExist:
        return HttpResponse('A Project and/or Program does not exist! Cannot proceed further.')
    return render(
            'project/programs/program_list.html',
            {'project':project,'program':program,'loggedinuser':loggedinuser, 'sharList':sharList})

def del_program(request, program_id):
    context = RequestContext(request)

    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0

    try:
       m.Distribution.objects.filter(programId=program_id).delete()
    except ObjectDoesNotExist:
       print('distribution do not exist')

    try:
       m.Agencies.objects.filter(programId=program_id).delete()
    except ObjectDoesNotExist:
       print('agencies do not exist')

    try:
       m.Transfers.objects.filter(programId=program_id).delete()
    except ObjectDoesNotExist:
       print('transfers do not exist')

    try:
       m.Ingredients.objects.filter(programId=program_id).delete()
    except ObjectDoesNotExist:
       print('ingredients do not exist')
    try:   
       m.Effectiveness.objects.get(programId_id = program_id).delete()
    except ObjectDoesNotExist:
       print('effectiveness does not exist')
    try:   
       progdesc = m.ProgramDesc.objects.get(programId_id = program_id)
       m.ParticipantsPerYear.objects.filter(programdescId_id = progdesc.id).delete()
       m.ProgramDesc.objects.get(programId_id = program_id).delete()
    except ObjectDoesNotExist:
       print('program desc does not exist')
    m.Programs.objects.get(pk = program_id).delete()
    upd = updateDate(project_id, None)
    return HttpResponseRedirect('/project/programs/' + project_id + '/program_list.html')


def dupl_program(request, program_id):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0

    prog = m.Programs.objects.get(pk = program_id)
    prog.progname = prog.progname + ' COPY' 
    prog.pk = None
    prog.save()

    try:
       progdesc = m.ProgramDesc.objects.get(programId_id = program_id)
       progdesc.programId_id = prog.id
       old_progdesc_id = progdesc.pk
       progdesc.pk = None
       progdesc.save()
       for part in m.ParticipantsPerYear.objects.filter(programdescId_id = old_progdesc_id):
          ppy = m.ParticipantsPerYear.objects.get(pk = part.id)
          ppy.programdescId_id = progdesc.id
          ppy.pk = None
          ppy.save()
    except ObjectDoesNotExist:
       print('program desc does not exist')

    try:
       eff = m.Effectiveness.objects.get(programId_id = program_id)
       eff.programId_id = prog.id
       eff.pk = None
       eff.save()
    except ObjectDoesNotExist:
       print('effectiveness does not exist')

    try:
       for i in  m.Ingredients.objects.filter(programId=program_id):
          ing = m.Ingredients.objects.get(pk = i.id)
          ing.programId = prog.id
          ing.pk = None
          ing.save()
          try:
             dis = m.Distribution.objects.get(ingredientId = program_id)
             dis.programId = prog.id
             dis.ingredientId = ing.id
             dis.pk = None
             dis.save()
          except ObjectDoesNotExist:
             print('distribution do not exist')
    except ObjectDoesNotExist:
       print('ingredients do not exist')

    try:
       ag = m.Agencies.objects.get(programId=program_id)
       ag.programId = prog.id
       ag.pk = None
       ag.save()
    except ObjectDoesNotExist:
       print('agencies do not exist')

    try:
       for t in m.Transfers.objects.filter(programId=program_id):
          trans = m.Transfers.objects.get(pk=t.id)
          trans.programId = prog.id
          trans.pk = None
          trans.save()
    except ObjectDoesNotExist:
       print('transfers do not exist')
    upd = updateDate(project_id, None)
    return HttpResponseRedirect('/project/programs/' + project_id + '/program_list.html')

def edit_program(request, program_id):
    if 'project_id' in request.session:
       project_id = request.session['project_id']
    else:
       project_id = 0
    prog = m.Programs.objects.get(pk=program_id)
    context = RequestContext(request)

    if request.method == 'POST':
        programform = ProgramsForm(request.POST,instance=prog)

        if programform.is_valid():
            progname = programform.save(commit=False)
            progname.save()
            upd = updateDate(project_id, program_id)
            return HttpResponseRedirect('/project/programs/'+project_id+'/program_list.html')
        else:
            print(programform.errors)

    else:
        programform = ProgramsForm(instance=prog)

    return render(
            'project/programs/edit_program.html',
            {'programform': programform, 'project_id':project_id}, context)

def index(request):
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    recent_projects = m.Projects.objects.filter(created_at__gt = two_days_ago).all()
    #template = loader.get_template('index.html')
 
    #context = Context({
        #'projects_list' : recent_projects
    #})
    #return HttpResponse(template.render(context))
    return render(request, 'index.html', {'projects_list' : recent_projects})

'''def about(request):
    context = RequestContext(request)
    return render('about.html', {}, context)
'''
def add_project(request):
    context = RequestContext(request)
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       if request.method == 'POST':
          projectform = ProjectsForm(data=request.POST)

          if projectform.is_valid():
             projectname = projectform.save()
             projectname.user = request.session['user']
             try:
                p = m.Projects.objects.filter(projectname = projectname.projectname, user = projectname.user).count()
                if p > 0:
                   return render('project/add_project.html',{'projectform':projectform,'err':'This project name is already taken. Please enter a unique name.'}, context)
             except ObjectDoesNotExist:
                print(projectname.projectname)
             projectname.save()
             for i in m.InflationIndices_orig.objects.all():
                 inf =  m.InflationIndices.objects.create(yearCPI=i.yearCPI, indexCPI=i.indexCPI, projectId=projectname.id)
             for g in m.GeographicalIndices_orig.objects.all():
                 geo = m.GeographicalIndices.objects.create(stateIndex=g.stateIndex, areaIndex=g.areaIndex, geoIndex=g.geoIndex, projectId=projectname.id)
             latest = m.InflationIndices_orig.objects.all().latest('yearCPI')
             s = m.Settings.objects.create(discountRateEstimates=3.5, yearEstimates = latest.yearCPI, stateEstimates='All states', areaEstimates="All areas", selectDatabase="[u'CBCSE',u'My']",limitEdn="[u'Select',u'General',u'Grades PK', u'Grades K-6', u'Grades 6-8', u'Grades 9-12',u'Grades K-12','PostSecondary']",limitSector="[u'Select',u'Any',u'Public',u'Private']",limitYear="[u'All',u'recent']",hrsCalendarYr=2080,hrsAcademicYr=1440,hrsHigherEdn=1560,projectId=projectname.id) 
             request.session['project_id'] = projectname.id
             return HttpResponseRedirect('/project/settings.html')
             #return render('project/add_project.html',{'projectform':projectform}, context)
          else:
             print(projectform.errors)

       else:
          projectform = ProjectsForm()        

       return render(
            'project/add_project.html',
            {'projectform': projectform}, context)

def edit_project(request, project_id):
    proj = m.Projects.objects.get(pk=project_id)
    context = RequestContext(request)
   
    if request.method == 'POST':
        projectform = ProjectsForm(request.POST,instance=proj)

        if projectform.is_valid():
            projectname = projectform.save(commit=False)
            try:
               p = m.Projects.objects.filter(projectname = projectname.projectname).count()
               if p > 1:
                  return render('project/edit_project.html',{'projectform':projectform,'err':'This project name is already taken. Please enter a unique name.'}, context)
            except ObjectDoesNotExist:
                print(projectname.projectname)
            projectname.updated_at = datetime.datetime.now()
            projectname.save(update_fields=['projectname', 'updated_at'])
            return HttpResponseRedirect('/project/project_list.html')
        else:
            print(projectform.errors)

    else:
        projectform = ProjectsForm(instance=proj)

    return render(
            'project/edit_project.html',
            {'projectform': projectform}, context)

def share_project(request, project_id):
    context = RequestContext(request)
    if 'user' in request.session:
       loggedinuser = request.session['user']     
    else:
       loggedinuser = 'ccc'
    f = open( '/home/amritha/costtool/documents/f.txt', 'w+' )
    # if shared user is deleted, mark delrec as Y, go through all the forms in the formset; insert the new rows - add deleted forms id to a list - ask user confirmation if he wants to delete the forms and only then delete
    delrec = 'N'
    shareList = []
    project = m.Projects.objects.get(pk=project_id)   
    projectname = project.projectname
    if loggedinuser == project.user:
       sameuser = 'Y'
    else:
       sameuser = 'N' 
    MFormSet = modelformset_factory(m.SharedProj, form=ShareProjForm, extra=10)
    if request.method == 'POST':
       shareform = MFormSet(request.POST,request.FILES,prefix="shareform" )
       if shareform.is_valid():
          proj1 = shareform.save(commit=False)
          shared_user = ""
          sid = 0
          for p in proj1:
              if (p.shared_user == loggedinuser):
                  return render('project/share_project.html',{'shareform':shareform,'sameuser': sameuser, 'delrec':delrec, 'loggedinuser' : loggedinuser, 'projectname': projectname,'shareduser': p.shared_user, 'err1':'The user name you have entered is ', 'err2':'. You cannot enter your own name. Please enter a valid user name.'}, context) 
              #try:
                 #existing = m.SharedProj.objects.filter(projectid=project_id).filter(shared_user=p.shared_user)
                 #return render('project/share_project.html',{'shareform':shareform,'shareduser': p.shared_user,'err1':'The user name you have entered is ', 'err2':'. He is already a shared project user. Please enter another user.'}, context)                   
              #except:
              try:
                 login = m.Login.objects.filter(user=p.shared_user).latest('startDate')
              except:
                  if p.shared_user != '': 
                      return render('project/share_project.html',{'shareform':shareform,'sameuser': sameuser,'delrec':delrec,'loggedinuser' : loggedinuser, 'projectname': projectname,'shareduser': p.shared_user,'err1':'The user name you have entered is ', 'err2':'. It does not exist. Please enter a valid user name.'}, context)    
              p.shared_date = datetime.datetime.now()
              p.projectid = project_id
              if p.shared_user != '':
                 p.save()
                 #upd = updateProj(project_id)
              if p.shared_user == '' and p.shared_date != '':                
                  delrec = 'Y'
                  sid = p.id
                  shareList.append(p.id)
                  #shareList.append(',')
          request.session['shareList'] = shareList

          if delrec == 'Y':
              if 'submit2' in request.POST:
                 request.session['button'] = 'first'
              else:
                 request.session['button'] = 'second' 
              return render(request,'project/alert_proj.html', {'sid':sid}) 
          upd = updateProj(project_id)
          if 'submit2' in request.POST:
             return HttpResponseRedirect('/project/project_list.html')
          else:
             return HttpResponseRedirect('/project/%s/share_project.html' % project_id) 
       else:
          print(shareform.errors)
          return render( 'project/share_project.html',{'shareform':shareform, 'sameuser': sameuser,'delrec':delrec,'loggedinuser' : loggedinuser,'projectname': projectname, 'err':shareform.errors},context)
    else:
       qset = m.SharedProj.objects.filter(projectid=project_id)
       #for q in qset:
           #oldList.append(q.shared_user)
       #f.write(''.join(oldList))
       f.write(sameuser)
       shareform = MFormSet(queryset=qset,prefix="shareform" )
       for form in shareform:
           if sameuser != 'Y':
              form.fields['shared_user'].widget.attrs['readonly'] = True 
    return render(
            'project/share_project.html',{'shareform':shareform, 'sameuser': sameuser,'delrec':delrec, 'loggedinuser' : loggedinuser, 'projectname': projectname},
             context)

def del_sharproj(request):                                                                                                              
    context = RequestContext(request)
    #f = open( '/home/amritha/costtool/documents/f.txt', 'w+' )
    if 'shareList' in request.session:
       for s in request.session['shareList']:
           try: 
              sharproj = m.SharedProj.objects.get(id=s)
              project_id = sharproj.projectid
              sharproj.delete()
              upd = updateProj(project_id)
           except ObjectDoesNotExist:
              print('shared project user does not exist')
    #if 'button' not in request.session:
        #button = request.session['button']
    #else:
        #button = 'first'
    if request.session['button'] == 'first':    
        return HttpResponseRedirect('/project/project_list.html')
    else:
        return HttpResponseRedirect('/project/%s/share_project.html' % project_id) 
 
def dupl_project(request, project_id):
    context = RequestContext(request)

    proj = m.Projects.objects.get(pk = project_id)
    proj.projectname = proj.projectname + ' COPY'
    proj.user = request.session['user'];
    proj.shared = None;
    proj.shared_user = None;
    proj.created_at = datetime.datetime.now()
    proj.pk = None
    proj.save()

    try:
       for i in m.InflationIndices.objects.filter(projectId=project_id):
          inf = m.InflationIndices.objects.get(pk = i.id)
          inf.projectId = proj.id
          inf.pk = None
          inf.save()
    except ObjectDoesNotExist:
          print('inf does not exist')

    try:
       for g in m.GeographicalIndices.objects.filter(projectId=project_id):
          geo = m.GeographicalIndices.objects.get(pk = g.id)
          geo.projectId = proj.id
          geo.pk = None
          geo.save()
    except ObjectDoesNotExist:
          print('geo does not exist')

    try:
       sett = m.Settings.objects.get(projectId=project_id)
       sett.projectId = proj.id
       sett.pk = None
       sett.save()
    except ObjectDoesNotExist:
       print('sett does not exist')

    for prog in m.Programs.objects.filter(projectId = project_id):
       prog2 = m.Programs.objects.get(pk = prog.id)
       prog2.progname = prog.progname + ' COPY'
       prog2.projectId = proj.id
       prog2.pk = None
       prog2.save()
       try:
          progdesc = m.ProgramDesc.objects.get(programId_id = prog.id)
          progdesc.programId_id = prog2.id
          old_progdesc_id = progdesc.pk
          progdesc.pk = None
          progdesc.save()
          for part in m.ParticipantsPerYear.objects.filter(programdescId_id = old_progdesc_id):
             ppy = m.ParticipantsPerYear.objects.get(pk = part.id)
             ppy.programdescId_id = progdesc.id
             ppy.pk = None
             ppy.save()
       except ObjectDoesNotExist:
          print('program desc does not exist')

       try:
          eff = m.Effectiveness.objects.get(programId_id = prog.id)
          eff.programId_id = prog2.id
          eff.pk = None
          eff.save()
       except ObjectDoesNotExist:
          print('effectiveness does not exist')

       try:
          for i in  m.Ingredients.objects.filter(programId=prog.id):
             ing = m.Ingredients.objects.get(pk = i.id)
             ing.programId = prog2.id
             ing.pk = None
             ing.save()
             try:
                dis = m.Distribution.objects.get(ingredientId = i.id)
                dis.programId = prog2.id
                dis.ingredientId = ing.id
                dis.pk = None
                dis.save()
             except ObjectDoesNotExist:
                print('distribution do not exist')
       except ObjectDoesNotExist:
          print('ingredients do not exist')

       try:
          ag = m.Agencies.objects.get(programId=prog.id)
          ag.programId = prog2.id
          ag.pk = None
          ag.save()
       except ObjectDoesNotExist:
          print('agencies do not exist')

       try:
          for t in m.Transfers.objects.filter(programId=prog.id):
             trans = m.Transfers.objects.get(pk=t.id)
             trans.programId = prog2.id
             trans.pk = None
             trans.save()
       except ObjectDoesNotExist:
          print('transfers do not exist')

    return HttpResponseRedirect('/project/project_list.html')

def project_list(request):
    #f = open( '/home/amritha/costtool/documents/f.txt', 'w+' )
    if 'project_id' in request.session:
        del request.session['project_id']

    if 'program_id' in request.session:
        del request.session['program_id']

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'ccc'
    try:
       login = m.Login.objects.filter(user=loggedinuser).latest('startDate')
       template = loader.get_template('project/project_list.html')
    except ObjectDoesNotExist:   
       template = loader.get_template('prices/message.html')
    
    allprojects = m.Projects.objects.filter(user = loggedinuser)

    #if loggedinuser in ('amritha_yahoo', 'ammtest', 'amritha', 'fh4', 'Atsuko Muroga', 'yilinpan','Maya Escueta' ):
    projlist = [] 
    for s in m.SharedProj.objects.filter(shared_user = loggedinuser):
           #f.write('\n') 
       projlist.append(s.projectid)
       #f.write(str(projlist))
       allprojects = allprojects | m.Projects.objects.filter(id__in=projlist)
    #f.close()
    allprojects = allprojects.order_by('-id')
    context = Context({
        'allprojects' : allprojects,'loggedinuser' : loggedinuser
    })
    return HttpResponse(template.render(context))

def del_project(request, project_id):
    context = RequestContext(request)
    
    for p in m.Programs.objects.filter(projectId = project_id): 
       try:
          m.Distribution.objects.filter(programId=p.id).delete()
       except ObjectDoesNotExist:
          print('distribution do not exist')

       try:
          m.Agencies.objects.filter(programId=p.id).delete()
       except ObjectDoesNotExist:
          print('agencies do not exist')

       try:
          m.Transfers.objects.filter(programId=p.id).delete()
       except ObjectDoesNotExist:
          print('transfers do not exist')

       try:
          m.Ingredients.objects.filter(programId=p.id).delete()
       except ObjectDoesNotExist:
          print('ingredients do not exist')
            
       try:
          m.Effectiveness.objects.get(programId_id = p.id).delete()
       except ObjectDoesNotExist:
          print('effectiveness does not exist')
            
       try:
          progdesc = m.ProgramDesc.objects.get(programId_id = p.id)
          m.ParticipantsPerYear.objects.filter(programdescId_id = progdesc.id).delete()
          m.ProgramDesc.objects.get(programId_id = p.id).delete()
       except ObjectDoesNotExist:
          print('program desc does not exist')
            
       m.Programs.objects.get(pk = p.id).delete()
    
    m.InflationIndices.objects.filter(projectId=project_id).delete()
    m.GeographicalIndices.objects.filter(projectId=project_id).delete()
    m.Settings.objects.get(projectId=project_id).delete()
    m.Projects.objects.get(pk=project_id).delete()
    return HttpResponseRedirect('/project/project_list.html')

def add_price(request):
    context = RequestContext(request)
    myUser = request.session['user']
    if request.method == 'POST':
        pricesform = PricesForm(data=request.POST,user = myUser)

        if pricesform.is_valid():
            priceProvider = pricesform.save(commit=False)
            priceProvider.priceProvider = request.session['user']
            priceProvider.save()
            return HttpResponseRedirect('/prices/my_price_list.html')
        else:
            print(pricesform.errors)
            form_errors = pricesform.errors
            return render('prices/add_price.html',{'form_errors': form_errors, 'pricesform': pricesform}, context)

    else:
        pricesform = PricesForm(user = myUser)

    return render(
            'prices/add_price.html',
            {'pricesform': pricesform}, context)

def view_price(request, price_id):
    price = m.Prices.objects.get(pk=price_id)

    template = loader.get_template('prices/view_price.html')
    context = Context({
        'price' : price
    })
    return HttpResponse(template.render(context))

def view_price2(request, price_id):
    price = m.Prices.objects.get(pk=price_id)
    if 'search_cat' in request.session:                                                                                                                                                                          
       cat = request.session['search_cat']
    else:
       cat = 'vvv'
    if 'search_edLevel' in request.session:
       edLevel = request.session['search_edLevel']
    else:
       edLevel = 'vvv'
    if 'search_sector' in request.session:
       sector = request.session['search_sector']
    else:
       sector = 'ccc'
    if 'search_ingredient' in request.session:
       ingredient = request.session['search_ingredient']
    else:
       ingredient = 'ccc'

    template = loader.get_template('prices/view_price2.html')
    context = Context({
        'cat' : cat, 'edLevel':  edLevel, 'sector': sector,'ingredient' : ingredient, 'price' : price
    })
    return HttpResponse(template.render(context))

def edit_price(request, price_id):
    price = m.Prices.objects.get(pk=price_id)
    myUser = request.session['user']
    context = RequestContext(request)

    if request.method == 'POST':
        pricesform = PricesForm(request.POST,instance=price,user = myUser)
        if pricesform.is_valid():
            priceProvider = pricesform.save()
            priceProvider.save()
            return HttpResponseRedirect('/prices/my_price_list.html')
        else:
            print(pricesform.errors)
    else:
        pricesform = PricesForm(instance=price,user = myUser)

    return render(
            'prices/edit_price.html',
            {'pricesform': pricesform}, context)

def del_price(request, price_id):
    context = RequestContext(request)
    m.Prices.objects.get(pk=price_id).delete()
    return HttpResponseRedirect('/prices/my_price_list.html')

def clear_prices(request):
    context = RequestContext(request)
    m.Prices.objects.filter(priceProvider=request.session['user']).delete()
    return HttpResponseRedirect('/prices/my_price_list.html')

def price_list(request):
    if 'user' not in request.session:
       return render(request,'prices/message.html')
    else:
       allprices = m.Prices.objects.filter(priceProvider='CBCSE').order_by('ingredient') 

       template = loader.get_template('prices/price_list.html')
       context = Context({'allprices' : allprices})
       return HttpResponse(template.render(context))

def my_price_list(request):
    allprices2 = m.Prices.objects.filter(priceProvider=request.session['user']).order_by('ingredient')

    template = loader.get_template('prices/my_price_list.html')
    context = Context({'allprices2' : allprices2})
    return HttpResponse(template.render(context))

def export_full_table(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=expanded_cost_table.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Expanded Cost Information")

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    programId = request.session['program_id']
    if 'project_id' in request.session:
       projectId = request.session['project_id']                                                                                                                                                                
    else:
       projectId = 0

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    sett = m.Settings.objects.get(projectId = projectId)
    try:
       programdesc = m.ProgramDesc.objects.get(programId_id = programId)
       noofpart = programdesc.numberofparticipants
       try:
          part = m.ParticipantsPerYear.objects.filter(programdescId_id = programdesc.id)[:1].get()
          partExists = True
       except ObjectDoesNotExist:
          partExists = False
    except ObjectDoesNotExist:
       noofpart = 1
       partExists = False

    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2

    font_style3 = xlwt.XFStyle()
    font_style3.pattern = pattern

    font_style5 = xlwt.XFStyle()
    font_style5.font.bold = True
    font_style5.pattern = pattern

    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
    money_xf.pattern = pattern3
    money_xf_22 = xlwt.XFStyle()
    money_xf_22.num_format_str = '$#,##0.00'
    money_xf_22.pattern = pattern

    money_xf2 = xlwt.XFStyle()
    money_xf2.num_format_str = '$#,##0.00'
    money_xf3 = xlwt.XFStyle()
    money_xf3.num_format_str = '#,##0.00'
    money_xf2.pattern = pattern2
    money_xf3.pattern = pattern2

    money_xf4 = xlwt.XFStyle()
    money_xf4.num_format_str = '#,##0.00'
    money_xf4.pattern = pattern3

    money_p = xlwt.XFStyle()
    money_p.num_format_str = '0.0\\%'
    money_p.pattern = pattern3
    money_p_22 = xlwt.XFStyle()
    money_p_22.num_format_str = '0.0\\%'
    money_p_22.pattern = pattern

    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3

    ab = xlwt.Alignment()
    ab.vert = a.VERT_CENTER
    ab.horz = a.HORZ_CENTER
    font_cent = xlwt.XFStyle()
    font_cent.alignment = ab
    font_cent.pattern = pattern3
    font_cent_22 = xlwt.XFStyle()
    font_cent_22.alignment = ab
    font_cent_22.pattern = pattern

    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT
    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern
    money_str_22.alignment = aR

    ws.write(0, 0, "Project", font_style5)
    ws.write(0, 1, "", font_style5)
    ws.write(0, 2, project.projectname, font_style4)
    ws.write(0, 3, "", font_style4)
    ws.write(1, 0, "Type of Analysis", font_style3)
    ws.write(1, 1, "", font_style5)
    ws.write(1, 2, project.typeanalysis, font_style4)
    ws.write(1, 3, "", font_style4)
    ws.write(2, 0, "Type of Cost", font_style3)
    ws.write(2, 1, "", font_style5)
    ws.write(2, 2, project.typeofcost, font_style4)
    ws.write(2, 3, "", font_style4)
    ws.write(3, 0, "Geographical location in which you are expressing costs", font_style3)
    ws.write(3, 1, "", font_style5)
    ws.write(3, 2, sett.stateEstimates + ' ' + sett.areaEstimates, font_style4)
    ws.write(3, 3, "", font_style4)
    ws.write(4, 0, "Year in which you are expressing costs", font_style3)
    ws.write(4, 1, "", font_style5)
    ws.write(4, 2, str(sett.yearEstimates), font_style4)
    ws.write(4, 3, "", font_style4)
    ws.write(5, 0, "Discount Rate", font_style3)
    ws.write(5, 1, "", font_style5)
    ws.write(5, 2, str(sett.discountRateEstimates), font_style4)
    ws.write(5, 3, "", font_style4)
    ws.write(7, 0, "Name of the Program", font_style5)
    ws.write(7, 1, "", font_style5)
    ws.write(7, 2, program.progname, font_style4)
    ws.write(7, 3, "", font_style4)
    ws.write(8, 0, "Short Name", font_style3)
    ws.write(8, 1, "", font_style5)
    ws.write(8, 2, program.progshortname, font_style4)
    ws.write(8, 3, "", font_style4)
    ws.write(9, 0, "Number of unique participants over program period", font_style3)
    ws.write(9, 1, "", font_style5)
    ws.write(9, 2, str(noofpart), font_style4)
    ws.write(9, 3, "", font_style4)

    cursor = database.cursor ()
    cursor2 = database.cursor()

    # Select from sql query
    sql = """SELECT costPerIngredient,percentageCost,costPerParticipant,ingredient,category,price,unitMeasurePrice,newMeasure,yearQtyUsed,quantityUsed,lifetimeAsset, FORMAT(CONVERT(interestRate, DECIMAL(10,2)),2)  interestRate,variableFixed,convertedPrice,priceAdjAmortization, benefitRate,priceAdjBenefits,percentageofUsage,yearPrice,case indexCPI when 'No inflation index available' then indexCPI else FORMAT(CONVERT(indexCPI, DECIMAL(10,2)),2) end  indexCPI,case priceAdjInflation when 'No index' then priceAdjInflation else FORMAT(CONVERT(priceAdjInflation, DECIMAL(10,2)),2) end  priceAdjInflation, statePrice,areaPrice,case geoIndex when 'No geographical index available' then geoIndex else FORMAT(CONVERT(geoIndex, DECIMAL(10,2)),2) end geoIndex,case priceAdjGeographicalArea when 'No index' then priceAdjGeographicalArea  else FORMAT(CONVERT(priceAdjGeographicalArea, DECIMAL(10,2)),2) end priceAdjGeographicalArea,priceNetPresentValue,case adjpriceperingredient when 'No inflation index available' then adjpriceperingredient when 'No geographical index available' then adjpriceperingredient else FORMAT(CONVERT(adjpriceperingredient, DECIMAL(10,2)),2) end adjPricePerIngredient,edLevel,sector,urlPrice,sourcePriceData,sourceBenefitData,yearBenefit,notes FROM costtool_ingredients WHERE programId = %(programId)s ORDER BY yearQtyUsed, ingredient"""

    sql2 = """SELECT yearqtyused, sum(costperingredient) sumcost, sum(percentageCost) sumperc, noofparticipants, sum(costPerParticipant) sumpart FROM costtool_ingredients, costtool_participantsperyear WHERE programid = %(programId)s  AND yearqtyused = yearnumber AND programdescid_id = (SELECT id FROM costtool_programdesc WHERE programid_id = %(programId)s) group by yearqtyused"""

    ing = m.Ingredients.objects.filter(programId = programId)[:1].get()
    ws.write(12, 0, 'Total Cost of program', font_style5)
    ws.write(12, 1, '', money_xf2)
    ws.write(12, 2, ing.totalCost, money_xf)
    ws.write(12, 3, "", font_style4)
    ws.write(13, 0, 'Average Cost per participant over all years', font_style5)
    ws.write(13, 1, '', money_xf2)
    ws.write(13, 2, ing.averageCost, money_xf)
    ws.write(13, 3, "", font_style4)
    ws.write(14, 0, 'Average Cost per participant / average effectiveness', font_style5)
    ws.write(14, 1, '', money_xf2)
    ws.write(14, 2, ing.effRatio, money_xf)
    ws.write(14, 3, "", font_style4)

    ws.write(0, 5, 'Costs by type', font_style5)
    ws.write(0, 6, '', money_xf2)
    ws.write(0, 7, '$ amount', font_style5)
    ws.write(0, 8, '% of Total', font_style5)

    fixtot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(variableFixed = 'Fixed'):
       if i.costPerIngredient is not None:
          fixtot = fixtot + i.costPerIngredient
       else:
          fixtot = fixtot
    fixperc = (fixtot * 100) / ing.totalCost
    ws.write(1, 5, 'Fixed Costs', font_style3)
    ws.write(1, 6, '', money_xf2)
    ws.write(1, 7, fixtot, money_xf)
    ws.write(1, 8, fixperc, money_p)

    ltot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(variableFixed = 'Lumpy'):
       if i.costPerIngredient is not None:
          ltot = ltot + i.costPerIngredient
       else:
          ltot = ltot
    lperc = (ltot * 100) / ing.totalCost
    ws.write(2, 5, 'Lumpy Costs', font_style3)
    ws.write(2, 6, '', money_xf2)
    ws.write(2, 7, ltot, money_xf)
    ws.write(2, 8, lperc, money_p)

    vartot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(variableFixed = 'Variable'):
       if i.costPerIngredient is not None:
          vartot = vartot + i.costPerIngredient
       else:
          vartot = vartot
    varperc = (vartot * 100) / ing.totalCost
    ws.write(3, 5, 'Variable Costs', font_style3)
    ws.write(3, 6, '', money_xf2)
    ws.write(3, 7, vartot, money_xf)
    ws.write(3, 8, varperc, money_p)

    ws.write(5, 5, 'Costs by ingredient category', font_style5)
    ws.write(5, 6, '', money_xf2)
    ws.write(5, 7, '$ amount', font_style5)
    ws.write(5, 8, '% of Total', font_style5)

    pertot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(category = 'Personnel'):
       if i.costPerIngredient is not None:
          pertot = pertot + i.costPerIngredient
       else:
          pertot = pertot
    perperc = (pertot * 100) / ing.totalCost
    ws.write(6, 5, 'Personnel Costs', font_style3)
    ws.write(6, 6, '', money_xf2)
    ws.write(6, 7, pertot, money_xf)
    ws.write(6, 8, perperc, money_p)

    mattot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(category = 'Material/Equipment'):
       if i.costPerIngredient is not None:
          mattot = mattot + i.costPerIngredient
       else:
          mattot = mattot
    matperc = (mattot * 100) / ing.totalCost
    ws.write(7, 5, 'Material/Equipment Costs', font_style3)
    ws.write(7, 6, '', money_xf2)
    ws.write(7, 7, mattot, money_xf)
    ws.write(7, 8, matperc, money_p)

    factot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(category = 'Facilities'):
       if i.costPerIngredient is not None:
          factot = factot + i.costPerIngredient
       else:
          factot = factot
    facperc = (factot * 100) / ing.totalCost
    ws.write(8, 5, 'Facilities Costs', font_style3)
    ws.write(8, 6, '', money_xf2)
    ws.write(8, 7, factot, money_xf)
    ws.write(8, 8, facperc, money_p)

    inptot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(category = 'Other Inputs'):
       if i.costPerIngredient is not None:
          inptot = inptot + i.costPerIngredient
       else:
          inptot = inptot
    inpperc = (inptot * 100) / ing.totalCost
    ws.write(9, 5, 'Other Inputs Costs', font_style3)
    ws.write(9, 6, '', money_xf2)
    ws.write(9, 7, inptot, money_xf)
    ws.write(9, 8, inpperc, money_p)

    row_num = 17

    if partExists:
        columns = [
           (u"Costs by year", 8000),
           (u"Total Cost for the Year", 4000),
           (u"% of Total Costs", 5000),
           (u"Number of participants", 4000),
           (u"Average Cost per participant", 5000),
        ]

        for col_num in xrange(len(columns)):
           ws.write(row_num, col_num, columns[col_num][0], font_style)
           # set column width
           ws.col(col_num).width = columns[col_num][1]

        try:
        # Execute the SQL command
           cursor2.execute(sql2,{'programId' : programId})
           # Fetch all the rows in a list of lists.
           results = cursor2.fetchall()
           for row in results:
              row_num = row_num + 1
              yearQtyUsed = row[0]
              sumcost = row[1]
              sumperc = row[2]
              noofparticipants = row[3]
              sumpart = row[4]
              for col_num in xrange(len(row)):
                 if col_num == 0:
                    ws.write(row_num, col_num, row[col_num], font_style)
                 elif col_num == 2:
                    ws.write(row_num, col_num, row[col_num], money_p)
                 elif col_num == 3:
                    ws.write(row_num, col_num, row[col_num], money_str)
                 else:
                    ws.write(row_num, col_num, row[col_num], money_xf)
        except:
           print("Error: unable to fetch data")

        row_num = 23

    columns = [
        (u"Cost Per Ingredient", 5000),
        (u"% of Total Cost", 5500),
        (u"Cost Per Participant", 5000),
        (u"Ingredient Name", 8000),
        (u"Category", 5000),
        (u"Original Price", 5000),
        (u"Original Unit of Measure", 5000),
        (u"Converted Unit of Measure", 5000),
        (u"Year Quantity Used", 3000),
        (u"Quantity Used", 4000),
        (u"Lifetime", 4000),
        (u"Interest Rate", 4000),
        (u"Variable, fixed or lumpy", 5000),
        (u"Price After Conversion", 5000),
        (u"PriceAdjAmortization", 5000),
        (u"Benefit Rate", 5000),
        (u"PriceAdjBenefits", 5000),
        (u"Percentage of Usage", 5000),
        (u"Year Price", 5000),
        (u"IndexCPI of Year Price", 5000),
        (u"PriceAdjInflation", 5000),
        (u"State Price", 5000),
        (u"Area Price", 5000),
        (u"Geographical Index of State Price & Area Price", 5000),
        (u"PriceAdjGeographicalArea", 5000),
        (u"Price Net Present Value", 5000),
        (u"AdjPricePerIngredient", 5000),
        (u"Ed Level of Price", 5000),
        (u"Sector of Price", 5000),
        (u"URL of Price", 20000),
        (u"Source of Price", 5000),
        (u"Source of Benefit Rate", 5000),
        (u"Year Benefit", 5000),
        (u"Description", 30000)
    ]

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    try:
    # Execute the SQL command
       cursor.execute(sql,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          row_num += 1
          costPerIngredient = row[0]
          percentageCost = row[1]
          costPerParticipant = row[2]
          ingredient = row[3]
          category = row[4]
          price  = row[5]
          unitMeasurePrice  = row[6]
          newMeasure = row[7]
          yearQtyUsed = row[8]
          quantityUsed  = row[9]
          lifetimeAsset  = row[10]
          interestRate = row[11]
          variableFixed = row[12]
          convertedPrice = row[13]
          priceAdjAmortization = row[14]
          benefitRate = row[15]
          priceAdjBenefits = row[16]
          percentageofUsage = row[17]
          yearPrice = row[18]
          indexCPI = row[19]
          priceAdjInflation = row[20]
          statePrice = row[21]
          areaPrice = row[22]
          geoIndex = row[23]
          priceAdjGeographicalArea = row[24]
          priceNetPresentValue = row[25]
          adjPricePerIngredient =row[26]
          edLevel = row[27]
          sector = row[28]
          urlPrice = row[29]
          sourcePriceData = row[30]
          sourceBenefitData = row[31]
          yearBenefit = row[32]
          notes = row[33]
          for col_num in xrange(len(row)):
             if row[8] % 2 == 0:
                if col_num == 8 or col_num ==9 or col_num ==10:
                   ws.write(row_num, col_num, row[col_num], font_cent_22)
                elif col_num == 18 or col_num == 19 or col_num == 20 or col_num == 23 or col_num == 24 or col_num == 26:
                   ws.write(row_num, col_num, row[col_num], money_str_22)
                elif col_num == 1 or col_num == 11 or col_num ==15 or col_num == 17:
                   ws.write(row_num, col_num, row[col_num], money_p_22)
                else:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
             else:
                if col_num == 8 or col_num ==9 or col_num ==10:
                   ws.write(row_num, col_num, row[col_num], font_cent)
                elif col_num == 18 or col_num == 19 or col_num == 20 or col_num == 23 or col_num == 24 or col_num == 26:
                   ws.write(row_num, col_num, row[col_num], money_str)
                elif col_num == 1 or col_num == 11 or col_num ==15 or col_num == 17:
                   ws.write(row_num, col_num, row[col_num], money_p)
                else:
                   ws.write(row_num, col_num, row[col_num], money_xf)

    except:
       print("Error: unable to fetch data")

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_cost_table(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=cost_table.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Cost Information")
    
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    programId = request.session['program_id']
    if 'project_id' in request.session:
       projectId = request.session['project_id']                                                                                                                                                                
    else:
       projectId = 0

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    sett = m.Settings.objects.get(projectId = projectId)
    try:
       programdesc = m.ProgramDesc.objects.get(programId_id = programId)
       noofpart = programdesc.numberofparticipants
       try: 
          part = m.ParticipantsPerYear.objects.filter(programdescId_id = programdesc.id)[:1].get()
          partExists = True 
       except ObjectDoesNotExist:
          partExists = False
    except ObjectDoesNotExist:
       noofpart = 1 
       partExists = False
 
    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2

    font_style3 = xlwt.XFStyle()
    font_style3.pattern = pattern

    font_style5 = xlwt.XFStyle()
    font_style5.font.bold = True
    font_style5.pattern = pattern  
    
    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
    money_xf.pattern = pattern3
    money_xf_22 = xlwt.XFStyle()
    money_xf_22.num_format_str = '$#,##0.00'
    money_xf_22.pattern = pattern

    money_xf2 = xlwt.XFStyle()
    money_xf2.num_format_str = '$#,##0.00'
    money_xf3 = xlwt.XFStyle()
    money_xf3.num_format_str = '#,##0.00'
    money_xf2.pattern = pattern2
    money_xf3.pattern = pattern2

    money_xf4 = xlwt.XFStyle()
    money_xf4.num_format_str = '#,##0.00'
    money_xf4.pattern = pattern3

    money_p = xlwt.XFStyle()
    money_p.num_format_str = '0.0\\%'
    money_p.pattern = pattern3
    money_p_22 = xlwt.XFStyle()
    money_p_22.num_format_str = '0.0\\%'
    money_p_22.pattern = pattern

    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3

    ab = xlwt.Alignment()
    ab.vert = a.VERT_CENTER
    ab.horz = a.HORZ_CENTER
    font_cent = xlwt.XFStyle()
    font_cent.alignment = ab
    font_cent.pattern = pattern3
    font_cent_22 = xlwt.XFStyle()
    font_cent_22.alignment = ab
    font_cent_22.pattern = pattern

    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT
    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern
    money_str_22.alignment = aR

    ws.write(0, 0, "Project", font_style5)
    ws.write(0, 1, "", font_style5)
    ws.write(0, 2, project.projectname, font_style4)
    ws.write(0, 3, "", font_style4) 
    ws.write(1, 0, "Type of Analysis", font_style3)
    ws.write(1, 1, "", font_style5)
    ws.write(1, 2, project.typeanalysis, font_style4)
    ws.write(1, 3, "", font_style4) 
    ws.write(2, 0, "Type of Cost", font_style3)
    ws.write(2, 1, "", font_style5)
    ws.write(2, 2, project.typeofcost, font_style4)
    ws.write(2, 3, "", font_style4) 
    ws.write(3, 0, "Geographical location in which you are expressing costs", font_style3)
    ws.write(3, 1, "", font_style5)
    ws.write(3, 2, sett.stateEstimates + ' ' + sett.areaEstimates, font_style4)
    ws.write(3, 3, "", font_style4) 
    ws.write(4, 0, "Year in which you are expressing costs", font_style3)
    ws.write(4, 1, "", font_style5)
    ws.write(4, 2, str(sett.yearEstimates), font_style4)
    ws.write(4, 3, "", font_style4) 
    ws.write(5, 0, "Discount Rate", font_style3)
    ws.write(5, 1, "", font_style5)
    ws.write(5, 2, str(sett.discountRateEstimates), font_style4)
    ws.write(5, 3, "", font_style4) 
    ws.write(7, 0, "Name of the Program", font_style5)
    ws.write(7, 1, "", font_style5)
    ws.write(7, 2, program.progname, font_style4)
    ws.write(7, 3, "", font_style4) 
    ws.write(8, 0, "Short Name", font_style3)
    ws.write(8, 1, "", font_style5)
    ws.write(8, 2, program.progshortname, font_style4)
    ws.write(8, 3, "", font_style4) 
    ws.write(9, 0, "Number of unique participants over program period", font_style3)
    ws.write(9, 1, "", font_style5)
    ws.write(9, 2, str(noofpart), font_style4)
    ws.write(9, 3, "", font_style4)
 
    cursor = database.cursor ()
    cursor2 = database.cursor()

    # Create the INSERT INTO sql query
    sql = """SELECT ingredient, category, yearQtyUsed, quantityUsed, newMeasure, variableFixed, case adjpriceperingredient when 'No inflation index available' then adjpriceperingredient when 'No geographical index available' then adjpriceperingredient else FORMAT(CONVERT(adjpriceperingredient, DECIMAL(10,2)),2) end adjPricePerIngredient, costPerIngredient, percentageCost, costPerParticipant,notes,totalCost, averageCost, effRatio FROM costtool_ingredients WHERE programId = %(programId)s ORDER BY yearQtyUsed, ingredient"""

    sql2 = """SELECT yearqtyused, sum(costperingredient) sumcost, sum(percentageCost) sumperc, noofparticipants, sum(costPerParticipant) sumpart FROM costtool_ingredients, costtool_participantsperyear WHERE programid = %(programId)s  AND yearqtyused = yearnumber AND programdescid_id = (SELECT id FROM costtool_programdesc WHERE programid_id = %(programId)s) group by yearqtyused"""

    ing = m.Ingredients.objects.filter(programId = programId)[:1].get()
    ws.write(12, 0, 'Total Cost of program', font_style5)
    ws.write(12, 1, '', money_xf2)
    ws.write(12, 2, ing.totalCost, money_xf)
    ws.write(12, 3, "", font_style4) 
    ws.write(13, 0, 'Average Cost per participant over all years', font_style5)
    ws.write(13, 1, '', money_xf2)
    ws.write(13, 2, ing.averageCost, money_xf)
    ws.write(13, 3, "", font_style4) 
    ws.write(14, 0, 'Average Cost per participant / average effectiveness', font_style5)
    ws.write(14, 1, '', money_xf2) 
    ws.write(14, 2, ing.effRatio, money_xf)
    ws.write(14, 3, "", font_style4) 

    ws.write(0, 5, 'Costs by type', font_style5)
    ws.write(0, 6, '', money_xf2)
    ws.write(0, 7, '$ amount', font_style5)
    ws.write(0, 8, '% of Total', font_style5) 

    fixtot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(variableFixed = 'Fixed'):
       if i.costPerIngredient is not None:
          fixtot = fixtot + i.costPerIngredient
       else:
          fixtot = fixtot
    fixperc = (fixtot * 100) / ing.totalCost
    ws.write(1, 5, 'Fixed Costs', font_style3)
    ws.write(1, 6, '', money_xf2)
    ws.write(1, 7, fixtot, money_xf)
    ws.write(1, 8, fixperc, money_p) 

    ltot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(variableFixed = 'Lumpy'):
       if i.costPerIngredient is not None:
          ltot = ltot + i.costPerIngredient
       else:
          ltot = ltot
    lperc = (ltot * 100) / ing.totalCost
    ws.write(2, 5, 'Lumpy Costs', font_style3)
    ws.write(2, 6, '', money_xf2)
    ws.write(2, 7, ltot, money_xf)
    ws.write(2, 8, lperc, money_p)

    vartot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(variableFixed = 'Variable'):
       if i.costPerIngredient is not None:
          vartot = vartot + i.costPerIngredient
       else:
          vartot = vartot
    varperc = (vartot * 100) / ing.totalCost
    ws.write(3, 5, 'Variable Costs', font_style3)
    ws.write(3, 6, '', money_xf2)
    ws.write(3, 7, vartot, money_xf)
    ws.write(3, 8, varperc, money_p)

    ws.write(5, 5, 'Costs by ingredient category', font_style5)
    ws.write(5, 6, '', money_xf2)
    ws.write(5, 7, '$ amount', font_style5)
    ws.write(5, 8, '% of Total', font_style5)

    pertot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(category = 'Personnel'):
       if i.costPerIngredient is not None:
          pertot = pertot + i.costPerIngredient
       else:
          pertot = pertot
    perperc = (pertot * 100) / ing.totalCost
    ws.write(6, 5, 'Personnel Costs', font_style3)
    ws.write(6, 6, '', money_xf2)
    ws.write(6, 7, pertot, money_xf)
    ws.write(6, 8, perperc, money_p)

    mattot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(category = 'Material/Equipment'):
       if i.costPerIngredient is not None:
          mattot = mattot + i.costPerIngredient
       else:
          mattot = mattot
    matperc = (mattot * 100) / ing.totalCost
    ws.write(7, 5, 'Material/Equipment Costs', font_style3)
    ws.write(7, 6, '', money_xf2)
    ws.write(7, 7, mattot, money_xf)
    ws.write(7, 8, matperc, money_p)

    factot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(category = 'Facilities'):
       if i.costPerIngredient is not None:
          factot = factot + i.costPerIngredient
       else:
          factot = factot
    facperc = (factot * 100) / ing.totalCost
    ws.write(8, 5, 'Facilities Costs', font_style3)
    ws.write(8, 6, '', money_xf2)
    ws.write(8, 7, factot, money_xf)
    ws.write(8, 8, facperc, money_p)

    inptot = 0
    for i in m.Ingredients.objects.filter(programId = programId).filter(category = 'Other Inputs'):
       if i.costPerIngredient is not None:
          inptot = inptot + i.costPerIngredient
       else:
          inptot = inptot
    inpperc = (inptot * 100) / ing.totalCost
    ws.write(9, 5, 'Other Inputs Costs', font_style3)
    ws.write(9, 6, '', money_xf2)
    ws.write(9, 7, inptot, money_xf)
    ws.write(9, 8, inpperc, money_p)

    row_num = 17

    if partExists:    
        columns = [
           (u"Costs by year", 8000),
           (u"Total Cost for the Year", 4000),
           (u"% of Total Costs", 5000),
           (u"Number of participants", 4000),
           (u"Average Cost per participant", 5000),
        ]

        for col_num in xrange(len(columns)):
           ws.write(row_num, col_num, columns[col_num][0], font_style)
           # set column width
           ws.col(col_num).width = columns[col_num][1]

        try:
        # Execute the SQL command
           cursor2.execute(sql2,{'programId' : programId})
           # Fetch all the rows in a list of lists.
           results = cursor2.fetchall()
           for row in results:
              row_num = row_num + 1
              yearQtyUsed = row[0] 
              sumcost = row[1]
              sumperc = row[2]
              noofparticipants = row[3] 
              sumpart = row[4]
              for col_num in xrange(len(row)):
                 if col_num == 0:
                    ws.write(row_num, col_num, row[col_num], font_style)
                 elif col_num == 2:
                    ws.write(row_num, col_num, row[col_num], money_p)
                 elif col_num == 3:
                    ws.write(row_num, col_num, row[col_num], money_str)
                 else:
                    ws.write(row_num, col_num, row[col_num], money_xf)
        except:
           print("Error: unable to fetch data")
 
        row_num = 23
 
    columns = [
        (u"Ingredient", 8000),
        (u"Category of ingredient", 5000),
        (u"Year in which quantity is used", 4000),
        (u"Quantity of Ingredient", 4000),
        (u"Unit of measure", 5000),
        (u"Variable, fixed or lumpy", 5000),
        (u"Adj. price of Ingredient", 6000),
        (u"Cost", 5000),
        (u"% of Total Cost", 5000),
        (u"Cost per participant", 5000),
        (u"Description", 30000)
    ]

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    try:
    # Execute the SQL command
       cursor.execute(sql,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          row_num = row_num + 1
          ingredient = row[0]
          category = row[1]
          yearQtyUsed = row[2]  
          quantityUsed  = row[3] 
          unitMeasurePrice  = row[4] 
          variableFixed = row[5] 
          adjPricePerIngredient =row[6] 
          costPerIngredient = row[7] 
          percentageCost = row[8] 
          costPerParticipant = row[9]
          notes = row[10]
          maxnum = row_num
          for col_num in xrange(len(row)):
             if row[2] % 2 == 0:
                if col_num == 2 or col_num == 3:
                   ws.write(row_num, col_num, row[col_num], font_cent_22)
                elif col_num == 6:
                   ws.write(row_num, col_num, row[col_num], money_str_22)
                elif col_num == 8:
                   ws.write(row_num, col_num, row[col_num], money_p_22)
                elif col_num == 0 or col_num == 1  or col_num == 4 or col_num == 5  or col_num == 7 or col_num ==9 or col_num ==10:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
             else:
                if col_num == 2 or col_num == 3:
                   ws.write(row_num, col_num, row[col_num], font_cent)
                elif col_num == 6:
                   ws.write(row_num, col_num, row[col_num], money_str)
                elif col_num == 8:
                   ws.write(row_num, col_num, row[col_num], money_p)
                elif col_num == 0 or col_num == 1  or col_num == 4 or col_num == 5  or col_num == 7 or col_num ==9 or col_num ==10:
                   ws.write(row_num, col_num, row[col_num], money_xf)
 
    except:
       print("Error: unable to fetch data")
    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_dist(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=distribution_of_costs.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Distribution of Costs")
  
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    if 'project_id' in request.session:
       projectId = request.session['project_id']
    else:
       projectId = 0
    if 'program_id' in request.session:
       programId = request.session['program_id']
    else:
       programId = 0   

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    sett = m.Settings.objects.get(projectId = projectId)
    try:
       programdesc = m.ProgramDesc.objects.get(programId_id = programId)
       noofpart = programdesc.numberofparticipants
       try:
          part = m.ParticipantsPerYear.objects.filter(programdescId_id = programdesc.id)[:1].get()
          partExists = True
       except ObjectDoesNotExist:
          partExists = False
    except ObjectDoesNotExist:
       noofpart = 1
       partExists = False

    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2

    font_style3 = xlwt.XFStyle()
    font_style3.pattern = pattern

    font_style5 = xlwt.XFStyle()
    font_style5.font.bold = True
    font_style5.pattern = pattern
    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT

    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
    money_xf.pattern = pattern3
    money_xf_22 = xlwt.XFStyle()
    money_xf_22.num_format_str = '$#,##0.00'
    money_xf_22.pattern = pattern

    money_xf2 = xlwt.XFStyle()
    money_xf2.num_format_str = '$#,##0.00'
    money_xf3 = xlwt.XFStyle()
    money_xf3.num_format_str = '#,##0.00'
    money_xf2.pattern = pattern2
    money_xf3.pattern = pattern2

    money_xf4 = xlwt.XFStyle()
    money_xf4.num_format_str = '#,##0.00'
    money_xf4.pattern = pattern3

    money_p = xlwt.XFStyle()
    money_p.num_format_str = '0.0\\%'
    money_p.pattern = pattern3
    money_p_22 = xlwt.XFStyle()
    money_p_22.num_format_str = '0.0\\%'
    money_p_22.pattern = pattern

    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3

    ab = xlwt.Alignment()
    ab.vert = a.VERT_CENTER
    ab.horz = a.HORZ_CENTER
    font_cent = xlwt.XFStyle()
    font_cent.alignment = ab
    font_cent.pattern = pattern3
    font_cent_22 = xlwt.XFStyle()
    font_cent_22.alignment = ab
    font_cent_22.pattern = pattern

    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern

    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3

    ab = xlwt.Alignment()
    ab.vert = a.VERT_CENTER
    ab.horz = a.HORZ_CENTER
    font_cent = xlwt.XFStyle()
    font_cent.alignment = ab
    font_cent.pattern = pattern3
    font_cent_22 = xlwt.XFStyle()
    font_cent_22.alignment = ab
    font_cent_22.pattern = pattern

    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT
    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern
    money_str_22.alignment = aR

    money_xfR = xlwt.XFStyle()
    money_xf_22R = xlwt.XFStyle()
    money_xfR.num_format_str = '$#,##0.00'
    money_xfR.pattern = pattern3
    money_xf_22R.num_format_str = '$#,##0.00'
    money_xf_22R.pattern = pattern
    money_xf_22R.alignment = aR
    money_xfR.alignment = aR
    
    ws.write(0, 0, "Project", font_style5)
    ws.write(0, 1, "", font_style5)
    ws.write(0, 2, project.projectname, font_style4)
    ws.write(0, 3, "", font_style4)
    ws.write(1, 0, "Type of Analysis", font_style3)
    ws.write(1, 1, "", font_style5)
    ws.write(1, 2, project.typeanalysis, font_style4)
    ws.write(1, 3, "", font_style4)
    ws.write(2, 0, "Type of Cost", font_style3)
    ws.write(2, 1, "", font_style5)
    ws.write(2, 2, project.typeofcost, font_style4)
    ws.write(2, 3, "", font_style4)
    ws.write(3, 0, "Geographical location in which you are expressing costs", font_style3)
    ws.write(3, 1, "", font_style5)
    ws.write(3, 2, sett.stateEstimates + ' ' + sett.areaEstimates, font_style4)
    ws.write(3, 3, "", font_style4)
    ws.write(4, 0, "Year in which you are expressing costs", font_style3)
    ws.write(4, 1, "", font_style5)
    ws.write(4, 2, str(sett.yearEstimates), font_style4)
    ws.write(4, 3, "", font_style4)
    ws.write(5, 0, "Discount Rate", font_style3)
    ws.write(5, 1, "", font_style5)
    ws.write(5, 2, str(sett.discountRateEstimates), font_style4)
    ws.write(5, 3, "", font_style4)
    ws.write(7, 0, "Name of the Program", font_style5)
    ws.write(7, 1, "", font_style5)
    ws.write(7, 2, program.progname, font_style4)
    ws.write(7, 3, "", font_style4)
    ws.write(8, 0, "Short Name", font_style3)
    ws.write(8, 1, "", font_style5)
    ws.write(8, 2, program.progshortname, font_style4)
    ws.write(8, 3, "", font_style4)
    ws.write(9, 0, "Number of unique participants over program period", font_style3)
    ws.write(9, 1, "", font_style5)
    ws.write(9, 2, str(noofpart), font_style4)
    ws.write(9, 3, "", font_style4)

    ing = m.Ingredients.objects.filter(programId = programId)[:1].get()
    ws.write(11, 0, 'Total Cost of program', font_style5)
    ws.write(11, 1, '', money_xf2)
    ws.write(11, 2, ing.totalCost, money_xf)
    ws.write(11, 3, "", font_style4)
    ws.write(12, 0, 'Average Cost per participant over all years', font_style5)
    ws.write(12, 1, '', money_xf2)
    ws.write(12, 2, ing.averageCost, money_xf)
    ws.write(12, 3, "", font_style4)
    ws.write(13, 0, 'Average Cost per participant / average effectiveness', font_style5)
    ws.write(13, 1, '', money_xf2)
    ws.write(13, 2, ing.effRatio, money_xf)
    ws.write(13, 3, "", font_style4)

    cursor = database.cursor ()

    # Create the INSERT INTO sql query
    sql = """SELECT d.ingredient, category, d.yearQtyUsed, cost, cost_agency1_percent, cost_agency1, cost_agency2_percent, cost_agency2, cost_agency3_percent, cost_agency3, cost_agency4_percent, cost_agency4, cost_other_percent, cost_other, total_cost, total_agency1, total_agency2, total_agency3, total_agency4, total_other FROM costtool_distribution d, costtool_agencies a,costtool_ingredients i  WHERE d.programId = a.programId AND d.programId = %(programId)s AND d.ingredientId = i.id ORDER BY yearQtyUsed, ingredient"""

    cursor2 = database.cursor ()

    # Create the INSERT INTO sql query
    sql2 = """SELECT grantName, grantYear, cost_agency1, cost_agency2, cost_agency3, cost_agency4, cost_other, total_cost, total_agency1, total_agency2, total_agency3, total_agency4, total_other, net_agency1, net_agency2, net_agency3, net_agency4, net_other FROM costtool_transfers d, costtool_agencies a  WHERE d.programId = a.programId AND d.programId = %(programId)s ORDER BY grantYear"""

    cursord = database.cursor ()
    cursorg = database.cursor ()
    cursor3 = database.cursor ()

    if partExists:
       sqld = """SELECT 'Gross Costs' cname, yearQtyUsed, noofparticipants, SUM(IFNULL (d.cost, 0.0)) cost, SUM(IFNULL (d.cost, 0.0)) / noofparticipants Costperparticipant, SUM(IFNULL (d.cost_agency1, 0.0)) gc1, SUM(IFNULL (d.cost_agency2,0.0)) gc2, SUM(IFNULL (d.cost_agency3,0.0)) gc3, SUM(IFNULL (d.cost_agency4,0.0)) gc4, SUM(IFNULL(d.cost_other,0.0)) goth FROM costtool_distribution d, costtool_participantsperyear p WHERE d.programid = %(programId)s and programdescid_id in (select id from costtool_programdesc where programid_id = %(programId)s) and yearQtyUsed = yearnumber group by yearQtyUsed UNION SELECT 'Transfers' cname, grantYear, noofparticipants,  SUM(IFNULL (total_amount,0.0)) cost, SUM(IFNULL (total_amount,0.0)) / noofparticipants Costperparticipant, SUM(IFNULL (t.cost_agency1,0.0)) t1, SUM(IFNULL (t.cost_agency2,0.0)) t2, SUM(IFNULL (t.cost_agency3 , 0.0)) t3, SUM(IFNULL (t.cost_agency4,0.0)) t4, SUM(IFNULL(t.cost_other, 0.0)) toth FROM costtool_transfers t, costtool_participantsperyear p WHERE t.programid = %(programId)s and programdescid_id in (select id from costtool_programdesc where programid_id = %(programId)s) and grantYear = yearnumber group by grantYear ORDER BY yearQtyUsed, cname"""

       sqlg = """SELECT 'Gross Costs' cname, yearQtyUsed, noofparticipants, SUM(IFNULL (d.cost, 0.0)) cost, SUM(IFNULL (d.cost, 0.0)) / noofparticipants Costperparticipant, SUM(IFNULL (d.cost_agency1, 0.0)) gc1, SUM(IFNULL (d.cost_agency2,0.0)) gc2, SUM(IFNULL (d.cost_agency3,0.0)) gc3, SUM(IFNULL (d.cost_agency4,0.0)) gc4, SUM(IFNULL(d.cost_other,0.0)) goth FROM costtool_distribution d, costtool_participantsperyear WHERE d.programid = %(programId)s and programdescid_id in (select id from costtool_programdesc where programid_id = %(programId)s) and yearQtyUsed = yearnumber group by yearQtyUsed"""

       sql3 = """SELECT 'Transfers' cname, grantYear,  noofparticipants, SUM(IFNULL (total_amount,0.0)) cost, SUM(IFNULL (total_amount,0.0)) / noofparticipants Costperparticipant, SUM(IFNULL (t.cost_agency1,0.0)) t1, SUM(IFNULL (t.cost_agency2,0.0)) t2, SUM(IFNULL (t.cost_agency3 , 0.0)) t3, SUM(IFNULL (t.cost_agency4,0.0)) t4, SUM(IFNULL(t.cost_other, 0.0)) toth FROM costtool_transfers t, costtool_participantsperyear WHERE t.programid = %(programId)s and programdescid_id in (select id from costtool_programdesc where programid_id = %(programId)s) and grantYear = yearnumber group by grantYear"""

    else:
       sqld = """SELECT 'Gross Costs' cname, yearQtyUsed, numberofparticipants, SUM(IFNULL (d.cost, 0.0)) cost, SUM(IFNULL (d.cost, 0.0)) / numberofparticipants Costperparticipant, SUM(IFNULL (d.cost_agency1, 0.0)) gc1, SUM(IFNULL (d.cost_agency2,0.0)) gc2, SUM(IFNULL (d.cost_agency3,0.0)) gc3, SUM(IFNULL (d.cost_agency4,0.0)) gc4, SUM(IFNULL(d.cost_other,0.0)) goth FROM costtool_distribution d, costtool_programdesc WHERE d.programid = %(programId)s and d.programid = programid_id  group by yearQtyUsed UNION SELECT 'Transfers' cname, grantYear, numberofparticipants,  SUM(IFNULL (total_amount,0.0)) cost, SUM(IFNULL (total_amount,0.0)) / numberofparticipants Costperparticipant, SUM(IFNULL (t.cost_agency1,0.0)) t1, SUM(IFNULL (t.cost_agency2,0.0)) t2, SUM(IFNULL (t.cost_agency3 , 0.0)) t3, SUM(IFNULL (t.cost_agency4,0.0)) t4, SUM(IFNULL(t.cost_other, 0.0)) toth FROM costtool_transfers t, costtool_programdesc  WHERE t.programid = %(programId)s and t.programid = programId_id group by grantYear ORDER BY yearQtyUsed, cname"""

       sqlg = """SELECT 'Gross Costs' cname, yearQtyUsed, numberofparticipants, SUM(IFNULL (d.cost, 0.0)) cost,SUM(IFNULL (d.cost, 0.0))/ numberofparticipants Costperparticipant, SUM(IFNULL (d.cost_agency1, 0.0)) gc1, SUM(IFNULL (d.cost_agency2,0.0)) gc2, SUM(IFNULL (d.cost_agency3,0.0)) gc3, SUM(IFNULL (d.cost_agency4,0.0)) gc4, SUM(IFNULL(d.cost_other,0.0)) goth FROM costtool_distribution d, costtool_programdesc WHERE d.programid = %(programId)s and d.programid = programid_id  group by yearQtyUsed"""

       sql3 = """SELECT 'Transfers' cname, grantYear, numberofparticipants, SUM(IFNULL (total_amount,0.0)) cost, SUM(IFNULL (total_amount,0.0))/numberofparticipants Costperparticipant, SUM(IFNULL (t.cost_agency1,0.0)) t1, SUM(IFNULL (t.cost_agency2,0.0)) t2, SUM(IFNULL (t.cost_agency3 , 0.0)) t3, SUM(IFNULL (t.cost_agency4,0.0)) t4, SUM(IFNULL(t.cost_other, 0.0)) toth FROM costtool_transfers t, costtool_programdesc  WHERE t.programid = %(programId)s and t.programid = programId_id  group by grantYear"""

    cursortot = database.cursor ()

    sqltot = """SELECT 'TOTAL GROSS COSTS ALL YEARS' cname, 'ALL' yearQtyUsed, numberofparticipants, SUM(IFNULL (d.cost, 0.0)) cost, FORMAT(CONVERT(SUM(IFNULL (d.cost, 0.0))/ numberofparticipants, DECIMAL(10,2)),2) costperparticipant,  SUM(IFNULL (d.cost_agency1, 0.0)) gc1, SUM(IFNULL (d.cost_agency2,0.0)) gc2, SUM(IFNULL (d.cost_agency3,0.0)) gc3, SUM(IFNULL (d.cost_agency4,0.0)) gc4, SUM(IFNULL(d.cost_other,0.0)) goth FROM costtool_distribution d, costtool_programdesc WHERE d.programid = %(programId)s AND d.programid = programId_id UNION SELECT 'NET COSTS AFTER TRANSFERS' cname, 'ALL' yearQtyUsed, numberofparticipants, total_cost, FORMAT(CONVERT(total_cost/numberofparticipants, DECIMAL(10,2)),2) costperparticipant, net_agency1, net_agency2, net_agency3, net_agency4, net_other FROM costtool_agencies a, costtool_programdesc  WHERE a.programid =  %(programId)s AND a.programid = programId_id UNION SELECT 'Percentage of net costs borne by agency' cname, 'ALL' yearQtyUsed, numberofparticipants, 100, 'N/A' costperparticipant,(net_agency1 * 100) / total_cost, (net_agency2 * 100) / total_cost, (net_agency3 * 100) / total_cost, (net_agency4 * 100) / total_cost, (net_other * 100) / total_cost FROM costtool_agencies a, costtool_programdesc  WHERE a.programId = %(programId)s AND a.programId = programId_id"""

    ag = m.Agencies.objects.get(programId = programId)

    columnd = [
        (u"Summary Table of Gross and Net Costs", 5000),
        (u"Year", 5000),
        (u"Number of participants", 5000),
        (u"Total Cost", 6000),
        (u"Cost per participant", 6000),
        (u"Cost to "+ag.agency1, 5000),
        (u"Cost to "+ag.agency2, 5000),
        (u"Cost to "+ag.agency3, 5000),
        (u"Cost to "+ag.agency4, 5000),
        (u"Cost to Other", 5000)
    ]
    
    columns2 = [
        (u"Table of transfers", 8000),
        (u"Year", 5000),
        (u"Cost to "+ag.agency1, 5000),
        (u"Cost to "+ag.agency2, 5000),
        (u"Cost to "+ag.agency3, 5000),
        (u"Cost to "+ag.agency4, 5000),
        (u"Cost to Other", 5000)
    ]

    columns = [
        (u"Ingredient", 15000),
        (u"Category of ingredient", 10000),
        (u"Year", 5000),
        (u"Cost", 6000),
        (u"Cost to "+ag.agency1+" (%)", 5000),
        (u"Cost to "+ag.agency1+" ($)", 5000),
        (u"Cost to "+ag.agency2+" (%)", 5000),
        (u"Cost to "+ag.agency2+" ($)", 5000),
        (u"Cost to "+ag.agency3+" (%)", 5000),
        (u"Cost to "+ag.agency3+" ($)", 5000),
        (u"Cost to "+ag.agency4+" (%)", 5000),
        (u"Cost to "+ag.agency4+" ($)", 5000),
        (u"Cost to Other (%)", 5000),
        (u"Cost to Other ($)", 5000)
    ]

    row_num = 16
    maxnum = row_num 
    mnum = row_num
    for col_num in xrange(len(columnd)):
        ws.write(row_num, col_num, columnd[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columnd[col_num][1]
   
    cursor1 = database.cursor ()
    sqlcount = """SELECT COUNT(*) FROM costtool_distribution WHERE programid = %(programId)s group by yearQtyUsed"""
    try:
       cursor1.execute(sqlcount,{'programId' : programId})
       res = cursor1.fetchone()
    except:
       print("Error: unable to fetch data cursor1")

    #row_num = mnum + int(''.join(map(str,res))) + 1
    try:
    # Execute the SQL command
       cursorg.execute(sqlg,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursorg.fetchall()
       for row in results:
          row_num += 1
          cname = row[0]
          yearQtyUsed = row[1]
          noofparticipants  = row[2]
          cost = row[3]
          costperparticipant = row[4]
          gc1  = row[5]
          gc2  = row[6]
          gc3 = row[7]
          gc4 = row[8]
          goth = row[9]
          mnum = row_num
          for col_num in xrange(len(row)):
             if col_num == 1 or col_num == 2:
                ws.write(row_num, col_num, row[col_num], font_cent)
             elif col_num == 0  or col_num == 3 or  col_num == 4 or col_num == 5 or  col_num == 6 or col_num == 7 or  col_num == 8 or col_num == 9:
                ws.write(row_num, col_num, row[col_num], money_xf)

    except:
       print("Error: unable to fetch data cursorg")
       mnum = row_num

    try:
    # Execute the SQL command
       cursor3.execute(sql3,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursor3.fetchall()
       for row in results:
          row_num += 1
          cname = row[0]
          grantYear = row[1]
          noofparticipants  = row[2]
          cost = row[3]
          costperparticipant = row[4]
          t1  = row[5]
          t2  = row[6]
          t3 = row[7]
          t4 = row[8]
          toth = row[9]
          mnum = row_num
          for col_num in xrange(len(row)):
             if col_num == 1 or col_num == 2:
                ws.write(row_num, col_num, row[col_num], font_cent_22)
             elif col_num == 0  or col_num == 3 or  col_num == 4 or col_num == 5 or  col_num == 6 or col_num == 7 or  col_num == 8 or col_num == 9:
                ws.write(row_num, col_num, row[col_num], money_xf_22)

    except:
       print("Error: unable to fetch data cursor3")
       mnum = row_num

    try:
    # Execute the SQL command
       cursord.execute(sqld,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursord.fetchall()
       initialyear = 1
       n1 = 0
       n2 = 0
       n3 = 0
       n4 = 0
       noth = 0
       ncost = 0
       noofparticipants = 0
       costperparticipant = 0
       mnum += 1
       for row in results:
          if initialyear != row[1]:
             ws.write(mnum, 0, 'Net Costs', money_xf)
             ws.write(mnum, 1, initialyear, font_cent)
             ws.write(mnum, 2, noofparticipants, font_cent)
             ws.write(mnum, 3, ncost, money_xf)
             ws.write(mnum, 4, costperparticipant, money_xf)
             ws.write(mnum, 5, n1, money_xf)
             ws.write(mnum, 6, n2, money_xf)
             ws.write(mnum, 7, n3, money_xf)
             ws.write(mnum, 8, n4, money_xf)
             ws.write(mnum, 9, noth, money_xf)
             n1 = 0
             n2 = 0
             n3 = 0
             n4 = 0
             noth = 0
             ncost = 0
             noofparticipants = row[2]
             costperparticipant = 0
             mnum += 1
             initialyear = row[1]

          ncost = ncost + row[3]
          noofparticipants = row[2]
          costperparticipant = costperparticipant + row[4]
          n1 = n1 + row[5]
          n2 = n2 + row[6]
          n3 = n3 + row[7]
          n4 = n4 + row[8]
          noth = noth + row[9]

    except:
       print("Error: unable to fetch data cursord")

    ws.write(mnum, 0, 'Net Costs', money_xf)
    ws.write(mnum, 1, initialyear, font_cent)
    ws.write(mnum, 2, noofparticipants, font_cent)
    ws.write(mnum, 3, ncost, money_xf)
    ws.write(mnum, 4, costperparticipant, money_xf)
    ws.write(mnum, 5, n1, money_xf)
    ws.write(mnum, 6, n2, money_xf)
    ws.write(mnum, 7, n3, money_xf)
    ws.write(mnum, 8, n4, money_xf)
    ws.write(mnum, 9, noth, money_xf)

    row_num = mnum

    try:
    # Execute the SQL command
       cursortot.execute(sqltot,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursortot.fetchall()
       for row in results:
          row_num += 1
          cname = row[0]
          yearQtyUsed = row[1]
          noofparticipants  = row[2]
          cost = row[3]
          costperparticipant = row[4]
          gc1  = row[5]
          gc2  = row[6]
          gc3 = row[7]
          gc4 = row[8]
          goth = row[9]
          maxnum = row_num
          for col_num in xrange(len(row)):
             if cname == 'NET COSTS AFTER TRANSFERS':
                if col_num == 1 or col_num == 2:
                   ws.write(row_num, col_num, row[col_num], font_cent)
                elif col_num == 0  or col_num == 3  or  col_num == 5 or  col_num == 6 or col_num == 7 or  col_num == 8 or col_num == 9:
                   ws.write(row_num, col_num, row[col_num], money_xf)
                elif col_num == 4:
                   ws.write(row_num, col_num, row[col_num], money_xfR)
             else:
                if cname == 'Percentage of net costs borne by agency':
                   if col_num == 1 or col_num == 2:
                      ws.write(row_num, col_num, row[col_num], font_cent_22)
                   elif col_num == 4:
                      ws.write(row_num, col_num, row[col_num], money_xf_22)
                   else:
                      ws.write(row_num, col_num, row[col_num], money_p_22)
                elif col_num == 1 or col_num == 2:
                   ws.write(row_num, col_num, row[col_num], font_cent_22)
                elif col_num == 0  or col_num == 3 or col_num == 5 or  col_num == 6 or col_num == 7 or  col_num == 8 or col_num == 9:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
                elif col_num == 4:
                   ws.write(row_num, col_num, row[col_num], money_xf_22R)

    except:
       print("Error: unable to fetch data cursortot")
 
    if maxnum > row_num:
       row_num = maxnum + 3
    else:
       row_num = row_num + 3

    for col_num in xrange(len(columns2)):
        ws.write(row_num, col_num, columns2[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns2[col_num][1]

    try:
    # Execute the SQL command
       cursor2.execute(sql2,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursor2.fetchall()

       for row in results:
          row_num += 1
          grantName = row[0]
          grantYear = row[1]
          cost_agency1  = row[2]
          cost_agency2 =row[3]
          cost_agency3 = row[4]
          cost_agency4 = row[5]
          cost_other = row[6]
          total_cost = row[7]
          total_agency1 = row[8]
          total_agency2 = row[9]
          total_agency3 = row[10]
          total_agency4 = row[11]
          total_other = row[12]
          net_agency1 = row[13]
          net_agency2 = row[14]
          net_agency3 = row[15]
          net_agency4 = row[16]
          net_other = row[17]
          maxnum = row_num 
          for col_num in xrange(len(row)):
             if row[1] % 2 == 0:
                if col_num == 1:
                   ws.write(row_num, col_num, row[col_num], font_cent_22)
                elif col_num == 0  or col_num == 2 or col_num == 3 or  col_num == 4 or col_num == 5 or  col_num == 6:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
             else:
                if col_num == 1:
                   ws.write(row_num, col_num, row[col_num], font_cent)
                elif col_num == 0 or col_num == 2 or col_num == 3 or  col_num == 4 or col_num == 5 or  col_num == 6:
                   ws.write(row_num, col_num, row[col_num], money_xf)

    except:
       maxnum = row_num 
       print("Error: unable to fetch data cursor2")

    if maxnum > row_num:
       row_num = maxnum + 3
    else:
       row_num = row_num + 3

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    try:
    # Execute the SQL command
       cursor.execute(sql,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          row_num += 1
          ingredient = row[0]
          category = row[1]
          yearQtyUsed = row[2]
          cost = row[3]
          cost_agency1_percent  = row[4]
          cost_agency1  = row[5]
          cost_agency2_percent = row[6]
          cost_agency2 =row[7]
          cost_agency3_percent = row[8]
          cost_agency3 = row[9]
          cost_agency4_percent = row[10]
          cost_agency4 = row[11]
          cost_other_percent = row[12]
          cost_other = row[13]
          total_cost = row[14]
          total_agency1 = row[15]
          total_agency2 = row[16]
          total_agency3 = row[17]
          total_agency4 = row[18]
          total_other = row[19]
          for col_num in xrange(len(row)):
             if row[2] % 2 == 0:
                if col_num == 2:
                   ws.write(row_num, col_num, row[col_num], font_cent_22)
                elif col_num == 4 or col_num == 6  or col_num == 8 or col_num == 10 or col_num == 12:
                   ws.write(row_num, col_num, row[col_num], money_p_22)
                elif col_num == 0 or col_num == 1 or col_num == 3  or col_num == 5 or col_num == 7  or col_num == 9 or col_num ==11 or col_num == 13:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
             else:
                if col_num == 2:
                   ws.write(row_num, col_num, row[col_num], font_cent)
                elif col_num == 4 or col_num == 6  or col_num == 8 or col_num == 10 or col_num == 12:
                   ws.write(row_num, col_num, row[col_num], money_p)
                elif col_num == 0 or col_num == 1 or col_num == 3  or col_num == 5 or col_num == 7  or col_num == 9 or col_num ==11 or col_num == 13:
                   ws.write(row_num, col_num, row[col_num], money_xf)
    except:
       print("Error: unable to fetch data cursor")

    # disconnect from server
    database.close()
    wb.save(response)
    return response


def export_to_inf(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=inflation_indices.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Inflation Indices")
   
    row_num = 0
   
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    if 'project_id' in request.session:
       projectId = request.session['project_id']                                                                                                                                                                
    else:
       projectId = 0
    cursor = database.cursor ()

    # Create the INSERT INTO sql query
    sql = """SELECT yearCPI, indexCPI FROM costtool_inflationindices WHERE projectId = %(projectId)s"""

    columns = [
        (u"Year", 3000),
        (u"CPI", 3000)
    ]

    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    try:
    # Execute the SQL command
       cursor.execute(sql,{'projectId' : projectId})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          row_num += 1
          yearCPI = row[0]
          indexCPI = row[1]
          for col_num in xrange(len(row)):
             ws.write(row_num, col_num, row[col_num], money_xf)

    except:
       print("Error: unable to fetch data")

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_to_geo(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=geographical_indices.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Geographical Indices")

    row_num = 0

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    if 'project_id' in request.session:
       projectId = request.session['project_id']                                                                                                                                                                
    else:
       projectId = 0
    cursor = database.cursor ()

    # Create the INSERT INTO sql query
    sql = """SELECT stateIndex, areaIndex, geoIndex FROM costtool_geographicalindices WHERE projectId = %(projectId)s"""

    columns = [
        (u"State", 4000),
        (u"Area", 6000),
        (u"Index", 3000)
    ]

    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    try:
    # Execute the SQL command
       cursor.execute(sql,{'projectId' : projectId})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          row_num += 1
          stateIndex = row[0]
          areaIndex = row[1]
          geoIndex = row[2]
          for col_num in xrange(len(row)):
             ws.write(row_num, col_num, row[col_num], money_xf)

    except:
       print("Error: unable to fetch data")

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_cbcse_prices(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=costout_prices.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("CostOut Prices")

    row_num = 0

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    cursor = database.cursor ()

    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2

    ab = xlwt.Alignment()
    ab.wrap = True
    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
    money_xf.pattern = pattern3
    money_xf_22 = xlwt.XFStyle()
    money_xf_22.num_format_str = '$#,##0.00'
    money_xf_22.pattern = pattern
    money_xf.alignment = ab
    money_xf_22.alignment = ab

    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT
    aR.wrap = True
    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern
    money_str_22.alignment = aR

    # Create the INSERT INTO sql query
    sql = """SELECT category, ingredient, edLevel, sector, descriptionPrice, unitMeasurePrice, CONVERT(price, DECIMAL(15,2))  price, yearPrice, statePrice, areaPrice, sourcePriceData, urlPrice, lastChecked, nextCheckDate FROM costtool_prices WHERE priceProvider = 'CBCSE'"""

    columns = [
        (u"Category", 5000),
        (u"Ingredient", 10000),
        (u"Education Level", 4000),
        (u"Sector", 3000),
        (u"Description of Price", 15000),
        (u"Unit of Measure", 4000),
        (u"Price", 4000),
        (u"Year", 3000),
        (u"State", 3000),
        (u"Area", 3000),
        (u"Source Price Data", 4000),
        (u"URL Price", 10000),
        (u"Last Checked", 5000),
        (u"Next Check Date", 5000)
    ]

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    try:
    # Execute the SQL command
       cursor.execute(sql)
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          row_num += 1
          category = row[0]
          ingredient = row[1]
          edLevel = row[2]
          sector = row[3]
          descriptionPrice = row[4]
          unitMeasurePrice = row[5]
          price = row[6]
          yearPrice = row[7]
          statePrice = row[8]
          areaPrice = row[9]
          sourcePriceData = row[10]
          urlPrice = row[11]
          lastChecked = row[12]
          nextCheckDate = row[13]
          for col_num in xrange(len(row)):
             if row_num  % 2 == 0:
                if col_num == 7:
                   ws.write(row_num, col_num, row[col_num], money_str_22)
                else:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
             else:
                if col_num == 7:
                   ws.write(row_num, col_num, row[col_num], money_str)
                else:
                   ws.write(row_num, col_num, row[col_num], money_xf)

    #changed
    #except (MySQLdb.Error, MySQLdb.Warning), e:
    except:
       print("Error reading data from MySQL table")

    # disconnect from server
    database.close()
    wb.save(response)
    return response

'''def export_cbcse_prices(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cbcse_prices.csv"'

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    cursor = database.cursor ()

    # Create the INSERT INTO sql query
    sql = """SELECT category, ingredient, edLevel, sector, descriptionPrice, unitMeasurePrice, CONVERT(price, DECIMAL(10,2))  price, yearPrice, statePrice, areaPrice, sourcePriceData, urlPrice, lastChecked,  nextCheckDate FROM costtool_prices WHERE priceProvider = 'CBCSE' limit 100"""

    # field names 
    columns = ['Category','Ingredient','Education Level','Sector','Description of Price','Unit of Measure','Price','Year', 'State','Area', 'Source Price Data','URL Price','Last Checked','Next Check Date' ]
    writer = csv.writer(response)
      
    # writing the fields 
    writer.writerow(columns) 
      
    try:
    # Execute the SQL command
       cursor.execute(sql)
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
           print(row[0]
           #print(row[1]
           #writer.writerow([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]])
    except:
       print("Error: unable to fetch data"
    # disconnect from server
    database.close()

    return response'''


def export_prices(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=my_prices.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("My Prices")

    row_num = 0

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    priceProvider = request.session['user']
    cursor = database.cursor ()

    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2

    ab = xlwt.Alignment()
    ab.wrap = True
    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
    money_xf.pattern = pattern3
    money_xf_22 = xlwt.XFStyle()
    money_xf_22.num_format_str = '$#,##0.00'
    money_xf_22.pattern = pattern
    money_xf.alignment = ab
    money_xf_22.alignment = ab

    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT
    aR.wrap = True
    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern
    money_str_22.alignment = aR

    # Create the INSERT INTO sql query
    sql = """SELECT category, ingredient, edLevel, sector, descriptionPrice, unitMeasurePrice, CONVERT(price, DECIMAL(15,2))  price, yearPrice, statePrice, areaPrice, sourcePriceData, urlPrice, lastChecked, nextCheckDate FROM costtool_prices WHERE priceProvider = %(priceProvider)s"""

    columns = [
        (u"Category", 5000),
        (u"Ingredient", 10000),
        (u"Education Level", 4000),
        (u"Sector", 3000),
        (u"Description of Price", 15000),
        (u"Unit of Measure", 4000),
        (u"Price", 4000),
        (u"Year", 3000),
        (u"State", 3000),
        (u"Area", 3000),
        (u"Source Price Data", 4000),
        (u"URL Price", 10000),
        (u"Last Checked", 5000),
        (u"Next Check Date", 5000)
    ]

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    try:
    # Execute the SQL command
       cursor.execute(sql,{'priceProvider' : priceProvider})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          row_num += 1
          category = row[0]
          ingredient = row[1]
          edLevel = row[2]
          sector = row[3]
          descriptionPrice = row[4]
          unitMeasurePrice = row[5]
          price = row[6]
          yearPrice = row[7]
          statePrice = row[8]
          areaPrice = row[9]
          sourcePriceData = row[10]
          urlPrice = row[11] 
          lastChecked = row[12]
          nextCheckDate = row[13]
          for col_num in xrange(len(row)):
             if row_num  % 2 == 0:
                if col_num == 7:
                   ws.write(row_num, col_num, row[col_num], money_str_22)
                else:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
             else:
                if col_num == 7:
                   ws.write(row_num, col_num, row[col_num], money_str)
                else:
                   ws.write(row_num, col_num, row[col_num], money_xf)

    except:
       print("Error: unable to fetch data")

    # disconnect from server
    database.close()
    wb.save(response)
    return response
   
def export_progdesc(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=program_desc.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Program Description")

    row_num = 0

    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    programId = request.session['program_id']
    if 'project_id' in request.session:
       projectId = request.session['project_id']                                                                                                                                                                
    else:
       projectId = 0

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    sett = m.Settings.objects.get(projectId = projectId)
    try:
       programdesc = m.ProgramDesc.objects.get(programId_id = programId)
       noofpart = programdesc.numberofparticipants
    except ObjectDoesNotExist:
       print('does not exist')
       noofpart = ''

    cursor = database.cursor ()
    cursor2 = database.cursor ()

    # Create the INSERT INTO sql query
    sql = """SELECT progobjective, progsubjects, progdescription, numberofparticipants, lengthofprogram, numberofyears FROM costtool_programdesc WHERE programId_id = %(programId)s""" 

    try:
       eff = m.Effectiveness.objects.get(programId_id = programId)
       effExists = True
    except ObjectDoesNotExist:
       effExists = False

    #Heading of tables
    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = xlwt.Style.colour_map['silver_ega']
    font_style.pattern = pattern2

    at = xlwt.Alignment()
    at.vert = at.VERT_CENTER
    font_style3 = xlwt.XFStyle()
    font_style3.pattern = pattern
    font_style3.alignment = at

    font_style5 = xlwt.XFStyle()
    font_style5.font.bold = True
    font_style5.pattern = pattern

    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']  
    money_xf.pattern = pattern3
    money_xf_22 = xlwt.XFStyle()
    money_xf_22.num_format_str = '$#,##0.00'
    money_xf_22.pattern = pattern

    money_xf2 = xlwt.XFStyle()
    money_xf2.num_format_str = '$#,##0.00'
    money_xf3 = xlwt.XFStyle()
    money_xf3.num_format_str = '#,##0.00'
    money_xf2.pattern = pattern2
    money_xf3.pattern = pattern2

    money_xf4 = xlwt.XFStyle()
    money_xf4.num_format_str = '#,##0.00'
    money_xf4.pattern = pattern3

    money_p = xlwt.XFStyle()
    money_p.num_format_str = '0.0\\%'
    money_p.pattern = pattern3
    money_p_22 = xlwt.XFStyle()
    money_p_22.num_format_str = '0.0\\%'
    money_p_22.pattern = pattern

    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    aL.wrap = True
    font_style4 = xlwt.XFStyle()
    font_style4.pattern = pattern3
    font_style4.alignment = aL

    ab = xlwt.Alignment()
    ab.vert = a.VERT_CENTER
    ab.horz = a.HORZ_CENTER
    font_cent = xlwt.XFStyle()
    font_cent.alignment = ab
    font_cent.pattern = pattern3
    font_cent_22 = xlwt.XFStyle()
    font_cent_22.alignment = ab
    font_cent_22.pattern = pattern

    aR = xlwt.Alignment()
    aR.horz = a.HORZ_RIGHT
    money_str = xlwt.XFStyle()
    money_str.pattern = pattern3
    money_str.alignment = aR
    money_str_22 = xlwt.XFStyle()
    money_str_22.pattern = pattern
    money_str_22.alignment = aR
    ws.col(2).width = 8000
    ws.col(3).width = 50000

    ws.write(0, 0, "Project", font_style5)
    ws.write(0, 1, "", font_style5)
    ws.write(0, 2, "", font_style5)
    ws.write(0, 3, project.projectname, font_style4)

    ws.write(1, 0, "Type of Analysis", font_style3)
    ws.write(1, 1, "", font_style5)
    ws.write(1, 2, "", font_style5)
    ws.write(1, 3, project.typeanalysis, font_style4)
    
    ws.write(2, 0, "Type of Cost", font_style3)
    ws.write(2, 1, "", font_style5)
    ws.write(2, 2, "", font_style5)
    ws.write(2, 3, project.typeofcost, font_style4)
    
    ws.write(3, 0, "Geographical location in which you are expressing costs", font_style3)
    ws.write(3, 1, "", font_style5)
    ws.write(3, 2, "", font_style5)
    ws.write(3, 3, sett.stateEstimates + ' ' + sett.areaEstimates, font_style4)
    
    ws.write(4, 0, "Year in which you are expressing costs", font_style3)
    ws.write(4, 1, "", font_style5)
    ws.write(4, 2, "", font_style5)
    ws.write(4, 3, str(sett.yearEstimates), font_style4)
    
    ws.write(5, 0, "Discount Rate", font_style3)
    ws.write(5, 1, "", font_style5)
    ws.write(5, 2, "", font_style5)
    ws.write(5, 3, str(sett.discountRateEstimates), font_style4)
    
    ws.write(7, 0, "Name of the Program", font_style5)
    ws.write(7, 1, "", font_style5)
    ws.write(7, 2, "", font_style5)
    ws.write(7, 3, program.progname, font_style4)
    
    ws.write(8, 0, "Short Name", font_style3)
    ws.write(8, 1, "", font_style5)
    ws.write(8, 2, "", font_style5)
    ws.write(8, 3, program.progshortname, font_style4)
    
    ws.write(9, 0, "Number of unique participants over program period", font_style3)
    ws.write(9, 1, "", font_style5)
    ws.write(9, 2, "", font_style5)
    ws.write(9, 3, str(noofpart), font_style4)

    try:
    # Execute the SQL command
       cursor.execute(sql,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          ws.write(12, 0, 'Objective of the program', font_style3)
          ws.write(12, 1, "", font_style5)
          ws.write(12, 2, "", font_style5)
          ws.write(12, 3, row[0], font_style4)
    
          ws.write(13, 0, 'Subjects / Participants', font_style3)
          ws.write(13, 1, "", font_style5)
          ws.write(13, 2, "", font_style5)
          ws.write(13, 3, row[1], font_style4)
    
          ws.write(14, 0, 'Brief description', font_style3)
          ws.write(14, 1, "", font_style5)
          ws.write(14, 2, "", font_style5)
          ws.write(14, 3, row[2], font_style4)
          
          ws.write(15, 0, 'Length of the program', font_style3)
          ws.write(15, 1, "", font_style5)
          ws.write(15, 2, "", font_style5)
          ws.write(15, 3, row[4], font_style4)
          
          ws.write(16, 0, 'Number of years', font_style3)
          ws.write(16, 1, "", font_style5)
          ws.write(16, 2, "", font_style5)
          ws.write(16, 3, str(row[5]), font_style4)

    except:
       print("Error: unable to fetch data")

   
    row_num = 19

    if effExists:
       ws.write(19, 0, "Source of effectiveness data", font_style3)
       ws.write(19, 1, "", font_style5)
       ws.write(19, 2, "", font_style5)
       ws.write(19, 3, eff.sourceeffectdata, font_style4)

       ws.write(20, 0, "URL", font_style3)
       ws.write(20, 1, "", font_style5)
       ws.write(20, 2, "", font_style5)
       ws.write(20, 3, eff.url, font_style4)

       ws.write(21, 0, "Description of effectiveness data", font_style3)
       ws.write(21, 1, "", font_style5)
       ws.write(21, 2, "", font_style5)
       ws.write(21, 3, eff.effectdescription, font_style4)
 
       ws.write(22, 0, "Average effectiveness per participant", font_style3)
       ws.write(22, 1, "", font_style5)
       ws.write(22, 2, "", font_style5)
       ws.write(22, 3, eff.avgeffectperparticipant, font_style4)
 
       ws.write(23, 0, "Unit of measure of effectiveness", font_style3)
       ws.write(23, 1, "", font_style5)
       ws.write(23, 2, "", font_style5)
       ws.write(23, 3, eff.unitmeasureeffect, font_style4)
       
       ws.write(24, 0, "Is the estimator effect of the treatment statistically significant?", font_style3)
       ws.write(24, 1, "", font_style5)
       ws.write(24, 2, "", font_style5)
       ws.write(24, 3, eff.sigeffect, font_style4)

       row_num = 27

    sql2 = """SELECT yearnumber, noofparticipants FROM costtool_participantsperyear WHERE programdescId_id = (SELECT id FROM costtool_programdesc WHERE programId_id = %(programId)s)"""

    columns = [
        (u"Year", 3000),
        (u"Number of participants per year", 7000)
    ]

    try:
       cursor2.execute(sql2,{'programId' : programId})
       results2 = cursor2.fetchall()
       if results2 != ():
          for col_num in xrange(len(columns)):
             ws.write(row_num, col_num, columns[col_num][0], font_style)
             # set column width
             ws.col(col_num).width = columns[col_num][1]

       for row in results2:
          row_num += 1
          yearnumber = row[0]
          noofparticipants = row[1]
          for col_num in xrange(len(row)):
             if row[0] % 2 == 0:
                if col_num == 0:
                   ws.write(row_num, col_num, row[col_num], font_cent_22)
                else:
                   ws.write(row_num, col_num, row[col_num], money_str_22)
             else:
                if col_num == 0:
                   ws.write(row_num, col_num, row[col_num], font_cent)
                else:
                   ws.write(row_num, col_num, row[col_num], money_str)
             #ws.write(row_num, col_num, row[col_num], font_style3)
    except:
       print("Error: unable to fetch data")


    # disconnect from server
    database.close()
    wb.save(response)
    return response
 
def import_excel(request):
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/home/amritha/costtool/documents/DBofPrices.xlsx")
    sheet = book.sheet_by_name("Ingredients")
    m.Prices.objects.filter(priceProvider='CBCSE').delete()

    # Establish a MySQL connection
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")
    #database = MySQLdb.connect (host="localhost", user = "root", passwd = "", db = "costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()
    
    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_prices (priceProvider,category,ingredient,edLevel,sector,descriptionPrice,unitMeasurePrice,price,yearPrice,statePrice,areaPrice,sourcePriceData,urlPrice,lastChecked,nextCheckDate, permissionDetails) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        priceProvider      = sheet.cell(r,0).value
        category  = sheet.cell(r,1).value
        ingredient          = sheet.cell(r,2).value
        edLevel     = sheet.cell(r,3).value
        sector       = sheet.cell(r,4).value
        descriptionPrice = sheet.cell(r,5).value
        unitMeasurePrice        = sheet.cell(r,6).value
        price       = sheet.cell(r,7).value
        yearPrice     = sheet.cell(r,8).value
        statePrice        = sheet.cell(r,9).value
        areaPrice         = sheet.cell(r,10).value
        sourcePriceData          = sheet.cell(r,11).value
        urlPrice   = sheet.cell(r,12).value
        lastChecked   = sheet.cell(r,13).value
        nextCheckDate   = sheet.cell(r,14).value
        permissionDetails = sheet.cell(r,15).value
        # Assign values from each row
        values = (priceProvider,category,ingredient,edLevel,sector,descriptionPrice,unitMeasurePrice,price,yearPrice,statePrice,areaPrice,sourcePriceData,urlPrice,lastChecked,nextCheckDate, permissionDetails)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/prices/imports.html')

def import_geo(request):
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/home/amritha/costtool/documents/GeographicalIndex.xlsx")
    sheet = book.sheet_by_name("Sheet1")
    m.GeographicalIndices_orig.objects.all().delete()

    # Establish a MySQL connection
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_geographicalindices_orig (stateIndex, areaIndex, geoIndex) VALUES (%s, %s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        stateIndex      = sheet.cell(r,0).value
        areaIndex  = sheet.cell(r,1).value
        geoIndex          = sheet.cell(r,2).value
        
        # Assign values from each row
        values = (stateIndex, areaIndex, geoIndex)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/prices/imports.html')

def import_inf(request):
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/home/amritha/costtool/documents/InflationIndex.xlsx")
    sheet = book.sheet_by_name("Sheet1")
    m.InflationIndices_orig.objects.all().delete()

    # Establish a MySQL connection
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_inflationindices_orig (yearCPI, indexCPI) VALUES (%s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        yearCPI      = sheet.cell(r,0).value
        indexCPI  = sheet.cell(r,1).value

        # Assign values from each row
        values = (yearCPI, indexCPI)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/prices/imports.html')

def import_benefits(request):
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/home/amritha/costtool/documents/Database of Benefits Rates.xls")
    sheet = book.sheet_by_name("Benefits")
    m.Benefits.objects.all().delete()

    # Establish a MySQL connection
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_benefits (SectorBenefit, PersonnelBenefit, TypeRateBenefit,	YearBenefit, BenefitRate, SourceBenefitData, URLBenefitData, LastChecked, NextCheckDate, permissionDetails) VALUES (%s, %s,%s, %s,%s, %s,%s, %s, %s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        SectorBenefit      = sheet.cell(r,0).value
        PersonnelBenefit = sheet.cell(r,1).value
        TypeRateBenefit      = sheet.cell(r,2).value
        YearBenefit = sheet.cell(r,3).value
        BenefitRate  = sheet.cell(r,4).value
        SourceBenefitData      = sheet.cell(r,5).value
        URLBenefitData  = sheet.cell(r,6).value
        LastChecked = sheet.cell(r,7).value 
        NextCheckDate = sheet.cell(r,8).value
        permissionDetails = sheet.cell(r,9).value

        # Assign values from each row
        values = (SectorBenefit, PersonnelBenefit, TypeRateBenefit, YearBenefit, BenefitRate, SourceBenefitData, URLBenefitData, LastChecked, NextCheckDate, permissionDetails)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/prices/imports.html')

def add_settings(request,project_id):
    request.session['project_id'] = project_id
    proj = m.Projects.objects.get(pk = project_id)
    context = RequestContext(request)
    result = 0
    try:
       setrec = m.Settings.objects.get(projectId=project_id)
       objectexists = True
       before_year = setrec.yearEstimates
       before_disc = setrec.discountRateEstimates
       before_state = setrec.stateEstimates
       before_area = setrec.areaEstimates
    except ObjectDoesNotExist:
       objectexists = False
    
    if request.method == 'POST':
        if objectexists:
           setform = SettingsForm(request.POST, instance=setrec)
        else:
           setform = SettingsForm(request.POST)
        
        if setform.is_valid():
            discountRateEstimates = setform.save(commit=False)
            discountRateEstimates.projectId = project_id
            discountRateEstimates.save()
            upd = updateDate(project_id, None)
            if objectexists:
               if (before_year != discountRateEstimates.yearEstimates) or (before_disc != discountRateEstimates.discountRateEstimates) or (before_state != discountRateEstimates.stateEstimates) or (before_area != discountRateEstimates.areaEstimates): 
                  result = calculations(project_id)
            #return HttpResponseRedirect('/project/project_list.html')
        else:
            print(setform.errors)

    else:
        if objectexists:
           setform = SettingsForm(instance=setrec)
        else:
           setform = SettingsForm()

    return render(
            'project/add_settings.html',
            {'frm1': setform, 'projname':proj.projectname}, context)

def addedit_inf(request):
    InfFormSet = modelformset_factory(m.InflationIndices,form=InflationForm,extra=20)
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    proj = m.Projects.objects.get(pk = project_id)
    setrec = m.Settings.objects.get(projectId=project_id)
    qset = m.InflationIndices.objects.filter(projectId=project_id)
    oldRecId = 0
    oldYear = 0
    result = 0
    for q in qset:
       if int(q.yearCPI) == setrec.yearEstimates: 
          oldRecId = q.id
          oldYear = q.yearCPI

    if request.method == 'POST':
       infform = InfFormSet(request.POST,request.FILES,prefix="infform")
       count = 0 
       if infform.is_valid():
          frm = infform.save(commit=False)
          for i in frm:
             if i.id == oldRecId:
                if i.yearCPI != oldYear:
                   count = 1
          for i in frm:
             if count != 1: 
                i.projectId = project_id
                if (i.indexCPI is None or i.indexCPI == '') and (i.yearCPI is not None and i.yearCPI != ''):
                   return render('project/inflation.html',{'infform':infform,'projname':proj.projectname, 'errtext': 'Please enter the CPI for the year you entered.'}, context)
                elif i.yearCPI == '' and i.indexCPI == '':
                   m.InflationIndices.objects.filter(id=i.id).delete()
                   return HttpResponseRedirect('/project/indices.html')
                elif (i.yearCPI == '' or int(i.yearCPI) > 9999 or int(i.yearCPI) < 1000) and (i.indexCPI is not None and i.indexCPI != ''):
                   return render('project/inflation.html',{'infform':infform,'projname':proj.projectname, 'errtext': 'Years must be entered as four-digit positive numbers.'}, context)
                try:
                   float(i.indexCPI)
                   i.save()
                   upd = updateDate(project_id, None)
                except IntegrityError as e:
                   return render('project/inflation.html',{'infform':infform,'projname':proj.projectname, 'errtext': 'Year must be an unique number.'}, context)
                except ValueError:
                   return render('project/inflation.html',{'infform':infform,'projname':proj.projectname, 'errtext': 'CPI must be a number.'}, context)
                if i.id == oldRecId: 
                   print(i.id)
                   result = calculations(project_id)
             else:
                return render ('project/inflation.html',{'infform':infform,'projname':proj.projectname, 'errtext': 'You cannot delete the inflation index for the year you selected in Project Settings.'},context) 
          if 'priceExists' in request.session:
             if request.session['priceExists'] == False:
                return HttpResponseRedirect('/project/programs/costs/'+request.session['price_id']+'/decideCat.html')
          #else:
             #return HttpResponseRedirect('/project/indices.html')
       else:
          form_errors = infform.errors
          return render ('project/inflation.html',{'infform':infform,'form.errors': form_errors,'projname':proj.projectname},context)
    else:
        qset = m.InflationIndices.objects.filter(projectId=project_id)
        infform = InfFormSet(queryset=qset,prefix="infform")
    return render ('project/inflation.html',{'infform':infform,'projname':proj.projectname},context)

def restore_inf(request):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    result = 0
    setrec = m.Settings.objects.get(projectId=project_id)
    latest = m.InflationIndices_orig.objects.all().latest('yearCPI')
    m.InflationIndices.objects.filter(projectId=project_id).delete()
    for e in m.InflationIndices_orig.objects.all():
        m.InflationIndices.objects.create(yearCPI = e.yearCPI,indexCPI = e.indexCPI, projectId=project_id)
    setrec.yearEstimates=latest.yearCPI
    setrec.save(update_fields=['yearEstimates'])
    result = calculations(project_id)
    upd = updateDate(project_id, None)
    return HttpResponseRedirect('/project/indices.html')

def addedit_geo(request):
    GeoFormSet = modelformset_factory(m.GeographicalIndices,form=GeographicalForm,extra=20)
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    proj = m.Projects.objects.get(pk = project_id)
    setrec = m.Settings.objects.get(projectId=project_id)
    qset = m.GeographicalIndices.objects.filter(projectId=project_id)
    oldRecId = 0
    oldState = ''
    oldArea = ''
    result = 0

    for q in qset:
       if q.stateIndex == setrec.stateEstimates and q.areaIndex == setrec.areaEstimates: 
          oldRecId = q.id
          oldState = q.stateIndex
          oldArea = q.areaIndex

    if request.method == 'POST':
       geoform = GeoFormSet(request.POST,request.FILES,prefix="geoform")
       count = 0

       if geoform.is_valid():
          frm = geoform.save(commit=False)
          for i in frm:
             if i.id == oldRecId:
                if i.stateIndex != oldState or i.areaIndex != oldArea:
                   count = 1
          for i in frm:
             if count != 1: 
                i.projectId = project_id  
                if (i.stateIndex is None or i.stateIndex == '' or i.areaIndex is None or i.areaIndex == '') and (i.geoIndex is not None and i.geoIndex != ''):
                   return render('project/geo.html',{'geoform':geoform,'projname':proj.projectname, 'errtext': 'Please enter the State and Area for the Index you entered.'}, context)
                elif ((i.stateIndex is not None and i.stateIndex != '') or (i.areaIndex is not None and i.areaIndex != '')) and (i.geoIndex is None or i.geoIndex == ''):
                   return render('project/geo.html',{'geoform':geoform,'projname':proj.projectname, 'errtext': 'Please enter the Index for the State and Area you entered.'}, context)
                elif i.stateIndex == '' and i.areaIndex == '' and i.geoIndex == '':
                   m.GeographicalIndices.objects.filter(id=i.id).delete()
                   return HttpResponseRedirect('/project/indices.html')

                try:
                   float(i.geoIndex)
                   i.save()
                   upd = updateDate(project_id, None)
                except IntegrityError as e:
                   return render('project/geo.html',{'geoform':geoform,'projname':proj.projectname,'errtext': 'The state / area combination must be unique in Geographical Indices.'})
                except ValueError:
                   return render('project/geo.html',{'geoform':geoform,'projname':proj.projectname, 'errtext': 'Index must be a number.'}, context)

                if i.id == oldRecId: 
                   result = calculations(project_id)
             else:
                return render ('project/geo.html',{'geoform':geoform,'projname':proj.projectname,'errtext': 'You cannot delete the geographical index for the state and area  you selected in Project Settings.'},context)    
          #return HttpResponseRedirect('/project/indices.html')
       else:
          form_errors = geoform.errors
          return render ('project/geo.html',{'geoform':geoform,'form.errors': form_errors,'projname':proj.projectname},context)
    else:
       qset = m.GeographicalIndices.objects.filter(projectId=project_id)                                                               
       geoform = GeoFormSet(queryset=qset,prefix="geoform")

    return render ('project/geo.html',{'geoform':geoform,'projname':proj.projectname},context) 

def restore_geo(request):
    context = RequestContext(request)
    if 'project_id' in request.session:
       project_id = request.session['project_id']                                                                                                                                                                
    else:
       project_id = 0
    result = 0
    setrec = m.Settings.objects.get(projectId=project_id)
    m.GeographicalIndices.objects.filter(projectId=project_id).delete()
    for e in m.GeographicalIndices_orig.objects.all():
        m.GeographicalIndices.objects.create(stateIndex = e.stateIndex,areaIndex = e.areaIndex, geoIndex = e.geoIndex, projectId=project_id)
    setrec.stateEstimates='All states' 
    setrec.areaEstimates='All areas'
    setrec.save(update_fields=['stateEstimates','areaEstimates'])
    result = calculations(project_id)
    upd = updateDate(project_id, None)
    return HttpResponseRedirect('/project/indices.html')
