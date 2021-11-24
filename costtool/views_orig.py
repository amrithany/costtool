from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect,render, render_to_response
from django.db import IntegrityError
from django.template import Context, loader, RequestContext
from django.contrib.auth import authenticate, login as auth_login
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Min
from costtool import models as m
from costtool.forms import TransfersForm, AgenciesForm,RegisterForm,License, LoginForm, PricesForm, PricesSearchForm, PriceIndicesForm, NonPerIndicesForm, WageDefaults, WageConverter,UMConverter, PriceBenefits, PriceSummary,MultipleSummary, UserForm, UserProfileForm, ProjectsForm, ProgramsForm, ProgramDescForm, ParticipantsForm, EffectForm,SettingsForm, GeographicalForm, GeographicalForm_orig, InflationForm, InflationForm_orig, IngredientsForm,IngredientsFullForm
from costtool.functions import calculations
from dateutil.relativedelta import relativedelta
from datetime import *

import datetime
import xlrd
import xlwt
import MySQLdb
import math
import random

def add_program(request):
    project_id = request.session['project_id']
    context = RequestContext(request)

    if request.method == 'POST':
        programform = ProgramsForm(request.POST)

        if programform.is_valid():
            progname = programform.save(commit=False)
            progname.projectId = project_id
            progname.save()
            return HttpResponseRedirect('/project/programs/'+project_id+'/program_list.html')
        else:
            print programform.errors

    else:
        programform = ProgramsForm()

    return render(request,
            'project/programs/add_program.html',
            {'programform': programform,'project_id':project_id})


def indices(request):
    project_id = request.session['project_id']
    return render(request,'project/indices.html',{'project_id':project_id})

def about(request):
    if 'user' in request.session:
        del request.session['user']
    if 'password' in request.session:   
       del request.session['password']
    template = loader.get_template('/about.html')
    return HttpResponse(template.render(context))

def logout(request):
    if 'user' in request.session:
        del request.session['user']
    if 'password' in request.session:
       del request.session['password']
    return render(request,'about.html')

def settings(request):
    project_id = request.session['project_id']
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
    request.session['project_id'] = project_id
    return render(request,'reports/reports.html', {'project_id':project_id})

def costeff(request):
    project_id = request.session['project_id']
    project = m.Projects.objects.get(pk=project_id)
    ProgList = []
    try:
       program = m.Programs.objects.filter(projectId=project_id)
       for p in program:
          ret = {}
          programdesc = m.ProgramDesc.objects.get(programId_id=p.id)
          ingredients = m.Ingredients.objects.filter(programId = p.id)
          eff = m.Effectiveness.objects.get(programId_id = p.id)
          try:
             ret['average_cost'] = ingredients[0].averageCost
             ret['total_cost'] = ingredients[0].totalCost
             if eff.avgeffectperparticipant is not None  and ingredients[0].averageCost is not None and ingredients[0].averageCost != 0:
                ret['effRatio'] = float(ingredients[0].averageCost) / float(eff.avgeffectperparticipant)
          except:
             ret['average_cost'] = 'n/a'
             ret['total_cost'] = 'n/a'
             ret['effRatio'] = 'n/a'
          ret['short_name'] = p.progshortname
          ret['lengthofprogram'] = programdesc.lengthofprogram
          ret['num_participants'] = programdesc.numberofparticipants
          ret['average_effect'] = eff.avgeffectperparticipant
          ret['unitmeasureeffect'] = eff.unitmeasureeffect
          ret['sigeffect'] = eff.sigeffect
          
          ProgList.append(ret)
    except ObjectDoesNotExist:
       return HttpResponse('A Project and/or Program does not exist! Cannot proceed further.')
    return render(request,'reports/costeff.html', {'ProjectName': project.projectname,'ProgList':ProgList})

def costanal(request):                                                                                                                
   return render(request,'reports/costanal.html')

def costanalbyyear(request):                                                                                                               
   return render(request,'reports/costanalbyyear.html')   

def compcostanal(request):
   project_id = request.session['project_id']
   project = m.Projects.objects.get(pk=project_id)
   ProgList = []
   MaxTotal = []
   try:
      program = m.Programs.objects.filter(projectId=project_id)
      for p in program:
         ret = {}
         ingredients = m.Ingredients.objects.filter(programId = p.id)
         #MaxTotal = m.Ingredients.objects.filter(programId = p.id).aggregate(Max('totalCost'))
         #MinTotal = m.Ingredients.objects.filter(programId = p.id).aggregate(Max('totalCost'))
         #MaxTotal = m.Ingredients.objects.filter(programId = p.id).order_by('totalCost')[0]
         #MinTotal = m.Ingredients.objects.filter(programId = p.id).order_by('-totalCost')[0] 
         try:
            ret['total_cost'] = ingredients[0].totalCost 
            ret['avg_cost'] = ingredients[0].averageCost
            MaxTotal.append(ingredients[0].totalCost)
            MinTotal = m.Ingredients.objects.filter(programId = p.id).aggregate(Max('totalCost'))
         except:
            ret['total_cost'] = 'n/a'
            ret['avg_cost'] = 'n/a'
            MaxTotal.append('n/a')
            MinTotal = 'n/a'
         ret['short_name'] = p.progshortname
         ProgList.append(ret)
   except ObjectDoesNotExist:
      return HttpResponse('A Project and/or Program does not exist! Cannot proceed further.')
   return render(request,'reports/compcostanal.html', {'ProjectName': project.projectname, 'ProgList':ProgList, 'MaxTotal':MaxTotal,'MinTotal':MinTotal})

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
               if login2.endDate <= date.today():
                  return render_to_response('login/login.html',{'loginform': loginform, 'err': 'Your license agreement has expired. Please re-register.'}, context)
               else: 
                  return HttpResponseRedirect('/project/project_list.html')
            else:
               return render_to_response('login/login.html',{'loginform': loginform, 'err': 'Invalid user or password'}, context)
         except ObjectDoesNotExist:
            return render_to_response('login/login.html',{'loginform': loginform, 'err': 'Invalid user or password'}, context)
 
      else:
         form_errors = 'Yes'
         print form_errors
   else:
      loginform = LoginForm()

   return render_to_response('login/login.html',{'loginform': loginform}, context)

def register(request):
   context = RequestContext(request)
   if request.method == 'POST':
      registerform = RegisterForm(request.POST)
      if registerform.is_valid():
         register = registerform.save(commit=False)
         try:
            login = m.Login.objects.filter(user=register.user).latest('startDate')
            if login.endDate > date.today():
               return render_to_response('register/register.html',{'registerform': registerform, 'err': 'The User Name you have entered already exists. Please select another one.'}, context)  
         except ObjectDoesNotExist:
            print 'xyz'
         if register.password != register.passwordagain:                                                                              
            return render_to_response('register/register.html',{'registerform': registerform, 'err': 'The password does not match the confirm password.'}, context)         
         if register.email != register.emailagain:
            return render_to_response('register/register.html',{'registerform': registerform, 'err': 'The email does not match the confirm email.'}, context)
         request.session['userR'] = register.user
         request.session['email'] = register.email
         request.session['passwordR'] = register.password
         request.session['firstName'] = register.firstName
         request.session['lastName'] = register.lastName
         request.session['addressline1'] = register.addressline1
         request.session['addressline2'] = register.addressline2
         request.session['city'] = register.city
         request.session['state'] = register.state
         request.session['zip'] = register.zip
         request.session['country'] = register.country
         request.session['phone'] = register.phone
         request.session['organisation'] = register.organisation
         request.session['position'] = register.position
         request.session['publicOrPrivate'] = register.publicOrPrivate 
         return HttpResponseRedirect('/register/license.html') 
      else:
         print registerform.errors
          
   else:                                                                                                                            
      registerform = RegisterForm()
                                                             
   return render_to_response('register/register.html',{'registerform': registerform}, context)

def license(request):
   context = RequestContext(request)
   if request.method == 'POST':
      licenseform = License(request.POST)
      if licenseform.is_valid():
         license = licenseform.save(commit=False)
         if license.licenseSigned == 'Yes':
            if request.session['phone'] is not None and request.session['phone'] != '':
               m.Login.objects.create(user=request.session['userR'], email=request.session['email'],password=request.session['passwordR'],firstName=request.session['firstName'],lastName=request.session['lastName'],addressline1=request.session['addressline1'],addressline2=request.session['addressline2'],city=request.session['city'],state=request.session['state'],zip=request.session['zip'],country=request.session['country'],phone=request.session['phone'],organisation=request.session['organisation'],position=request.session['position'],publicOrPrivate=request.session['publicOrPrivate'], licenseSigned ='Yes',endDate= datetime.datetime.now() + relativedelta(years=2)) 
            else:
               m.Login.objects.create(user=request.session['userR'], email=request.session['email'],password=request.session['passwordR'],firstName=request.session['firstName'],lastName=request.session['lastName'],addressline1=request.session['addressline1'],addressline2=request.session['addressline2'],city=request.session['city'],state=request.session['state'],zip=request.session['zip'],country=request.session['country'],organisation=request.session['organisation'],position=request.session['position'],publicOrPrivate=request.session['publicOrPrivate'], licenseSigned ='Yes',endDate= datetime.datetime.now() + relativedelta(years=2))
            for p in m.Projects.objects.filter(user = 'Demo admin'):
               obj = m.Projects.objects.get(pk=p.id)
               obj.user = request.session['userR']
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
                     print 'program desc does not exist'

                  try:
                     eff = m.Effectiveness.objects.get(programId_id = pr.id)
                     eff.programId_id = prog.id
                     eff.pk = None
                     eff.save()
                  except ObjectDoesNotExist:
                     print 'effectiveness does not exist'

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
                           print 'distribution do not exist'
 
                  except ObjectDoesNotExist:
                     print 'ingredients do not exist'

                  try:
                     ag = m.Agencies.objects.get(programId=pr.id)
                     ag.programId = prog.id
                     ag.pk = None
                     ag.save()
                  except ObjectDoesNotExist:
                     print 'agencies do not exist'

                  try:
                     for t in m.Transfers.objects.filter(programId=pr.id):
                        trans = m.Transfers.objects.get(pk=t.id)
                        trans.programId = prog.id
                        trans.pk = None
                        trans.save()
                  except ObjectDoesNotExist:
                     print 'transfers do not exist'
 
            return HttpResponseRedirect('/login/login.html')
         else:        
            return HttpResponseRedirect('/about.html')
      else:
         form_errors = 'Select Yes or No to proceed'
         print form_errors
         print licenseform.errors 
         return render_to_response('register/license.html',{'licenseform': licenseform, 'form_errors':form_errors}, context)
   else:                                                                                                                            
      licenseform = License()
   return render_to_response('register/license.html',{'licenseform': licenseform}, context)

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


