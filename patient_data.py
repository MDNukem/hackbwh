from fhirclient.models.bundle import Bundle
from fhirclient.models.address import Address
import logging
import requests
import settings

class PatientData(object):

	def __init__(self, pt_id, patient):
		self.ptid = pt_id
		self.patient_obj = patient
		self.allergies = None
		self.medications = None
		self.demographics = None

	def collect_all(self):
		self._collect_allergies()
		self._collect_medications()
		self._collect_demographics()

		data_object = {'allergies':self.allergies, 'medications':self.medications, 'demographics':self.demographics}
		return data_object

	def _collect_allergies(self):
		''' Collects all allergies and puts all text-based representations of the allergies into a list
		'''
		
		rsession = requests.Session()
		rsession.headers.update({"Accept":"application/json"})
		ar = rsession.get(PatientData._build_search_url(settings.FHIR_ALLERGY_ENDPOINT, patient_id=self.ptid))

		allergy_bundle = Bundle(jsondict=ar.json())
		allergens_display = []

		if allergy_bundle.entry != None:
			for a in allergy_bundle.entry:
				logging.debug("Found an allergy: "+a.resource.substance.text)
				allergens_display.append(a.resource.substance.text)

		self.allergies = allergens_display

	def _collect_medications(self):
		''' Collects all medications and puts all text-based representations of the meds into a list
		'''
		rsession = requests.Session()
		rsession.headers.update({"Accept":"application/json"})
		mr = rsession.get(PatientData._build_search_url(settings.FHIR_MED_ENDPOINT, patient_id=self.ptid))

		med_bundle = Bundle(jsondict=mr.json())
		med_display = []
		if med_bundle.entry != None:
			for m in med_bundle.entry:
				logging.debug("Found a medication: "+m.resource.medicationReference.display)
				med_display.append(m.resource.medicationReference.display)
		
		self.medications = med_display

	def _collect_demographics(self):
		''' Collects demographics '''
		self.demographics = {'address':self.patient_obj.address[0].as_json(), 'first_name':self.patient_obj.name[0].given[0], 'last_name':self.patient_obj.name[0].family[0]}
		

	@staticmethod
	def _build_search_url(url, **kwargs):
		for key, val in kwargs.iteritems():
			if url.count('{{'+key+'}}') > 0:
				url = url.replace('{{'+key+'}}',val)

		return url