#!/usr/bin/env python3
"""
Functions for:
    -ingesting KMS formated coordinate and observation files and calculate mean
        error on observations.
    -merging coordinates and observations from multiple files.

KMS is used to underline the legacy nature of these functions.

20170329: Code is only tested on leveling data

Created on Wed Mar 29 09:36:55 2017
"""

__version__ = "0.1"
__author__ = "Lars Stenseng"


from re import sub, split, DOTALL, MULTILINE
from math import sqrt


""" Ingest KMS formated coordinate files and return a dictionary of coordinates
with station-id as key. For each station a list is returned with:
    Dimension 1/2/3
    North coord/Elevation
    Unit
    East coord (2D and 3D only)
    Unit (2D and 3D only)
    Elevation (3D only)
    Unit (3D only)
    Station description
    KMS minilabel
    Station comment
"""
def kmsCoord2Dict(inputFileName):
    count = 0
    count1D = 0
    count2D = 0
    count3D = 0
    stations = {}
    with open(inputFileName, mode="r") as iFile:
        text = iFile.read()
        text2 = sub(r'\*.*?;', '', text, flags=DOTALL)
        text3 = sub(r'\s+\n', '\n', text2, flags=MULTILINE)
        lines = text3.split("\n")
        for line in lines:
            count = count + 1
            if line[0:17].strip().startswith("#"):
                kmsLabel = line.strip()
            elif line[0:17].strip().startswith("-1z"):
                kmsLabel = ""
            else:
                stationCoord = []
                stationInfo = []
                stationComment = ""
                stationId = line[0:17].replace(" ", "")
                stationDesc = line[18:21].replace(" ", "")
                count = count + 1
                cols = split("  +", line[21:].strip())
                for element in cols:
                    if element.strip().endswith((" m", " dg", " rad")):
                        value = "".join(element.strip().split(" ")[:-1])
                        unit = element.strip().split(" ")[-1]
                        stationCoord.append(value)
                        stationCoord.append(unit)
                    if element.strip().endswith((" sx", " nt")):
                        value = element.strip()
                        unit = element.strip().split(" ")[-1]
                        stationCoord.append(value)
                        stationCoord.append(unit)
                if len(stationCoord) == 2:
                    count1D = count1D + 1
                    stationComment = cols[1:]
                elif len(stationCoord) == 4:
                    count2D = count2D + 1
                    stationComment = cols[2:]
                elif len(stationCoord) == 6:
                    count3D = count3D + 1
                    stationComment = cols[3:]
                if len(stationCoord) > 0:
                    stationInfo.append(stationDesc)
                    stationInfo.append(kmsLabel)
                    stations[stationId] = [int(len(stationCoord)/2),
                                           stationCoord, stationInfo,
                                           stationComment]
    print("Read {} lines with {} 1D, {} 2D, and {} 3D coordinates from {}"
          .format(count, count1D, count2D, count3D, inputFileName))
    return stations


""" Ingest KMS formated observations files and return a list of observations.
For each station a list is returned with:
    Station occupation
    Station target
    Observation
    Distance
    Calculated mean error
    No. of sets
    Journal no.
    Observation year
    Observation date
"""
def kmsObs2List(inputFileName):
    count = 0
    countObs = 0
    obsInfo = []
    with open(inputFileName, mode="r") as iFile:
        text = iFile.read()
        text2 = sub(r'\*.*?;', '', text, flags=DOTALL)
        text3 = sub(r'\s+\n', '\n', text2, flags=MULTILINE)
        lines = text3.split("\n")
        for line in lines:
            count = count + 1
            obsCol = split("  +", line.strip())
            if line[0:12].strip().startswith("#"):
                kmsLabelCol = split(" +", line.strip())
                kmsLabel = kmsLabelCol[0]
                obsErrorType = kmsLabelCol[2]
                obsErrorMd = float(kmsLabelCol[1])
                obsErrorMc = float(kmsLabelCol[3])
            elif line[0:12].strip().startswith("-1a"):
                kmsLabel = ""
                stationFrom = ""
            elif obsCol[0].strip() != "":
                if obsCol[0].strip().endswith("a"):
                    stationFrom = (obsCol[0].replace("a", "").replace(" ", "")
                                  .strip())
                    obsYear = obsCol[1].strip()
                    obsSets = float( obsCol[2].replace(" ", "").strip() )
                    obsJournalNo = obsCol[3].strip()
                else:
                    countObs += 1
                    stationTo = obsCol[0].replace(" ", "").strip()
                    obsValue = (float(obsCol[1].replace("m", "")
                                .replace(" ", "")))
                    obsDist = (float(obsCol[2].replace("m", "")
                               .replace(" ", "")) / 1000.0)
                    obsDate = obsCol[3].strip()
                    obsSetUps = float(obsCol[4].replace(" ", "").strip())
                    if obsErrorType == "ne":
                        obsStdev = sqrt((obsErrorMd**2 * obsDist
                                        + obsErrorMc**2)
                                        / obsSets)
                    elif obsErrorType == "ppm":
                        obsDistSingle = (obsDist - 2 * 0.025) / (obsSetUps - 1)
                        obsStdev = sqrt((obsErrorMd**2 \
                                        * (2 * 0.025**2 + (obsSetUps - 1)
                                        * obsDistSingle**2)
                                        + obsErrorMc**2) / obsSets)
                    obsInfo.append([stationFrom, stationTo, obsValue, obsDist,
                                     obsStdev, obsSets, obsJournalNo, obsYear,
                                     obsDate, kmsLabel, obsErrorMd,
                                     obsErrorType, obsErrorMc])
    print("Read {} lines with {} observations from {}"
          .format(count, countObs, inputFileName))
    return obsInfo


def kmsMergeCoords(kmsDictList):
    stations = {}
    for kmsDict in kmsDictList:
        for id, data in kmsDict.items():
            if data[0] == 1:
                if id in stations:
                    stations[id][3] = data[1][0]
                    if stations[id][0] == 2:
                        stations[id][0] = 3
                else:
                    stations[id] = [data[0], 0.0, 0.0, data[1][0]]
            elif data[0] == 2:
                if id in stations:
                    stations[id][3] = data[1][0]
                    if stations[id][0] == 1:
                        stations[id][1] = data[1][0]
                        stations[id][2] = data[1][2]
                else:
                    stations[id] = [data[0], data[1][0], data[1][2], 0.0]
            elif data[0] == 3:
                stations[id] = [data[0], data[1][0], data[1][2], data[1][4]]
    return stations

if __name__ == "__main__":
    koter = kmsCoord2Dict("/Users/stens/Code/Python/KMS2GAMA-xml/koter")
    koordinater = kmsCoord2Dict("/Users/stens/Code/Python/KMS2GAMA-xml/koordinater")
    print("")

    coordList=[]
    coordList.append(koordinater)
    coordList.append(koter)
    joinCoord = kmsMergeCoords(coordList)

    for id in ["G.M.182/183", "G.M.644", "134-10-09039"]:
        print(id)
        print(koordinater[id])
        print(koter[id])
        print(joinCoord[id])
        print("")

    r_vand = kmsObs2List("/Users/stens/Code/Python/KMS2GAMA-xml/r_vand")
    r_obs = kmsObs2List("/Users/stens/Code/Python/KMS2GAMA-xml/r_obs")
    joinr = []
    joinr.extend(r_vand)
    joinr.extend(r_obs)

    print(r_vand[0])
    print(joinr[0])
    print(r_obs[-1])
    print(joinr[-1])