def tutorial1_pdf(request):
   with open('/home/amritha/costtool/documents/Tutorial_1__Add_personnel_ingredient__IB.pdf', 'r') as pdf:                               
      response = HttpResponse(pdf.read(), content_type='application/pdf')
      response['Content-Disposition'] = 'inline;filename=Tutorial_1__Add_personnel_ingredient__IB.pdf'
      return response
   pdf.closed

def tutorial2_pdf(request):
   with open('/home/amritha/costtool/documents/Tutorial 2, Adding a new ingredient.pdf', 'r') as pdf:     
      response = HttpResponse(pdf.read(), content_type='application/pdf')
      response['Content-Disposition'] = 'inline;filename=Tutorial 2, Adding a new ingredient.pdf'
      return response
   pdf.closed

def tutorial3_pdf(request):
   with open('/home/amritha/costtool/documents/Tutorial 3, How to choose a price.pdf', 'r') as pdf:
      response = HttpResponse(pdf.read(), content_type='application/pdf')
      response['Content-Disposition'] = 'inline;filename=Tutorial 3, How to choose a price.pdf'
      return response
   pdf.closed
   
def tutorial4_pdf(request):
   with open('/home/amritha/costtool/documents/Tutorial 4, Project Settings.pdf', 'r') as pdf:
      response = HttpResponse(pdf.read(), content_type='application/pdf')
      response['Content-Disposition'] = 'inline;filename=Tutorial 4, Project Settings.pdf'                                          
      return response                                                                                                                    
   pdf.closed

def tutorial5_pdf(request):
   with open('/home/amritha/costtool/documents/Tutorial 5, Adding facilities prices.pdf', 'r') as pdf:
      response = HttpResponse(pdf.read(), content_type='application/pdf')
      response['Content-Disposition'] = 'inline;filename=Tutorial 5, Adding facilities prices.pdf'                                       
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

def full_table(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    projectname = request.session['projectname']
    progname = request.session['programname']
    result = 0
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
          i = m.Ingredients.objects.get(pk=request.POST.get('id'))
          i.ingredient = request.POST.get('ingredient')
          i.category = request.POST.get('category')
          i.yearQtyUsed = request.POST.get('yearQtyUsed')
          i.variableFixed = request.POST.get('variableFixed')
          i.quantityUsed = request.POST.get('quantityUsed')
          if i.quantityUsed is None:
             i.quantityUsed = 1 
          i.lifetimeAsset = request.POST.get('lifetimeAsset')
          i.interestRate = request.POST.get('interestRate')
          i.benefitRate = request.POST.get('benefitRate')
          i.percentageofUsage = request.POST.get('percentageofUsage')
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
          i.save(update_fields=['ingredient','category','yearQtyUsed','variableFixed','quantityUsed','lifetimeAsset','interestRate','benefitRate', 'percentageofUsage','priceAdjAmortization','priceAdjBenefits'])   
          result = calculations(project_id)
       else:
          print 'no id given'
    return render_to_response('project/programs/costs/full_table.html',{'ingredients':ingredients,'project_id':project_id, 'program_id':program_id,'total_cost':round(total_cost,3),'avg_cost':avg_cost,'eff_ratio':eff_ratio,'projectname':projectname, 'programname':progname, 'discountRateEstimates':discountRateEstimates, 'infEstimate':infEstimate,'geoEstimate':geoEstimate, 'geoArea':'' },context)

def tabbedlayout(request,project_id,program_id):
    project = m.Projects.objects.get(pk=project_id)
    program = m.Programs.objects.get(pk=program_id)
    request.session['program_id'] = program_id
    request.session['projectname'] = project.projectname
    request.session['programname'] = program.progname

    effectform = EffectForm()
    total_cost = 0                                                                                                                                    
    avg_cost = ''
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
        old_total = 0
        for q in m.ParticipantsPerYear.objects.filter(programdescId=programdesc.id):
           old_total = old_total + q.noofparticipants
    except ObjectDoesNotExist:
        form1 = ProgramDescForm(request.POST)
        numberofparticipants = 1
        noofyears = 1
        progid = 0
        objectexists = False
        recordExists = False
        old_total = 0
    
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
        ingRecordExists = True
    except ObjectDoesNotExist:
       total_cost = 0
       avg_cost = ''
       eff_ratio = None    
       ingRecordExists = False
    
    try:
       ing = m.Ingredients.objects.get(programId = program_id)
       recordExists = True
    except MultipleObjectsReturned:
       recordExists = True
    except ObjectDoesNotExist:
       recordExists = False

    try:
       ag = m.Agencies.objects.get(programId = program_id)
       agency1 = ag.agency1
       agency2 = ag.agency2
       agency3 = ag.agency3
       agency4 = ag.agency4
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
               programdesc = m.ProgramDesc.objects.get(pk=id.id)
               partform = PartFormSet(request.POST,request.FILES, instance=programdesc,prefix="partform" )
               if partform.is_valid():
                  partform.save()
                  m.ParticipantsPerYear.objects.filter(noofparticipants__isnull=True).delete()
                  queryset = m.ParticipantsPerYear.objects.filter(programdescId=id.id)
                  programdesc.numberofyears=queryset.count()
                  total = 0
                  if (m.ParticipantsPerYear.objects.filter(programdescId=id.id).count() == 0) and programdesc.lengthofprogram == 'More than one year':
                     errtext = 'You have selected the length of the program as More than one year but have not entered the number of participants per year.'
                     return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'errtext':errtext,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'form1','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'partform.errors':partform.errors,'frm2':effectform,'frm4':distform, 'frm5':transform})

                  else:
                     for q in queryset:
                        total = float(total) + float(q.noofparticipants)
                     if total != old_total: 
                        programdesc.numberofparticipants = total / programdesc.numberofyears   
                  if programdesc.lengthofprogram == 'One year or less':
                     programdesc.numberofyears = 1 
                     m.ParticipantsPerYear.objects.filter(programdescId=id.id).delete()
                  programdesc.save()
                  ing = m.Ingredients.objects.filter(programId = program_id)
                  for i in ing:
                     if programdesc.numberofparticipants is not None:
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
                           i.costPerParticipant = float(i.costPerIngredient) / float(numberofparticipants)
                     i.save(update_fields=['averageCost','effRatio','costPerParticipant'])
                  
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
                  except ObjectDoesNotExist:
                     print 'no transfer records'

                  request.session['programdescId'] = programdesc.id
                  if project.typeanalysis == 'Cost Analysis':
                     return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')
                  else:
                     return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=effform')
               else:
                  print partform.errors
                  return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'form1','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'partform.errors':partform.errors,'frm2':effectform,'frm4':distform, 'frm5':transform})

            else:
               print form1.errors
               return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'form1','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'form1.errors':form1.errors,'frm2':effectform,'frm4':distform, 'frm5':transform})

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
             ing = m.Ingredients.objects.filter(programId = program_id)
             for i in ing:
                if sourceeffectdata.avgeffectperparticipant is not None  and i.averageCost is not None:
                   if sourceeffectdata.avgeffectperparticipant == '0':
                      i.effRatio = None                                                                                                
                      eff_ratio = None
                   else:   
                      i.effRatio = float(i.averageCost) / float(avgeff)
                      eff_ratio = round(i.effRatio,2)
                else:
                   i.effRatio = None 
                i.save(update_fields=['effRatio'])
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')
          else:
             print effectform.errors
             return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'effform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm2':effectform, 'frm3':ingform,'effectform.errors':effectform.errors,'frm4':distform, 'frm5':transform})

    else:
       if effobjexists:                                                                                                            
          effectform = EffectForm(instance=effect)
       else:
          effectform = EffectForm()   

    IngFormSet = modelformset_factory(m.Ingredients,extra=20)

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
                         ing.costPerIngredient = round(float(ing.adjPricePerIngredient) * float(ing.quantityUsed),3)
                      else:
                         ing.costPerIngredient = round(float(ing.adjPricePerIngredient) * float(ing.quantityUsed) * float(ing.percentageofUsage) / 100,3) 
                   try:
                      partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=progid, yearnumber=ing.yearQtyUsed)
                      if ing.costPerIngredient is not None: 
                         ing.costPerParticipant = round(float(ing.costPerIngredient) / float(partperyear.noofparticipants),3)
                      ing.save(update_fields=['ingredient', 'quantityUsed','variableFixed','costPerIngredient','costPerParticipant']) 
                   except ObjectDoesNotExist:
                      if ing.costPerIngredient is not None: 
                         ing.costPerParticipant = round(float(ing.costPerIngredient),3) / float(numberofparticipants)
                      ing.save(update_fields=['ingredient', 'quantityUsed','variableFixed','costPerIngredient','costPerParticipant'])
          
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
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')
          else:
             print ingform.errors
             return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'costform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'ingform.errors':ingform.errors,'frm2':effectform,'frm4':distform,'frm5':transform})
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
             form.fields['quantityUsed'].widget.attrs['readonly'] = True
    
    DistFormSet = modelformset_factory(m.Distribution,extra=20)
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

                if dist.cost_other_percent < 0:
                   return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'distform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'distform_errors':'The percentage cost spread between the different agencies cannot be greater than 100.','frm2':effectform,'frm4':distform, 'frm5':transform})
                else:
                   if dist.cost_agency1_percent != 0  or dist.cost_agency1_percent != 0  or dist.cost_agency1_percent != 0 or dist.cost_agency1_percent != 0:
                      dist.save(update_fields=['cost_agency1','cost_agency1_percent','cost_agency2','cost_agency2_percent','cost_agency3','cost_agency3_percent','cost_agency4','cost_agency4_percent','cost_other','cost_other_percent'])
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=distform')

          else:
             print distform.errors
             return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'effform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm2':effectform, 'frm3':ingform,'distform.errors':distform.errors,'frm4':distform,'frm5':transform})       
    else:
       try:
          inglist = m.Ingredients.objects.filter(programId = program_id)
          try:
             ag = m.Agencies.objects.get(programId = program_id)
          except ObjectDoesNotExist:
             m.Agencies.objects.create(agency1 = 'Program Sponsor', agency2 = 'Government Agencies', agency3 = 'Private Organizations', agency4 = 'Students/Parents', programId = program_id)
             ag = m.Agencies.objects.get(programId = program_id)
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

          ag.total_agency1 = total_agency1
          ag.total_agency2 = total_agency2
          ag.total_agency3 = total_agency3
          ag.total_agency4 = total_agency4
          ag.total_other = total_other
          ag.save(update_fields=['total_agency1','total_agency2','total_agency3','total_agency4','total_other','total_cost'])
       except ObjectDoesNotExist:
          print 'no point in doing anything if no records in Ingredients'
   
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
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=transform')
 
          else:
             print transform.errors
             return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'eff_ratio':eff_ratio,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'active':'effform','project':project,'program':program,'frm1':form1,'partform':partform, 'frm2':effectform, 'frm3':ingform,'distform.errors':distform.errors,'frm4':distform,'frm5':transform, 'transform.errors':transform.errors})

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
  
       except ObjectDoesNotExist:
          print 'agencies do not exist'
 
       transform = TransFormSet(queryset = trans,prefix="transform")
       for form in transform:
          form.fields['grantName'].widget.attrs['readonly'] = True
          form.fields['grantYear'].widget.attrs['readonly'] = True
          form.fields['cost_agency1'].widget.attrs['readonly'] = True
          form.fields['cost_agency2'].widget.attrs['readonly'] = True
          form.fields['cost_agency3'].widget.attrs['readonly'] = True
          form.fields['cost_agency4'].widget.attrs['readonly'] = True
          form.fields['cost_other'].widget.attrs['readonly'] = True             

    return render (request,'project/programs/effect/tabbedview.html',{'recordExists': recordExists,'net_agency1':net_agency1,'net_agency2':net_agency2,'net_agency3':net_agency3,'net_agency4':net_agency4,'net_other':net_other,'agency1': agency1,'agency2': agency2,'agency3': agency3,'agency4': agency4,'total_agency1':total_agency1,'total_agency2':total_agency2,'total_agency3':total_agency3,'total_agency4':total_agency4,'total_other':total_other,'noofyears':noofyears,'total_cost':total_cost,'avg_cost':avg_cost,'eff_ratio':eff_ratio,'project':project,'program':program,'frm1':form1,'partform':partform, 'frm3':ingform,'frm2':effectform, 'frm4':distform, 'frm5':transform})

