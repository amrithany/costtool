from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from costtool.models import Login, Benefits,UserProfile, Projects, Programs, ProgramDesc, ParticipantsPerYear, Effectiveness, Prices, Settings,GeographicalIndices, GeographicalIndices_orig, InflationIndices, InflationIndices_orig, Ingredients
from crispy_forms.bootstrap import *
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('organisation','position','licenseSigned','signed_at')

class LoginForm(forms.ModelForm):
    user = forms.CharField(label="User Name")
    password = forms.CharField(label="Password",widget=forms.PasswordInput)

    class Meta:
        model = Login
        fields = ('user', 'password')

class RegisterForm(forms.ModelForm):
   user = forms.CharField(label="User Name")
   email = forms.CharField(required=False, label="Email address")
   password = forms.CharField(label="Password",widget=forms.PasswordInput)
   organisation = forms.CharField(required=False, label="Organization")
   position = forms.CharField(required=False, label="Position")
   publicOrPrivate = forms.ChoiceField(choices=(('Public','Public Institution'), ('Private','Private Institution')),label="For the purpose of the license agreement, are you signing as a public institution or a private institution (including individuals)?")
   
   class Meta:
      model = Login
      fields = ('user', 'email','password','organisation','position','publicOrPrivate')

class License(forms.ModelForm):
   pdf = forms.CharField(required=False,  widget=forms.Textarea(), label="", initial="This is a test CBCSE costtool kit license agreement.")
   licenseSigned = forms.ChoiceField(widget=forms.RadioSelect, choices=(('Yes', 'Yes, I agree to the terms.'),('No','No, please log me out')), label="")

   class Meta:
       model = Login
       fields = ('pdf','licenseSigned',)

   def __init__(self, *args, **kwargs):
      super(License, self).__init__(*args, **kwargs)
      self.fields['pdf'].widget.attrs['readonly'] = True

class ProjectsForm(forms.ModelForm):
    projectname  = forms.CharField(label="Project Name:",error_messages = {'required': "The Project Name is required"})
    typeanalysis  = forms.ChoiceField(choices=(('Cost Analysis','Cost Analysis'),
                                               ('Cost-Effectiveness Analysis', 'Cost-Effectiveness Analysis')), label="Type of Analysis:")
    typeofcost = forms.ChoiceField(choices=(('Total Costs', 'Total Costs'), ('Incremental Costs', 'Incremental Costs')),label="Are you considering?")

    class Meta:
        model = Projects
        fields = ('id','projectname','typeanalysis','typeofcost')

    def clean_projectname(self):
        projectname = self.cleaned_data['projectname']
        try:
           Projects.objects.get(projectname = self.cleaned_data['projectname'])
           raise forms.ValidationError("This project name is already taken.  Please enter an unique name.")
        except Projects.DoesNotExist:
           pass    
           return projectname

