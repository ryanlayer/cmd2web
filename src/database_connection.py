import sqlite3
from sqlite3 import Error
import cmd2web
import datetime
class DatabaseConnection:
    def __init__(self,db_file):
        try:
            self.conn = sqlite3.connect(db_file)
            # return self.conn
        except Error as e:
            print(e)
        # return None

    def close(self):
        self.conn.close()

    def get_restricted_access(self,group_name):
        cur = self.conn.cursor()
        cur.execute("select RestrictedGroup from Groups where GroupName='{0}'".format(group_name))

        rows = cur.fetchall()
        if(len(rows) > 0):
            [restricted_acess]=rows[0]
            # 0 means restricted group so token will be needed
            if(restricted_acess == 1):
                return True
            else:
                return False

        else:
            # //Error Record does not exist for the servicename
            return cmd2web.Server.error('Record does not exist for the service')

    def check_token_access(self,group_name,token):
        cur = self.conn.cursor()
        cur.execute("select k.groupID, k.Expiry from Keys k  join Groups s on s.GroupID = k.GroupID where s.GroupName='{0}' and k.token='{1}';".format(group_name,token))

        rows = cur.fetchall()
        if(len(rows) > 0):
            group_id, date_expiry_str = rows[0]
            format_str = "%m-%d-%Y"
            expiry_date = datetime.datetime.strptime(date_expiry_str, format_str)
            current_date = datetime.datetime.now()
            if(current_date<=expiry_date):
                return True
            else:
                return cmd2web.Server.error('Wrong or expired token. Access Denied')

        else:
            # //Error
            return False

 
# if __name__ == '__main__':
#     s = DatabaseConnection("../DBScript/CMD2WEB.sqlite")
#     print(s.get_restricted_access("rmsk"))
#     print(s.get_restricted_access("rmsk2"))
#     print(s.check_token_access("rmsk","12223453445"))