def add_agency(request):
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    context = RequestContext(request)
    try:
       agency = m.Agencies.objects.get(programId=program_id)
    except ObjectDoesNotExist:
       print 'object does not exist'

    if request.method == 'POST':
        agencyform = AgenciesForm(request.POST,instance=agency)

        if agencyform.is_valid():
            agency1 = agencyform.save(commit=False)
            agency1.save(update_fields=['agency1','agency2','agency3','agency4'])
            return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=distform')
        else:
            print agencyform.errors

    else:
        agencyform = AgenciesForm(instance=agency)

    return render(request,
            'project/programs/dist/add_agency.html',
            {'project_id':project_id,'program_id':program_id,'agencyform': agencyform})

def add_transfer(request):
    project_id = request.session['project_id']
    program_id = request.session['program_id']
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
       print 'object does not exist'
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
                return render_to_response ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)  
 
             for transfer1 in transfers:
                transfer1.programId = program_id
                transfer1.grantFrom = request.POST.get('grantFrom')
                transfer1.grantTo = request.POST.get('grantTo')
                transfer1.grantName = request.POST.get('desc')
                transfer1.perparticipantOrTotal = request.POST.get('pOrTotal')
                if transfer1.grantName == '' or transfer1.grantName is None:
                   err = 'Enter the name of the transfer/subsidy/fee'
                   return render_to_response ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)  

                if transfer1.grantFrom == transfer1.grantTo:
                   err = 'From and To cannot be the same agency'
                   transfer1.grantName = request.POST.get('desc')
                   return render_to_response ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)

                if transfer1.perparticipantOrTotal == 'Total':
                   transfer1.total_amount = transfer1.grantAmount
                else:
                   try:
                      partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=progdesc.id, yearnumber=transfer1.grantYear)
                      print float(partperyear.noofparticipants)
                      print transfer1.grantAmount
                      if transfer1.grantAmount is not None: 
                         transfer1.total_amount =  float(transfer1.grantAmount) * float(partperyear.noofparticipants)
                   except ObjectDoesNotExist:
                      transfer1.total_amount = transfer1.grantAmount

                if transfer1.total_amount is not None:
                   if transfer1.grantFrom == ag1:
                      transfer1.cost_agency1 = transfer1.total_amount
                   elif transfer1.grantFrom == ag2:
                      transfer1.cost_agency2 = transfer1.total_amount
                   elif transfer1.grantFrom == ag3:
                      transfer1.cost_agency3 = transfer1.total_amount
                   elif transfer1.grantFrom == ag4:
                      transfer1.cost_agency4 = transfer1.total_amount
                   elif transfer1.grantFrom == 'Other':
                      transfer1.cost_other = transfer1.total_amount
                   
                   if transfer1.grantTo == ag1:
                      transfer1.cost_agency1 = -transfer1.total_amount
                   elif transfer1.grantTo == ag2:
                      transfer1.cost_agency2 = -transfer1.total_amount
                   elif transfer1.grantTo == ag3:
                      transfer1.cost_agency3 = -transfer1.total_amount
                   elif transfer1.grantTo == ag4:
                      transfer1.cost_agency4 = -transfer1.total_amount
                   elif transfer1.grantTo == 'Other':
                      transfer1.cost_other = -transfer1.total_amount

                   transfer1.save()
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=transform')
          else:
             print transferform.errors
             return render_to_response ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors},context)

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
                return render_to_response ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)

             if transfer1.grantName == '' or transfer1.grantName is None:
                   err = 'Enter the name of the transfer/subsidy/fee'
                   return render_to_response ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors,'err': err},context)

             if transfer1.grantFrom == transfer1.grantTo:
                err = 'From and To cannot be the same agency'
                return render_to_response ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'err': err},context)

             if transfer1.perparticipantOrTotal == 'Total':
                transfer1.total_amount = transfer1.grantAmount
             else:
                if transfer1.averageno is None:
                   transfer1.total_amount = transfer1.grantAmount * avgno
                else:
                   transfer1.total_amount = transfer1.grantAmount * transfer1.averageno

             if transfer1.grantFrom == ag1:
                transfer1.cost_agency1 = transfer1.total_amount
             elif transfer1.grantFrom == ag2:
                transfer1.cost_agency2 = transfer1.total_amount
             elif transfer1.grantFrom == ag3:
                transfer1.cost_agency3 = transfer1.total_amount
             elif transfer1.grantFrom == ag4:
                transfer1.cost_agency4 = transfer1.total_amount
             elif transfer1.grantFrom == 'Other':
                transfer1.cost_other = transfer1.total_amount

             if transfer1.grantTo == ag1:
                transfer1.cost_agency1 = -transfer1.total_amount
             elif transfer1.grantTo == ag2:
                transfer1.cost_agency2 = -transfer1.total_amount
             elif transfer1.grantTo == ag3:
                transfer1.cost_agency3 = -transfer1.total_amount
             elif transfer1.grantTo == ag4:
                transfer1.cost_agency4 = -transfer1.total_amount
             elif transfer1.grantTo == 'Other':
                transfer1.cost_other = -transfer1.total_amount

             transfer1.save() 
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=transform')
          else:
              print transferform.errors
              return render_to_response ('project/programs/transfer/add_transfer.html',{'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform,'transferform.errors': transferform.errors},context)
       else:
           transferform = TransfersForm()

    return render(request,
            'project/programs/transfer/add_transfer.html',
            {'ptext': ptext,'pcount':pcount,'project_id':project_id,'program_id':program_id,'avgno':avgno,'ag1':ag1,'ag2':ag2,'ag3':ag3,'ag4':ag4,'transferform': transferform})

def del_transfer(request, trans_id):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']

    m.Transfers.objects.get(pk=trans_id).delete()
    
    return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=transform')

def del_ingredient(request, ing_id):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
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
    return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')

def dupl_ingredient(request, ing_id):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
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

    m.Ingredients.objects.create(SourceBenefitData = ingredient.SourceBenefitData, category = ingredient.category, ingredient = ingredient.ingredient, edLevel = ingredient.edLevel, sector = ingredient.sector, unitMeasurePrice = ingredient.unitMeasurePrice, price =  ingredient.price, sourcePriceData = ingredient.sourcePriceData, urlPrice = ingredient.urlPrice, newMeasure = ingredient.newMeasure, convertedPrice = ingredient.convertedPrice, yearPrice = ingredient.yearPrice, statePrice = ingredient.statePrice, areaPrice = ingredient.areaPrice, programId = ingredient.programId, lifetimeAsset = ingredient.lifetimeAsset, interestRate = ingredient.interestRate, benefitRate = ingredient.benefitRate, indexCPI = ingredient.indexCPI, geoIndex = ingredient.geoIndex, quantityUsed = ingredient.quantityUsed, variableFixed = ingredient.variableFixed, yearQtyUsed = ingredient.yearQtyUsed, priceAdjAmortization = ingredient.priceAdjAmortization, percentageofUsage = ingredient.percentageofUsage, adjPricePerIngredient = ingredient.adjPricePerIngredient, priceAdjInflation = ingredient.priceAdjInflation, priceAdjBenefits = ingredient.priceAdjBenefits,priceAdjGeographicalArea = ingredient.priceAdjGeographicalArea, priceNetPresentValue = ingredient.priceNetPresentValue, costPerIngredient = ingredient.costPerIngredient, costPerParticipant = ingredient.costPerParticipant )

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
    
    return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html?activeform=costform')

def search_costs(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    projectname = request.session['projectname'] 
    progname = request.session['programname']

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
            print costform.errors
            return HttpResponse(costform.errors)
    else:
       costform = PricesSearchForm()
    return render_to_response('project/programs/costs/search_costs.html',{'costform':costform,'choicesEdn':choicesEdn,'choicesSec':choicesSec,'project_id':project_id, 'program_id':program_id,'projectname':projectname, 'programname':progname},context)

def price_search(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    projectname = request.session['projectname']
    progname = request.session['programname']       

    if 'new_price' in request.session:
        del request.session['new_price']

    if 'new_measure' in request.session:
        del request.session['new_measure']

    try:
       sett = m.Settings.objects.get(projectId = project_id)
       if 'CBCSE' in sett.selectDatabase and 'My' in sett.selectDatabase:
          prices = m.Prices.objects.all()
       elif 'CBCSE' in sett.selectDatabase:
          prices = m.Prices.objects.filter(priceProvider = 'CBCSE')
       elif 'My' in sett.selectDatabase:
          prices = m.Prices.objects.filter(priceProvider = 'User')

       #if 'recent' in sett.limitYear:
          #prices = m.Prices.objects.all().prefetch_related('ingredient')
          #latest('yearPrice')
          #prices = prices.latest('yearPrice')
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
          prices = prices.filter(ingredient__icontains = ingredient)
       if 'recent' in sett.limitYear:
          ingredients = m.Prices.objects.all().values_list('ingredient',flat=True)
          #ingredients = prices.values_list('ingredient',flat=True)
                   #this should give us a list of all ingredients
          price_pks = []                                                                                                       
          for ingredient in ingredients:
             price = m.Prices.objects.filter(ingredient=ingredient).order_by('-yearPrice')[0]
             price_pks.append(price.pk)
          prices = prices.filter(pk__in=price_pks)

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
       inf = m.InflationIndices.objects.get(projectId=request.session['project_id'],yearCPI=price.yearPrice)
       request.session['priceExists'] = True
       if price.category == 'Personnel':
          return HttpResponseRedirect('/project/programs/costs/'+ price_id +'/price_indices.html')
       else:
          return HttpResponseRedirect('/project/programs/costs/'+ price_id +'/nonper_indices.html')
    except ObjectDoesNotExist:
       request.session['priceExists'] = False 
       return render_to_response('project/programs/costs/gotoinf.html',{'yearPrice':price.yearPrice},context)

def gotoinf(request):
   return render(request,'project/programs/costs/gotoinf.html')
    
def price_indices(request,price_id):
    price = m.Prices.objects.get(pk=price_id)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    projectname = request.session['projectname']
    progname = request.session['programname'] 

    cat =  request.session['search_cat']
    edLevel =  request.session['search_edLevel']
    sector =  request.session['search_sector']
    ingredient = request.session['search_ingredient']

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
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    projectname = request.session['projectname']
    progname = request.session['programname'] 

    cat =  request.session['search_cat']
    edLevel =  request.session['search_edLevel']
    sector =  request.session['search_sector']
    ingredient = request.session['search_ingredient']

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
            print form.errors
            return render_to_response('project/programs/costs/nonper_indices.html',{'form':form, 'price':price, 'new_price' : new_price, 'new_measure' : new_measure, 'cat' : cat, 'edLevel':  edLevel, 'sector': sector,'ingredient' : ingredient,'project_id':project_id, 'program_id':program_id,'form.errors':form.errors,'projectname':projectname, 'programname':progname},context)
    else:
        form = NonPerIndicesForm()

    return render_to_response('project/programs/costs/nonper_indices.html',{'form':form, 'price':price, 'new_price' : new_price, 'new_measure' : new_measure, 'cat' : cat, 'edLevel':  edLevel, 'sector': sector,'ingredient' : ingredient,'project_id':project_id, 'program_id':program_id, 'projectname':projectname, 'programname':progname},context)

def um_converter(request):
    context = RequestContext(request)
    price_id = request.session['price_id']
    project_id = request.session['project_id']

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
    listLen=['Inches','Feet','Yards','Miles','Millimeter','Centimeter','Kilometer']
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
                    if measure == 'Sq. Inch':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price * 0.006
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price * 0.0007
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price * 0.000000159
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price * 0.000000000249
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price * 0.0006
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price * 0.000000000645
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price * 0.0000000645

                    if measure == 'Sq. Foot' or measure == 'Sq. Ft.':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price * 144
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price * 0.111
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price * 0.0000229
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price * 0.00000003587
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price * 0.092
                        if newMeasure.newMeasure == 'Sq. Kilometer':
			    newMeasure.convertedPrice = price * 0.0000000929
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price * 0.00000929

                    if measure == 'Sq. Yard':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price * 1296
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price * 9
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price * 0.0002
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price * 0.000000322
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price * 0.83
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price * 0.000000836
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price * 0.0000836

                    if measure == 'Acre':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price * 0.00000627
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price * 4840
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price * 43560
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price * 0.0015
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price * 4046.86
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price * 0.00404
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price * 0.404

                    if measure == 'Sq. Mile':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price * 0.000000004014
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price * 0.000003098
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price * 0.000000278
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price * 640
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price * 0.00000259
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price * 2.5899
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price * 258.999

                    if measure == 'Sq. Meter':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price * 1550
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price * 1.19
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price * 10.76
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price * 0.00024
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price * 0.000000386
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price * 0.000001
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price * 0.0001

                    if measure == 'Sq. Kilometer':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price * 0.000000001550
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price * 0.000001196
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price * 0.0000001076
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price * 247.105
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price * 0.386
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price * 0.000001
                        if newMeasure.newMeasure == 'Hectare':
                            newMeasure.convertedPrice = price * 100

                    if measure == 'Hectare':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasure == 'Sq. Inch':
                            newMeasure.convertedPrice = price * 0.0000001550
                        if newMeasure.newMeasure == 'Sq. Yard':
                            newMeasure.convertedPrice = price * 11959.9
                        if newMeasure.newMeasure == 'Sq. Foot':
                            newMeasure.convertedPrice = price * 107639
                        if newMeasure.newMeasure == 'Acre':
                            newMeasure.convertedPrice = price * 2.471
                        if newMeasure.newMeasure == 'Sq. Mile':
                            newMeasure.convertedPrice = price * 0.00386
                        if newMeasure.newMeasure == 'Sq. Meter':
                            newMeasure.convertedPrice = price * 10000
                        if newMeasure.newMeasure == 'Sq. Kilometer':
                            newMeasure.convertedPrice = price * 0.01

                    request.session['new_measure'] = newMeasure.newMeasure
                    new_measure = newMeasure.newMeasure
                if measureType == 'listVol':
                    if measure == 'Fluid Ounces':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price * 0.125
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price * 0.0625
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price * 0.03125
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price * 0.0078
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price * 0.029

                    if measure == 'Cups':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price * 8
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price * 0.5
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price * 0.25
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price * 0.0625
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price * 0.236

                    if measure == 'Pints':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price * 2
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price * 16
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price * 0.5
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price * 0.125
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price * 0.473

                    if measure == 'Quarts':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price * 4
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price * 2
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price * 32
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price * 0.25
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price * 0.946

                    if measure == 'Gallons':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price * 16
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price * 8
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price * 4
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price * 128
                        if newMeasure.newMeasureVol == 'Liters':
                            newMeasure.convertedPrice = price * 3.785

                    if measure == 'Liters':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureVol == 'Cups':
                            newMeasure.convertedPrice = price * 4.22
                        if newMeasure.newMeasureVol == 'Pints':
                            newMeasure.convertedPrice = price * 2.11
                        if newMeasure.newMeasureVol == 'Quarts':
                            newMeasure.convertedPrice = price * 1.05
                        if newMeasure.newMeasureVol == 'Gallons':
                            newMeasure.convertedPrice = price * 0.264
                        if newMeasure.newMeasureVol == 'Fluid Ounces':
                            newMeasure.convertedPrice = price * 33.81

                    request.session['new_measure'] = newMeasure.newMeasureVol
                    new_measure = newMeasure.newMeasureVol

                if measureType == 'listLen':
                    if measure == 'Inches':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price * 0.083
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price * 0.027
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price * 0.00001578
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price * 25.4
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price * 2.54
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price * 0.0000254

                    if measure == 'Feet':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price * 12
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price * 0.3333
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price * 0.00018
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price * 304.8
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price * 30.48
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price * 0.000304

                    if measure == 'Yards':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price * 36
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price * 3
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price * 0.00056
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price * 914.4
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price * 91.44
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price * 0.0009144

                    if measure == 'Miles':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price * 63360
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price * 5280
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price * 1760
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price * 0.00000160934
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price * 160934
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price * 1.609

                    if measure == 'Millimeter':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price * 0.039
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price * 0.00328
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price * 0.00109
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price * 0.000000621
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price * 0.1
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price * 0.000001

                    if measure == 'Centimeter':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price * 0.393
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price * 0.0328
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price * 0.0109
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price * 0.00000621
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price * 10
                        if newMeasure.newMeasureLen == 'Kilometer':
                            newMeasure.convertedPrice = price * 0.00001

                    if measure == 'Kilometer':
                        newMeasure.convertedPrice = price
                        if newMeasure.newMeasureLen == 'Inches':
                            newMeasure.convertedPrice = price * 39370.1
                        if newMeasure.newMeasureLen == 'Feet':
                            newMeasure.convertedPrice = price * 3280.84
                        if newMeasure.newMeasureLen == 'Yards':
                            newMeasure.convertedPrice = price * 1093.61
                        if newMeasure.newMeasureLen == 'Miles':
                            newMeasure.convertedPrice = price * 0.621
                        if newMeasure.newMeasureLen == 'Centimeter':
                            newMeasure.convertedPrice = price * 100000
                        if newMeasure.newMeasureLen == 'Millimeter':
                            newMeasure.convertedPrice = price * 0.000001

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
                print form.errors

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

    return render_to_response('project/programs/costs/umconverter.html',{'form':form, 'price':price,'measure':measure,'measureType':measureType, 'new_price' : new_price, 'new_measure' : new_measure, 'price_id':price_id},context)

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

    project_id = request.session['project_id']
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
                if measure == 'Hour':
                    newMeasure.convertedPrice = price 
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price * 8
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price * 40
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * hrsCalendarYr
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * hrsAcademicYr
                    if newMeasure.newMeasure == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * hrsHigherEdn

                if measure == 'Day': 
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price /  8
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price *  5
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / 8)
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / 8)
                    if newMeasure.newMeasure == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / 8)

                if measure == 'Week': 
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price / 40
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price /  5
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * 52
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * 36
                    if newMeasure.newMeasure == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * 39

                if measure == 'Calendar Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price / hrsCalendarYr
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price / (hrsCalendarYr / 8)
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price / 52
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / hrsCalendarYr)
                    if newMeasure.newMeasure == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / hrsCalendarYr)

                if measure == 'K-12 Academic Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price / hrsAcademicYr
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price / (hrsAcademicYr / 8)
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price / 36
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / hrsAcademicYr)
                    if newMeasure.newMeasure == 'Higher Ed Academic Year' or newMeasure.newMeasureTime == 'Higher Education Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / hrsAcademicYr)

                if measure == 'Higher Ed Academic Year' or measure == 'Higher Education Academic Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price / hrsHigherEdn
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price / (hrsHigherEdn / 8)
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price / 39
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / hrsHigherEdn)
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / hrsHigherEdn)

                request.session['new_price'] = round(float(newMeasure.convertedPrice),3)
                request.session['new_measure'] = newMeasure.newMeasure 
                return HttpResponseRedirect('/project/programs/costs/wage_converter.html')
            else:
                print form.errors

        if 'use' in request.POST:
            price_id = request.session['price_id']
            return HttpResponseRedirect('/project/programs/costs/'+ price_id + '/price_indices.html')

    else:
        form = WageConverter(initial={'convertedPrice':new_price,'newMeasure':new_measure})

    return render_to_response('project/programs/costs/wage_converter.html',{'form':form, 'convertedPrice':new_price,'newMeasure':new_measure,'price':price, 'price_id':price_id,'measure':measure, 'hrsCalendarYr': hrsCalendarYr, 'hrsAcademicYr':hrsAcademicYr, 'hrsHigherEdn':hrsHigherEdn},context)
 
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
            print form.errors
    else:
       form = WageDefaults(initial={'hrsCalendarYr': hrsCalendarYr, 'hrsAcademicYr':hrsAcademicYr, 'hrsHigherEdn':hrsHigherEdn}) 

    return render_to_response('project/programs/costs/wage_defaults.html',{'form':form},context)

