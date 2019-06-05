import os
import socket
import select
import time
from optparse import OptionParser

def reConnect(raddr, rport):
	remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try :
		remote.connect((raddr, rport))
		return remote
	except Exception as reason:
		print("connect error: %s" %(reason))
		return False

def portMap(laddr, lport, raddr, rport):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	closed = True

	# 监听端口
	try :
		server.bind((laddr, lport))
		server.listen(4)
		print("listen on %s %s" %(laddr, lport))
	except Exception as reason:
		print("bind failed: %s" %(reason))
		exit(0)

	rlist = [server]
	# 循环调用
	while True:
		# 连接端口
		if closed :
			remote = reConnect(raddr, rport)
			if remote :
				closed = False
			else :
				time.sleep(3)
				continue
		#print("there %s in rlist" %(len(rlist)))
		rs, ws, xs = select.select(rlist, [], [])
		for sockfd in rs:
			if sockfd == server:
				local, addr = server.accept()
				print("connect from %s" %(str(addr)))
				rlist.append(local)
				rlist.append(remote)
				rlist.remove(sockfd)
				continue
			elif sockfd == local:
				try:
					data = sockfd.recv(4096)
				except Exception as reason:
					print("recv local error: %s" %(reason))
					data = b''
				#print("server -> remote %s" %(data))
				if len(data):
					remote.send(data)
				else:
					remote.shutdown(2)
					remote.close()
					rlist = [server]
					closed = True
			elif sockfd == remote:
				try:
					data = sockfd.recv(4096)
				#print("server <- remote %s" %(data))
				except Exception as reason:
					print("recv remote error: %s" %(reason))
					data = b''
				if len(data):
					local.send(data)
				else:
					sockfd.shutdown(2)
					sockfd.close()
					rlist = [server]
					closed = True

if __name__ == "__main__":
	optParser = OptionParser()
	optParser.add_option('-l','--laddr', dest='laddr', default="127.0.0.1")
	optParser.add_option("-p","--lport", dest="lport")
	optParser.add_option('-R','--raddr', dest='raddr')
	optParser.add_option("-P","--rport", dest="rport")
	opts, args = optParser.parse_args()
	portMap(
		laddr=opts.laddr, lport=int(opts.lport),
		raddr=opts.raddr, rport=int(opts.rport))
