from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse, HttpResponseRedirect
from costtool import models as m
import math
import datetime

def calculations2(project_id, program_id):
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

   p =  m.Programs.objects.get(pk = program_id)
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
         i.priceAdjInflation = str(round(float(i.priceAdjBenefits) * (float(indexCPI) / float(infinf)),3))

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
            i.priceAdjGeographicalArea = str(round(float(i.priceAdjInflation) * (float(geoEstimate.geoIndex) / float(geoIndex)),3))
         if i.priceAdjGeographicalArea == 'No index':
            i.geoIndex = 'No geographical index available'
            i.priceNetPresentValue = None
            i.adjPricePerIngredient = 'No geographical index available'
            i.costPerIngredient = None
            i.costPerParticipant = None
            i.save(update_fields=['indexCPI','geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])
         else:
            i.priceNetPresentValue = round(float(i.priceAdjGeographicalArea) * math.exp((1 - int(i.yearQtyUsed)) * (setrec.discountRateEstimates/100)),3)
            i.adjPricePerIngredient = round(i.priceNetPresentValue,3)
            if i.percentageofUsage == 100:
               if i.adjPricePerIngredient is not None and i.quantityUsed is not None and i.quantityUsed != '':
                  i.costPerIngredient = round(i.adjPricePerIngredient * float(i.quantityUsed),3)
            else:
               if i.adjPricePerIngredient is not None and i.quantityUsed is not None and i.quantityUsed != '':
                  i.costPerIngredient = round(i.adjPricePerIngredient * float(i.quantityUsed) * (float(i.percentageofUsage)/100),3)

            try:
               partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=programdescid, yearnumber=i.yearQtyUsed)
               i.costPerParticipant = round(float(i.costPerIngredient) / float(partperyear.noofparticipants),3)                      
               i.save(update_fields=['indexCPI','geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])
            except ObjectDoesNotExist:
               if i.costPerIngredient is not None:
                  if numberofparticipants is None:
                     i.costPerParticipant = round(float(i.costPerIngredient),3)
                  elif numberofparticipants == 0:                                                                                                                                                    
                     i.costPerParticipant = round(float(i.costPerIngredient),3) / float("inf")
                  else:
                     i.costPerParticipant = round(float(i.costPerIngredient),3) / float(numberofparticipants)
               i.save(update_fields=['indexCPI', 'geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])

   p = m.Programs.objects.get(pk = program_id)
   total_cost = 0
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
         if numberofparticipants is not None:
            if numberofparticipants == 0:
               i.averageCost = float(i.totalCost) / float("inf")
            else:
               i.averageCost = float(i.totalCost) / float(programdesc.numberofparticipants)
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
   print 'costPerParticipant'   
   print i.costPerParticipant 
   return 1

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
            i.priceAdjInflation = str(round(float(i.priceAdjBenefits) * (float(indexCPI) / float(infinf)),3))
         
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
               i.priceAdjGeographicalArea = str(round(float(i.priceAdjInflation) * (float(geoEstimate.geoIndex) / float(geoIndex)),3)) 
            if i.priceAdjGeographicalArea == 'No index':
               i.geoIndex = 'No geographical index available'  
               i.priceNetPresentValue = None
               i.adjPricePerIngredient = 'No geographical index available'
               i.costPerIngredient = None
               i.costPerParticipant = None
               i.save(update_fields=['indexCPI','geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])
            else:   
               i.priceNetPresentValue = round(float(i.priceAdjGeographicalArea) * math.exp((1 - int(i.yearQtyUsed)) * (setrec.discountRateEstimates/100)),3)
               i.adjPricePerIngredient = round(i.priceNetPresentValue,3)
               if i.percentageofUsage == 100:
                  if i.adjPricePerIngredient is not None and i.quantityUsed is not None and i.quantityUsed != '':
                     i.costPerIngredient = round(i.adjPricePerIngredient * float(i.quantityUsed),3)
               else:
                  if i.adjPricePerIngredient is not None and i.quantityUsed is not None and i.quantityUsed != '':
                     i.costPerIngredient = round(i.adjPricePerIngredient * float(i.quantityUsed) * (float(i.percentageofUsage)/100),3)
      
               try:
                  partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=programdescid, yearnumber=i.yearQtyUsed)
                  i.costPerParticipant = round(float(i.costPerIngredient) / float(partperyear.noofparticipants),3)                                   
                  i.save(update_fields=['indexCPI','geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])           
               except ObjectDoesNotExist:
                  if i.costPerIngredient is not None:
                     i.costPerParticipant = round(float(i.costPerIngredient),3) / float(numberofparticipants)
                  i.save(update_fields=['indexCPI', 'geoIndex','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue','adjPricePerIngredient','costPerIngredient', 'costPerParticipant'])

   for p in m.Programs.objects.filter(projectId = project_id):
      total_cost = 0
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


def updateDate(project_id, program_id):
   if project_id is not None:
      proj = m.Projects.objects.get(pk=project_id)
      proj.updated_at = datetime.datetime.now()
      proj.save(update_fields=['updated_at'])

   if program_id is not None:
      prog = m.Programs.objects.get(pk=program_id)
      prog.updated_at = datetime.datetime.now()
      prog.save(update_fields=['updated_at'])
   return 1

def updateProj(project_id):
   if project_id is not None:
      proj = m.Projects.objects.get(pk=project_id)
      #f = open( '/home/amritha/costtool/documents/f.txt', 'w+' )
      #f.write(project_id)
      try: 
         sharedproj = m.SharedProj.objects.get(projectid = project_id)
         proj.shared = 'Y'
      except MultipleObjectsReturned:
         proj.shared = 'Y' 
      except ObjectDoesNotExist:
         proj.shared = 'N'
      #f.write(proj.shared)
      #f.close()
      proj.updated_at = datetime.datetime.now()                                                                                                                                                                   
      proj.save(update_fields=['shared', 'updated_at'])
   return 1
