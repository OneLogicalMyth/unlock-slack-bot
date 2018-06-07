import sqlite3
import datetime

class database(object):

	def __init__(self):
		self.db = sqlite3.connect('data.db')
		self.setup()

	def setup(self):
		with self.db:
			self.db.execute('CREATE TABLE IF NOT EXISTS unlocked(id INTEGER PRIMARY KEY, userid TEXT, name TEXT, count INT)')

	def close(self):
		self.db.close()

	def add_unlocked(self,userid,name):
		with self.db:
			self.db.execute("INSERT INTO unlocked(userid,name,count) VALUES(:userid,:name,:count)",{'userid':userid,'name':name,'count':1})

	def update_unlocked(self,userid,name,count):
		with self.db:
			self.db.execute('UPDATE unlocked SET name=:name, count=:count WHERE userid=:userid',{'userid':userid,'name':name,'count':count})

	def get_unlocked(self,userid=None):
		self.db.row_factory = lambda C, R: { c[0]: R[i] for i, c in enumerate(C.description) }
		cur = self.db.cursor()

		if not userid:
			cur.execute("SELECT userid, name, count FROM unlocked")
		else:
			cur.execute('SELECT userid, name, count FROM unlocked WHERE userid=:userid', {'userid':userid})

		result = cur.fetchall()

		return result
