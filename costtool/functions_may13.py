from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from costtool import models as m
import math

def calculations(project_id):    
   setrec = m.Settings.objects.get(projectId=project_id)  
   try:
      infEstimate = m.InflationIndices.objects.get(projectId=project_id,yearCPI=setrec.yearEstimates)
      indexCPI = infEstimate.indexCPI
   except ObjectDoesNotExist:
      indexCPI = 'No inflation index available'
   
   try:
      geoEstimate = m.GeographicalIndices.objects.get(projectId=project_id,stateIndex=setrec.stateEstimates,areaIndex=setrec.areaEstimates)
      sgeoIndex = geoEstimate.geoIndex
   except ObjectDoesNotExist:
      sgeoIndex =  'No geographical index available'

   for p in m.Programs.objects.filter(projectId = project_id):
      try: 
         programdesc = m.ProgramDesc.objects.get(programId = p.id)
         programdescid = programdesc.id 
         numberofparticipants = programdesc.numberofparticipants
      except ObjectDoesNotExist:
         numberofparticipants = 1
         programdescid = 0

      try:
         eff = m.Effectiveness.objects.get(programId_id = p.id)
         avgeff = eff.avgeffectperparticipant
      except ObjectDoesNotExist:
         avgeff = None

      for i in m.Ingredients.objects.filter(programId = p.id):
         try:                                                                                                       
            inf = m.InflationIndices.objects.get(projectId=project_id,yearCPI=i.yearPrice)
            infinf = inf.indexCPI
         except ObjectDoesNotExist:
            infinf = 'No inflation index available'

         i.indexCPI = infinf
         try:
            geo = m.GeographicalIndices.objects.get(projectId=project_id,stateIndex=i.statePrice,areaIndex=i.areaPrice)
            geoIndex = geo.geoIndex
         except ObjectDoesNotExist:                                                                                 
            geoIndex = 'No geographical index available'
         
         i.geoIndex = geoIndex 
         if infinf == 'No inflation index available' or indexCPI == 'No inflation index available':
            i.priceAdjInflation = 'No index'
         else:
            i.priceAdjInflation = str(float(i.priceAdjBenefits) * (float(indexCPI) / float(infinf)))
         
         if i.priceAdjInflation == 'No index':
            i.indexCPI = 'No inflation index available' 
            i.priceAdjGeographicalArea = None 
            i.priceNetPresentValue = None
            i.adjPricePerIngredient = 'No inflation index available'
            i.costPerIngredient = None
            i.costPerParticipant = None
            i.save(update_fields=['indexCPI','geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])
         else:
            if geoIndex == 'No geographical index available' or sgeoIndex == 'No geographical index available':
               i.priceAdjGeographicalArea = 'No index'
            else:
               i.priceAdjGeographicalArea = str(float(i.priceAdjInflation) * (float(geoEstimate.geoIndex) / float(geoIndex))) 
            if i.priceAdjGeographicalArea == 'No index':
               i.geoIndex = 'No geographical index available'  
               i.priceNetPresentValue = None
               i.adjPricePerIngredient = 'No geographical index available'
               i.costPerIngredient = None
               i.costPerParticipant = None
               i.save(update_fields=['indexCPI','geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])
            else:   
               i.priceNetPresentValue = float(i.priceAdjGeographicalArea) * math.exp((1 - int(i.yearQtyUsed)) * (setrec.discountRateEstimates/100))
               i.adjPricePerIngredient = i.priceNetPresentValue
               if i.percentageofUsage == 100:
                  i.costPerIngredient = i.adjPricePerIngredient * float(i.quantityUsed)
               else:
                  i.costPerIngredient = i.adjPricePerIngredient * float(i.quantityUsed) * (float(i.percentageofUsage)/100)
      
               try:
                  partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=programdescid, yearnumber=i.yearQtyUsed)
                  i.costPerParticipant = float(i.costPerIngredient) / float(partperyear.noofparticipants)                                   
                  i.save(update_fields=['indexCPI','geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])           
               except ObjectDoesNotExist:
                  i.costPerParticipant = float(i.costPerIngredient) / float(numberofparticipants)
                  i.save(update_fields=['indexCPI', 'geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])
                                                                                                                                          
   for p in m.Programs.objects.filter(projectId = project_id):
      total_cost = 0
      ing = m.Ingredients.objects.filter(programId = p.id)
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
         if numberofparticipants is not None and i.totalCost is not None and  float(i.totalCost) != 0.000:
            i.averageCost = float(i.totalCost) / float(numberofparticipants)
            avg_cost = round(i.averageCost,2)
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
   
   return 1
