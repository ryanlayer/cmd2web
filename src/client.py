import cmd2web

s = cmd2web.Client.connect('http://127.0.0.1:8080')

try:
    R = s.run('simpleRepeat', 
              chromosome=10, 
              start=105053143, 
              end=105054173,
              type='DEL')

except Exception as e:
    print(str(e))

print(R)