class SettingsForm(forms.ModelForm):
    choicesEdlevel = (('Select','Select all'), ('General','General'), ('Grades PK', 'Grades PK'), ('Grades K-6','Grades K-6'), ('Grades 6-8','Grades 6-8'),('Grades 9-12','Grades 9-12'),('Grades K-12', 'Grades K-12'), ('PostSecondary', 'PostSecondary'))
    choicesSector = (('Select', 'Select all'),('Any', 'Any sector'),('Private','Private'),('Public','Public'))
    choicesYear = (('All', 'See prices from all years'),('recent','See most recent prices only'))
    yrquery = InflationIndices.objects.values_list('yearCPI', flat=True).distinct()
    yrquery_choices =  [(id, id) for id in yrquery]
    iquery = GeographicalIndices.objects.values_list('stateIndex', flat=True).distinct()
    iquery_choices =  [(id, id) for id in iquery]
    areaquery = GeographicalIndices.objects.values_list('areaIndex', flat=True).distinct()
    areaquery_choices =  [(id, id) for id in areaquery]
    discountRateEstimates = forms.DecimalField(required=False,max_digits=6,decimal_places=2,min_value=0,max_value=100,initial=3,label="Discount Rate for programs in which costs are incurred over multiple years (input number from 0 to 100):")
    yearEstimates = forms.ChoiceField(yrquery_choices, required=False, widget=forms.Select(),label="In which year do you want to express costs?")
    stateEstimates  = forms.ChoiceField(iquery_choices, required=False, widget=forms.Select(), label="In which geographical location do you want to express costs?")
    areaEstimates = forms.ChoiceField(areaquery_choices, required=False, widget=forms.Select(), label="")
    selectDatabase = forms.MultipleChoiceField(choices=(('CBCSE','CBCSE Database of Educational Resource Prices'),('My','Database MyPrices')),required=False,label="Select which database of prices you will use (can select more than one):", widget=forms.CheckboxSelectMultiple())
    limitEdn = forms.MultipleChoiceField(choices=choicesEdlevel,required=False,label="<strong>EDUCATIONAL LEVEL</strong>", widget=forms.CheckboxSelectMultiple())
    limitSector = forms.MultipleChoiceField(choices=choicesSector,required=False,label="<strong>SECTOR</strong>",widget=forms.CheckboxSelectMultiple())
    limitYear = forms.MultipleChoiceField(choices=choicesYear,required=False,label="<strong>YEAR</strong>",widget=forms.CheckboxSelectMultiple())
    hrsCalendarYr = forms.IntegerField(required=False,initial=2080,min_value=0,label="Number of hours in the calendar year: The calendar year consists of 2,080 working hours (52 weeks, 5 days a week, 8 hrs a day) according to the U.S. Bureau of Labor Statistics. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the calendar year in the following cell:")
    hrsAcademicYr = forms.IntegerField(required=False,initial=1440,min_value=0,label="Number of hours in the K-12 academic year: The academic year consists of 1,440 working hours (36 weeks, 5 days a week, 8 hrs a day) according to CBCSE. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the K-12 academic year in the following cell:")
    hrsHigherEdn = forms.IntegerField(required=False,initial=1560,min_value=0,label="Number of hours in the higher education academic year: The academic year consists of 1,560 working hours (39 weeks, 5 days a week, 8 hrs a day) according to CBCSE. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the higher education academic year in the following cell:")

    class Meta:
        model = Settings
        fields = ('discountRateEstimates','yearEstimates','stateEstimates','areaEstimates', 'selectDatabase','limitEdn','limitSector','limitYear','hrsCalendarYr','hrsAcademicYr','hrsHigherEdn')

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        instance = getattr(self, 'instance', None)
        yrquery = InflationIndices.objects.filter(projectId = instance.projectId).values_list('yearCPI', flat=True).distinct()
        yrquery_choices = [(id, id) for id in yrquery]  
        self.fields['yearEstimates']=forms.ChoiceField(choices=yrquery_choices, required=False, widget=forms.Select(),label="In which year do you want to express costs?") 
        iquery = GeographicalIndices.objects.filter(projectId = instance.projectId).values_list('stateIndex', flat=True).distinct()
        iquery_choices =  [(id, id) for id in iquery]
        areaquery = GeographicalIndices.objects.filter(projectId = instance.projectId).values_list('areaIndex', flat=True).distinct()
        areaquery_choices =  [(id, id) for id in areaquery]
        self.fields['stateEstimates']  = forms.ChoiceField(choices=iquery_choices, required=False, widget=forms.Select(), label="In which geographical location do you want to express costs?")        
        self.fields['areaEstimates'] = forms.ChoiceField(choices=areaquery_choices, required=False, widget=forms.Select(), label="")
        if not instance.pk:
            self.fields['selectDatabase'].widget.attrs={"checked":""}
            self.fields['limitEdn'].widget.attrs={"checked":""}
            self.fields['limitSector'].widget.attrs={"checked":""}
            self.fields['limitYear'].widget.attrs={"checked":"All"}
        self.fields['yearEstimates'].empty_label = None
        self.fields['stateEstimates'].empty_label = None
        self.fields['areaEstimates'].empty_label = None 
        self.helper.layout = Layout(
             HTML("""<hr><p><strong>DEFINE SETUP</strong></p>"""),
             'discountRateEstimates',
             'yearEstimates',
             'stateEstimates',  
             'areaEstimates',   
            Button('EditIndices', 'Option to edit price indices', css_class='btn-primary',onclick="gotofunc();"),
            HTML("""<hr><p><strong>DEFINE PRICE SEARCH</strong></p>"""),
            'selectDatabase',
            HTML("""<br><p>Limit database of prices by the following criteria:</p>"""), 
            Div(
                Row('limitEdn',   css_class='span6'),
                Row('limitSector', css_class='span6'),
                Row('limitYear',   css_class='span6'),
            css_class='row-fluid'),
            HTML("""<hr><p><strong>DEFINE DEFAULT VALUES FOR WAGE CONVERTER</strong></p>"""),
            'hrsCalendarYr',
            'hrsAcademicYr',
            'hrsHigherEdn',
        )

        self.helper.form_tag = False

class GeographicalForm(forms.ModelForm):
    stateIndex = forms.CharField(required=False,label="State")
    areaIndex  = forms.CharField(required=False,label="Area")
    #geoIndex = forms.DecimalField(max_digits=8,decimal_places=3,required=False,label="Index")
    geoIndex = forms.CharField(required=False,label="Index")

    class Meta:
        model = GeographicalIndices
        unique_together = ["stateIndex", "areaIndex"]
        fields = ('stateIndex', 'areaIndex','geoIndex')

    def __init__(self, *args, **kwargs):
        super(GeographicalForm, self).__init__(*args, **kwargs)
        self.queryset = GeographicalIndices.objects.all()

