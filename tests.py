import tests

while True:
    try:
        selection = int(input("1 = server, 0 = client"))
        break
    except ValueError:
        print("must be valid input")

if (selection == 1):
    tests.Launch_Server.Start()

if (selection == 0):
    tests.Launch_Client.Start()
