with open("cake") as f:
    cake = f.read().strip()

if cake == "THE CAKE IS A LIE":
    print(True)
else:
    print(False, "ola k ase")
