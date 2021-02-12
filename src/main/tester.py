class obiekt(object):
    def __init__(self,id):
        self.id = id

nazwa = obiekt

firstobject = nazwa(1)
second = nazwa(2)

print firstobject.id
print second.id