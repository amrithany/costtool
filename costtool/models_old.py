#commenting out everything

from django.db import models as m
from django.contrib.auth.models import User
import datetime 

from django.core.files.storage import FileSystemStorage
class Videos(m.Model):
   videoName = m.CharField(max_length=256, null=True, blank=True)
   link = m.CharField(max_length=256, null=True, blank=True)
   vDate = m.DateTimeField(default=datetime.datetime.now)

   def __unicode__(self):
       return self.id

class MyFileStorage(FileSystemStorage):
    # This method is actually defined in Storage
    def get_available_name(self, name):
        self.delete(name)
        return name

class FileUpload(m.Model):
    docfile = m.FileField(storage=MyFileStorage(),upload_to='documents/temp',null=True, blank=True)
    docName = m.CharField(max_length=256, null=True, blank=True)
    docDate = m.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.id


class About(m.Model):
    web = m.CharField(max_length=256)
    email = m.CharField(max_length=256)
    sendemail = m.CharField(max_length=256)

    def __unicode__(self):
        return self.web

class Projects(m.Model):
    projectname = m.CharField(max_length=256)
    typeanalysis = m.CharField(max_length=256)
    typeofcost = m.CharField(max_length=256) 
    created_at = m.DateTimeField(default=datetime.datetime.now)
    updated_at = m.DateTimeField()
    user = m.CharField(max_length=200,null=True, blank=True)
    shared =  m.CharField(max_length=1,null=True, blank=True)
    def __unicode__(self):
        return unicode(self.projectname) 

class SharedProj(m.Model):
     projectid = m.IntegerField(null=True,blank=True)
     shared_user =  m.CharField(max_length=200,null=True, blank=True)
     shared_date = m.DateTimeField(null=True, blank=True)

     def __unicode__(self):
         return self.id

class Settings(m.Model):
    discountRateEstimates = m.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)
    yearEstimates = m.IntegerField(null=True,blank=True)
    stateEstimates = m.CharField(max_length=2000,null=True, blank=True)
    areaEstimates = m.CharField(max_length=2000,null=True, blank=True)
    selectDatabase = m.TextField(max_length=256,null=True, blank=True)
    limitEdn = m.TextField(max_length=256,null=True, blank=True)
    limitSector = m.TextField(max_length=2000,null=True, blank=True)
    limitYear = m.TextField(max_length=2000,null=True, blank=True)
    hrsCalendarYr = m.IntegerField(null=True,blank=True)
    hrsAcademicYr = m.IntegerField(null=True,blank=True)
    hrsHigherEdn = m.IntegerField(null=True,blank=True)
    projectId = m.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return self.discountRateEstimates

class GeographicalIndices(m.Model):
    stateIndex = m.CharField(max_length=250,null=True, blank=True)
    areaIndex  = m.CharField(max_length=250,null=True, blank=True)
    geoIndex = m.CharField(max_length=100,null=True,blank=True)
    projectId = m.IntegerField(null=True,blank=True)

    class Meta:
       unique_together = ("stateIndex","areaIndex","projectId")

    def __unicode__(self):
        return self.stateIndex

class GeographicalIndices_orig(m.Model):
    stateIndex = m.CharField(max_length=250,null=True, blank=True)
    areaIndex  = m.CharField(max_length=250,null=True, blank=True)
    #geoIndex = m.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)
    geoIndex = m.CharField(max_length=100,null=True,blank=True)

    def __unicode__(self):
        return self.stateIndex

class InflationIndices(m.Model):
    yearCPI  = m.CharField(max_length=10,null=True, blank=True)
    indexCPI = m.CharField(max_length=10,null=True,blank=True)
    projectId = m.IntegerField(null=True,blank=True)

    #class Meta:
       #unique_together = ("yearCPI","projectId")

    def __unicode__(self):
        return unicode(self.yearCPI)

class InflationIndices_orig(m.Model):
    yearCPI  = m.IntegerField(null=True, blank=True)
    #indexCPI = m.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)
    indexCPI = m.CharField(max_length=10,null=True,blank=True)

    def __unicode__(self):
        return self.yearCPI

class Benefits(m.Model):
    SectorBenefit = m.CharField(max_length=100,null=True,blank=True)	
    PersonnelBenefit = m.CharField(max_length=256,null=True,blank=True)	
    TypeRateBenefit = m.CharField(max_length=256,null=True,blank=True)	
    YearBenefit = m.CharField(max_length=100,null=True,blank=True)	
    BenefitRate = m.CharField(max_length=100,null=True,blank=True)	
    SourceBenefitData = m.CharField(max_length=100,null=True,blank=True)	
    URLBenefitData = m.CharField(max_length=256,null=True,blank=True)
    LastChecked = m.CharField(max_length=2000,null=True, blank=True)
    NextCheckDate = m.CharField(max_length=256,null=True, blank=True)
    permissionDetails = m.CharField(max_length=256,null=True, blank=True)

    def __unicode__(self):
        return self.SectorBenefit

