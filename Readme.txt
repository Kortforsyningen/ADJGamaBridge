Readme - Pub fil ved brug af Gnu-Gama
-Simon Krarup Steensen

Lars Stensengs script gamaAdJKMS.py
	-Brug gamaAdjKMS_modified.py
	-output er setup_modified.xml, hvor description tagget er brugt
	-Description passeres u�ndret igennem Gnu-Gama og i setup_modified.xml bare en string
	-Den indeholder �rstal for m�linger, s�vel som tidspunkt(dato,tidspunkt) for alle fiks-punkter
	-I "modified" versionen s� er linje 71 til 105 indsat. S�vel som description tag i gamaXMLTemplate

output_to_pubdvr90.py
	-Opstiller hele pub filen udfra filen out_modified.xml, modified version indeholder description tag.
	-Argument for path of navn p� input filen (out_modified.xml)
	-Argument for �nsket path og navn p� pub-filen
	-Filen matcher slutningen af strings med tags i r�dderne af xml-filen. Dette vil derfor v�re u�ndret
		i tilf�lde af nyt introduceret lignende tag
	-description �ndres til en dictionary, s� hvert �rstal(tidspunkt for fiks) kan hentes med navnet som n�gle
	-Tidspunkt for Gnu-Gama udregning, hentes via file_path p� xml filen
	-Diagonal elementer fra covarians matricen har samme r�kkef�lge som resten af dataen.
	-Stadig uvist, hvad original index tagget i xml filen egentlig betyder


