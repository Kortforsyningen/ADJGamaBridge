# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 11:16:55 2017

@author: b035777 - Simon Krarup Steensen

"""
#Tidstagning brugt i starten til at teste fart af forskellige metoder
#import time                                                                    
#startTime = time.time()    

import datetime
import os
import xml.etree.ElementTree as ET
from math import sqrt
import argparse

parser = argparse.ArgumentParser()
#Defining name and path of the input xml file
parser.add_argument("path_input", help="Path of output file from Gnu-Gama", type=str)                   
#Defining name and path of the pub text file
parser.add_argument('pub_out', help='Full path(and name) of the text pub file', type=str)               

args = parser.parse_args()

#script_dir = os.path.dirname(__file__)
#print script_dir
#folder = 'examples'
#sub_folder = 'vestkyst'
#filename = 'output_modified.xml'
#file_path_out = os.path.join(script_dir , folder , sub_folder , filename)

path_input = args.path_input
file_path_out = os.path.join(path_input)

"""
Åbner træet og arbejder derefter med rødderne for at finde de nødvendige data
"""
tree = ET.parse(file_path_out)
root = tree.getroot()

index = 0
#Finder nødvendige index til sub_roots, upåvirket ved nye elementer i out.xml filen
for child in root:                                                              
#Bruger endswith, og medtager }, hvis nu et andet tag som slutter på det samme introducres
    if child.tag.endswith('}coordinates'):                                      
        coor_sub_root_ind = index
        coor_sub_root = child
    if child.tag.endswith('}network-processing-summary'):
        network_para_sub_root_ind = index
        network_para_sub_root = child
#    print child
    if child.tag.endswith('}description'):
        description_index = index
#        description_sub_root = child
    
    index = index + 1    
index = 0

description = root[description_index].text
#Description tagget som er passeret gennem GnuGama laves til en dictionary
description_dict = dict(e.split(':') for e in description.split(','))           

#De 3 loops kommer frem det totale z-count, altså antal koder til indlæsning
for child in network_para_sub_root:                                             
    if child.tag.endswith('}coordinates-summary'):
        for child in child:
            if child.tag.endswith('}coordinates-summary-adjusted'):
                for line in child:
                    if line.tag.endswith('}count-z'):
                        num_of_elements = int(line.text)
#                        print (num_of_elements)
                        break                
    index = index + 1
index=0

#Loop som finder index for de forskellige subroots der skal bruges
for child in coor_sub_root:                                                     
    if child.tag.endswith('}adjusted'):                                         
        adj_subsub_root_ind = index
#        print child.tag
    if child.tag.endswith('}fixed'):
        fixed_subsub_root_ind = index
#        print child.tag
    if child.tag.endswith('}cov-mat'):
        cov_subsub_root_ind = index
#        print child.tag
    if child.tag.endswith('}original-index'):                                   
        #Bruges pt. ikke. Det er ikke index til cov-mat!
        ori_subsub_root_ind = index
#        print child.tag
    index = index + 1

original_index = []
for line in coor_sub_root[ori_subsub_root_ind]:                                 
    original_index.append(int(line.text))

#Gemmer alle elementer i cov-mat,
cov = []
for line in coor_sub_root[cov_subsub_root_ind]:                                 
    #Bortset fra linjer der ikke slutter på flt. Siden den indeholder stadard linjer om størrelse
    if line.tag.endswith('}flt') is False:                                      
        continue                                                            
        #Næste step i loop
    cov.append(float(line.text))
                
pub_name = args.pub_out 
#f = open('pubdvr_xml2text', 'w')
f = open(pub_name, 'w')
f.write('#DK_wor   DK_h_dvr90\n')                                               
        
#Tager tidspunkt for tidspunkt på out filen
file_time_unix = os.path.getmtime(file_path_out)                                
#Unix tid ønsket format
gnu_gama_time = datetime.datetime.fromtimestamp(int(file_time_unix)).strftime('%Y%m%d,%H.%M')   

f.write('beregningsdato    ' + str(gnu_gama_time) + '\n')
f.write('prodnr       4081\nbnorm           0\n')
f.write('\n\n')

#Nedskriver x-antal fix punkter. Øverste fix-punkts linjer
for line in coor_sub_root[fixed_subsub_root_ind]:                               
    year = description_dict[line[0].text+'f']
    f.write('{:>17s}'.format( line[0].text))
    f.write('{:>14.5f}m  {}    {}\n'.format(round( float(line[1].text), 5), year ,
    description_dict['fix_date'+line[0].text] + ',' + description_dict['fix_time' + line[0].text] ))
#description_dict['fix_time']
f.write('\n\n-1x\n')

i=0
#Loopet indskriver alle datapunkterne
for line in root[coor_sub_root_ind][adj_subsub_root_ind]:                       
    #Tager dict fra description til at finde årstallet
    year = description_dict[line[0].text]                                       
    
    if line[0].text[0:2].endswith('-'):                                         
        #Data punkter med kun et bogstav f.eks K, bliver K + mellemrum og resten
        line[0].text=line[0].text[0] + ' ' + line[0].text[1:]                               
    f.write('{:>17s}{:>14.5f}m'.format( line[0].text , float(line[1].text)))
    f.write('{:^8} {:08} {:02} {}'.format(year , 00000000 , 2, 1))
                                
    #Antager samme rækkefølge i cov-matn som data, hvilket er den rigtige metode
    sigma = sqrt(cov[i])                                                        
    sigma_app = int(round( sigma , 0 ))
    f.write(' {:03}\n'.format(sigma_app))
    #i bruges som index i listen med original index
    i=i+1                                                                       

f.write('-1z')
f.close()

 #printer tiden for script eksekvering
#print ('The script took {} seconds!'.format(time.time() - startTime))         
