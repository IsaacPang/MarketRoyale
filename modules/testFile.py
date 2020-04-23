class Junk:
    def givefunc(self, gimme=1):
        if gimme == 1:
            return self.func1
        else:
            return self.func2

    def func1(self, teststring=None):
        if teststring:
            return teststring
        else:
            return 'This is func1'
    def func2(self, teststring=None):
        if teststring:
            return teststring
        else:
            return 'This is func2'

    def testfunc(self,gimme=1):
        chosen_func = self.givefunc(gimme)
        mystr = f"{chosen_func()}\n{chosen_func('Print this test string')}"
        print(mystr)

if __name__ == "__main__":
    j = Junk()
    j.testfunc()
    j.testfunc(0)