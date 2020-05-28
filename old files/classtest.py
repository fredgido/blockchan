class Geeks:
    def __init__(self):
        self._age = [0]
        print("initialized "+hex(id(self._age)))

    # using property decorator
    # a getter function
    @property
    def age(self):
        print("getter method called")
        print("getter "+hex(id(self._age)))

        return self._age

        # a setter function

    @age.setter
    def age(self, a):
        print("setter method called")
        print("setter "+hex(id(self._age)))

        self._age = a


mark = Geeks()

mark.age[0] = 19
mark.age.append(0)
print("setter " + hex(id(mark.age)))

print(mark.age)
print(len(mark.age))