# import requests
# filename='/home/rohit/test3.txt'
# f = open (filename)
# r =  requests.post(url='http://127.0.0.1:8080/f?service=simpleFileGrep&pattern=zip', files =  {'file':f})
# print(r.status_code)
# print(r.headers)
# print(r.json())


import click
import requests


@click.group()
# @click.option('-i', '--input', type=click.File('r'))
def cli():
    """Command line interface for database interaction."""
    pass


@cli.command()
@click.option('--url', help='The url with parameters')
@click.option('--filepath', help='Path of the input file.')
def uploadRunCommand(url, filepath):

    """Description: Pass your own input file to a service. \n
         Input parameters required: \n
        - url - URL with the parameters \n
        - filepath - Path of the input file \n
        Example Usage: python UploadFileTool.py uploadRunCommand --url='http://127.0.0.1:8080/f?service=simpleFileGrep&pattern=zip' --filepath=/home/rohit/test3.txt """

    if (url != None and filepath != None):
        f = open(filepath)
        r = requests.post(url=url, files={'file': f})
        print(r.json())

    else:
        print(url,filepath)
        print("Parameter missing")
    # click.echo('Hello %s! - %s! - %d' % gname, gtype,restricted)


if __name__ == '__main__':
    cli()