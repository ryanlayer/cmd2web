import click
from flask import Flask,request
import os
import random
from DBInsertion import DBInsertion
from datetime import datetime,timedelta
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.config['UPLOAD_FOLDER']='/tmp/cmd2webfiles'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
current_directory= os.path.dirname(__file__)
database_file_path = os.path.join(current_directory, "../DBScript/CMD2WEB.sqlite")
database_object = DBInsertion(database_file_path)
@click.group()
# @click.option('-i', '--input', type=click.File('r'))
def cli():
    """Command line interface for database interaction."""
    pass


@cli.command()
@click.option('--gname', help='The group name.')
@click.option('--gtype', help='Type of the group.')
@click.option('--restricted', help='If the group is restricted group. 1 if group is restricted ,0 if not restricted.')
def createGroup(gname, gtype,restricted):
    """Description:Create a new group. \n
    Input parameters required: \n
    - gname - Group Name \n
    - gytpe - Group Type \n
    - restricted - Boolean indicating whether group is restricted \n
    Example Usage: python DBCommandLineTool.py creategroup --gname=DummyGroup --gtype=Test --restricted=1 """
    group_name = gname
    group_type = gtype

    if (group_name != None and restricted != None):
    # insert
            print(group_name, group_type, restricted)
            database_object.insert_group(group_name, group_type, restricted)
            print("Group {0} created".format(group_name))

    else:
        print(group_name, group_type, restricted)
        print("Parameter missing")
    # click.echo('Hello %s! - %s! - %d' % gname, gtype,restricted)


@cli.command()
@click.option('--gid', help='The group id.')
@click.option('--token', help='Token for the user associated to a group.Format (mm-dd-yyyy).')
@click.option('--expiry', help='Expiry date for the token.')
@click.option('--email', help='Email id of the user.')
def createKeyByGroupID(gid, token, expiry, email):
    """Description:Create  new token by group id.\n
     Input parameters required: \n
    - gid - Group ID \n
    - token - Token for the user \n
    - expiry - Token expiry date \n
    - email - Email id of the user\n
    Example Usage: python DBCommandLineTool.py createkeybygroupid --gid=9 --token=122344434 --expiry=04-27-2019 --email=ro@colorado.edu"""

    group_id = gid
    token = token
    expiry = expiry
    user_email = email
    if(expiry==None):
        expiry = getNewDate()

    if(token==None):
        token = generateNewToken()

    if (group_id != None and token != None and expiry != None and user_email != None):
        database_object.insert_key(group_id, token, expiry, user_email)
        print("Token:{0} inserted for the user:{1} with expiry:{2}".format(token, user_email, expiry))
    else:
        print("Parameter missing")
    # click.echo('Hello %s! - %s! - %s! - %s!' % gid, token, expiry, email)


# Generate new date
def getNewDate():
    newdate = datetime.now() + timedelta(days=365)
    expiry = newdate.strftime('%m-%d-%Y')
    return expiry

# Generate new random token
def generateNewToken():
    new_token= random.randint(10000000,99999999)
    if(database_object.check_token_exists(new_token)):
        return generateNewToken()
    else:
        return new_token

@cli.command()
@click.option('--gname', help='The group name.')
@click.option('--token', help='Token for the user associated to a group.')
@click.option('--expiry', help='Expiry date for the token. Format (mm-dd-yyyy).')
@click.option('--email', help='Email id of the user.')
def createKeyByGroupName(gname, token, expiry, email):
    """Description:Create  new token by group name. \n
     Input parameters required: \n
    - gname - Group Name \n
    - token - Token for the user \n
    - expiry - Token expiry date \n
    - email - Email id of the user\n
    Example Usage: python DBCommandLineTool.py createkeybygroupname --gname=DummyGroup --token=122344435 --expiry=05-27-2019 --email=rom@colorado.edu """
    group_name = gname
    token = token
    expiry = expiry
    user_email = email
    if(expiry==None):
        expiry = getNewDate()

    if(token==None):
        token = generateNewToken()
    group_id = None
    if (group_name != None):
        # get group id
        group_id = database_object.get_group_name_from_id(group_name)
    else:
        return "No group name"
    if (group_id != None and token != None and expiry != None and user_email != None):
        database_object.insert_key(group_id, token, expiry, user_email)
        print("Token:{0} inserted for the user:{1} with expiry:{2}".format(token, user_email, expiry))
    else:
        print("Parameter missing")

@cli.command()
@click.option('--gname', help='The group name.')
def deleteGroup(gname):
    """Description:Delete group by name.\n
     Input parameters required: \n
    - gname - Group Name \n
    Example Usage: python DBCommandLineTool.py deletegroup  --gname=DummyGroup"""
    group_name = gname
    if (group_name != None):
        database_object.delete_group(group_name)
        print("Deleted group {0}".format(group_name))
    else:
        print("Check group info")
    # click.echo('Hello %s! - %s! - %s! - %s!' % gname, token, expiry, email)


@cli.command()
@click.option('--gname', help='The group name.')
def deleteKeyByGroup(gname):
    """Description:Delete key by group name.\n
    Input parameters required: \n
    - gname - Group Name \n
    Example Usage: python DBCommandLineTool.py deletekeybygroup  --gname=DummyGroup"""
    group_name = gname
    if (group_name != None):
        database_object.delete_group_keys(group_name)
        print("Deleted keys for group {0}".format(group_name))
    else:
        print("Check group info")
    # click.echo('Hello %s! - %s! - %s! - %s!' % gname, token, expiry, email)

@cli.command()
@click.option('--email', help='The user email.')
def deleteKeyByUser(email):
    """Description:Delete key by group user.\n
    Input parameters required: \n
    - email - email id of the user \n
    Example Usage: python DBCommandLineTool.py deletekeybyuser --email=rom@colorado.edu"""
    user_email = email
    if (user_email != None):
        database_object.delete_user_keys(user_email)
        print("Deleted keys for user {0}".format(user_email))
    else:
        print("Check group info")
    # click.echo('Hello %s! - %s! - %s! - %s!' % gname, token, expiry, email)

@cli.command()
@click.option('--email', help='The user email.')
def getKeyByUser(email):
    """Description:Get Keys by User.\n
    Input parameters required: \n
    - email - email id of the user \n
    Example Usage: python DBCommandLineTool.py getkeybyuser --email=rom2@colorado.edu"""
    user_email = email
    if (user_email != None):
        result = database_object.get_user_keys(user_email)
        print(result)
    else:
        print("Check group info")

@cli.command()
@click.option('--gname', help='The Group name.')
def getKeyByGroupName(gname):
    """Description:Get keys by Group.\n
    Input parameters required: \n
    - gname - Group name \n
    Example Usage: python DBCommandLineTool.py getkeybygroupname --gname=DummyGroup"""
    group_name = gname
    if (group_name != None):
        result = database_object.get_user_keys_by_group_name(group_name)
        print(result)
    else:
        print("Check group info")

@cli.command()
def getGroupList():
    """Description:Get all the groups.\n
    Input parameters required: \n
    None \n
    Example Usage: python DBCommandLineTool.py getgrouplist """
    result = database_object.get_group_list()
    print(result)

@cli.command()
def getKeyList():
    """Description:Get all the keys.\n
    Input parameters required: \n
    None \n
    Example Usage: python DBCommandLineTool.py getkeylist """
    result = database_object.get_key_list()
    print(result)


if __name__ == '__main__':
    cli()