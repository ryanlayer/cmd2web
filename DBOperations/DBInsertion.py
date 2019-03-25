import sqlite3
import pandas as pd
from sqlite3 import Error
class DBInsertion:
    def __init__(self,db_file):
        try:
            self.conn = sqlite3.connect(db_file,check_same_thread=False)
            # return self.conn
        except Error as e:
            print(e)

    # Close connection when deconstructor is called.
    def __del__(self):
        self.conn.close()

    #Insert new group
    def insert_group(self,group_name,group_type,restricted):
        cur = self.conn.cursor()
        cur.execute("Insert into Groups(GroupName,GroupType,RestrictedGroup) values('{0}','{1}',{2})".format(group_name,group_type,restricted))
        self.conn.commit()

    def get_group_name_from_id(self,gid):
        cur = self.conn.cursor()
        cur.execute("select GroupID from Groups where GroupName='{0}'".format(gid))
        rows = cur.fetchall()
        if(len(rows) > 0):
            return rows[0][0]
        else:
            # //Error Record does not exist for the gid
            return "Group ID does not exist";

    #Insert new key in the Keys table for a particular user with expiry date
    def insert_key(self,group_id,token,expiry,user_email):
        cur = self.conn.cursor()
        cur.execute("Insert into Keys(GroupID,Token,Expiry,UserEmail) values({0},'{1}','{2}','{3}')".format(group_id,token,expiry,user_email))
        self.conn.commit()

    #Delete the group. Should keys be deleted for that group?
    def delete_group(self,group_name):
        cur = self.conn.cursor()
        cur.execute("Delete from Groups where GroupName='{0}'".format(group_name))
        self.conn.commit()

    #Delete the keys belonging to a particular group
    def delete_group_keys(self,group_name):
        cur = self.conn.cursor()
        cur.execute("Delete from Keys where GroupID in (select GroupID from Groups where GroupName='{0}')".format(group_name))
        self.conn.commit()

    #Delete the keys for a particular user
    def delete_user_keys(self,user_email):
        cur = self.conn.cursor()
        cur.execute("Delete from Keys where UserEmail ='{0}'".format(user_email))
        self.conn.commit()

    # Get all keys for a user based on user id
    def get_user_keys(self, user_email):
        query="Select * from Keys where UserEmail ='{0}'".format(user_email)
        data = pd.read_sql_query(query, self.conn)
        return data
        # self.conn.commit()

    # Get all keys for a user based on group name
    def get_user_keys_by_group_name(self,group_name):
        query = "Select * from Keys where GroupID in (select GroupID from Groups where GroupName='{0}')".format(group_name)
        data = pd.read_sql_query(query, self.conn)
        return data

    # Get groups list
    def get_group_list(self):
        query = "Select * from Groups"
        data = pd.read_sql_query(query, self.conn)
        return data

    # Get keys list
    def get_key_list(self):
        query = "Select * from Keys"
        data = pd.read_sql_query(query, self.conn)
        return data

    # Check token
    def check_token_exists(self,token):
        cur = self.conn.cursor()
        query='select Token from Keys where Token={0}'.format(token)
        cur.execute(query)
        rows = cur.fetchall()
        if len(rows) > 0:
            return True
        else:
            return False