from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
import settings, logging
from exporter import Exporter
from importer import Importer
from exporter import FhirParser

app = Flask(__name__)


@app.route("/")
def export_page():
    return render_template('home_page.html')

@app.route("/search", methods=['GET'])
def search():
	search_term = request.args.get('query','')
	if search_term != '':
		patient_results = Exporter.search(search_term)
		patient_html_data = FhirParser.parse_results_for_html(patient_results)

		return render_template('search_results.html', search_term=search_term, results=patient_html_data)
	else:
		return redirect(url_for('export_page'))

@app.route("/export", methods=['GET'])
def export_patient():
	patient_id = request.args.get('pt_id','')
	exporter = Exporter(patient_id)
	page_resource = exporter.export_page_resource()

	return render_template('export_page.html', patient=page_resource, id=patient_id)

@app.route("/send", methods=['GET'])
def send_doc():
	patient_id = request.args.get('pt_id','')
	recipient = request.args.get('addr','')
	logging.debug("Sending email for patient id "+patient_id)
	exporter = Exporter(patient_id)
	exporter.collect_data(recipient)

	return render_template('success_page.html')

@app.route("/discharges/<uuid>", methods=['GET'])
def get_discharge_page(uuid):
	data_importer = Importer()
	snapshot_data = data_importer.retrieve_snapshot_data(uuid)
	if snapshot_data == None:
		return render_template('patient_not_found.html')
	else:
		logging.debug(str(snapshot_data))
		return render_template('discharge_page.html', discharge_data=snapshot_data)

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	logging.debug('Starting Export Demo')
	app.run(debug=True)