class GeographicalForm_orig(forms.ModelForm):
    stateIndex = forms.CharField(required=False,label="State")
    areaIndex  = forms.CharField(required=False,label="Area")
    geoIndex = forms.CharField(required=False,label="Index")

    class Meta:
        model = GeographicalIndices
        fields = ('stateIndex', 'areaIndex','geoIndex')

    def __init__(self, *args, **kwargs):
        super(GeographicalForm_orig, self).__init__(*args, **kwargs)
        self.queryset = GeographicalIndices_orig.objects.all()

class InflationForm(forms.ModelForm):
    yearCPI  = forms.CharField(required=False,label="Year")
    indexCPI = forms.CharField(required=False,label="CPI")

    class Meta:
        model = InflationIndices
        fields = ('yearCPI','indexCPI')

    def __init__(self, *args, **kwargs):
        super(InflationForm, self).__init__(*args, **kwargs)
        self.queryset = InflationIndices.objects.all()

    def clean_yearCPI(self):        
        yearCPI = self.cleaned_data['yearCPI']
        if (yearCPI == '' or int(yearCPI) > 9999) or (int(yearCPI) < 1000):
           raise forms.ValidationError("Years must be entered as four-digit positive numbers.")
        else:
           pass   
           return yearCPI

class InflationForm_orig(forms.ModelForm):
    yearCPI  = forms.IntegerField(required=False,label="Year")
    indexCPI = forms.DecimalField(max_digits=8,decimal_places=3,required=False,label="CPI")

    class Meta:
        model = InflationIndices_orig
        fields = ('yearCPI','indexCPI')

    def __init__(self, *args, **kwargs):
        super(InflationForm_orig, self).__init__(*args, **kwargs)
        self.queryset = InflationIndices_orig.objects.all()

class ProgramsForm(forms.ModelForm):
    progname = forms.CharField(label="Name of the program:",error_messages = {'required': "The Program Name is required"})
    progshortname = forms.CharField(label="Short name (this is used in reports):",error_messages = {'required': "The Short Name is required"})

    class Meta:
        model = Programs
        exclude = ['projectId']
        fields = ('progname','progshortname')

