from database import database

class unlocked(object):

	def connect(self):
		self.db = database()


	def unlocked(self,userid,name):
		self.connect()
		data = self.db.get_unlocked(userid)
		if data:
			new_count = int(data[0]["count"]) + 1
			self.db.update_unlocked(userid,name,new_count)
		else:
			new_count = 1
			self.db.add_unlocked(userid,name)
		self.db.close()

		return "<@" + userid + "> You have been marked as leaving your machine unlocked and unattended. Your new count is " + str(new_count) + ". :zany_face:"


	def stats(self):
		self.connect()
		data = self.db.get_unlocked()
		userlist = ""
		if data:
			for user in data:
				if user["count"] > 0:
					userlist += "" + user["name"] + ": Your current unlocked count is " + str(user["count"]) + ".\n"

			if not userlist == "":
				response = userlist
		else:
			response = "Appears everyone is being well behaved and not left their workstations unlocked. :disappointed:"
		self.db.close()

		return response
