import settings
import requests
import logging, uuid
from fhirclient.models.patient import Patient
from patient_data import PatientData
import pydocumentdb.document_client as document_client

class DBManager(object):
	def __init__(self):
		self.client = document_client.DocumentClient(settings.DOCDB_URI,
                                                {'masterKey': settings.DOCDB_PRIMARY_KEY})
        

		self.db = next((data for data in self.client.ReadDatabases() if data['id'] == settings.DOCUMENTDB_DATABASE))
		self.coll = next((coll for coll in self.client.ReadCollections(self.db['_self']) if coll['id'] == settings.DOCUMENTDB_COLLECTION))

	def store_data(self, data):
		self.client.CreateDocument(self.coll['_self'], data)

class FhirParser(object):
	@staticmethod
	def parse_response(response):
		'''
		Returns a tuple containing (patient model, full url to patient) 
		'''

		res_obj = response.json()
		results_list = res_obj.get('entry', [])
		results = []
		for patient in results_list:
			ptlink = patient['fullUrl']
			newpt = Patient(jsondict=patient['resource'])
			
			results.append( (newpt, ptlink) )

		return results
	
	@staticmethod
	def parse_results_for_html(results):
		retval = []
		for r in results:
			retval.append(
					{'name': FhirParser.get_patient_name(r[0]), 'id':FhirParser._get_id(r[1])}
				)
		return retval

	@staticmethod
	def _get_id(fullurl):
		t = fullurl.rpartition('/')
		return t[2]

	@staticmethod
	def get_patient_name(patient):
		''' Accepts a FHIR Patient resource and their name in <first last> format '''
		name = patient.name[0].given[0] + " " + patient.name[0].family[0]
		return name

	def __init__(self):
		pass

class Exporter(object):

	@staticmethod
	def _build_search_url(url, **kwargs):
		for key, val in kwargs.iteritems():
			if url.count('{{'+key+'}}') > 0:
				url = url.replace('{{'+key+'}}',val)

		return url

	@staticmethod
	def _search(**kwargs):
		''' Search for a patient using given, family, and mrn 
		
		:param: given The patient's given name.
		:param: family The patient's family name.
		:param: mrn The patient's medical record number.
		'''
		
		mrn = None
		given_name = None
		family_name = None

		for key,val in kwargs.iteritems():
			if key == 'mrn':
				mrn = val
			elif key == 'given':
				given_name = val
			elif key == 'family':
				family_name = val

		rsession = requests.Session()
		rsession.headers.update({"Accept":"application/json"})

		if mrn != None:
			req_url = Exporter._build_search_url(settings.FHIR_SEARCH_PATIENT_MRN, mrn=mrn)
			logging.debug('MRN Search URL='+str(req_url))
			return rsession.get(req_url)

		if given_name != None and family_name != None:
			req_url = Exporter._build_search_url(settings.FHIR_SEARCH_PATIENT_FULLNAME, last_name=family_name, first_name=given_name)
			return rsession.get(req_url)

		elif family_name != None:
			req_url = Exporter._build_search_url(settings.FHIR_SEARCH_PATIENT_FAMILYNAME, last_name=family_name)
			return rsession.get(req_url)
		
		return None

	@staticmethod
	def search(query):
		logging.debug('Searching for "'+str(query)+'"')
		results = None

		if query.isdigit():
			#Search for MRN
			results = Exporter._search(mrn=query)
			logging.debug('MRN Search:\n'+str(results))
		else:
			#Search for patient name
			q_parts = query.split(' ')
			if len(q_parts) > 1:
				fname = q_parts[0]
				lname = q_parts[1]
				results = Exporter._search(given=fname, family=lname)
			else:
				#They only put one name part in - search for a last name
				name = q_parts[0]
				results = Exporter._search(family=name)

		if results != None:
			results = FhirParser.parse_response(results)

		return results
	
	@classmethod
	def get_resource_for_id(classtype, id):
		rsession = requests.Session()
		rsession.headers.update({"Accept":"application/json"})

		patient_rsrc = rsession.get(Exporter._build_search_url(settings.FHIR_PATIENT_ENDPOINT, patient_id=id))

		return Patient(jsondict=patient_rsrc.json())


	def __init__(self, patient_id):
		self.pt_id = patient_id

	def patient_resource(self):
		return self.get_resource_for_id(self.pt_id)


	def export_page_resource(self):
		pt = self.patient_resource()

		resource = {'name': FhirParser.get_patient_name(pt), 'patient':pt}

		return resource


	def collect_data(self):
		'''Collects all of the data that we want the PCP to access and stores it in our DB 
		'''
		dbm = DBManager()
		pd = PatientData(self.pt_id, self.patient_resource())
		doc_to_push = pd.collect_all()
		doc_to_push['id'] = str(uuid.uuid4())
		dbm.store_data(doc_to_push)

	def _send_email(self):
		pass
        


