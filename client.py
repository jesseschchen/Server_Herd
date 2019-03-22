import asyncio
import sys
import json
import time



async def send_IAMAT(reader, writer):
	message = "IAMAT f +34.068-118.445 " + str(time.time())
	print("sent: %r" % message)
	writer.write(message.encode())
	data = await reader.read(100)
	print("IAMAT reply: %r" % data.decode())

#async def send_IAMAT2(reader, writer):
#	message = "IAMAT suck.a.fat.dick.cunts +72.068-078.445 1512106467.425"
#	print("sent: %r" % message)
#	writer.write(message.encode())
#	data = await reader.read(100)
#	print("IAMAT reply: %r" % data.decode())

#async def send_IAMAT3(reader, writer):
#	message = "IAMAT suck.a.fat.dick.cunts +72.068-078.445"
#	print("sent: %r" % message)
#	writer.write(message.encode())
#	data = await reader.read(100)
#	print("IAMAT reply: %r" % data.decode())

async def send_WHATSAT(reader, writer):
	client = input("client: ")
	radius = input("radius: ")
	count = input("count: ")
	message = "WHATSAT " + client + " " + radius + " " + count
	print("send: %r" % message)
	writer.write(message.encode())
	#data = await reader.read()
	#print("DATA: ")
	#print(data.decode())
	json_data = await reader.read()
	print(json_data.decode())
	#json.loads(json_data.decode())

#async def send_WHATSAT2(reader, writer):
#	message = "WHATSAT fuck.my.shit.up 10 "
#	print("send: %r" % message)
#	writer.write(message.encode())
#	data = await reader.read()
#	print(data.decode())





async def tcp_echo_client(loop):
	port_num = input("port number: ")
	reader, writer = await asyncio.open_connection('127.0.0.1', port_num, loop=loop) 
	message = input("[0,1]: ")
	if int(message) == 0:
		await send_IAMAT(reader, writer)
		#input()
		#await send_WHATSAT2(reader, writer)
	elif int(message) == 1:
		await send_WHATSAT(reader, writer)
	elif int(message) == 2:
		await send_IAMAT2(reader, writer)
	elif int(message) == 3:
		await send_IAMAT3(reader, writer)
	elif int(message) == 4:
		await send_WHATSAT2(reader, writer)

	print('Closed connection')
	writer.close()


async def chat_loop(loop):
	reader, writer = await asyncio.open_connection('127.0.0.1', 8888,
                                                   loop=loop) 
	while(1):
		print("what message tryna send: ")
		message = input()
		#print("message: %r" % message)
		writer.write(message.encode())
		data = await reader.read(100)
		print("echo: %r" % data.decode())
	writer.close()


message = 'Hello World!'
loop = asyncio.get_event_loop()
loop.run_until_complete(tcp_echo_client(loop))
loop.close()