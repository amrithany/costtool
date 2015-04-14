if avgeff is not None and i.averageCost is not None:
    1579                    i.effRatio = float(i.averageCost) / float(avgeff)
    1580                 else:
        1581                    i.effRatio = None

try:
    1474        eff = m.Effectiveness.objects.get(programId_id = request.session['program_id'])
    1475        avgeff = eff.avgeffectperparticipant
    1476     except ObjectDoesNotExist:
        1477        avgeff = None

        avgeff = None
         367     eff_Ratio = None 

     else:
          330                    i.averageCost = None
           331                    avg_cost = None
            332 
             333                 if avgeff is not None and i.averageCost is not None:
                  334                    i.effRatio = float(i.averageCost) / float(avgeff)
                   335                    eff_ratio = round(i.effRatio,2)
                    336                 else:
                         337                    i.effRatio = None
                          338                    eff_ratio = None
                           339 
                            340                 i.save(update_fields=['totalCost','averageCost','percentageCost','effRatio'])         
f = ingform.save(commit=False)                                                                                          
 331              for ing in f:

     def clean(self):                                                                                                                  
         158         cleaned_data = super(InflationForm, self).clean()
         159         iid = self.cleaned_data['id']
         160         try:
             161            InflationIndices.objects.get(pk = iid, yearCPI = self.cleaned_data['yearCPI'])
             162            raise forms.ValidationError("That year already exists.  Please enter an unique year.")
             163         except InflationIndices.DoesNotExist:
                 164            pass
                 165         return cleaned_data

i.priceAdjInflation = str(float(i.priceAdjBenefits) * (float(infEstimate.indexCPI) / float(infinf)))
            178           i.priceAdjGeographicalArea = str(float(i.priceAdjInflation) * (float(geoEstimate.geoIndex) / float(geoIndex)))
             179           i.priceNetPresentValue = float(i.priceAdjGeographicalArea) * math.exp((1 - int(i.yearQtyUsed)) * (discountRateEstimates/100))
                  180           i.adjPricePerIngredient = i.priceNetPresentValue
                   181           i.costPerIngredient = i.adjPricePerIngredient * float(i.quantityUsed) * (float(i.percentageofUsage)/100)
                    182           try:
                     183              partperyear = m.ParticipantsPerYear.objects.get(programdescId_id=programdesc.id, yearnumber=i.yearQtyUsed)
                      184              i.costPerParticipant = float(i.costPerIngredient) / float(partperyear.noofparticipants)
                       185              i.save(update_fields=['ingredient','category','yearQtyUsed','variableFixed','quantityUsed','lifetimeAsset','interestRate','benefitRate', 'percentageofUsage','priceAdjAmortization','priceAdjBenefits','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue', 'adjPricePerIngredient','costPerIngredient', 'costPerParticipant']) 
                        186           except ObjectDoesNotExist:
                         187              i.costPerParticipant = ''
                          188              i.save(update_fields=['ingredient','category','yearQtyUsed','variableFixed','quantityUsed','lifetimeAsset','interestRate','benefitRate', 'percentageofUsage','priceAdjAmortization','priceAdjBenefits','priceAdjInflation','priceAdjGeographicalArea','priceNetPresentValue', 'adjPricePerIngredient','costPerIngredient', 'costPerParticipant']) 
                           189           total_cost = 0
                            190           ing = m.Ingredients.objects.filter(programId = program_id)
                             191           for i in ing:
                              192               total_cost = total_cost + i.costPerIngredient
                               193           for i in ing:
                                194               i.totalCost = total_cost
                                 195               i.percentageCost = i.costPerIngredient * 100 /i.totalCost
                                 if numberofparticipants is not None:
                                      197                  i.averageCost = float(i.totalCost) / float(numberofparticipants)
                                       198                  avg_cost = round(i.averageCost,2)
                                        199                  i.save(update_fields=['totalCost','averageCost','percentageCost'])
                                         200               else:
                                              201                  i.save(update_fields=['totalCost','percentageCost'])
