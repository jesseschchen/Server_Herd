from ClientRecord import Client_Record
import asyncio
import time
import json
import socket
import ssl
import os
import sys



class Server:
    def __init__(self, name, port, loop):
        self.name = name
        self.loop = loop
        self.port = port
        self.friends = list()
        self.record_list = list()
        self.fd = open(name+".log", 'w')
        self.printable = 1

    def print(self, string):
        if self.printable:
            print(string)

    def get_name(self):
        return self.name

    def parse_coord(self, gps):
        plus = gps.find('+', 1)
        minu = gps.find('-', 1)
        ind = max(plus, minu)
        lat = float(gps[0:ind])
        lon = float(gps[ind:])
        return (lat, lon)

    def valid_gps(self, gps):
        plus = gps.find('+', 1)
        minu = gps.find('-', 1)
        try:
            ind = max(plus, minu)
            lat = float(gps[0:ind])
            lon = float(gps[ind:])
        except: 
            return 0
        if (gps[0] != '+' and gps[0] != '-')\
            or (plus == -1 and minu == -1):
            return 0
        return 1


    def add_friend(self, host, port, name):
        for friend in self.friends:
            if friend[0] == host and friend[1] == port:
                return
        self.friends.append((host, port, name))

    def display_friends(self):
        self.print("DISPLAY FRIENDS")
        for friend in self.friends:
            self.print("host: %r" % friend[0])
            self.print("port: %r" % friend[1])

    def plus_timediff(self, timediff):
        if timediff > 0:
            return "+"+("%.9f" % timediff)
        return ("%.9f" % timediff)


    async def have_record(self, new_record):
        for record in self.record_list:
            if record.get_id() == new_record.get_id() and \
            record.get_server() == new_record.get_server() and \
            record.get_gps() == new_record.get_gps() and \
            record.get_ts() == new_record.get_ts() and \
            record.get_timediff() == new_record.get_timediff():
                return 1
        return 0

    async def have_record_notime(self, new_record):
        for record in self.record_list:
            if record.get_id() == new_record.get_id() and \
            record.get_server() == new_record.get_server() and \
            record.get_gps() == new_record.get_gps():
                return 1
        return 0
    
    async def insert_record(self, new_record):
        for record in self.record_list:
            if record.get_id() == new_record.get_id():
                if await self.have_record(new_record):
                    self.print("RECORD ALREADY EXISTS")
                    self.fd.write("RECORD ALREADY EXISTS\n")
                    self.fd.flush()
                    return Client_Record("0", "0", "0", "0", "0")
                else:
                    record.update(new_record.get_server(), new_record.get_ts(), new_record.get_gps(), new_record.get_timediff())
                    self.print("MODIFY RECORD")
                    self.fd.write("MODIFY RECORD\n")
                    self.write_record(record)
                    self.print_record(record)
                    self.fd.flush()
                    return record
        self.print("CREATE NEW RECORD")
        self.fd.write("CREATE NEW RECORD\n")
        self.write_record(new_record)
        self.print_record(new_record)
        self.fd.flush()
        self.record_list.append(new_record)
        return new_record

    async def give_record(self, c_id):
        for record in self.record_list:
            if record.get_id() == c_id:
                return record
        return -1

    def display_records(self):
        self.print("DISPLAY RECORDS: %r" % self.name)
        for record in self.record_list:
            self.print("id: %r" % record.get_id())
            self.print("server: %r" % record.get_server())
            self.print("ts: %r" % record.get_ts())
            self.print("gps: %r" % record.get_gps())
            self.print("time_diff: %.9f" % record.get_timediff())

    def print_record(self, record):
        self.print("id: %r" % record.get_id())
        self.print("server: %r" % record.get_server())
        self.print("ts: %r" % record.get_ts())
        self.print("gps: %r" % record.get_gps())
        self.print("time_diff: %.9f" % record.get_timediff())

    def write_record(self, record):
        self.fd.write("\tid: %r\n" % record.get_id())
        self.fd.write("\tserver: %r\n" % record.get_server())
        self.fd.write("\tts: %r\n" % record.get_ts())
        self.fd.write("\tgps: %r\n" % record.get_gps())
        self.fd.write("\ttime_diff: %.9f\n" % record.get_timediff())

    async def send_record(self, record, friend):
        
        try:
            reader, writer = await asyncio.open_connection(friend[0], friend[1], loop=self.loop) 
        except: 
            self.print("ERROR: Failed to connect to server: "+friend[2])
            self.fd.write("ERROR: Failed to connect to server: %r\n" % friend[2])
            self.fd.flush()
            return
        message = "UPDATE " + record.get_id()+" "+record.get_server()+" "+("%.9f" % record.get_ts())+" "+record.get_gps() \
            +" "+("%.9f" % record.get_timediff())+" "+ self.name
        writer.write(message.encode())
        await writer.drain()
        writer.close()

    async def flood_record(self, record):
        for friend in self.friends:
            await self.send_record(record, friend)

    async def forward_record(self, record, incoming_server):
        for friend in self.friends:
            if friend[2] != incoming_server: # valid friend
                await self.send_record(record, friend)



    async def handle_IAMAT(self, writer, word_list, message):
        new_message = "? " + message
        if len(word_list) != 4:
            writer.write(new_message.encode())
            return
        #parse info
        c_id = word_list[1]
        gps = word_list[2]
        try: 
            ts = float(word_list[3])
        except: 
            writer.write(new_message.encode())
            return
        time_diff = time.time() - ts

        if not self.valid_gps(gps) or ts < 0:
            writer.write(new_message.encode())
            return

        #reply with AT
        parsed_record = Client_Record(c_id, self.name, ts, gps, time_diff)
        updated_record = Client_Record("0", "0", "0", "0", "0")
        if await self.have_record_notime(parsed_record):
            old_record = await self.give_record(c_id)
            #old timestamp
            if old_record.get_ts() > ts: #use old_record
                reply = "AT" + " " + self.name +" "+ self.plus_timediff(old_record.get_timediff()) \
                    +" "+ c_id +" "+ gps +" "+ ("%.9f" % old_record.get_ts())+"\n"
            else:
                reply = "AT" + " " + self.name +" "+ self.plus_timediff(time_diff) \
                    +" "+ c_id +" "+ gps +" "+ ("%.9f" % ts)+"\n"
                updated_record = await self.insert_record(parsed_record)


        else:
            reply = "AT" + " " + self.name +" "+ self.plus_timediff(time_diff) +" "+ c_id +" "+ gps +" "+ ("%.9f" % ts)+"\n"
            updated_record = await self.insert_record(parsed_record)

        self.print("IAMAT reply: %r" % reply)
        writer.write(reply.encode())
        self.fd.write("SEND_REPLY: "+reply+"\n")
        self.fd.flush()

        #add information to database
        #self.display_records()

        #flood infomration to neigbhor servers
        if not updated_record.is_none():
            await self.flood_record(updated_record)

    async def handle_WHATSAT(self, writer, word_list, message):
        new_message = "? " + message
        if len(word_list) != 4:
            writer.write(new_message.encode())
            return
        #parse info
        c_id = word_list[1]
        try: 
            rad = float(word_list[2])
        except:
            writer.write(new_message.encode())
            return
        try: 
            num = int(word_list[3])
        except:
            writer.write(new_message.encode())
            return

        match_record = await self.give_record(c_id)
        if match_record == -1 or rad > 50 or num > 20 \
            or rad < 0 or num < 0:
            new_message = "? " + message
            writer.write(new_message.encode())
            return


        match_server = match_record.get_server()
        match_timediff = match_record.get_timediff()
        match_gps = match_record.get_gps()
        (lat, lon) = self.parse_coord(match_gps)
        match_ts = match_record.get_ts()


        #reply with AT
        reply = "AT " + match_server +" "+ self.plus_timediff(match_timediff) +" "+ \
            c_id +" "+ match_gps +" "+ ("%0.9f" % match_ts)
        self.print("Reply: %r" % reply)


        #look up google places
        request = "GET /maps/api/place/nearbysearch/json?location=" \
            +str(lat)+","+str(lon)+"&radius="+str(rad)+"&key=go away" \
            +" HTTP/1.1\r\n" \
            +"Host: "+"maps.googleapis.com\r\n" \
            +"Content-Type: text/plain; charset=utf-8\r\n\r\n\r\n"
        maps2 = 'maps.googleapis.com'
        try:
            reader2, writer2 = await asyncio.open_connection(maps2, 443, loop=self.loop, ssl=True)
        except:
            writer.write(reply.encode())
            writer.drain()
            return
        writer2.write(request.encode())
        await writer2.drain()

        end = "\r\n\r\n"
        new_data = await reader2.readuntil(end.encode())
        data2 = await reader2.readuntil(end.encode())

        json_resp = data2.decode()
        print(json_resp)
        

        

        l_ind = json_resp.find("{")
        r_ind = json_resp.rfind("}")
        json_msg = json_resp[l_ind:r_ind+2]  


        combo = reply + "\n" + json_msg
        self.fd.write("SEND_REPLY: \n"+combo+"\n")
        self.fd.flush()
        writer.write(combo.encode())
        writer.drain()

    async def handle_UPDATE(self, word_list, message):
        update_record = Client_Record(word_list[1], word_list[2], float(word_list[3]), word_list[4], float(word_list[5]))

        insert = await self.insert_record(update_record)
        self.fd.write("\n")
        if not insert.is_none():
            await self.forward_record(update_record, word_list[6])
            #self.display_records()



    async def handle_message(self, reader, writer):
        data = await reader.read(200)
        message = data.decode()
        self.print("\n%r : RECEIVE: %r" % (self.name, message))
        self.fd.write("RECEIVE: %r\n" % message)
        self.fd.flush()
        addr = writer.get_extra_info('peername')
        word_list = message.split()
        if len(word_list) < 1:
            writer.close()
            return
        if word_list[0] == 'IAMAT':
            await self.handle_IAMAT(writer, word_list, message)
        elif word_list[0] == 'WHATSAT':
            await self.handle_WHATSAT(writer, word_list, message)
        elif word_list[0] == 'UPDATE':
            await self.handle_UPDATE(word_list, message)
        else:
            writer.write(("? " + message).encode())

        await writer.drain()
        writer.close()

    def open_server(self):
        self.print("creating_server %r : %r" % (self.name, self.port))
        self.fd.write("Creating server: %r : %r\n" % (self.name, self.port))
        self.fd.flush()
        coro = asyncio.start_server(self.handle_message, '127.0.0.1', self.port, loop = self.loop)
        self.server = self.loop.run_until_complete(coro)

        return self.server

    def close_server(self):
        self.fd.write("DISPLAY RECORDS: %r\n" % self.name)
        for record in self.record_list:
            self.fd.write("id: %r\n" % record.get_id())
            self.fd.write("server: %r\n" % record.get_server())
            self.fd.write("ts: %r\n" % record.get_ts())
            self.fd.write("gps: %r\n" % record.get_gps())
            self.fd.write("time_diff: %r\n" % record.get_timediff())        
        self.fd.close()
        self.server.close()

