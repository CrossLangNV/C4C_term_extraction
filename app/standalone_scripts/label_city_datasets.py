"""
this is the basic version of data labeling for sentence classification
"""
import argparse
import re

life_events_de = ['Datum und Zeit','Schritte', 'Registrierung', 'Unternehmens', 'Steuernummer', 'Antrag', 'Einstellung von Mitarbeitern', 'Beantragung', 'Beantragung von Genehmigungen', 'Körperschaftsteuererklärung', 'Regelmäßiger Geschäftsbetrieb', 'Vorlage von Finanzberichten', 'Unternehmensgründung', 'Job verlieren', 'arbeitslos', 'registrieren', 'Hilfsdienste', 'Schulungsprogramme', 'Studieren', 'Registrierungsprozess', 'Antragsverfahren für Studentendarlehen', 'Finanzierungsprogramme', 'Noten', 'Unterhaltsgeld', 'Online-Rentenansprüche', 'Ruhestand', 'Reisepasses', 'Ersatzgeburtsurkunde', 'Unterhaltsgeld', 'Gewalt', 'unverheiratete', 'Unfall', 'Rechtsanspruch', 'Schadensersatz', 'Berücksichtigung', 'Zulassungspflichten', 'Versicherungspflichten', 'Adresse', 'Gemeinderegister']
life_events_fr = ['date et l\'heure', 'étapes', 'enregistrement', 'entreprises', 'numéro d\'identification fiscale', 'embauche d\'employés', 'demande de permis', 'déclaration de revenus des sociétés','opération commerciale régulière', 'soumission de rapport financier', 'création d\'entreprise', 'perte d\'emploi', 'chômage', 'inscription','soutien', 'programmes de formation', 'études','financement', 'pension', 'retraite', 'passeport', 'acte de naissance', 'pension alimentaire', 'indemnisation', 'contrepartie', 'obligations d\'autorisation', 'obligations d\'assurance']
life_events_nl = ['datum en tijd', 'registratie', 'bedrijf', 'belastingnummer', 'aanvraag', 'werknemers inhuren', 'aanvragen', 'vergunning', 'aangifte','vennootschapsbelasting', 'bedrijfsvoering', 'financiële rapporten', 'bedrijf starten', 'baan verliezen', 'werklozen',  'studeren', 'registratieproces', 'aanvraagprocedure','studieleningen', 'financieringsprogramma','cijfers','alimentatie', 'pensioenrechten', 'pensioen', 'paspoort', 'vervangende geboorteakte', 'alimentatie', 'geweld', 'ongehuwd', 'ongeval', 'rechtsvordering', 'compensatie', 'tegenprestatie','verzekering','adres ','gemeenteregister ']
url_pattern = ['www', 'http', '\.com']
phone_pattern = ["^(?:(?:\(?(?:00|\+)([1-4]\d\d|[1-9]\d?)\)?)?[\-\.\ \\\/]?)?((?:\(?\d{1,}\)?[\-\.\ \\\/]?){0,})(?:[\-\.\ \\\/]?(?:#|ext\.?|extension|x)[\-\.\ \\\/]?(\d+))?$"]
phone_pattern = ["^(?:(?:\(?(?:00|\+)([1-4]\d\d|[1-9]\d?)\)?)?[\-\.\ \\\/]?)?((?:\(?\d{1,}\)?[\-\.\ \\\/]?){0,})(?:[\-\.\ \\\/]?(?:#|ext\.?|extension|x)[\-\.\ \\\/]?(\d+))?$"]
other_pattern = ['euro', 'Euro', '$', '€', '£', '@']
position_pattern_de = ['strasse', 'straße', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September','Oktober', 'November', 'Dezember', 'Uhr']
position_pattern_nl = ['straat', 'januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december', 'uur']
position_pattern_fr = ["rue", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre", "heure"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--lang')
    args = parser.parse_args()
    if args.lang == 'DE':
        PATTERNS = life_events_de + url_pattern + phone_pattern + other_pattern + position_pattern_de
    elif args.lang == 'FR':
        PATTERNS = life_events_fr + url_pattern + phone_pattern + other_pattern + position_pattern_fr
    elif args.lang == 'NL':
        PATTERNS = life_events_nl + url_pattern + phone_pattern + other_pattern + position_pattern_nl

    with open(args.input) as tf, open(args.output, 'a') as wf:
        for line in tf:
            valid = False
            for pattern in PATTERNS:
                match = re.compile(pattern).findall(line)
                if match != [] and any(x != '' for x in match):
                    valid = True
                    break  # one valid match is enough
            if valid:
                wf.write('1\n')
            else:
                wf.write('0\n')
    wf.close()
    tf.close()