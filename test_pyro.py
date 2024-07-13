import Pyro4

print("Pyro4 version:", Pyro4.__version__)
print("Attributes in Pyro4:", dir(Pyro4))
print("Attributes in Pyro4.naming:", dir(Pyro4.naming) if hasattr(Pyro4, 'naming') else "No attribute 'naming'")
