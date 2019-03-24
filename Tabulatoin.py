from __future__ import print_function
import itertools
import copy


class AMinTerm:
    """
    This class holds all the input values by end-user in data field.
    Another variable listB will store all the objects from table B (i.e. Table 2), that includes this specific minTerms
    """
    def __init__(self, ip):
        self.data = ip
        self.listB = []


class MinTerms:
    """
    This class stores list of all AMinTerm objects.
    It also stores few global variable, that will be initialize after user completes input entry.
    e.g. bitCount stores the MSB position.
    inputCount stores number of inputs, excluding don't care condition
    totalCount stores number of inputs, including don't care condition
    """
    def __init__(self):
        self.minTerms = []
        self.bitCount = 0
        self.inputCount = 0
        self.totalCount = 0

    def set_globals(self):
        """
        This function will be called after user completes input entry.
        it will  initialize all global variable
        :return: None
        """
        maximum = copy.copy(max(self.minTerms, key=lambda x: x.data))
        if maximum.data == 0:
            self.bitCount = 1
        else:
            while maximum.data > 0:
                maximum.data >>= 1
                self.bitCount += 1

        self.totalCount = len(self.minTerms)


class ClassA:
    """
    This class is for table A i.e. Table 1.
    it stores parameters for each cell in table 1.
    """
    def __init__(self, ip):
        self.data = ip
        self.prime_implicants = True
        self.one_count = bin(ip).count('1')
        self.underscore = 0


class ClassB:
    """
    This class is for table B i.e. Table 2.
    it stores parameters for each cell in table B.
    """
    def __init__(self, data, us):
        self.data = data
        self.underscore = us

    def __eq__(self, other):
        """
        This method is needed to check presence of object of Class B in the list of such object.
        Without this method, UID of object will be compared and list membership check fails.
        """
        return self.data == other.data and self.underscore == other.underscore


def Input():
    """
    This method prompt necessary messages for end-user and takes user input.
    It creates new object of type AMinTerm for each input and then append it in the member list of MinTerms object
    :return: object of MinTerms class
    """

    mts = MinTerms()

    print("Etner decimal values as Sum of Products. Range [0:256). Enter negative value to terminate. ")
    x = input()
    while x >= 0:
        amt = AMinTerm(x)
        mts.minTerms.append(amt)
        x = input()
    mts.inputCount = len(mts.minTerms)

    x = raw_input("Any Don't care condition ? Y/N ")
    if (x == 'y') or (x == 'Y'):
        x = input()
        while x > 0:
            amt = AMinTerm(x)
            mts.minTerms.append(amt)
            x = input()

    mts.set_globals()
    return mts


def TableA(input):
    """
    The first column will be intialized as listA by taking values as per user entered min terms.
    The terms will be combined and second column will be formed as holdList.
    Then holdList will be copied to listA and same process will be continued,
    untill the generated holdList is empty.
    :param input: object of MinTerms class
    :return: listB. This list contains all the objects of Class B.
    """

    listA = []
    listB = []

    for x in input.minTerms:
        a = ClassA(x.data)
        listA.append(a)

    inputList = listA
    inputList.sort(key=lambda x: x.data)

    while True:
        holdList = []
        holdCount = 0

        tempTupleList = itertools.combinations(inputList, 2)
        tempFilterTupleList = filter(lambda x: ((x[0].underscore == x[1].underscore) and
                                               ( (x[1].one_count - x[0].one_count) == 1)
                                     and (bin(x[1].data - x[0].data).count('1') == 1)), tempTupleList)

        for hTemp in tempFilterTupleList:
            hTemp[0].prime_implicants = False
            hTemp[1].prime_implicants = False
            tempA = ClassA(hTemp[0].data)
            tempA.underscore = hTemp[1].data - hTemp[0].data + hTemp[1].underscore
            holdList.append(tempA)
            holdCount += 1

        for x in inputList:
            if x.prime_implicants:
                tempB = ClassB(x.data, x.underscore)
                if tempB not in listB:
                    listB.append(tempB)

        if holdCount == 0:
            break

        inputList = [x for x in holdList]

    return listB


def TableB(listB, input):
    """
    The first column will be intialized as listA by taking values as per user entered min terms.
    The terms will be combined and second column will be formed as holdList.
    Then holdList will be copied to listA and same process will be continued,
    untill the generated holdList is empty.
    :param input: listB contains objects of Class B and object of MinTerms class
    :return: listDisplay. This list contains all the objects of Class B type, used to display final output
    count variable indiicates that the list contains essential prime implicants upto count in the output list.
    """
    listDisplay = []
    bAndMinTermsTuple = itertools.product(listB, input.minTerms[:input.inputCount])

    for b, m in bAndMinTermsTuple:
        if b.data == (b.data & m.data):
            if m.data == ((b.data | b.underscore) & m.data):
                m.listB.append(b)

    for m in input.minTerms:
        if len(m.listB) == 1:
            if m.listB[0] not in listDisplay:
                listDisplay.append(m.listB[0])
            if m.listB[0] in listB:
                listB.remove(m.listB[0])

    count = len(listDisplay)

    displayAndMinTermsTuple = itertools.product(listDisplay, input.minTerms)

    for d, m in displayAndMinTermsTuple:
        if d in m.listB:
            m.listB = []

    bAndMinTermsTuple = itertools.product(listB, input.minTerms)
    for b, m in bAndMinTermsTuple:
        if b in m.listB:
            if b not in listDisplay:
                listDisplay.append(b)
            if b in listB:
                listB.remove(b)
            m.listB = []

    return listDisplay, count


def Display(listDisplay, mts, count):
    """
    This method display the final answer. It ignore bits as pwe underscore variable of ClassB object. It prints ' symbol
    if the bit is reset in data vraible of classB object
    TODO : Remove + sign at the end and dispaly the answer on Karnough Map.
    :param listDisplay: list of all classB type objects to be displayed as final answer.
    :param mts: MinTerms object. It contains all user inputs and global variable
    :param count: till count, all the objects are essential prime implicants. After that non-essential prime implicants.
    :return: None
    """

    if count > 0:
        print("Essential prime implicants are:")
        for x in listDisplay[:count]:
            character = 65
            i = 2 ** (mts.bitCount - 1)
            while i > 0:
                if x.underscore & i:
                    pass
                else:
                    print("{}".format(chr(character)), end = '')
                    if not (x.data & i):
                        print("'", end='')
                character = character + 1
                i >>= 1
            print(" + ", end ='')

    if len(listDisplay) > count:
        print("\nnonEssential prime implicants are:")
        for x in listDisplay[count:]:
            character = 65
            i = 2 ** (mts.bitCount - 1)
            while i > 0:
                if x.underscore & i:
                    pass
                else:
                    print("{}".format(chr(character)), end = '')
                    if not (x.data & i):
                        print("'", end='')
                character = character + 1
                i >>= 1
            print(" + ", end ='')
    return


if __name__ == '__main__':
    mts = Input()
    listB = TableA(mts)
    listDisplay, count = TableB(listB, mts)
    Display(listDisplay, mts, count)
