import sqlite3
import time

def now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


# =================================================================
# Info Table
# 
#   PID |   DATE
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


# =================================================================
# UCX_TEST Result Table
#   
#   IP1             |   IP2             |   case    |   iter  |   typical_lat(us)  |   avg_lat(us)  |   overall_lat(us) |   avg_bw(MB/s)  | overall_bw(MB/s)    |   avg_mr(msg/s)  |   overall_mr(msg/s) 
#   172.168.201.15  |   172.168.201.16  |   ucp_get |           
#   172.168.201.15  |   172.168.201.16  |           |
#
#
# =================================================================


# =================================================================
# PERF_V2_TEST Result Table
#
# =================================================================

class DataBase:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

        if not self.available(): self.init_table()


    def init_table(self):
        # info table
        self.cursor.execute('''CREATE TABLE info  (PID INT NOT NULL, DATE CHAR(20)); ''')
        self.conn.commit()

        # insert -1
        self.update_info(-1, now())

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
        # lat: usec
        # bw: MB/s
        # mr: msg/s

        self.cursor.execute('''CREATE TABLE ucx_test
                            (   IP1 CHAR(16), 
                                IP2 CHAR(16),
                                type    CHAR(28),
                                iter    INT,   
                                typical_lat     FLOAT,
                                avg_lat         FLOAT,
                                overall_lat     FLOAT,
                                avg_bw          FLOAT,
                                overall_bw      FLOAT,
                                avg_mr          FLOAT,
                                overall_mr      FLOAT,
                                PRIMARY KEY (IP1, IP2, type)); ''')
        self.conn.commit()

        # perf_test result
        # lat: usec
        # bw: MB/s
        # mr: msg/s

        self.cursor.execute('''CREATE TABLE perf_test
                            (   IP1 CHAR(16), 
                                IP2 CHAR(16),
                                type            CHAR(15),
                                transfer_type   CHAR(4),   
                                version         CHAR(2),
                                bw              FLOAT,
                                lat             FLOAT,
                                PRIMARY KEY (IP1, IP2, type, transfer_type, version)); ''')
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
    
    def update_info(self, pid, date):
        self.cursor.execute("REPLACE INTO info (PID, DATE) VALUES ({}, '{}');".format(pid, date))
        self.conn.commit()
    
    def available(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='info';")
        row = self.cursor.fetchall()
        if len(row) == 0:
            return False 
        return True

    def get_pid(self):
        self.cursor.execute("SELECT PID FROM info")
        row = self.cursor.fetchall()[0]
        pid = row[0]
        return pid

    def format_info(self):
        self.cursor.execute("SELECT * FROM info")
        row = self.cursor.fetchall()[0]
        format_str = 'Backend Pid: %d, '
        return 'Backend Pid: %d, Start Time: %s, Now: %s\n' % (row[0], row[1], now())
    
    def delete_top(self, ip):
        if isinstance(ip, list):
            assert len(ip) == 2
            ip1 = ip[0]
            ip2 = ip[1]
        else:
            ip1 = ip
            ip2 = "*"
        cmd = "DELETE from top WHERE IP1='{}' AND IP2='{}'".format(ip1, ip2)
        self.cursor.execute(cmd)
        self.conn.commit()

    def update_top(self, ip, phase, status, date, delete=False):
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
            s += format_str % (tuple(row)) 
        return s
        
    def update_ucx_test(self, data):
        assert isinstance(data, list)
        assert len(data) == 11
        cmd = "REPLACE INTO ucx_test (IP1, IP2, type, iter, typical_lat, avg_lat, overall_lat, avg_bw, overall_bw, avg_mr, overall_mr) VALUES ('{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {});".format(*data)
        self.cursor.execute(cmd)
        self.conn.commit()

    def format_ucx_test(self):
        self.cursor.execute("SELECT * FROM ucx_test")
        vals = self.cursor.fetchall()
        # only show avg data
        format_str = '%16s | %16s | %28s | %7d | %15f | %15f | %15f\n'
        s = '%16s | %16s | %28s | %7s | %15s | %15s | %15s\n' % ("IP1", "IP2", "type", "iter", "avg_lat(usec)", "avg_bw(MB/s)", "avg_mr(msg/s)")
        for row in vals:
            s += format_str % (row[0], row[1], row[2], row[3], row[5], row[7], row[9])
        return s

    def update_perf_test(self, data):
        assert isinstance(data, list)
        assert len(data) == 6
        if 'lat' in data[2]:
            cmd = "REPLACE INTO perf_test (IP1, IP2, type, transfer_type, version, bw, lat) VALUES ('{}', '{}', '{}', '{}', '{}', {}, {});".format(data[0], data[1], data[2], data[3], data[4], 'NULL', data[5])
        elif 'bw' in data[2]:
            cmd = "REPLACE INTO perf_test (IP1, IP2, type, transfer_type, version, bw, lat) VALUES ('{}', '{}', '{}', '{}', '{}', {}, {});".format(data[0], data[1], data[2], data[3], data[4], data[5], 'NULL')
        else:
            raise Exception("Unkown perf test type {}".format(data[2]))
        self.cursor.execute(cmd)
        self.conn.commit()

    def format_perf_test(self):
        self.cursor.execute("SELECT * FROM perf_test")
        vals = self.cursor.fetchall()
        format_lat_str = '%16s | %16s | %15s | %15s | %7s | %10s | %10f\n'
        format_bw_str = '%16s | %16s | %15s | %15s | %7s | %10f | %10s\n'
        s = '%16s | %16s | %15s | %15s | %7s | %10s | %10s\n' % ("IP1", "IP2", "type", "transfer_type", "version", "bw(Gb/s)", "lat(usec)")
        for row in vals:
            if 'lat' in row[2]:
                s += format_lat_str % (tuple(row))
            elif 'bw' in row[2]:
                s += format_bw_str % (tuple(row))
            else:
                raise Exception("Unkown perf test type {}".format(row[2]))
        return s
        





