Readme - Pub fil ved brug af Gnu-Gama
-Simon Krarup Steensen

Lars Stensengs script gamaAdJKMS.py
	-Brug gamaAdjKMS_modified.py
	-output er setup_modified.xml, hvor description tagget er brugt
	-Description passeres uændret igennem Gnu-Gama og i setup_modified.xml bare en string
	-Den indeholder årstal for målinger, såvel som tidspunkt(dato,tidspunkt) for alle fiks-punkter
	-I "modified" versionen så er linje 71 til 105 indsat. Såvel som description tag i gamaXMLTemplate

output_to_pubdvr90.py
	-Opstiller hele pub filen udfra filen out_modified.xml, modified version indeholder description tag.
	-Argument for path of navn på input filen (out_modified.xml)
	-Argument for ønsket path og navn på pub-filen
	-Filen matcher slutningen af strings med tags i rødderne af xml-filen. Dette vil derfor være uændret
		i tilfælde af nyt introduceret lignende tag
	-description ændres til en dictionary, så hvert årstal(tidspunkt for fiks) kan hentes med navnet som nøgle
	-Tidspunkt for Gnu-Gama udregning, hentes via file_path på xml filen
	-Diagonal elementer fra covarians matricen har samme rækkefølge som resten af dataen.
	-Stadig uvist, hvad original index tagget i xml filen egentlig betyder


