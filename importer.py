from exporter import DBManager

class Importer(object):
	def __init__(self):
		self.dbm = DBManager()

	def retrieve_snapshot_data(self, uuid):
		return self.dbm.read_data(uuid)