class ProgramDescForm(forms.ModelForm):
    progobjective = forms.CharField(required=False, widget=forms.Textarea(), label="Objective of the program:")
    progsubjects = forms.CharField(required=False, widget=forms.Textarea(), label="Subjects / Participants:")
    progdescription = forms.CharField(required=False, widget=forms.Textarea(), label="Brief description:")
    numberofparticipants = forms.DecimalField(required=False, max_digits=6,decimal_places=2,min_value=0.1,label="Average number of participants:")
    lengthofprogram = forms.ChoiceField(required=False,choices=(('One year or less', 'One year or less'), ('More than one year', 'More than one year')),initial = 'One year or less',label="Length of the program (once you save this page, you cannot change this selection):")

    class Meta:
        model = ProgramDesc
        exclude = ['programId']
        fields = ('progobjective','progsubjects','progdescription', 'lengthofprogram', 'numberofparticipants')
        #fields = ('progobjective','progsubjects','progdescription', 'lengthofprogram')       

    def __init__(self, *args, **kwargs):
        super(ProgramDescForm, self).__init__(*args, **kwargs)
        self.lengthofprogram = 'One year or less' 
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
             Field('progobjective', rows="4", cols="100", css_class='input-xlarge'),
             Field('progsubjects', rows="4", cols="100", css_class='input-xlarge'), 
             Field('progdescription', rows="4", cols="100", css_class='input-xlarge'),
             'lengthofprogram',   
            Div(
                Row('numberofparticipants',   css_class='span6'),
                Row(HTML("""<font color="blue">This number will be used to calculate the  average costs of this program per participant.</font><br><br>""")),
                css_class='row-fluid'),
        )

        self.helper.form_tag = False

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['lengthofprogram'].widget.attrs['disabled'] = True       
        self.fields['progobjective'].widget.attrs['cols'] = 200

    def clean_lengthofprogram(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.lengthofprogram
        else: 
            return self.cleaned_data['lengthofprogram']

class ParticipantsForm(forms.ModelForm):
    yearnumber = forms.CharField(required=False,widget = forms.TextInput(attrs={'readonly':'readonly'}), label="Year:")
    noofparticipants = forms.DecimalField(required=False,max_digits=6,decimal_places=2, min_value=0.01, label="Number of participants per year:")

    class Meta:
        model = ParticipantsPerYear
        exclude = ['programId']
        fields = ('yearnumber', 'noofparticipants')

    def __init__(self, *args, **kwargs):
        super(ParticipantsForm, self).__init__(*args, **kwargs)

    def clean_yearnumber(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.yearnumber
        else:
            return self.cleaned_data['yearnumber']

class EffectForm(forms.ModelForm):
    sourceeffectdata = forms.CharField(required=False, widget=forms.Textarea(), label = "Source of effectiveness data:")
    url = forms.URLField(required=False, label = "URL (The URL must start with http://www.):")
    effectdescription = forms.CharField(required=False, widget=forms.Textarea(), label = "Description of effectiveness data:")
    avgeffectperparticipant = forms.DecimalField(max_digits=6,decimal_places=2,label = "Average effectiveness per participant:")
    unitmeasureeffect = forms.CharField(required=False, label = "What is the unit of this measure of effectiveness?")
    sigeffect = forms.ChoiceField(required=False, choices=(('Sig.' ,'Sig.'), ('Not Sig.','Not Sig.')), label = "Is the estimator effect of the treatment statistically significant?")

    class Meta:
        model = Effectiveness
        exclude = ['programId']
        fields = ('sourceeffectdata', 'url', 'effectdescription', 'avgeffectperparticipant','unitmeasureeffect', 'sigeffect') 

    def __init__(self, *args, **kwargs):
        super(EffectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('sourceeffectdata', rows="4", cols="100", css_class='input-xlarge'),
            'url',
            Field('effectdescription', rows="4", cols="100", css_class='input-xlarge'),
          )
        self.helper.form_tag = False

class IngredientsFullForm(forms.ModelForm):
    ingredient  = forms.CharField(required=False,label="Ingredient Name")
    yearQtyUsed = forms.IntegerField(required=False, label="Year in which quantity is used")
    quantityUsed  = forms.DecimalField(required=False,label="Quantity of ingredient")
    newMeasure = forms.CharField(required=False, label="Unit of Measure")
    variableFixed = forms.ChoiceField(choices=(('Fixed','Fixed'),('Variable','Variable'),('Lumpy','Lumpy')),required=False,label="Variable, Fixed or Lumpy")
    adjPricePerIngredient = forms.DecimalField(required=False, label="Adj. price of ingredient")
    costPerIngredient = forms.DecimalField(required=False,label="Cost")
    percentageCost = forms.DecimalField(required=False, label="% of Total Cost")
    costPerParticipant = forms.DecimalField(required=False, label="Cost per Participant")
    totalCost = forms.DecimalField(required=False)    
    catquery = Prices.objects.values_list('category', flat=True).distinct()
    catquery_choices =  [('All','All')] +[(id, id) for id in catquery]
    category = forms.ChoiceField(choices=catquery_choices, initial="All", required=False, widget=forms.Select(),label="Category")
    edLevel = forms.ChoiceField(required=False, label="Education level to be served")
    sector = forms.ChoiceField(required=False, label="Sector")
    unitMeasurePrice = forms.CharField(required=False, label="Original Unit of Measure")
    price = forms.CharField(required=False,label="Original Price")
    lifetimeAsset = forms.IntegerField(required=False,label="Lifetime of the asset" )
    interestRate = forms.DecimalField(required=False, label="Interest rate")
    yearPrice = forms.CharField(required=False, label="Year Price")
    statePrice  = forms.CharField(required=False, label="State Price")
    areaPrice = forms.CharField(required=False, label="Area Price")
    sourcePriceData = forms.CharField(required=False,label="Source")
    urlPrice = forms.CharField(required=False)
    hrsCalendarYr = forms.IntegerField(required=False)
    hrsAcademicYr = forms.IntegerField(required=False)
    hrsHigherEdn = forms.IntegerField(required=False)
    newMeasureVol = forms.CharField(required=False)
    newMeasureLen = forms.CharField(required=False)
    newMeasureTime = forms.CharField(required=False)
    convertedPrice = forms.DecimalField(required=False, label="Price after conversion")
    priceAdjAmortization = forms.DecimalField(required=False, label="PriceAdjAmortization" )
    benefitRate = forms.CharField(required=False, label="Benefit Rate")
    SourceBenefitData = forms.CharField(required=False)
    YearBenefit = forms.CharField(required=False)
    priceAdjBenefits = forms.DecimalField(required=False,label="PriceAdjBenefits")
    percentageofUsage  = forms.IntegerField(required=False,label="Percentage of Usage")
    geoIndex = forms.CharField(required=False,label="Geographical Index of State Price & Area Price")
    indexCPI = forms.CharField(required=False,label="IndexCPI of Year Price")
    priceAdjInflation = forms.CharField(required=False, label="PriceAdjInflation")
    priceAdjGeographicalArea = forms.CharField(required=False, label="PriceAdjGeographicalArea")
    priceNetPresentValue = forms.DecimalField(required=False, label="PriceAdjAmortization")                                        
    averageCost = forms.DecimalField(required=False)                     
    class Meta:
       model = Ingredients
       fields = ( 'ingredient', 'yearQtyUsed','quantityUsed','unitMeasurePrice','variableFixed','adjPricePerIngredient','costPerIngredient','percentageCost','costPerParticipant','totalCost','hrsCalendarYr', 'hrsAcademicYr', 'hrsHigherEdn','category','edLevel','sector','unitMeasurePrice', 'price','lifetimeAsset', 'interestRate', 'yearPrice', 'statePrice', 'areaPrice','sourcePriceData','urlPrice','benefitRate','newMeasureVol','newMeasureLen', 'newMeasureTime','convertedPrice','priceAdjAmortization','SourceBenefitData','YearBenefit','priceAdjBenefits','percentageofUsage','geoIndex','indexCPI','priceAdjInflation','priceAdjGeographicalArea', 'priceNetPresentValue','averageCost')

class IngredientsForm(forms.ModelForm):
   ingredient  = forms.CharField(required=False,label="Ingredients")
   yearQtyUsed = forms.IntegerField(required=False, label="Year in which quantity is used",widget = forms.TextInput(attrs={'readonly':'readonly'}))
   quantityUsed  = forms.DecimalField(required=False,label="Quantity of ingredient")
   newMeasure = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Unit of Measure")
   variableFixed = forms.ChoiceField(choices=(('Fixed','Fixed'),('Variable','Variable'),('Lumpy','Lumpy')),required=False,label="Variable,fixed or lumpy")
   adjPricePerIngredient = forms.DecimalField(required=False, label="Adj. price of ingredient", widget = forms.TextInput(attrs={'readonly':'readonly'}))
   costPerIngredient = forms.DecimalField(required=False,label="Cost")
   percentageCost = forms.DecimalField(required=False, label="% of Total Cost")
   costPerParticipant = forms.DecimalField(required=False, label="Cost per Participant")
   totalCost = forms.DecimalField(required=False)
   class Meta:
       model = Ingredients
       fields = ( 'ingredient', 'yearQtyUsed','quantityUsed','unitMeasurePrice','variableFixed','adjPricePerIngredient','costPerIngredient','percentageCost','costPerParticipant','totalCost')
 
class PricesSearchForm(forms.ModelForm):
   catquery = Prices.objects.values_list('category', flat=True).distinct()
   catquery_choices =  [('All','All')] +[(id, id) for id in catquery]
   edquery = Prices.objects.exclude(edLevel = ' ').values_list('edLevel', flat=True).distinct()
   edquery_choices =  [(id, id) for id in edquery]
   secquery = Prices.objects.exclude(sector = ' ').values_list('sector', flat=True).distinct()
   secquery_choices =  [(id, id) for id in secquery]
   category = forms.ChoiceField(choices=catquery_choices, initial="All", required=False, widget=forms.Select(),label="Category:")
   edLevel = forms.ChoiceField(edquery_choices, required=False, widget=forms.Select(), label="Education level to be served:")
   sector = forms.ChoiceField(secquery_choices, required=False, widget=forms.Select(),label="Sector:")
   ingredient  = forms.CharField(required=False,label="Ingredient:")

   class Meta:
       model = Prices
       fields = ('category','edLevel','sector','ingredient')

class PriceIndicesForm(forms.ModelForm):
   unitMeasurePrice = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Unit of Measure:")
   price = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Price per unit:")
   yearPrice = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Year of the listed price:")
   statePrice  = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}), label="To which geographical location does this price correspond to?")
   areaPrice = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}), label="")
   sourcePriceData = forms.CharField(required=False,widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Source:")

   class Meta:
       model = Prices
       fields = ('unitMeasurePrice', 'price', 'yearPrice', 'statePrice', 'areaPrice', 'sourcePriceData')

class NonPerIndicesForm(forms.ModelForm):
   unitMeasurePrice = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Unit of Measure:")
   price = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Price per unit:")
   lifetimeAsset = forms.IntegerField(required=False,initial=1, min_value = 1,label="Lifetime of the asset:" )
   interestRate = forms.DecimalField(required=False, initial=3.5, min_value = 0.0, max_digits=7,decimal_places=3, label="Interest rate:")
   yearPrice = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Year of the listed price:")
   statePrice  = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}), label="To which geographical location does this price correspond to?")
   areaPrice = forms.CharField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}), label="")
   sourcePriceData = forms.CharField(required=False,widget = forms.TextInput(attrs={'readonly':'readonly'}),label="Source:")

   class Meta:
       model = Ingredients
       fields = ('unitMeasurePrice', 'price', 'lifetimeAsset', 'interestRate', 'yearPrice', 'statePrice', 'areaPrice', 'sourcePriceData')

