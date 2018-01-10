#!/usr/bin/python3
from ftplib import FTP
from ftplib import FTP_TLS
from ssl import *
import argparse, os
from pathlib import Path


class FTPClient_Control:

	def __init__ (self, host, user=None, passwd=None, verbose = 1, action=True):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.verbose = verbose
		self.path = str(Path.home())+'ftp/files/'
		self.action = action

	def ftp_connect(self):
		'''
		Connects to the ftp server, prints banner and quits.
		'''
		try:
			with FTP(host=self.host, user=self.user, passwd=self.passwd) as ftp:
				ftp.set_debuglevel(self.verbose)			
				ftp.prot_p()
				ftp.getwelcome()
				self.__actionLoop__(ftp)
				ftp.quit()

		except Exception as e:
			print(str(e))		

	def secure_ftps(self):	
		'''
		creates a secure ftp connection. Uses default credentials.
		prints banner and quits.
		'''
		auth = create_default_context(purpose=Purpose.CLIENT_AUTH)
		
		try:
			with FTP_TLS(host=self.host, user=self.user, passwd=self.passwd, context=auth) as ftp:
				ftp.set_debuglevel(self.verbose)
				ftp.prot_p()
				ftp.getwelcome()
				if self.action: self.__actionLoop__(ftp)

		except Exception as e:
			print(str(e))

	def upload(self, ftp, file, path=None):
		ext = os.path.splitext(file)[1]
		try:
			if ext in ('.txt', '.htm', '.html'):
				ftp.storlines('STOR ' + file, open(file))
			else:
				ftp.storbinary('STOR ' + file, open(file, 'rb'), 1024)	
		except Exception as e:
			print(str(e))		

	def getFile(self, ftp, file):
		try:
			ftp.retrbinary('RETR ' + file, open(file, 'wb').write)
		except Exception as e:
			print(str(e))
	
	def mkDir(self, ftp):
		print('Name of new directory?')
		name = input('> ')
		ftp.mkd(name)

	def remove(self, ftp):
		'''
		This one needs fixing
		'''
		print('Name of file or dir to be removed?')
		name = input('> ')
		file_check = self.__is_dir__(ftp, name)
		if file_check:
			ftp.rmd(name)
			print (file_check)
		else:
			ftp.delete(name)	

	def rename(self, ftp):
		print('Which would you like to rename?')
		current = input('File Name: ')
		new = input('New name: ')
		ftp.rename(current,new)

	
	def __is_dir__(self, ftp, file):
		'''
		This attempt is based on size, then on 
		parsed data. 
		'''
		file_check = ftp.sendcmd('MLST '+ path + file)
		if ftp.size(file) == None:
			return True	 
		elif 'type=dir;' in file_check: 
			return True
		else:
			return False	


	def __actionLoop__(self, ftp):
		validate = self.action
		while validate:
			print(ftp.nlst())
			print('''
				Next step?
				Commands: DwnL, UpL, ChDir, Rem, Make, Exit''')
			comm = input('> ')
			command = comm.lower()			
			if command == 'dwnl':
				print('Which File or Folder?')
				get = input('> ')
				self.getFile(ftp, get)
			elif command == 'upl':
				print('Which File or Folder?')
				upl = input('> ')
				self.upload(ftp, upl)
			elif command == 'chdir':
				print('Which Directory?')
				chng = input('> ')
				ftp.cwd(chng)
			elif command == 'rem':
				self.remove(ftp)
			elif command == 'make':
				self.mkDir(ftp)		
			elif command == 'exit':
				validate = False
				ftp.quit()			



def parser():
	'''
	Command Line Parser. All optional except --host.
	'''
	parser = argparse.ArgumentParser(usage="%(prog)s --host <host name> --user <user name> --pass <password>")
	parser.add_argument('--host', required=True, dest="host", help="The address or ip address of the desired ftp server. REQUIRED")
	parser.add_argument('--user', dest="user", help="The username to access the desired ftp server. Optional")
	parser.add_argument('--pass', dest="passwd", help="The password to access the desired ftp server. Optional")
	parser.add_argument('--secure', dest = "secure", action="store_true", help = 'Connect to a secure (sftp or ftps) server. Optional')
	parser.add_argument('--verbose', nargs='?', dest = 'verbose', default=1, const=2, help="Makes the client print more information about each ftp transfer/connection. Optional")
	args = parser.parse_args()

	client = FTPClient_Control(host, args.user, args.passwd, args.verbose)
	if not args.host:
		print(parser.print_help())
	elif args.secure:
		client.secure_ftps()
	else:	
		client.ftp_connect()

if __name__ == '__main__':
	parser()	
