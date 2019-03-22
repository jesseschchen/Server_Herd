from ServerClass import Server
import asyncio

async def handle_echo_fun(reader, writer):
    while(1):
        data = await reader.read(100)
        print("data: %r" % data)
        message = data.decode()
        print("message: %r" % message)
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))

        print("Send: %r" % message)
        writer.write(data)
        await writer.drain()
    print("Close the client socket")
    writer.close()


def create_herd(name_list, loop):
    server_herd = list()
    port = 15240
    for name in name_list:
        s = Server(name, port, loop)
        server_herd.append(s)
        s.open_server()
        port += 1
    return server_herd

def add_herd_friends(herd):
    for member in herd:
        name = member.get_name()
        if name == "Alford":
            member.add_friend("127.0.0.1", 15242, "Hamilton") #hamilton
            member.add_friend("127.0.0.1", 15244, "Welsh") #welsh
        elif name == "Ball":
            member.add_friend("127.0.0.1", 15243, "Holiday") #holiday
            member.add_friend("127.0.0.1", 15244, "Welsh") #welsh
        elif name == "Hamilton":
            member.add_friend("127.0.0.1", 15240, "Alford") #alford
            member.add_friend("127.0.0.1", 15243, "Holiday") #holiday
        elif name == "Holiday":
            member.add_friend("127.0.0.1", 15241, "Ball") #ball
            member.add_friend("127.0.0.1", 15242, "Hamilton") #hamilton
        elif name == "Welsh":
            member.add_friend("127.0.0.1", 15240, "Alford") #alford
            member.add_friend("127.0.0.1", 15241, "Ball") #ball



def main():
    loop = asyncio.get_event_loop()
    #coro = asyncio.start_server(handle_echo_fun, '127.0.0.1', 8888, loop=loop)
    #server = loop.run_until_complete(coro)
    herd = create_herd(('Alford', 'Ball', 'Hamilton', 'Holiday', 'Welsh'), loop)
    add_herd_friends(herd)
    # Serve requests until Ctrl+C is pressed
    for member in herd:
        print('Serving on {}'.format(member.server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        for member in herd: 
            member.close_server()
        exit()
    # Close the server
    for member in herd: 
        member.close_server()

    #loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == '__main__':
    main()