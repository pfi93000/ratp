#!/usr/bin/python

# si reinstallation de raspian
# interface graphique raspian
# Raspberry Pi Configuration
# Localisation
#   Set Locale...
#      Language : fr (french)
#      Country : FR (France)
#      Character Set : UTF-8
#   Set Timezone...
#      Area : Europe
#      Location : Paris
#   Set Keyboard...
#      France / French
#   Set WiFi Country...
#      FR France
# Interfaces
#    SSH : Enabled
# System
#   Hostname :
#   Change Password...
# ok and reboot
# icone WiFi dans la barre de taches, et attendre 10 secondes
#  wifi et mot de passe

# echo "mise a jour"
# sudo apt-get update -y
# sudo apt-get upgrade -y
# sudo apt-get dist-upgrade -y
# echo "installation du client SOAP zeep"
# sudo apt-get install python-lxml python-zeep
# echo "installation du lecteur LCD"
# sudo apt-get install build-essential python-dev python-smbus python-pip git
# sudo apt autoremove
# sudo pip install RPi.GPIO
# cd ~
# git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
# cd Adafruit_Python_CharLCD
# sudo python setup.py install

# remplir la demande d'accès à l'API et l'envoyer par mail à la RATP (réponse sous 3 semaines)
# https://data.ratp.fr/page/temps-reel/
# et télécharger le fichier Wsiv.wsdl
# mettre le fichier Wsiv.wsdl dans le répertoire /home/pi/ratp/
# ainsi que les fichiers pin.py et ratp.py
#
# copier ratp.service dans /etc/systemd/system
# systemctl daemon-reload
# systemctl enable ratp.service
# systemctl daemon-reload
# systemctl start ratp.service


# bibliotheque pour permettre de faire une pause
import time

# bibliotheque pour gerer l'ecran LCD
import Adafruit_CharLCD as LCD

# Raspberry Pi pin configuration:
# Define LCD column and row size for 16x2 LCD.
from pin import lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows

# prise de controle de la broche d'alimentation
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) 				# Use BCM GPIO numbers
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.HIGH)
time.sleep(2)


# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

# Print a two line message
lcd.clear()
lcd.message('Bus de Noisy\na Republique')

# bibliotheque pour creer un client SOAP
import zeep

# bibliotheque pour gerer des differences de dates
from datetime import datetime

# le fichier Wsiv.wsdl vient du site de la RATP et decrit toutes les operations realisables par un client SOAP
wsdl = 'file:///home/pi/ratp/Wsiv.wsdl'

# creation d'un client SOAP avec la bibliotheque zeep
client = zeep.Client(wsdl=wsdl)

try:
    # boucle infinie
    while True:
        maintenant = datetime.now()
        if maintenant.hour > 6 and maintenant.hour <11:
        #if True:
            # broche pour alimenter l'ecran LCD
            GPIO.output(27, GPIO.HIGH)
            # initialisation du tableau avec les horaires de passage
            tableau = []
            # initialisation de l'heure de comparaison pour tous les bus
            heure_lecture = datetime.now()
            print(heure_lecture)
            # Define the line object for SOAP
            line_type = client.get_type('ns0:Line')
            for identifiant in ['B303', 'B310', 'B320']:
                line = line_type(id = identifiant)
                
                #print(client.service.getDirections(line))
                
                # Define the station object for SOAP
                station_type = client.get_type('ns0:Station')
                station = station_type(name = 'Republique', line = line)
                
                # Define the direction object for SOAP (A Aller   R Retour   * les 2 sens)
                direction_type = client.get_type('ns0:Direction')
                direction = direction_type(sens = 'R')
                
                # Lecture des horaires
                try:
                    time.sleep(2)
                    print("lecture de la base de donnees RATP")
                    horaire=client.service.getMissionsNext(station, direction)
                    print("Analyse du retour")
                    for i in range(0,len(horaire['missions'])):
                        if horaire['missions'][i]['stationsDates'] != [] :
                            annee = horaire['missions'][i]['stationsDates'][0][0:4]
                            mois = horaire['missions'][i]['stationsDates'][0][4:6]
                            jour = horaire['missions'][i]['stationsDates'][0][6:8]
                            heure = horaire['missions'][i]['stationsDates'][0][8:10]
                            minute = horaire['missions'][i]['stationsDates'][0][10:12]
                            heure_et_minute = heure + ':' + minute
                            #calcul sur les dates avec la bibliotheque datetime
                            passage = datetime(int(annee), int(mois), int(jour), int(heure), int(minute))
                            duree = passage - heure_lecture
                            duree_en_minutes = duree.seconds / 60
                            #print(identifiant + ' ' + heure_et_minute + ' (' + str(duree_en_minutes) + ' mn)')
                            # sauvegarde des lectures dans un tableau, si j'ai assez de temps pour y aller
                            if duree_en_minutes >= 4:
                                tableau.append({ 'duree':duree_en_minutes, 'heure':heure_et_minute, 'id':identifiant, 'doublon':' '})
                                #print('ajout dans le tableau fait')
                except:
                    horaire=[]
            
            # tri du tableau suivant la duree
            tableau.sort(key=lambda trie: trie['duree'])
        
            # efface les doublons
            taille = lcd_rows if len(tableau) > lcd_rows else len(tableau)
            for ligne in range(0,taille): 
                if len(tableau) > ligne:    # attention avec la suppression de lignes...
                    for indice in range(len(tableau)-1,ligne,-1):
                        if tableau[indice]['heure'] == tableau[ligne]['heure']:
                            del tableau[indice]
                            tableau[ligne]['doublon']='+'
            
            # affichage des horaires
            print("effacement de l'ecran")
            lcd.clear()
            taille = lcd_rows if len(tableau) > lcd_rows else len(tableau)
            print("affichage a l'ecran")
            for i in range(0,taille):
                    lcd.message(tableau[i]['id'][1:] + tableau[i]['doublon'] + ' ' + tableau[i]['heure'] + ' ' + str(tableau[i]['duree']) + 'mn\n')
                    print(tableau[i]['id'][1:] + tableau[i]['doublon'] + ' ' + tableau[i]['heure'] + ' ' + str(tableau[i]['duree']) + 'mn\n')
            
            # 2 ou 3 lectures par minute pour rafraichir assez souvent l'ecran
            time.sleep(15)

        else:
            lcd.clear()
            espace = '    '
            if ( maintenant.minute % 4 ) == 1:
                espace = '   '
            if ( maintenant.minute % 4 ) == 2:
                espace = '  '
            if ( maintenant.minute % 4 ) == 3:
                espace = ' '
            lcd.message(espace + str("%02d" % maintenant.day) + '/' + str("%02d" % maintenant.month) + '/' + str(maintenant.year) + '\n' + espace + str("%02d" % maintenant.hour) + 'h' + str("%02d" % maintenant.minute) )
            print(espace + str("%02d" % maintenant.day) + '/' + str("%02d" % maintenant.month) + '/' + str(maintenant.year) + espace + str("%02d" % maintenant.hour) + 'h' + str("%02d" % maintenant.minute) )
            time.sleep(15)
            GPIO.output(27, GPIO.LOW)
            time.sleep(15)

#Gestion des erreurs lors de la boucle    
except KeyboardInterrupt:
        print('interrupted!')

#retour au programme principal

#sortie du programme
GPIO.output(27, GPIO.LOW)
GPIO.cleanup()
