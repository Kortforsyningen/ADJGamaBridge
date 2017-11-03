#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from xml.etree import ElementTree
from re import split


parser = ArgumentParser()
parser.add_argument("input", help="Gama input XML file.")
parser.add_argument("-o", "--output", help="Gama text output file.")
parser.add_argument("-x", "--xmloutput", help="Gama output XML file.")
parser.add_argument("-s", "--stations", help = "File with stations as points.")
parser.add_argument("-d", "--distances", \
                    help="File with observations as lines")
arguments = parser.parse_args()

inTree = ElementTree.parse(arguments.input)
coord = {}
for point in inTree.findall(".//point"):
    coord[point.attrib.get("id")] = [point.attrib.get("x"), 
                                     point.attrib.get("y"), 
                                     point.attrib.get("z")]
#    coord[id].extend([z])
observations = []
for obs in inTree.findall(".//dh"):
    observations.append([obs.attrib.get("from"), obs.attrib.get("to"),
                         obs.attrib.get("dist"), obs.attrib.get("val"),
                         obs.attrib.get("stdev")])
print("Found {} points and {} observations in XML files."
      .format(len(coord), len(observations)))

with open(arguments.output) as iFile:
    text = iFile.readlines()
    iFile.close()
adjFixBegin = text.index("Fixed points\n")
adjHgtBegin = text.index("Adjusted heights\n")
adjObsBegin = text.index("Adjusted observations\n")
for i in range(adjFixBegin + 6, adjHgtBegin - 2):
    adjOut = split(" +", text[i].strip())
    coord[adjOut[0]].extend([0.0, coord[adjOut[0]][2], 0.0, 0.0])
for i in range(adjHgtBegin + 6, adjObsBegin - 2):
    adjOut = split(" +", text[i].strip())
    coord[adjOut[1]].extend([adjOut[3], adjOut[4], adjOut[5],
                            adjOut[6]])
outTree = ElementTree.parse(arguments.xmloutput)  
with open(arguments.stations , "w") as out1File:
    out1File.write("WKT\tPoint id\tZ [m]\tZ correction [m]\tZ adjusted [m]\t\
                   std.dev [mm]\tconf.i.[mm]\n")
    for id in coord:
        if len(coord[id]) == 7:
            ptOutput = ("POINT ({} {})\t{}\t{}\t{}\t{}\t{}\t{}\n"
                        .format(coord[id][0], coord[id][1], id, coord[id][2], 
                         coord[id][3], coord[id][4], 
                         coord[id][5], coord[id][6]))
        elif (len(coord[id]) == 3) and (True):
            ptOutput = ("POINT ({} {})\t{}\t{}\tNone\tNone\tNone\tNone\n"
                        .format(coord[id][0], coord[id][1], id, coord[id][2]))
        out1File.write(ptOutput)
    out1File.close()
with open(arguments.distances , "w") as out2File:
    out2File.write("WKT\tidFrom\tidTo\tdist [km]\tval [m]\tstdev [mm]\n") 
    for obs in observations:
        lnOutput = "LINESTRING ({} {}, {} {})\t{}\t{}\t{}\t{}\t{}\n"\
                    .format(coord[obs[0]][0], coord[obs[0]][1], 
                            coord[obs[1]][0], coord[obs[1]][1], 
                            obs[0], obs[1], obs[2], obs[3], obs[4])
        out2File.write(lnOutput)
    out2File.close() 