class Programs(m.Model):
    progname = m.CharField(max_length=256)
    progshortname = m.CharField(max_length=256)
    projectId = m.IntegerField(null=True,blank=True)
    created_at = m.DateTimeField(default=datetime.datetime.now)
    updated_at = m.DateTimeField()

    def __unicode__(self):
        return self.progname

class ProgramDesc(m.Model):
    progobjective = m.CharField(max_length=2000,null=True, blank=True)
    progsubjects = m.CharField(max_length=2000,null=True, blank=True)
    progdescription = m.CharField(max_length=2000,null=True, blank=True)
    numberofparticipants = m.DecimalField(max_digits=12,decimal_places=2, null=True, blank=True)
    lengthofprogram = m.CharField(max_length=256)
    numberofyears = m.IntegerField(null=True, blank=True)
    #changed
    programId = m.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.id

class ParticipantsPerYear(m.Model):
    yearnumber = m.IntegerField(null=True, blank=True)
    noofparticipants = m.DecimalField(max_digits=14,decimal_places=2, null=True, blank=True)
    programdescId = m.ForeignKey(ProgramDesc,on_delete=m.CASCADE)

    def __unicode__(self):
        return self.yearnumber 

class Effectiveness(m.Model):
    sourceeffectdata = m.CharField(max_length=2000,null=True, blank=True)
    url = m.CharField(max_length=256,null=True, blank=True)
    effectdescription = m.CharField(max_length=2000,null=True, blank=True)
    avgeffectperparticipant = m.CharField(max_length=256,null=True, blank=True)
    unitmeasureeffect = m.CharField(max_length=2000,null=True, blank=True)
    sigeffect = m.CharField(max_length=10,null=True, blank=True)
    #programId = m.OneToOneField(Programs)
    #changed
    programId = m.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.sourceeffectdata   

class Distribution(m.Model):
    ingredient = m.CharField(max_length=2000,null=True, blank=True)
    cost = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    yearQtyUsed = m.IntegerField(null=True,blank=True)
    cost_agency1_percent = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency1 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency2_percent = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency2 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency3_percent = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency3 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency4_percent = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency4 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_other_percent = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_other = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    programId = m.IntegerField(null=True,blank=True)
    ingredientId = m.IntegerField(null=True,blank=True)
 
    def __unicode__(self):
        return self.ingredient

class Agencies(m.Model):
    agency1 = m.CharField(max_length=256,null=True, blank=True)
    agency2 = m.CharField(max_length=256,null=True, blank=True)
    agency3 = m.CharField(max_length=256,null=True, blank=True)
    agency4 = m.CharField(max_length=256,null=True, blank=True)
    total_agency1 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    total_agency2 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    total_agency3 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    total_agency4 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True) 
    total_other = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    net_agency1 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    net_agency2 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    net_agency3 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    net_agency4 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    net_other = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    total_cost = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    programId = m.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return self.agency1

class Transfers(m.Model):
    grantFrom = m.CharField(max_length=256,null=True, blank=True)
    grantTo = m.CharField(max_length=256,null=True, blank=True)
    grantAmount = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    grantYear = m.IntegerField(null=True,blank=True)
    perparticipantOrTotal = m.CharField(max_length=20,null=True, blank=True)
    grantName = m.CharField(max_length=256,null=True, blank=True)
    total_amount = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    averageno = m.DecimalField(max_digits=6,decimal_places=2,null=True, blank=True)
    cost_agency1 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency2 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency3 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_agency4 = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    cost_other = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    programId = m.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return self.grantFrom

class UserProfile(m.Model):
    #user = m.OneToOneField(User)
    #changed
    user = m.CharField(blank=True, null=True)
    organisation = m.CharField(max_length=2000)
    position = m.CharField(max_length=2000)
    licenseSigned = m.CharField(max_length=3)
    signed_at = m.DateField('Date')

    def __unicode__(self):
        return self.user.username

class Login(m.Model):
    user = m.CharField(max_length=200)
    oldemail = m.CharField(max_length=200, null=True, blank=True)
    email = m.CharField(max_length=200, null=True, blank=True)
    emailagain = m.CharField(max_length=200, null=True, blank=True)
    oldpassword = m.CharField(max_length=200, null=True, blank=True)
    password = m.CharField(max_length=200)
    passwordagain = m.CharField(max_length=200)
    firstName = m.CharField(max_length=200, null=True, blank=True)
    lastName = m.CharField(max_length=200, null=True, blank=True)
    addressline1 =  m.CharField(max_length=2000, null=True, blank=True)
    addressline2 = m.CharField(max_length=2000, null=True, blank=True)
    city = m.CharField(max_length=200, null=True, blank=True)
    state = m.CharField(max_length=200, null=True, blank=True)
    zip = m.CharField(max_length=200, null=True, blank=True)
    country = m.CharField(max_length=200, null=True, blank=True)
    phone = m.BigIntegerField(null=True,blank=True)
    organisation = m.CharField(max_length=2000,null=True, blank=True)
    type_of_org = m.CharField(max_length=2000,null=True, blank=True) 
    other_org = m.CharField(max_length=2000,null=True, blank=True) 
    position = m.CharField(max_length=2000,null=True, blank=True)
    other_pos = m.CharField(max_length=2000,null=True, blank=True)
    publicOrPrivate = m.CharField(max_length=8,null=True, blank=True) 
    licenseSigned = m.CharField(max_length=3,null=True, blank=True)
    startDate = m.DateField(default=datetime.datetime.now,null=True, blank=True)
    endDate = m.DateField(null=True, blank=True)
    lastLogin = m.DateField(null=True, blank=True)
    timesLoggedin = m.IntegerField(null=True,blank=True) 

    def __unicode__(self):
        return self.user

