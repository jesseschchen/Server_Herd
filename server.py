from ServerClass import Server
import asyncio
import sys

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


def create_herd(name_list, loop, active_name):
    server_herd = list()
    port = 15240
    for name in name_list:
        s = Server(name, port, loop)
        server_herd.append(s)
        s.open_server()
        port += 1
        if name != active_name:
            s.printable = 0
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
    print("CREATING SERVER HERD...")
    loop = asyncio.get_event_loop()
    herd = create_herd(('Alford', 'Ball', 'Hamilton', 'Holiday', 'Welsh'), loop, sys.argv[1])
    add_herd_friends(herd)

    for member in herd:
        print('Serving on {}'.format(member.server.sockets[0].getsockname()))
    if len(sys.argv) > 1:
        print("PRINTING OUTPUT FROM: %r" %sys.argv[1])
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        for member in herd: 
            member.close_server()
        exit()

    for member in herd: 
        member.close_server()

    loop.close()



if __name__ == '__main__':
    main()