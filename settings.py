FHIR_ENDPOINT = 'https://open-ic.epic.com/FHIR/api/FHIR/DSTU2/'

FHIR_PATIENT_ENDPOINT = FHIR_ENDPOINT + 'Patient/{{patient_id}}'

FHIR_SEARCH_PATIENT_FULLNAME = FHIR_ENDPOINT+'Patient?family={{last_name}}&given={{first_name}}'
FHIR_SEARCH_PATIENT_FAMILYNAME = FHIR_ENDPOINT+'Patient?family={{last_name}}'
FHIR_SEARCH_PATIENT_MRN = FHIR_ENDPOINT+'Patient?identifier={{mrn}}'

FHIR_ALLERGY_ENDPOINT = FHIR_ENDPOINT + 'AllergyIntolerance?patient={{patient_id}}'
FHIR_MED_ENDPOINT = FHIR_ENDPOINT + 'MedicationOrder?patient={{patient_id}}&status=active'


MAIL_ENDPOINT = 'https://api.mailgun.net/v3/sandbox6db6e8f7e49b43d998cd964d1169a560.mailgun.org/messages'
MAIL_AUTH = ("api", "key-c0b62784c7b865fa07c0040cf8e34a00")


DOCDB_PRIMARY_KEY = '/1hLi17UMpT7k3lMVJzaPG97h/z02Szzd/9/S6O8EdQLMNZ7VlwIta82RIVYMLrzXY54hydSa06LH2TEswgFxw=='
DOCDB_URI = 'https://bwhdischarger.documents.azure.com:443/'
DOCDB_CXNSTR = 'AccountEndpoint='+DOCDB_URI+';AccountKey='+DOCDB_PRIMARY_KEY+';'
DOCUMENTDB_DATABASE = 'permalinks'
DOCUMENTDB_COLLECTION = 'dischargeData'