class WageDefaults(forms.ModelForm):
    hrsCalendarYr = forms.IntegerField(required=False,initial=2080,min_value=0,label="Number of hours in the calendar year: The calendar year consists of 2,080 working hours (52 weeks, 5 days a week, 8 hrs a day) according to the U.S. Bureau of Labor Statistics. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the calendar year in the following cell:")
    hrsAcademicYr = forms.IntegerField(required=False,initial=1440, min_value=0,label="Number of hours in the K-12 academic year: The academic year consists of 1,440 working hours (36 weeks, 5 days a week, 8 hrs a day) according to CBCSE. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the K-12 academic year in the following cell:")
    hrsHigherEdn = forms.IntegerField(required=False,initial=1560, min_value=0,label="Number of hours in the higher education academic year: The academic year consists of 1,560 working hours (39 weeks, 5 days a week, 8 hrs a day) according to CBCSE. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the higher education academic year in the following cell:")
   
    class Meta:
       model = Ingredients
       fields = ('hrsCalendarYr', 'hrsAcademicYr', 'hrsHigherEdn')

class PriceBenefits(forms.ModelForm):
   benefitRate = forms.CharField(required=False,label="Enter fringe benefit rate as a percentage of salary/wage:")

   class Meta:
       model = Ingredients
       fields = ('benefitRate',)

   def __init__(self, data=None, *args, **kwargs):
       super(PriceBenefits, self).__init__(data, *args, **kwargs)
       self.initial['benefitRate'] = 0


   def clean_benefitRate(self):
       benefitRate = self.cleaned_data['benefitRate']
       if float(benefitRate) < 0:
          raise forms.ValidationError("Ensure that Benefit Rate is a positive number.")
       else:
          pass
          return benefitRate