class Prices(m.Model):
    priceProvider = m.CharField(max_length=256,null=True, blank=True)
    category = m.CharField(max_length=256,null=True, blank=True)
    ingredient = m.CharField(max_length=2000,null=True, blank=True)	
    edLevel = m.CharField(max_length=256,null=True, blank=True)	
    sector = m.CharField(max_length=256,null=True, blank=True)
    descriptionPrice = m.CharField(max_length=2000,null=True, blank=True)	
    unitMeasurePrice = m.CharField(max_length=256,null=True, blank=True)	
    price = m.CharField(max_length=100,null=True, blank=True)	
    yearPrice = m.CharField(max_length=100,null=True, blank=True)	
    statePrice = m.CharField(max_length=256,null=True, blank=True)	
    areaPrice = m.CharField(max_length=256,null=True, blank=True)	
    sourcePriceData = m.CharField(max_length=256,null=True, blank=True)	
    urlPrice = m.CharField(max_length=2000,null=True, blank=True)	
    lastChecked = m.CharField(max_length=2000,null=True, blank=True)	
    nextCheckDate = m.CharField(max_length=256,null=True, blank=True)
    permissionDetails = m.CharField(max_length=256,null=True, blank=True)

    def __unicode__(self):
        return unicode(self.priceProvider)

class Ingredients(m.Model):
    category = m.CharField(max_length=256,null=True, blank=True)
    ingredient = m.CharField(max_length=2000,null=True, blank=True)
    edLevel = m.CharField(max_length=256,null=True, blank=True)
    sector = m.CharField(max_length=256,null=True, blank=True)
    unitMeasurePrice = m.CharField(max_length=256,null=True, blank=True)
    price = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    sourcePriceData = m.CharField(max_length=256,null=True, blank=True)
    urlPrice = m.CharField(max_length=2000,null=True, blank=True)
    hrsCalendarYr = m.IntegerField(null=True,blank=True)
    hrsAcademicYr = m.IntegerField(null=True,blank=True)
    hrsHigherEdn = m.IntegerField(null=True,blank=True)
    newMeasure = m.CharField(max_length=256,null=True, blank=True)
    newMeasureVol = m.CharField(max_length=256,null=True, blank=True)
    newMeasureLen = m.CharField(max_length=256,null=True, blank=True)
    newMeasureTime = m.CharField(max_length=256,null=True, blank=True)
    convertedPrice = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    lifetimeAsset = m.CharField(max_length=2000,null=True, blank=True)
    interestRate = m.CharField(max_length=2000,null=True, blank=True)
    priceAdjAmortization = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    benefitRate = m.CharField(max_length=2000,null=True, blank=True)
    SourceBenefitData = m.CharField(max_length=100,null=True,blank=True)
    YearBenefit = m.CharField(max_length=100,null=True,blank=True)
    priceAdjBenefits = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    percentageofUsage  = m.DecimalField(max_digits=19,decimal_places=9,null=True,blank=True)
    yearPrice = m.IntegerField(null=True, blank=True)
    statePrice = m.CharField(max_length=256,null=True, blank=True)
    areaPrice = m.CharField(max_length=256,null=True, blank=True)
    geoIndex = m.CharField(max_length=500,null=True, blank=True)
    indexCPI = m.CharField(max_length=500,null=True, blank=True)  
    yearQtyUsed = m.IntegerField(null=True,blank=True)
    quantityUsed = m.CharField(max_length=15,null=True,blank=True)
    variableFixed = m.CharField(max_length=10,null=True,blank=True)
    priceAdjInflation = m.CharField(max_length=2000,null=True, blank=True)  
    priceAdjGeographicalArea = m.CharField(max_length=500,null=True, blank=True)  
    priceNetPresentValue = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    adjPricePerIngredient = m.CharField(max_length=500,null=True, blank=True)  
    costPerIngredient = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    totalCost = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    averageCost = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)                    
    effRatio = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)            
    percentageCost = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    costPerParticipant = m.DecimalField(max_digits=12,decimal_places=3,null=True,blank=True)
    programId = m.IntegerField(null=True,blank=True)
    notes = m.CharField(max_length=2000,null=True, blank=True)

    class Meta:
        ordering = ['ingredient','category']

    def __unicode__(self):
        return unicode(self.id)
