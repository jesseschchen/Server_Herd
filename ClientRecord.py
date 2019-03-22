class Client_Record:
    def __init__(self, id, server, ts, gps, time_diff):
        self.id = id
        self.server = server
        self.ts = ts
        self.gps = gps
        self.time_diff = time_diff


    def update(self, new_server, new_ts, new_gps, new_time_diff):
        self.server = new_server
        self.ts = new_ts
        self.gps = new_gps
        self.time_diff = new_time_diff

    def get_id(self):
    	return self.id

    def get_server(self):
    	return self.server

    def get_gps(self):
    	return self.gps

    def is_none(self):
    	if self.id == "0" and self.server == "0" and self.gps == "0":
    		return 1
    	return 0

    def get_ts(self):
    	return self.ts

    def get_timediff(self):
    	return self.time_diff