class Benefits(forms.ModelForm):
    SectorBenefit = forms.CharField(required=False,label="Sector")
    EdLevelBenefit = forms.CharField(required=False,label="Ed Level")
    PersonnelBenefit = forms.CharField(required=False,label="Personnel")
    TypeRateBenefit = forms.CharField(required=False,label="Type Rate")
    YearBenefit = forms.CharField(required=False,label="Year")
    BenefitRate = forms.CharField(required=False,label="Benefit Rate")
    SourceBenefitData = forms.CharField(required=False,label="Source")
    URLBenefitData = forms.CharField(required=False,label="URL")

    class Meta:
       model = Benefits
       fields = ('SectorBenefit', 'EdLevelBenefit', 'PersonnelBenefit', 'TypeRateBenefit', 'YearBenefit', 'BenefitRate', 'SourceBenefitData', 'URLBenefitData')

class WageConverter(forms.ModelForm):
   choicesPersonnel = (('Hour','Hour'),('Day','Day'),('Week','Week'),('K-12 Academic Year','K-12 Academic Year'), ('Higher Ed Academic Year', 'Higher Ed Academic Year'),('Calendar Year','Calendar Year'))
   newMeasure = forms.ChoiceField(choicesPersonnel, required=False, widget=forms.Select(),label="Convert to")
   convertedPrice = forms.DecimalField(required=False, label="Converted value:", widget = forms.TextInput(attrs={'readonly':'readonly'}))

   class Meta:
       model = Ingredients
       fields = ('newMeasure',)

class UMConverter(forms.ModelForm):
   choicesPersonnel = (('Sq. Inch', 'Sq. Inch'),('Sq. Foot','Sq. Foot'),('Sq. Yard','Sq. Yard'),('Acre','Acre'), ('Sq. Mile', 'Sq. Mile'),('Sq. Meter','Sq. Meter'),('Sq. Kilometer','Sq. Kilometer'), ('Hectare','Hectare'))
   choicesVolume = (('Fluid Ounces', 'Fluid Ounces'), ('Cups', 'Cups'), ('Pints','Pints'), ('Quarts','Quarts'), ('Gallons','Gallons'),('Liters','Liters'))     
   choicesLength = (('Inches', 'Inches'), ('Feet','Feet'),('Yards','Yards'),('Miles','Miles'),('Millimeter','Millimeter'),('Centimeter','Centimeter'),('Kilometer','Kilometer'))
   choicesTime = (('Hour','Hour'),('Day','Day'),('Week','Week'),('K-12 Academic Year','K-12 Academic Year'),('Higher Ed Academic Year', 'Higher Ed Academic Year'),('Calendar Year','Calendar Year'))
   newMeasure = forms.ChoiceField(choicesPersonnel, required=False, widget=forms.Select(),label="Convert to")
   newMeasureVol = forms.ChoiceField(choicesVolume, required=False, widget=forms.Select(),label="Convert to")
   newMeasureLen = forms.ChoiceField(choicesLength, required=False, widget=forms.Select(),label="Convert to")
   newMeasureTime = forms.ChoiceField(choicesTime, required=False, widget=forms.Select(),label="Convert to")
   convertedPrice = forms.DecimalField(required=False, label="Converted value:", widget = forms.TextInput(attrs={'readonly':'readonly'}))

   class Meta:
       model = Ingredients
       fields = ('newMeasure','newMeasureVol','newMeasureLen', 'newMeasureTime',)

