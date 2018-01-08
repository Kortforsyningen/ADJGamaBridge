#!/usr/bin/env python3x
"""
What is this

Created on Wed Mar 29 11:29:21 2017
"""

__version__ = "0.0"
__author__ = "Lars Stenseng"


from xml.dom.minidom import parseString
from argparse import ArgumentParser

from kmsread import kmsCoord2Dict, kmsObs2List, kmsMergeCoords

parser = ArgumentParser()
parser.add_argument("output", help="Gama output XML file.")
parser.add_argument("-s", "--stations", required = True, action = "append",
                                        help = "KMS file with station point coordinates. \
                                        Repeat arg to include additional files. \
                                        Repeated stations may be fully or partly \
                            overwritten.")
parser.add_argument("-o", "--observations", required = True, action="append",
                                        help="KMS file with observations. \
                                        Repeat arg to include additional files.")
parser.add_argument("-f", "--fixed", required = True, action="append",
                                        help="Stations to be fixed in adjustment.")
arguments = parser.parse_args()

gamaXMLTemplate = """\
<?xml version="1.0" encoding="UTF-8"?>
<gama-local>
  <network axes-xy="en" angles="left-handed" epoch="0.0">
  <description></description>
    <parameters
      sigma-apr="1.0"
      conf-pr="0.95"
      tol-abs="1000.0"
      sigma-act="apriori"
      algorithm="gso"
      update-constrained-coordinates="no"
      angles="400"
      latitude="55.7"
      ellipsoid="grs80"
      cov-band="0"
    />
  </network>
</gama-local>
"""
#<description></description>

coordList=[]
for stationFileName in arguments.stations:
    stations = kmsCoord2Dict(stationFileName)
    coordList.append(stations)
coordAll = kmsMergeCoords(coordList)
obsAll = []
for observationsFileName in arguments.observations:
    observations = kmsObs2List(observationsFileName)
    obsAll.extend(observations)
stationsFromTo = [station[0] for station in obsAll]
stationsFromTo.extend([station[1] for station in obsAll])
stationsWithoutCoord = list(set(stationsFromTo) - set(coordAll.keys()))
stationsWithoutHgt = [id for id in coordAll if coordAll[id][0] == 2]
stationsWithoutObs = list(set(coordAll.keys()) - set(stationsFromTo))
print("\nStations without coordinates: {}".format(stationsWithoutCoord))
print("Stations without elevation: {}".format(stationsWithoutHgt))
print("Stations without observations: {}\n".format(stationsWithoutObs))

#Start of modification, except description tag in the GamaXMLTemplate
year_str = ''
for observation in obsAll:
    year_str = year_str + observation[0] + ':' + str(observation[7]) + ','
year_str = year_str[:-1]

description_dict = dict(e.split(':') for e in year_str.split(','))

for i in range(len(arguments.fixed)):
    try:
        yr = stations[arguments.fixed[i]][3][0]
        index_fix = year_str.find(arguments.fixed[i])
        
        year_len = len(stations[arguments.fixed[i]][3][0])
        
        year_str = year_str[:index_fix + len(arguments.fixed[i])] + 'f' + year_str[index_fix + len(arguments.fixed[i]):]
        
        if len(description_dict[arguments.fixed[i]])==0:
            year_str = year_str[:index_fix+len(arguments.fixed[i])+1+1] + yr + year_str[index_fix+len(arguments.fixed[i])+1+1:]
            
        else:
            year_str = year_str[:index_fix + len(arguments.fixed[i])+5+1] + '/' + yr + year_str[index_fix+len(arguments.fixed[i])+5+1:]
#            year_str = year_str + ',' + 'fix_time:' + stations[arguments.fixed[0]][3][1].replace(' ','')
            
        fix_date_str = stations[arguments.fixed[i]][3][1].replace(' ','')
        fix_date_list = fix_date_str.split(',')
        year_str = year_str + ',' + 'fix_date' + arguments.fixed[i] + ':' + fix_date_list[0]
        year_str = year_str + ',' + 'fix_time' + arguments.fixed[i] + ':' + fix_date_list[1]
            
    except NameError:
        print('NameError in fixed. Year not saved to fixed')
    except IndexError:
        print('IndexError in fixed. Year not saved to fixed')

#End of modification
description_index = gamaXMLTemplate.index('<description>')
gamaXMLTemplate = gamaXMLTemplate[:description_index + len('<description>')] + year_str + gamaXMLTemplate[len('<description>') + description_index:]

gamaXML = parseString(gamaXMLTemplate)

pointObs = gamaXML.createElement("points-observations")
gamaXML.getElementsByTagName("network")[0].appendChild(pointObs)

for id in coordAll:
    point = gamaXML.createElement("point")
    if id in arguments.fixed:
        point.setAttribute("fix", "Z")
    else:
        point.setAttribute("adj", "z")
    point.setAttribute("id", id)
    if coordAll[id][0] == 2 or coordAll[id][0] == 3:
        point.setAttribute("x", coordAll[id][2])
    if coordAll[id][0] == 2 or coordAll[id][0] == 3:
        point.setAttribute("y", coordAll[id][1])
    if coordAll[id][0] == 1 or coordAll[id][0] == 3:
        point.setAttribute("z", coordAll[id][3])
    gamaXML.getElementsByTagName("points-observations")[0].appendChild(point)
for id in stationsWithoutCoord:
    point = gamaXML.createElement("point")
    point.setAttribute("adj", "z")
    point.setAttribute("id", id)
    gamaXML.getElementsByTagName("points-observations")[0].appendChild(point)
hDiffObs = gamaXML.createElement("height-differences")
gamaXML.getElementsByTagName("points-observations")[0].appendChild(hDiffObs)
for observation in obsAll:
    hDiff = gamaXML.createElement("dh")
    hDiff.setAttribute("from", observation[0])
    hDiff.setAttribute("to", observation[1])
    hDiff.setAttribute("val", "{:.5f}".format(observation[2]))
    hDiff.setAttribute("dist", "{:.5f}".format(observation[3]))
    hDiff.setAttribute("stdev", "{:.5f}".format(observation[4]))
    gamaXML.getElementsByTagName("height-differences")[0].appendChild(hDiff)

outFile = open(arguments.output, mode="w")
#gamaXML.getElementsByTagName("parameters")[0].setAttribute("cov-band", "-1")
gamaXML.writexml(outFile, addindent="\t", newl="\n")
outFile.close()

print("Points written to Gama XML file. 1D: {} 2D: {} 3D: {}"
      .format(len([id for id in coordAll if coordAll[id][0] == 1]),
              len([id for id in coordAll if coordAll[id][0] == 2]),
              len([id for id in coordAll if coordAll[id][0] == 3])))