def price_benefits(request,price_id):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    projectname = request.session['projectname']                                                                                     
    progname = request.session['programname'] 
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
            print form.errors
            return render_to_response('project/programs/costs/price_benefits.html',{'form':form, 'benefitRate':benefitRate,'price':price, 'project_id':project_id, 'program_id':program_id,'projectname':projectname, 'programname':progname,'form.errors':form.errors},context)
    else:
        form = PriceBenefits()
    return render_to_response('project/programs/costs/price_benefits.html',{'form':form, 'benefitRate':benefitRate,'price':price, 'project_id':project_id, 'program_id':program_id,'projectname':projectname, 'programname':progname},context)

def benefits(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
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

    project_id = request.session['project_id']
    program_id = request.session['program_id']
    projectname = request.session['projectname']
    progname = request.session['programname']

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
       pcount = m.ParticipantsPerYear.objects.filter(programdescId_id=programdesc.id).count()
       numberofparticipants = programdesc.numberofparticipants
    except ObjectDoesNotExist:
       pcount = 0
       numberofparticipants = 1
    
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
             for ingredient in ingredients:
                 ingredient.variableFixed = request.POST.get('variableFixed2')  
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
                 print ingredient.priceAdjAmortization
                 if ingredient.category == 'Personnel':
                    ingredient.priceAdjBenefits = round(round(ingredient.priceAdjAmortization,3) * (1 + float(ingredient.benefitRate)/100),3)
                 else:
                    ingredient.priceAdjBenefits = round(ingredient.priceAdjAmortization,3)
                 print ingredient.priceAdjBenefits
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
                 print ingredient.priceAdjInflation
                 print ingredient.priceAdjGeographicalArea
                 print ingredient.priceNetPresentValue
                 print ingredient.adjPricePerIngredient
                 print ingredient.costPerIngredient
                 print ingredient.costPerParticipant
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
                   i.averageCost = float(i.totalCost) / float(numberofparticipants)
                else:
                   i.averageCost = None

                if avgeff is not None and i.averageCost is not None:
                   i.effRatio = float(i.averageCost) / float(avgeff)
                else:
                   i.effRatio = None

                i.save(update_fields=['totalCost','averageCost','percentageCost','effRatio'])

             return HttpResponseRedirect('/project/programs/effect/'+ project_id + '/' + program_id + '/tabbedview.html?activeform=costform')
             
          else:
             print form.errors
             return render_to_response('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'new_measure':new_measure,'projectname':projectname, 'programname':progname,'form.errors':form.errors},context)
       else:
          form = MFormSet(queryset=m.Ingredients.objects.none(),initial=[{'yearQtyUsed': "%d" % (i+1)} for i in range(10)])
    else:
       if request.method == 'POST':
          form = PriceSummary(request.POST)
          if form.is_valid():
             ingredient = form.save(commit=False)
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
                   if numberofparticipants is not None and  numberofparticipants != 1:
                      ingredient.costPerParticipant = round(float(ingredient.costPerIngredient),3) / float(numberofparticipants)
             #print ingredient.priceAdjAmortization
             #print ingredient.priceAdjBenefits
             #print ingredient.priceAdjInflation
             #print ingredient.priceAdjGeographicalArea
             #print ingredient.priceNetPresentValue
             #print ingredient.adjPricePerIngredient
             #print ingredient.costPerIngredient
             #print ingredient.costPerParticipant
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
                   i.save(update_fields=['totalCost','averageCost','percentageCost'])
                else:
                   i.save(update_fields=['totalCost','percentageCost'])
             return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/' + program_id + '/tabbedview.html?activeform=costform')
          else:
             print form.errors

       else:
          form = PriceSummary()
    return render_to_response('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'projectname':projectname, 'programname':progname,'new_measure':new_measure},context)

def program_list(request,project_id):
    request.session['project_id'] = project_id
    try:
        project = m.Projects.objects.get(pk=project_id)
        program = m.Programs.objects.filter(projectId=project_id)
    except ObjectDoesNotExist:
        return HttpResponse('A Project and/or Program does not exist! Cannot proceed further.')
    return render_to_response(
            'project/programs/program_list.html',
            {'project':project,'program':program})

def del_program(request, program_id):
    context = RequestContext(request)
    project_id = request.session['project_id']
    try:
       m.Distribution.objects.filter(programId=program_id).delete()
    except ObjectDoesNotExist:
       print 'distribution do not exist'

    try:
       m.Agencies.objects.filter(programId=program_id).delete()
    except ObjectDoesNotExist:
       print 'agencies do not exist'

    try:
       m.Transfers.objects.filter(programId=program_id).delete()
    except ObjectDoesNotExist:
       print 'transfers do not exist'

    try:
       m.Ingredients.objects.filter(programId=program_id).delete()
    except ObjectDoesNotExist:
       print 'ingredients do not exist'
    try:   
       m.Effectiveness.objects.get(programId_id = program_id).delete()
    except ObjectDoesNotExist:
       print 'effectiveness does not exist'
    try:   
       progdesc = m.ProgramDesc.objects.get(programId_id = program_id)
       m.ParticipantsPerYear.objects.filter(programdescId_id = progdesc.id).delete()
       m.ProgramDesc.objects.get(programId_id = program_id).delete()
    except ObjectDoesNotExist:
       print 'program desc does not exist'
    m.Programs.objects.get(pk = program_id).delete()
    return HttpResponseRedirect('/project/programs/' + project_id + '/program_list.html')

def dupl_program(request, program_id):
    context = RequestContext(request)
    project_id = request.session['project_id']

    prog = m.Programs.objects.get(pk = program_id)
    prog.progname = prog.progname + str(random.randint(0,9))
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
       print 'program desc does not exist'

    try:
       eff = m.Effectiveness.objects.get(programId_id = program_id)
       eff.programId_id = prog.id
       eff.pk = None
       eff.save()
    except ObjectDoesNotExist:
       print 'effectiveness does not exist'

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
             print 'distribution do not exist'
    except ObjectDoesNotExist:
       print 'ingredients do not exist'
    try:
       ag = m.Agencies.objects.get(programId=program_id)
       ag.programId = prog.id
       ag.pk = None
       ag.save()
    except ObjectDoesNotExist:
       print 'agencies do not exist'

    try:
       for t in m.Transfers.objects.filter(programId=program_id):
          trans = m.Transfers.objects.get(pk=t.id)
          trans.programId = prog.id
          trans.pk = None
          trans.save()
    except ObjectDoesNotExist:
       print 'transfers do not exist'

    return HttpResponseRedirect('/project/programs/' + project_id + '/program_list.html')

def index(request):
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    recent_projects = m.Projects.objects.filter(created_at__gt = two_days_ago).all()
    template = loader.get_template('index.html')
 
    context = Context({
        'projects_list' : recent_projects
    })
    return HttpResponse(template.render(context))

def project_detail(request, projects_id):
    try:
        project = m.Projects.objects.get(pk=projects_id)
    except m.Projects.DoesNotExist:
        raise Http404
    return render(request, 'projects/detail.html', {'projects':project})

def project_upload(request):
    if request.method == 'GET':
        return render(request, 'projects/upload.html', {})
    elif request.method == 'POST':
        project = m.Projects.objects.create(projectname=request.POST['projectname'],
                                            typeanalysis=request.POST['typeanalysis'],
                                            created_at=datetime.utcnow())
        return HttpResponseRedirect(reverse('project_detail', kwargs={'projects_id': projects.id}))       

def register2(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=True)
            profile.user = user
            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
            'register/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect('/admin/costtool')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render_to_response('login/login.html', {}, context)

def about(request):
    context = RequestContext(request)
    return render_to_response('about.html', {}, context)

def add_project(request):
    context = RequestContext(request)

    if request.method == 'POST':
        projectform = ProjectsForm(data=request.POST)

        if projectform.is_valid():
            projectname = projectform.save()
            projectname.user = request.session['user']
            projectname.save()
            for i in m.InflationIndices_orig.objects.all():
                inf =  m.InflationIndices.objects.create(yearCPI=i.yearCPI, indexCPI=i.indexCPI, projectId=projectname.id)
            for g in m.GeographicalIndices_orig.objects.all():
                geo = m.GeographicalIndices.objects.create(stateIndex=g.stateIndex, areaIndex=g.areaIndex, geoIndex=g.geoIndex, projectId=projectname.id)
            latest = m.InflationIndices_orig.objects.all().latest('yearCPI')
            s = m.Settings.objects.create(discountRateEstimates=3.5, yearEstimates = latest.yearCPI, stateEstimates='All states', areaEstimates="All areas", selectDatabase="[u'CBCSE',u'My']",limitEdn="[u'Select',u'General',u'Grades PK', u'Grades K-6', u'Grades 6-8', u'Grades 9-12',u'Grades K-12','PostSecondary']",limitSector="[u'Select',u'Any',u'Public',u'Private']",limitYear="[u'All',u'recent']",hrsCalendarYr=2080,hrsAcademicYr=1440,hrsHigherEdn=1560,projectId=projectname.id) 
            request.session['project_id'] = projectname.id
            return HttpResponseRedirect('/project/settings.html')
            #return render_to_response('project/add_project.html',{'projectform':projectform}, context)
        else:
            print projectform.errors

    else:
        projectform = ProjectsForm()        

    return render_to_response(
            'project/add_project.html',
            {'projectform': projectform}, context)

def project_list(request):
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

    context = Context({
        'allprojects' : allprojects
    })
    return HttpResponse(template.render(context))

def del_project(request, project_id):
    context = RequestContext(request)
    
    for p in m.Programs.objects.filter(projectId = project_id): 
       try:
          m.Distribution.objects.filter(programId=p.id).delete()
       except ObjectDoesNotExist:
          print 'distribution do not exist'

       try:
          m.Agencies.objects.filter(programId=p.id).delete()
       except ObjectDoesNotExist:
          print 'agencies do not exist'

       try:
          m.Transfers.objects.filter(programId=p.id).delete()
       except ObjectDoesNotExist:
          print 'transfers do not exist'

       try:
          m.Ingredients.objects.filter(programId=p.id).delete()
       except ObjectDoesNotExist:
          print 'ingredients do not exist'
            
       try:
          m.Effectiveness.objects.get(programId_id = p.id).delete()
       except ObjectDoesNotExist:
          print 'effectiveness does not exist'
            
       try:
          progdesc = m.ProgramDesc.objects.get(programId_id = p.id)
          m.ParticipantsPerYear.objects.filter(programdescId_id = progdesc.id).delete()
          m.ProgramDesc.objects.get(programId_id = p.id).delete()
       except ObjectDoesNotExist:
          print 'program desc does not exist'
            
       m.Programs.objects.get(pk = p.id).delete()
    
    m.InflationIndices.objects.filter(projectId=project_id).delete()
    m.GeographicalIndices.objects.filter(projectId=project_id).delete()
    m.Settings.objects.get(projectId=project_id).delete()
    m.Projects.objects.get(pk=project_id).delete()
    return HttpResponseRedirect('/project/project_list.html')

def add_price(request):
    context = RequestContext(request)
    if request.method == 'POST':
        pricesform = PricesForm(data=request.POST)

        if pricesform.is_valid():
            priceProvider = pricesform.save(commit=False)
            priceProvider.priceProvider = request.session['user']
            priceProvider.save()
            return HttpResponseRedirect('/prices/my_price_list.html')
        else:
            print pricesform.errors

    else:
        pricesform = PricesForm()

    return render_to_response(
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
    
    template = loader.get_template('prices/view_price2.html')
    context = Context({
        'price' : price
    })
    return HttpResponse(template.render(context))

def edit_price(request, price_id):
    price = m.Prices.objects.get(pk=price_id)
    context = RequestContext(request)

    if request.method == 'POST':
        pricesform = PricesForm(request.POST,instance=price)
        if pricesform.is_valid():
            priceProvider = pricesform.save()
            priceProvider.save()
            return HttpResponseRedirect('/prices/my_price_list.html')
        else:
            print priceform.errors
    else:
        pricesform = PricesForm(instance=price)

    return render_to_response(
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

    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
    programId = request.session['program_id']
    projectId = request.session['project_id']

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    sett = m.Settings.objects.get(projectId = projectId)
    programdesc = m.ProgramDesc.objects.get(programId_id = programId)
    try:
       part = m.ParticipantsPerYear.objects.filter(programdescId_id = programdesc.id)[:1].get()
       partExists = True
    except ObjectDoesNotExist:
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
    pattern.pattern_fore_colour = 22
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = 22
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
    pattern3.pattern_fore_colour = 7
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
    ws.write(9, 0, "Average number of participants", font_style3)
    ws.write(9, 1, "", font_style5)
    ws.write(9, 2, str(programdesc.numberofparticipants), font_style4)
    ws.write(9, 3, "", font_style4)

    cursor = database.cursor ()
    cursor2 = database.cursor()

    # Select from sql query
    sql = """SELECT costPerIngredient,percentageCost,costPerParticipant,ingredient,category,price,unitMeasurePrice,newMeasure,yearQtyUsed,quantityUsed,lifetimeAsset,FORMAT(CONVERT(interestRate, DECIMAL(10,2)),2)  interestRate,variableFixed,convertedPrice,priceAdjAmortization,FORMAT(CONVERT(benefitRate, DECIMAL(10,2)),2) benefitRate,priceAdjBenefits,percentageofUsage,yearPrice,case indexCPI when 'No inflation index available' then indexCPI else FORMAT(CONVERT(indexCPI, DECIMAL(10,2)),2) end  indexCPI,case priceAdjInflation when 'No index' then priceAdjInflation else FORMAT(CONVERT(priceAdjInflation, DECIMAL(10,2)),2) end  priceAdjInflation, statePrice,areaPrice,case geoIndex when 'No geographical index available' then geoIndex else FORMAT(CONVERT(geoIndex, DECIMAL(10,2)),2) end geoIndex,case priceAdjGeographicalArea when 'No index' then priceAdjGeographicalArea  else FORMAT(CONVERT(priceAdjGeographicalArea, DECIMAL(10,2)),2) end priceAdjGeographicalArea,priceNetPresentValue,case adjpriceperingredient when 'No inflation index available' then adjpriceperingredient when 'No geographical index available' then adjpriceperingredient else FORMAT(CONVERT(adjpriceperingredient, DECIMAL(10,2)),2) end adjPricePerIngredient,edLevel,sector,urlPrice,sourcePriceData,sourceBenefitData,yearBenefit FROM costtool_ingredients WHERE programId = %(programId)s ORDER BY yearQtyUsed"""

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
           print "Error: unable to fetch data"

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
        (u"Year Benefit", 5000)
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
       print "Error: unable to fetch data"

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_cost_table(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=cost_table.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Cost Information")

    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
    programId = request.session['program_id']
    projectId = request.session['project_id']

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    sett = m.Settings.objects.get(projectId = projectId)
    programdesc = m.ProgramDesc.objects.get(programId_id = programId)
    try:
       part = m.ParticipantsPerYear.objects.filter(programdescId_id = programdesc.id)[:1].get()
       partExists = True
    except ObjectDoesNotExist:
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
    pattern.pattern_fore_colour = 22
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = 22
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
    pattern3.pattern_fore_colour = 7
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
    ws.write(9, 0, "Average number of participants", font_style3)
    ws.write(9, 1, "", font_style5)
    ws.write(9, 2, str(programdesc.numberofparticipants), font_style4)
    ws.write(9, 3, "", font_style4) 

    cursor = database.cursor ()
    cursor2 = database.cursor()

    # Create the INSERT INTO sql query
    sql = """SELECT ingredient, category, yearQtyUsed, quantityUsed, unitMeasurePrice, variableFixed, case adjpriceperingredient when 'No inflation index available' then adjpriceperingredient when 'No geographical index available' then adjpriceperingredient else FORMAT(CONVERT(adjpriceperingredient, DECIMAL(10,2)),2) end adjPricePerIngredient, costPerIngredient, percentageCost, costPerParticipant,totalCost, averageCost, effRatio FROM costtool_ingredients WHERE programId = %(programId)s ORDER BY yearQtyUsed"""

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
          print "Error: unable to fetch data"

       row_num = 23

    columns = [
        (u"Ingredient", 8000),
        (u"Category of ingredient", 5000),
        (u"Year in which quantity is used", 4000),
        (u"Quantity of Ingredient", 4000),
        (u"Unit of measure", 5000),
        (u"Variable, fixed or lumpy", 5000),
        (u"Adj. price of Ingredient", 5000),
        (u"Cost", 5000),
        (u"% of Total Cost", 5000),
        (u"Cost per participant", 5000),
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
          maxnum = row_num
          for col_num in xrange(len(row)):
             if row[2] % 2 == 0:
                if col_num == 2 or col_num == 3:
                   ws.write(row_num, col_num, row[col_num], font_cent_22)
                elif col_num == 6:
                   ws.write(row_num, col_num, row[col_num], money_str_22)
                elif col_num == 8:
                   ws.write(row_num, col_num, row[col_num], money_p_22)
                elif col_num == 0 or col_num == 1  or col_num == 4 or col_num == 5  or col_num == 7 or col_num ==9:
                   ws.write(row_num, col_num, row[col_num], money_xf_22)
             else:
                if col_num == 2 or col_num == 3:
                   ws.write(row_num, col_num, row[col_num], font_cent)
                elif col_num == 6:
                   ws.write(row_num, col_num, row[col_num], money_str)
                elif col_num == 8:
                   ws.write(row_num, col_num, row[col_num], money_p)
                elif col_num == 0 or col_num == 1  or col_num == 4 or col_num == 5  or col_num == 7 or col_num ==9:
                   ws.write(row_num, col_num, row[col_num], money_xf)
    except:
       print "Error: unable to fetch data"
    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_dist(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=distribution_of_costs.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Distribution of Costs")
   
    row_num = 8
   
    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
    projectId = request.session['project_id']
    programId = request.session['program_id']

    cursor = database.cursor ()

    # Create the INSERT INTO sql query
    sql = """SELECT ingredient, yearQtyUsed, cost, cost_agency1_percent, cost_agency1, cost_agency2_percent, cost_agency2, cost_agency3_percent, cost_agency3, cost_agency4_percent, cost_agency4, cost_other_percent, cost_other, total_cost, total_agency1, total_agency2, total_agency3, total_agency4, total_other FROM costtool_distribution d, costtool_agencies a  WHERE d.programId = a.programId AND d.programId = %(programId)s"""

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    ag = m.Agencies.objects.get(programId = programId)
    
    columns = [
        (u"Ingredient", 8000),
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

    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 7
    font_style.pattern = pattern

    font_style2 = xlwt.XFStyle()
    font_style3 = xlwt.XFStyle()

    pattern = xlwt.Pattern() 
    # Create the Pattern 
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN 
    # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12 
    pattern.pattern_fore_colour = 22 
    # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on... style = xlwt.XFStyle() # Create the Pattern style.pattern = pattern # Add Pattern to Style worksheet.write(0, 0, 'Cell Contents', style) workbook.save('Excel_Workbook.xls')
    font_style3.pattern = pattern

    ws.write(0, 0, "Project:", font_style3)
    ws.write(0, 1, project.projectname, font_style3)
    ws.write(1, 0, "Type of Analysis:", font_style3)
    ws.write(1, 1, project.typeanalysis, font_style3)
    ws.write(2, 0, "Type of Cost:", font_style3)
    ws.write(2, 1, project.typeofcost, font_style3)
    ws.write(4, 0, "Name of the Program:", font_style3)
    ws.write(4, 1, program.progname, font_style3)
    ws.write(5, 0, "Short Name:", font_style3)
    ws.write(5, 1, program.progshortname, font_style3)

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    money_xf = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 7
    font_style.pattern = pattern
    money_xf.pattern = pattern

    money_xf.num_format_str = '$#,##0.00'
    money_xf2 = xlwt.XFStyle()
    pattern = xlwt.Pattern() 
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 22
    money_xf2.num_format_str = '$#,##0.00'
    money_xf2.pattern = pattern

    try:
    # Execute the SQL command
       cursor.execute(sql,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()

       for row in results:
          row_num += 1
          ingredient = row[0]
          yearQtyUsed = row[1]
          cost = row[2]
          cost_agency1_percent  = row[3]
          cost_agency1  = row[4]
          cost_agency2_percent = row[5]
          cost_agency2 =row[6]
          cost_agency3_percent = row[7]
          cost_agency3 = row[8]
          cost_agency4_percent = row[9]
          cost_agency4 = row[10]
          cost_other_percent = row[11]
          cost_other = row[12]
          total_cost = row[13]
          total_agency1 = row[14]
          total_agency2 = row[15]
          total_agency3 = row[16]
          total_agency4 = row[17]
          total_other = row[18]
          maxnum = row_num
          for col_num in xrange(len(row)):
             if col_num == 0 or col_num == 1 or col_num == 3 or col_num == 5 or col_num == 7 or col_num == 9 or col_num == 11:
                ws.write(row_num, col_num, row[col_num], font_style)
             elif col_num == 2 or col_num == 4 or col_num == 6 or col_num == 8 or col_num == 10 or col_num == 12:
                ws.write(row_num, col_num, row[col_num], money_xf)
       ws.write(maxnum + 3, 0, "Grand Total", money_xf2)
       ws.write(maxnum + 3, 1, total_cost, money_xf2)
       ws.write(maxnum + 4, 0, "Total Cost to "+ag.agency1, money_xf2)
       ws.write(maxnum + 4, 1, total_agency1, money_xf2)      
       ws.write(maxnum + 5, 0, "Total Cost to "+ag.agency2, money_xf2)
       ws.write(maxnum + 5, 1, total_agency2, money_xf2)
       ws.write(maxnum + 6, 0, "Total Cost to "+ag.agency3, money_xf2)
       ws.write(maxnum + 6, 1, total_agency3, money_xf2)
       ws.write(maxnum + 7, 0, "Total Cost to "+ag.agency4, money_xf2)
       ws.write(maxnum + 7, 1, total_agency4, money_xf2)
       ws.write(maxnum + 8, 0, "Total Cost to Other", money_xf2)
       ws.write(maxnum + 8, 1, total_other, money_xf2)
    except:
       print "Error: unable to fetch data"

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_trans(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=transfers_subsidies_fees.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Transfers, Subsidies and Fees")

    row_num = 8

    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
    projectId = request.session['project_id']
    programId = request.session['program_id']

    cursor = database.cursor ()

    # Create the INSERT INTO sql query
    sql = """SELECT grantName, grantYear, cost_agency1, cost_agency2, cost_agency3, cost_agency4, cost_other, total_cost, total_agency1, total_agency2, total_agency3, total_agency4, total_other, net_agency1, net_agency2, net_agency3, net_agency4, net_other FROM costtool_transfers d, costtool_agencies a  WHERE d.programId = a.programId AND d.programId = %(programId)s"""

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    ag = m.Agencies.objects.get(programId = programId)

    columns = [
        (u"Cash transfers, subsidies and fees", 8000),
        (u"Year", 5000),
        (u"Cost to "+ag.agency1, 5000),
        (u"Cost to "+ag.agency2, 5000),
        (u"Cost to "+ag.agency3, 5000),
        (u"Cost to "+ag.agency4, 5000),
        (u"Cost to Other", 5000)
    ]

    a = xlwt.Alignment()
    a.wrap = True
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style4 = xlwt.XFStyle()
    font_style4.font.bold = True
    font_style4.alignment = a
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 7
    font_style4.pattern = pattern

    font_style2 = xlwt.XFStyle()
    font_style3 = xlwt.XFStyle()

    pattern = xlwt.Pattern()
    # Create the Pattern
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    pattern.pattern_fore_colour = 22
    # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on... style = xlwt.XFStyle() # Create the Pattern style.pattern = pattern # Add Pattern to Style worksheet.write(0, 0, 'Cell Contents', style) workbook.save('Excel_Workbook.xls')
    font_style3.pattern = pattern

    ws.write(0, 0, "Project:", font_style3)
    ws.write(0, 1, project.projectname, font_style3)
    ws.write(1, 0, "Type of Analysis:", font_style3)
    ws.write(1, 1, project.typeanalysis, font_style3)
    ws.write(2, 0, "Type of Cost:", font_style3)
    ws.write(2, 1, project.typeofcost, font_style3)
    ws.write(4, 0, "Name of the Program:", font_style3)
    ws.write(4, 1, program.progname, font_style3)
    ws.write(5, 0, "Short Name:", font_style3)
    ws.write(5, 1, program.progshortname, font_style3)

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style4)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    money_xf = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 7
    font_style.pattern = pattern
    money_xf.pattern = pattern

    money_xf.num_format_str = '$#,##0.00'
    money_xf2 = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 22
    money_xf2.num_format_str = '$#,##0.00'
    money_xf2.pattern = pattern

    try:
    # Execute the SQL command
       cursor.execute(sql,{'programId' : programId})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()

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
             if col_num == 0 or col_num == 1:
                ws.write(row_num, col_num, row[col_num], font_style)
             elif col_num == 6 or col_num == 2 or col_num == 3 or col_num == 4 or col_num == 5:
                ws.write(row_num, col_num, row[col_num], money_xf)
       ws.write(maxnum + 3, 0, "Total Cost:", money_xf2)
       ws.write(maxnum + 3, 1, total_cost, money_xf2)

       ws.write(maxnum + 4, 0, "", font_style4)
       ws.write(maxnum + 5, 0, "Gross Cost", money_xf2)
       ws.write(maxnum + 6, 0, "Net Cost", money_xf2)

       ws.write(maxnum + 4, 1, "Cost to "+ag.agency1, font_style4)
       ws.write(maxnum + 5, 1, total_agency1, money_xf2)
       ws.write(maxnum + 6, 1, net_agency1, money_xf2)

       ws.write(maxnum + 4, 2, "Cost to "+ag.agency2, font_style4)
       ws.write(maxnum + 5, 2, total_agency2, money_xf2)
       ws.write(maxnum + 6, 2, net_agency2, money_xf2)

       ws.write(maxnum + 4, 3, "Cost to "+ag.agency3, font_style4)
       ws.write(maxnum + 5, 3, total_agency3, money_xf2)
       ws.write(maxnum + 6, 3, total_agency3, money_xf2)

       ws.write(maxnum + 4, 4, "Cost to "+ag.agency4, font_style4)
       ws.write(maxnum + 5, 4, total_agency4, money_xf2)
       ws.write(maxnum + 6, 4, net_agency4, money_xf2)

       ws.write(maxnum + 4, 5, "Cost to Other", font_style4)
       ws.write(maxnum + 5, 5, total_other, money_xf2)
       ws.write(maxnum + 6, 5, net_other, money_xf2)

    except:
       print "Error: unable to fetch data"

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
   
    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
    projectId = request.session['project_id']
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
       print "Error: unable to fetch data"

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

    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool") 
    projectId = request.session['project_id']
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
       print "Error: unable to fetch data"

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_cbcse_prices(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=cbcse_prices.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("CBCSE Prices")

    row_num = 0

    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
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
    pattern.pattern_fore_colour = 22
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = 22
    font_style.pattern = pattern2

    ab = xlwt.Alignment()
    ab.wrap = True
    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = 7
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
    sql = """SELECT category, ingredient, edLevel, sector, descriptionPrice, unitMeasurePrice, CONVERT(price, DECIMAL(10,2))  price, yearPrice, statePrice, areaPrice, sourcePriceData, urlPrice, lastChecked, nextCheckDate FROM costtool_prices WHERE priceProvider = 'CBCSE'"""

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

    except:
       print "Error: unable to fetch data"

    # disconnect from server
    database.close()
    wb.save(response)
    return response

def export_prices(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=my_prices.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("My Prices")

    row_num = 0

    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
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
    pattern.pattern_fore_colour = 22
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = 22
    font_style.pattern = pattern2

    ab = xlwt.Alignment()
    ab.wrap = True
    money_xf = xlwt.XFStyle()
    money_xf.num_format_str = '$#,##0.00'
    pattern3 = xlwt.Pattern()
    pattern3.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern3.pattern_fore_colour = 7
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
    sql = """SELECT category, ingredient, edLevel, sector, descriptionPrice, unitMeasurePrice, CONVERT(price, DECIMAL(10,2))  price, yearPrice, statePrice, areaPrice, sourcePriceData, urlPrice, lastChecked, nextCheckDate FROM costtool_prices WHERE priceProvider = %(priceProvider)s"""

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
       print "Error: unable to fetch data"

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

    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
    programId = request.session['program_id']
    projectId = request.session['project_id']

    project = m.Projects.objects.get(pk = projectId)
    program = m.Programs.objects.get(pk = programId)
    sett = m.Settings.objects.get(projectId = projectId)
    try:
       programdesc = m.ProgramDesc.objects.get(programId_id = programId)
       noofpart = programdesc.numberofparticipants
    except ObjectDoesNotExist:
       print 'does not exist'
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
    pattern.pattern_fore_colour = 22
    pattern2 = xlwt.Pattern()
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern2.pattern_fore_colour = 22
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
    pattern3.pattern_fore_colour = 7
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

    ws.write(7, 0, "Name of the Program", font_style5)
    ws.write(7, 1, "", font_style5)
    ws.write(7, 2, "", font_style5)
    ws.write(7, 3, program.progname, font_style4)
    ws.write(7, 4, "", font_style4)

    ws.write(8, 0, "Short Name", font_style3)
    ws.write(8, 1, "", font_style5)
    ws.write(8, 2, "", font_style5)
    ws.write(8, 3, program.progshortname, font_style4)
    ws.write(8, 4, "", font_style4)

    ws.write(9, 0, "Average number of participants", font_style3)
    ws.write(9, 1, "", font_style5)
    ws.write(9, 2, "", font_style5)
    ws.write(9, 3, str(noofpart), font_style4)
    ws.write(9, 4, "", font_style4)

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
          ws.write(12, 4, "", font_style4)

          ws.write(13, 0, 'Subjects / Participants', font_style3)
          ws.write(13, 1, "", font_style5)
          ws.write(13, 2, "", font_style5)
          ws.write(13, 3, row[1], font_style4)
          ws.write(13, 4, "", font_style4)

          ws.write(14, 0, 'Brief description', font_style3)
          ws.write(14, 1, "", font_style5)
          ws.write(14, 2, "", font_style5)
          ws.write(14, 3, row[2], font_style4)
          ws.write(14, 4, "", font_style4)

          ws.write(15, 0, 'Length of the program', font_style3)
          ws.write(15, 1, "", font_style5)
          ws.write(15, 2, "", font_style5)
          ws.write(15, 3, row[4], font_style4)
          ws.write(15, 4, "", font_style4)

          ws.write(16, 0, 'Number of years', font_style3)
          ws.write(16, 1, "", font_style5)
          ws.write(16, 2, "", font_style5)
          ws.write(16, 3, str(row[5]), font_style4)
          ws.write(16, 4, "", font_style4)

    except:
       print "Error: unable to fetch data"


    row_num = 19

    if effExists:
       ws.write(19, 0, "Source of effectiveness data", font_style3)
       ws.write(19, 1, "", font_style5)
       ws.write(19, 2, "", font_style5)
       ws.write(19, 3, eff.sourceeffectdata, font_style4)
       ws.write(19, 4, "", font_style4)

       ws.write(20, 0, "URL", font_style3)
       ws.write(20, 1, "", font_style5)
       ws.write(20, 2, "", font_style5)
       ws.write(20, 3, eff.url, font_style4)
       ws.write(20, 4, "", font_style4)

       ws.write(21, 0, "Description of effectiveness data", font_style3)
       ws.write(21, 1, "", font_style5)
       ws.write(21, 2, "", font_style5)
       ws.write(21, 3, eff.effectdescription, font_style4)
       ws.write(21, 4, "", font_style4)

       ws.write(22, 0, "Average effectiveness per participant", font_style3)
       ws.write(22, 1, "", font_style5)
       ws.write(22, 2, "", font_style5)
       ws.write(22, 3, eff.avgeffectperparticipant, font_style4)
       ws.write(22, 4, "", font_style4)

       ws.write(23, 0, "Unit of measure of effectiveness", font_style3)
       ws.write(23, 1, "", font_style5)
       ws.write(23, 2, "", font_style5)
       ws.write(23, 3, eff.unitmeasureeffect, font_style4)
       ws.write(23, 4, "", font_style4)

       ws.write(24, 0, "Is the estimator effect of the treatment statistically significant?", font_style3)
       ws.write(24, 1, "", font_style5)
       ws.write(24, 2, "", font_style5)
       ws.write(24, 3, eff.sigeffect, font_style4)
       ws.write(24, 4, "", font_style4)

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
       print "Error: unable to fetch data"


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
    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")
    #database = MySQLdb.connect (host="localhost", user = "root", passwd = "", db = "costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()
    
    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_prices (priceProvider,category,ingredient,edLevel,sector,descriptionPrice,unitMeasurePrice,price,yearPrice,statePrice,areaPrice,sourcePriceData,urlPrice,lastChecked,nextCheckDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

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
        # Assign values from each row
        values = (priceProvider,category,ingredient,edLevel,sector,descriptionPrice,unitMeasurePrice,price,yearPrice,statePrice,areaPrice,sourcePriceData,urlPrice,lastChecked,nextCheckDate)

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
    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")

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
    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")

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
    book = xlrd.open_workbook("/home/amritha/costtool/documents/Benefits.xlsx")
    sheet = book.sheet_by_name("Benefits")
    m.Benefits.objects.all().delete()

    # Establish a MySQL connection
    database = MySQLdb.connect (host="mysql.server", user = "amritha", passwd = "pass", charset="utf8", db = "amritha$costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_benefits (SectorBenefit, PersonnelBenefit, TypeRateBenefit,	YearBenefit, BenefitRate, SourceBenefitData, URLBenefitData, LastChecked, NextCheckDate) VALUES (%s, %s,%s, %s,%s, %s,%s, %s, %s)"""

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

        # Assign values from each row
        values = (SectorBenefit, PersonnelBenefit, TypeRateBenefit, YearBenefit, BenefitRate, SourceBenefitData, URLBenefitData, LastChecked, NextCheckDate)

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
            if objectexists:
               if (before_year != discountRateEstimates.yearEstimates) or (before_disc != discountRateEstimates.discountRateEstimates) or (before_state != discountRateEstimates.stateEstimates) or (before_area != discountRateEstimates.areaEstimates): 
                  result = calculations(project_id)
            return HttpResponseRedirect('/project/project_list.html')
        else:
            print setform.errors

    else:
        if objectexists:
           setform = SettingsForm(instance=setrec)
        else:
           setform = SettingsForm()

    return render_to_response(
            'project/add_settings.html',
            {'frm1': setform, 'projname':proj.projectname}, context)

def addedit_inf(request):
    InfFormSet = modelformset_factory(m.InflationIndices,form=InflationForm,extra=20)
    context = RequestContext(request)
    project_id = request.session['project_id']   
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
                if (i.indexCPI is None or i.indexCPI == '') and i.yearCPI is not None:
                   return render_to_response('project/inflation.html',{'infform':infform,'errtext': 'Please enter the CPI for the year you entered.'}) 
                try:
                   i.save()
                except IntegrityError as e:
                   return render_to_response('project/inflation.html',{'infform':infform,'errtext': 'Year must be an unique number.'})
                if i.id == oldRecId: 
                   print i.id
                   result = calculations(project_id)
             else:
                return render_to_response ('project/inflation.html',{'infform':infform,'errtext': 'You cannot delete the inflation index for the year you selected in Project Settings.'},context) 
          if request.session['priceExists'] == False:
             return HttpResponseRedirect('/project/programs/costs/'+request.session['price_id']+'/decideCat.html')
          else:
             return HttpResponseRedirect('/project/indices.html')
       else:
          form_errors = infform.errors
          return render_to_response ('project/inflation.html',{'infform':infform,'form.errors': form_errors},context)
    else:
        qset = m.InflationIndices.objects.filter(projectId=project_id)
        infform = InfFormSet(queryset=qset,prefix="infform")
    return render_to_response ('project/inflation.html',{'infform':infform},context)

def restore_inf(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    result = 0
    setrec = m.Settings.objects.get(projectId=project_id)
    latest = m.InflationIndices_orig.objects.all().latest('yearCPI')
    m.InflationIndices.objects.filter(projectId=project_id).delete()
    for e in m.InflationIndices_orig.objects.all():
        m.InflationIndices.objects.create(yearCPI = e.yearCPI,indexCPI = e.indexCPI, projectId=project_id)
    setrec.yearEstimates=latest.yearCPI
    setrec.save(update_fields=['yearEstimates'])
    result = calculations(project_id)
    return HttpResponseRedirect('/project/indices.html')

def addedit_geo(request):
    GeoFormSet = modelformset_factory(m.GeographicalIndices,form=GeographicalForm,extra=20)
    context = RequestContext(request)
    project_id = request.session['project_id']
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
                try:
                   i.save()
                except IntegrityError as e:
                   return render_to_response('project/geo.html',{'geoform':geoform,'errtext': 'The state / area combination must be unique in Geographical Indices.'})
                if i.id == oldRecId: 
                   result = calculations(project_id)
             else:
                return render_to_response ('project/geo.html',{'geoform':geoform,'errtext': 'You cannot delete the geographical index for the state and area  you selected in Project Settings.'},context)    
          return HttpResponseRedirect('/project/indices.html')
       else:
          form_errors = geoform.errors
          return render_to_response ('project/geo.html',{'geoform':geoform,'form.errors': form_errors},context)
    else:
       qset = m.GeographicalIndices.objects.filter(projectId=project_id)                                                               
       geoform = GeoFormSet(queryset=qset,prefix="geoform")

    return render_to_response ('project/geo.html',{'geoform':geoform},context) 

def restore_geo(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    result = 0
    setrec = m.Settings.objects.get(projectId=project_id)
    m.GeographicalIndices.objects.filter(projectId=project_id).delete()
    for e in m.GeographicalIndices_orig.objects.all():
        m.GeographicalIndices.objects.create(stateIndex = e.stateIndex,areaIndex = e.areaIndex, geoIndex = e.geoIndex, projectId=project_id)
    setrec.stateEstimates='All states' 
    setrec.areaEstimates='All areas'
    setrec.save(update_fields=['stateEstimates','areaEstimates'])
    result = calculations(project_id)
    return HttpResponseRedirect('/project/indices.html')
