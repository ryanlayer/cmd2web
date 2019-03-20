import sqlite3
from sqlite3 import Error
import cmd2web
import sys
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

    def get_restricted_access(self,group_list):
        cur = self.conn.cursor()
        query='SELECT RestrictedGroup FROM Groups WHERE GroupName IN (%s)' % ','.join('"{}"'.format(i) for i in group_list)
        sys.stderr.write("\n\n\nQuery: {0}\n\n\n".format(query))
        cur.execute(query)

        rows = cur.fetchall()
        give_access=False
        if(len(rows) > 0):
            for i in rows:
                if i[0]==1:
                    give_access=True
                    break
                else:
                    give_access=False
            if(give_access==True):
                 return True
            else:
                return False
            # [restricted_acess]=rows[0]
            # # 0 means restricted group so token will be needed
            # if(restricted_acess == 1):
            #     return True
            # else:
            #     return False

        else:
            # //Error Record does not exist for the servicename
            return cmd2web.Server.error('Record does not exist for the service')

    def check_token_access(self,group_list,token):
        cur = self.conn.cursor()
        query='select k.groupID, k.Expiry from Keys k  join Groups s on s.GroupID = k.GroupID where s.GroupName in (%s)' % ','.join('"{}"'.format(i) for i in group_list) + ' and k.token={0}'.format(token)
        sys.stderr.write("\n\n\nQuery: {0}\n\n\n".format(query))
        cur.execute(query)

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