class PriceSummary(forms.ModelForm):
   yearQtyUsed = forms.IntegerField(required=False, min_value=0,label="Year:",widget = forms.TextInput(attrs={'readonly':'readonly'}))
   quantityUsed  = forms.DecimalField(label="Quantity of ingredient needed:")
   variableFixed = forms.ChoiceField(choices=(('Fixed','Yes, this is a Fixed quantity. (i.e., stays the same regardless of the number of program participants)'),('Variable','No, this is a Variable quantity (i.e., changes in direct proportion to the number of program participants)'),('Lumpy','No, this is a Lumpy quantity (i.e., changes when the number of participants increases or decreases by a certain amount, e.g., goes up after 30 more participants are added, then again at 60 etc.)')),required=False,widget=forms.RadioSelect(),label="Does this number stay fixed even if number of participants change?")
   percentageofUsage  = forms.DecimalField(label="Percentage of Usage", initial=100,min_value = 0.00, max_value = 100.00, max_digits=6,decimal_places=2 )
   lifetimeAsset = forms.IntegerField(required=False,initial=1, min_value = 1,label="Lifetime of the asset:" )                        
   interestRate = forms.DecimalField(required=False, initial=3.5, min_value = 0.0, max_digits=7,decimal_places=3, label="Interest rate:")
   
   class Meta:
       model = Ingredients
       fields = ('yearQtyUsed','quantityUsed', 'variableFixed','percentageofUsage','lifetimeAsset','interestRate')

   def __init__(self, *args, **kwargs):
       super(PriceSummary, self).__init__(*args, **kwargs)
       self.initial['variableFixed'] = 'Variable'

class MultipleSummary(forms.ModelForm):
   yearQtyUsed = forms.IntegerField(required=False, min_value=0,label="Year:",widget = forms.TextInput(attrs={'readonly':'readonly'}))
   quantityUsed  = forms.DecimalField(label="Quantity of ingredient needed:")
   variableFixed = forms.ChoiceField(choices=(('Fixed','Yes. This is a Fixed quantity.'),('Variable','No. This is a Variable quantity.'),('Lumpy','No. This is a Lumpy quantity.')),required=False,widget=forms.RadioSelect())
   percentageofUsage  = forms.DecimalField(label="Percentage of Usage",min_value = 0.00, max_value = 100.00, max_digits=6,decimal_places=2)
   lifetimeAsset = forms.IntegerField(required=False,initial=1, min_value = 1,label="Lifetime of the asset:" )                        
   interestRate = forms.DecimalField(required=False, initial=3.5, min_value = 0.0, max_digits=7,decimal_places=3, label="Interest rate:")

   class Meta:
       model = Ingredients
       fields = ('yearQtyUsed', 'quantityUsed','variableFixed','percentageofUsage','lifetimeAsset','interestRate')
    
   def __init__(self, *args, **kwargs):
       super(MultipleSummary, self).__init__(*args, **kwargs)
       self.initial['variableFixed'] = 'Variable'

