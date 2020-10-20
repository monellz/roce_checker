import sqlite3

# =================================================================
# Info Table
# 
#   PID |
#   101 |
#
# =================================================================

# =================================================================
# Top Table
#   
#   IP1             |   IP2             |   phase               |   status  |   date
#   172.168.201.15  |   *               |   nopassword_check    |   RUNNING |   
#   172.168.201.15  |   172.168.201.16  |   connection_check    |   RUNNING |
#   172.168.201.15  |   172.168.201.16  |   ucx_test            |   FAIL    |
#
# =================================================================

class DataBase:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()


    def init_table(self):
        # info table
        self.cursor.execute('''CREATE TABLE info  (PID INT NOT NULL); ''')
        self.conn.commit()

        # insert -1
        self.update_pid(-1)

        # top table
        self.cursor.execute('''CREATE TABLE top 
                            (   IP1 CHAR(16),
                                IP2 CHAR(16),
                                PHASE   CHAR(20),
                                STATUS  CHAR(10),
                                DATE    CHAR(20),
                                PRIMARY KEY (IP1, IP2)); ''')    
        self.conn.commit()

        # DATA
        # ucx_test result

    def close(self):
        self.cursor.close()
        self.conn.close()
    
    def update_info(self, pid, date):
        self.cursor.execute("REPLACE INTO info (PID) VALUES ({});".format(pid))
        self.conn.commit()

    def get_pid(self):
        self.cursor.execute("SELECT IP1 FROM info")
        row = self.cursor.fetchall()[0]
        pid = row[0]
        return pid

    def format_info(self):
        self.cursor.execute("SELECT * FROM info")
        row = self.cursor.fetchall()[0]
        format_str = 'Backend Pid: %d, '
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return 'Backend Pid: %d, Start Time: %s, Now: %s\n' % (row[0], row[1], now)

    def update_top(self, ip, phase, status, date):
        if isinstance(ip, list):
            assert len(ip) == 2
            ip1 = ip[0]
            ip2 = ip[1]
        else:
            ip1 = ip
            ip2 = "*"
        cmd = "REPLACE INTO top (IP1, IP2, PHASE, STATUS, DATE) VALUES ('{}', '{}', '{}', '{}', '{}');".format(ip1, ip2, phase, status, date)
        self.cursor.execute(cmd)
        self.conn.commit()
    
    def format_top(self):
        self.cursor.execute("SELECT * FROM top")
        vals = self.cursor.fetchall()
        format_str = '%16s | %16s | %20s | %10s | %20s \n'
        s = format_str % ("IP1", "IP2", "PHASE", "STATUS", "DATE")
        for row in vals:
            s += format_str % (row[0], row[1], row[2], row[3], row[4]) 
        return s
        


# ===============
# UCX_TEST Result Table
#   
#   target                          |   bindwidth            
#   172.168.201.15-172.168.201.16   |   
#   172.168.201.15-172.168.201.16   |             
#
#
#   target:     one ip or two ips(joined by '-')
#   bindwidth:    
#
# ===============



