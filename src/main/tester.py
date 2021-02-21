def my_print(kwargs):
    print kwargs["5"]

a = {"3":1, "5":"elo"}
my_print(**a)