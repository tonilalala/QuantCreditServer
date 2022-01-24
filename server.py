import socket
import argparse
import threading 
from model import TickersTracker
import time
import warnings
warnings.filterwarnings("ignore")
parser = argparse.ArgumentParser(description = "This is the server for the multithreaded socket demo!")
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostname())
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 8888)
parser.add_argument('--tickers', metavar = 'tickers', type = str, nargs = '?', default = 'AAPL,IBM')
parser.add_argument('--filenames', metavar = 'filenames', type = str, nargs = '?', default = '')
parser.add_argument('--minutes', metavar = 'minutes', type = int,  default = 5)

def on_new_client(client, connection, tickers_tracker):
	ip = connection[0]
	port = connection[1]
	print(f"THe new connection was made from IP: {ip}, and port: {port}!")
	while True:
		msg = client.recv(1024)
		if msg.decode() == 'exit':
			break
		try:
			instruction = msg.decode().split(" ")
			print(instruction)
		except Exception as e:
			reply = "Message error: " + e
		# client --price
		if instruction[0] != "client":
			reply = "Message must start with 'client'! Try again!"
		elif instruction[1] == "--price":
			reply = tickers_tracker.query_price_by_time(instruction[2])

		elif instruction[1] == "--signal":
			reply = tickers_tracker.query_signal_by_time(instruction[2])
		elif instruction[1] == "--del_ticker":
			status = tickers_tracker.del_ticker(instruction[2])
			reply = "Delete ticker {symbol}, Return Code: {code}".format(symbol=instruction[2], code=status)

		elif instruction[1] == "--add_ticker":
			status = tickers_tracker.add_ticker(instruction[2])
			reply = "Add ticker {symbol}, Return Code: {code}".format(symbol=instruction[2],code=status)
		elif instruction[1] == "--reset":
			status = tickers_tracker.reset()
			if status == 1:
				reply = "Reset Error! Return Code: {code}, maybe exceed API limitation, try later!".format(code=status)
			else:
				reply = "Reset successfully! Return Code: {code}".format(code=status)
		else:
			reply = "Invalid message! Try again!"

		client.sendall(reply.encode('utf-8'))
	print(f"The client from ip: {ip}, and port: {port}, has gracefully diconnected!")
	client.close()

def dynamic_update_tracker(interval, tickers_tracker):
	while True:
		time.sleep(interval * 60)
		tickers_tracker.update_tickers()

if __name__ == '__main__':

	args = parser.parse_args()
	print(f"Running the server on: {args.host} and port: {args.port}")
	# init ticker tracker
	if args.filenames.split(",")[0] == "":
		file_names = []
	else:
		file_names = args.filenames.split(",")
	assert args.minutes in [5,15,30,60]
	tickers_tracker = TickersTracker(symbols=args.tickers.split(","), interval=args.minutes, filenames=file_names)
	# updating thread
	t = threading.Thread(target=dynamic_update_tracker, args=(args.minutes, tickers_tracker))
	t.start()

	# socket thread connect with client
	sck = socket.socket()
	sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		sck.bind((args.host, args.port))
		sck.listen(5)
	except Exception as e:
		raise SystemExit(f"We could not bind the server on host: {args.host} to port: {args.port}, because: {e}")
	while True:
		try:
			client, ip = sck.accept()
			threading._start_new_thread(on_new_client, (client, ip, tickers_tracker))
		except KeyboardInterrupt:
			print(f"Gracefully shutting down the server!")
			exit()
		except Exception as e:
			print(f"Error: {e}")
			exit()
	sck.close()