import operator 

# parcellationLesionContributionSortedLh = [[],
# [],
# [],
# [('7', 102), ('3', 243)],
# [],
# [],
# [],
# [('5', 153)],
# [],
# [],
# [],
# [],
# [],
# [],
# [],
# [],
# []]


# parcellationLesionContributionSortedRh = [[('3', 41)],
# [],
# [],
# [],
# [('6', 99), ('3', 122)],
# [],
# [('6', 62), ('3', 366)],
# [],
# [('7', 34)],
# [('7', 403)],
# [('5', 198)],
# [],
# [('5', 222), ('6', 389)],
# [],
# [],
# [],
# [('3', 92)]]

parcellationLesionContributionSortedLh = [[('6', 14), ('5', 16), ('3', 20), ('4', 32), ('8', 44), ('2', 61), ('7', 76), ('1', 159)], [('1', 25)], [], [('4', 4), ('7', 5), ('1', 12), ('2', 26)], [('1', 75)], [('2', 13)], [('1', 4)], [('1', 225)], 
[('1', 40)], [('1', 51), ('2', 82)], [('1', 80)], [], [('1', 10)], [('1', 25)], [('1', 62)], [('2', 33), ('1', 35)], [('6', 1), ('7', 4), ('2', 28), ('4', 30), ('8', 67)], [('7', 13), ('2', 44), ('1', 79)], [], [('1', 9)], [], [('6', 2), ('8', 34), ('1', 99), ('4', 139)], [('2', 3), ('8', 4)], [('2', 28), ('1', 107), ('8', 159), ('4', 588)], [('8', 7), ('5', 10), ('1', 202)], [], [('7', 16), ('1', 21)], [('5', 3), ('8', 13), ('3', 16), ('7', 42), ('4', 79), ('2', 118)], [('8', 7), ('7', 8), ('5', 15), ('2', 17), ('4', 17), ('1', 367)], [('1', 360)], [('1', 115)], [], [], [('1', 41)], [('2', 1), ('4', 2), ('1', 146)]]


parcellationLesionContributionSortedRh = [[('6', 13), ('4', 14), ('5', 25), ('3', 39), ('8', 51), ('2', 67), ('7', 84), ('1', 106)], [], [('2', 2), ('7', 32)], [('8', 1), ('6', 3), ('5', 6), ('7', 15)], [('1', 17)], [], [('5', 16)], [('3', 9), ('7', 22), ('5', 59), ('6', 75)], [('6', 4), ('5', 51)], [('1', 5), ('7', 7), ('5', 29)], [], [], [], [], [('3', 10), ('5', 23)], [], [('3', 1), ('6', 14), ('4', 15), ('2', 18), ('1', 33), ('8', 44)], [('6', 4), ('3', 10), ('7', 24)], [], [('1', 8), ('2', 9), ('7', 11), ('3', 24)], [], [('4', 4), ('1', 6), ('3', 21), ('5', 28), ('6', 186)], [('1', 2), ('5', 4), ('8', 9), ('2', 11), ('7', 15)], [('4', 1), ('7', 16), ('5', 61), ('8', 91), ('6', 100), ('3', 160)], [('8', 8), ('7', 13), ('1', 58)], [], [('7', 2), ('8', 5), ('5', 9), ('6', 12), ('3', 34)], [('4', 1), ('6', 4), ('8', 9), ('3', 15), ('5', 22), ('2', 82), ('7', 132)], [('8', 1), ('7', 6), ('6', 25), ('1', 31), ('5', 69)], [('6', 12), ('1', 21), ('5', 48)], [('5', 8), ('1', 14), ('3', 41), ('6', 71)], [], [], [('5', 17)], [('5', 3), ('3', 5), ('1', 7)]]

def getTopNLesions(n, parcellationLabel, parcellationLesionContributionSortedLh, parcellationLesionContributionSortedRh, isLeftHemisphere):
      topLesionIds = []
      indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
      parcellationIndex = list(indexToParcellationDict.keys())[list(indexToParcellationDict.values()).index(parcellationLabel)]

      if(isLeftHemisphere):
          lesionsAndImpactCountOnParcellation = parcellationLesionContributionSortedLh[parcellationIndex]
      else:
          lesionsAndImpactCountOnParcellation = parcellationLesionContributionSortedRh[parcellationIndex]
          
      reversedList = lesionsAndImpactCountOnParcellation[::-1]
      topN = reversedList[:n]
      for item in topN:
        topLesionIds.append(int(item[0]))
      return topLesionIds