class PricesForm(forms.ModelForm):
    yrquery = InflationIndices.objects.values_list('yearCPI', flat=True).distinct()
    yrquery_choices =  [(id, id) for id in yrquery]
    iquery = GeographicalIndices.objects.values_list('stateIndex', flat=True).distinct()
    iquery_choices =  [(id, id) for id in iquery]
    areaquery = GeographicalIndices.objects.values_list('areaIndex', flat=True).distinct()
    areaquery_choices =  [(id, id) for id in areaquery]
    choicesPersonnel = (('Hour','Hour'),('Day','Day'),('Week','Week'),('K-12 Academic Year','K-12 Academic Year'), ('Higher Ed Academic Year', 'Higher Ed Academic Year'),('Calendar Year','Calendar Year'),('Sq. Inch', 'Sq. Inch'),('Sq. Foot','Sq. Foot'),('Sq. Yard','Sq. Yard'),('Acre','Acre'), ('Sq. Mile', 'Sq. Mile'),('Sq. Meter','Sq. Meter'),('Sq. Kilometer','Sq. Kilometer'), ('Hectare','Hectare'),('Fluid Ounces', 'Fluid Ounces'), ('Cups', 'Cups'), ('Pints','Pints'), ('Quarts','Quarts'), ('Gallons','Gallons'),('Liters','Liters'),('Inches', 'Inches'), ('Feet','Feet'),('Yards','Yards'),('Miles','Miles'),('Millimeter','Millimeter'),('Centimeter','Centimeter'),('Kilometer','Kilometer'),('Sq. Ft. * Hrs', 'Sq. Ft. * Hrs'), ('Units', 'Units'),('Other','Other'))
    choicesNonPer = (('Inches','Inches'),('Meters','Meters'),('Sq. Ft.','Sq. Ft.'), ('Sq. Mt.', 'Sq. Mt.'),('Item','Item'))
    catquery = Prices.objects.values_list('category', flat=True).distinct()
    catquery_choices =  [(id, id) for id in catquery]
    edquery = Prices.objects.exclude(edLevel = ' ').values_list('edLevel', flat=True).distinct()
    edquery_choices =  [('All','All')] +[(id, id) for id in edquery]
    secquery = Prices.objects.exclude(sector = ' ').values_list('sector', flat=True).distinct()
    secquery_choices =  [(id, id) for id in secquery]

    category = forms.ChoiceField(catquery_choices, widget=forms.Select(),label="Select the category for this ingredient:")
    ingredient  = forms.CharField(max_length=50,label="Name of the ingredient:")
    edLevel = forms.ChoiceField(edquery_choices, required=False, widget=forms.Select(), label="Education level to be served:")
    sector = forms.ChoiceField(secquery_choices, required=False, widget=forms.Select(),label="Sector:")
    #sector =  forms.CharField(widget=forms.Textarea(attrs('selectBoxOptions':';'.join(secquery_choices)))),label="Sector:",required=False)
    descriptionPrice = forms.CharField(required=False,max_length=200, label="Description:")
    unitMeasurePrice = forms.ChoiceField(choicesPersonnel, widget=forms.Select(),label="Unit of Measure:")
    price = forms.CharField(label="Price per unit (enter number with no commas, for e.g., 1200.10 or 456):")
    yearPrice = forms.ChoiceField(yrquery_choices, widget=forms.Select(),label="Year of the listed price:")
    statePrice  = forms.ChoiceField(iquery_choices,  widget=forms.Select(), label="To which geographical location does this price correspond to?")
    areaPrice = forms.ChoiceField(areaquery_choices,  widget=forms.Select(), label="")
    sourcePriceData = forms.CharField(required=False,max_length=200,label="Source:")
    urlPrice = forms.URLField(required=False,max_length=200,label="URL (The URL must start with http://www.):")
    lastChecked = forms.CharField(required=False, label="Last Checked:")    
    nextCheckDate = forms.CharField(required=False,label="Next Check Date:")
    class Meta:
        model = Prices
        fields = ('ingredient','category','edLevel','sector','descriptionPrice','unitMeasurePrice','price','statePrice','areaPrice','yearPrice','sourcePriceData','urlPrice', 'lastChecked','nextCheckDate')
    def __init__(self, *args, **kwargs):
        super(PricesForm, self).__init__(*args, **kwargs)
        latest = InflationIndices.objects.all().latest('yearCPI')
        yrquery = InflationIndices.objects.values_list('yearCPI', flat=True).distinct()
        yrquery_choices = [(id, id) for id in yrquery]  
        self.fields['yearPrice']=forms.ChoiceField(choices=yrquery_choices, initial=latest.yearCPI, required=False, widget=forms.Select(),label="Year of the listed price")
        iquery = GeographicalIndices.objects.values_list('stateIndex', flat=True).distinct()
        iquery_choices =  [(id, id) for id in iquery]
        areaquery = GeographicalIndices.objects.values_list('areaIndex', flat=True).distinct()
        areaquery_choices =  [(id, id) for id in areaquery]
        self.fields['statePrice']  = forms.ChoiceField(choices=iquery_choices, required=False, widget=forms.Select(), label="To which geographical location does this price correspond to?", initial="All states")
        self.fields['areaPrice'] = forms.ChoiceField(choices=areaquery_choices, required=False, widget=forms.Select(), label="", initial="All areas")
        error_css_class = 'error'

    def clean_price(self):
        price = self.cleaned_data['price']
        try: 
           if float(price) < 0.01:
              raise forms.ValidationError("Price must be greater than or equal to 0.1.")
           else:
              if not round(float(price),3): 
                 raise forms.ValidationError("Price must be a number with 3 decimal places.") 
              pass
              return price
        except ValueError:
           raise forms.ValidationError("Price must be a number.") 