# def getTopNRegions(n, lesionID, parcellationLesionContributionSortedLh, parcellationLesionContributionSortedRh):
#       topParcellationLabels = []
#       indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
#       lesionFootPrintMagnitudeOnParcellationLabels = dict()
#       for item in parcellationLesionContributionSortedLh:
#           if(item): # list not empty
#               for entry in item:
#                   if(lesionID ==int(entry[0])):
#                       #print("found here", parcellationLesionContributionSortedLh.index(item), ",", entry[1])
#                       lesionFootPrintMagnitudeOnParcellationLabels.update({'%d'%parcellationLesionContributionSortedLh.index(item):entry[1]})
#       for item in parcellationLesionContributionSortedRh:
#           if(item): # list not empty
#               for entry in item:
#                   if(lesionID ==int(entry[0])):
#                       #print("found here", parcellationLesionContributionSortedLh.index(item), ",", entry[1])
#                       lesionFootPrintMagnitudeOnParcellationLabels.update({'%d'%parcellationLesionContributionSortedRh.index(item):entry[1]})

#       sortedAndReversedFootPrint = sorted(lesionFootPrintMagnitudeOnParcellationLabels.items(), key=operator.itemgetter(1))[::-1]
#       print(sortedAndReversedFootPrint)

#       # compute parcellation labels

#       for item in sortedAndReversedFootPrint:
#           topParcellationLabels.append(indexToParcellationDict[int(item[0])])
#       return topParcellationLabels[:n] # return top n


def getTopNRegions(n, lesionID, parcellationLesionContributionSortedLh, parcellationLesionContributionSortedRh):
      topParcellationLabelsLh = []
      topParcellationLabelsRh = []
      indexToParcellationDict = {0:-1,1:1,2:2,3:3,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:13,13:14,14:15,15:16,16:17,17:18,18:19,19:20,20:21,21:22,22:23,23:24,24:25,25:26,26:27,27:28,28:29,29:30,30:31,31:32,32:33,33:34,34:35}
      combinedList = []
      print(parcellationLesionContributionSortedLh)
      for item in parcellationLesionContributionSortedLh:
          if(item): # list not empty
              for entry in item:
                  if(lesionID ==int(entry[0])):
                      combinedList.append(['l', '%d'%parcellationLesionContributionSortedLh.index(item),entry[1]])

      for item in parcellationLesionContributionSortedRh:
          if(item): # list not empty
              for entry in item:
                  if(lesionID ==int(entry[0])):
                      combinedList.append(['r','%d'%parcellationLesionContributionSortedRh.index(item), entry[1]])
           
      combinedListsorted = sorted(combinedList, key=operator.itemgetter(2))
      finalList = combinedListsorted[::-1][:n]


      #compute parcellation labels
      for item in finalList:
          item[1] = indexToParcellationDict[int(item[1])]
          #print(item)
          if(item[0]=='l'):
              topParcellationLabelsLh.append(item[1])
          else:
              topParcellationLabelsRh.append(item[1])
        
      return topParcellationLabelsLh, topParcellationLabelsRh

# topLesionIds = getTopNLesions(2, 7, parcellationLesionContributionSortedLh, parcellationLesionContributionSortedRh, False)
# print("TOP LESION IDS", topLesionIds)

# topParcellationLabels = getTopNRegions(3, 5, parcellationLesionContributionSortedLh, parcellationLesionContributionSortedRh)
# print("TOP PARCELLATION LABELS", topParcellationLabels)


topParcellationLabelsLh, topParcellationLabelsRh = getTopNRegions(40, 1, parcellationLesionContributionSortedLh, parcellationLesionContributionSortedRh)
print("TOP PARCELLATION LABELS", topParcellationLabelsLh, topParcellationLabelsRh)


# a = [[['6', 14], ['5', 16], ['3', 20], ['4', 32], ['8', 44], ['2', 61], ['7', 76], ['1', 159]], [['1', 25]], [], [['4', 4], ['7', 5], ['1', 12], ['2', 26]], [['1', 75]], [['2', 13]], [['1', 4]], [['1', 225]], [['1', 40]], [['1', 51], ['2', 82]], [['1', 80]], [], [['1', 10]], [['1', 25]], [['1', 62]], [['2', 33], ['1', 35]], [['6', 1], ['7', 4], ['2', 28], ['4', 30], ['8', 67]], [['7', 13], ['2', 44], ['1', 79]], [], 
# [['1', 9]], [], [['6', 2], ['8', 34], ['1', 99], ['4', 139]], [['2', 3], ['8', 4]], [['2', 28], ['1', 107], ['8', 159], ['4', 588]], [['8', 7], ['5', 10], ['1', 202]], [], [['7', 16], ['1', 21]], [['5', 3], ['8', 
# 13], ['3', 16], ['7', 42], ['4', 79], ['2', 118]], [['8', 7], ['7', 8], ['5', 15], ['2', 17], ['4', 17], ['1', 367]], [['1', 360]], [['1', 115]], [], [], [['1', 41]], [['2', 1], ['4', 2], ['1', 146]]]


# for elem in a:
#     for i in range(len(elem)):
#         elem[i] = tuple(elem[i])

# print(a)
