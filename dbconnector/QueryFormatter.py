import unittest




def formatQuery(q):
    q = q.strip("\\")
    splits = q.split()
    outStr=""
    currentmwe = ""
    parsingQuotes =False
    for split in splits:
        if split == "AND" or split == "OR" or split == "NOT":
            if currentmwe != "":
                outStr += '"{}"'.format(currentmwe.strip()) +" "
            outStr += split + " "
            currentmwe = ""
            continue

        if parsingQuotes:
            if split.endswith("\"") or split.endswith("\'"):
                parsingQuotes = False

            split = split.replace('\"', "")
            split = split.replace('\'', "").strip()
            if split != "":
                currentmwe+= split + " "

            continue

        if split.startswith("\"") or split.startswith("\'") :
            if currentmwe != "":
                outStr += '"{}"'.format(currentmwe.strip()) + " "
            currentmwe = ""
            split = split.replace('\"',"" )
            split = split.replace('\'',"" ).strip()
            if split != "":
                currentmwe += split + " "
            parsingQuotes = True
            continue
        currentmwe += split + " "
    outStr += '"{}"'.format(currentmwe.strip())

    return outStr.strip()


class TestFormatQuery(unittest.TestCase):
    def test(self):

        testStr = "Breast Cancer"
        expectedStr = '"{}"'.format(testStr)
        self.assertEqual(expectedStr,formatQuery(testStr))

        testStr = "Terminal Breast Cancer"
        expectedStr = '"{}"'.format(testStr)
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = '"Breast Cancer"'
        expectedStr = '{}'.format(testStr)
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = '"Terminal Breast Cancer"'
        expectedStr = '{}'.format(testStr)
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "Cancer"
        expectedStr = '"{}"'.format(testStr)
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = '"Cancer"'
        expectedStr = '{}'.format(testStr)
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "Breast Cancer AND male"
        expectedStr = '"{0}" AND "{1}"'.format("Breast Cancer","male")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "Breast Cancer AND large male"
        expectedStr = '"{0}" AND "{1}"'.format("Breast Cancer", "large male")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = '"Breast Cancer" AND "large male"'
        expectedStr = '"{0}" AND "{1}"'.format("Breast Cancer", "large male")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = '"Breast Cancer" AND "male"'
        expectedStr = '"{0}" AND "{1}"'.format("Breast Cancer", "male")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = '"Breast Cancer" AND "large male" OR female'
        expectedStr = '"{0}" AND "{1}" OR "{2}"'.format("Breast Cancer", "large male", "female")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = 'Breast Cancer AND large male OR female'
        expectedStr = '"{0}" AND "{1}" OR "{2}"'.format("Breast Cancer", "large male", "female")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = 'Breast Cancer AND large male OR female'
        expectedStr = '"{0}" AND "{1}" OR "{2}"'.format("Breast Cancer", "large male", "female")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "NOT Cancer"
        expectedStr = 'NOT "{}"'.format("Cancer")
        self.assertEqual(expectedStr, formatQuery(testStr))
        expectedStr = 'NOT "{}"'.format("Cancer")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "NOT 'Cancer'"
        expectedStr = 'NOT "{}"'.format("Cancer")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "NOT Breast Cancer"
        expectedStr = 'NOT "{}"'.format("Breast Cancer")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "NOT 'Breast Cancer'"
        expectedStr = 'NOT "{}"'.format("Breast Cancer")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "Lung Cancer AND NOT Breast Cancer"
        expectedStr = '"{0}" AND NOT "{1}"'.format("Lung Cancer","Breast Cancer")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "'Lung Cancer' AND NOT \"Breast Cancer\""
        expectedStr = '"{0}" AND NOT "{1}"'.format("Lung Cancer", "Breast Cancer")
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "Lung Cancer\\"
        expectedStr = "\"Lung Cancer\""
        self.assertEqual(expectedStr, formatQuery(testStr))

        testStr = "\Lung Cancer"
        expectedStr = "\"Lung Cancer\""
        self.assertEqual(expectedStr, formatQuery(testStr))


if __name__ == '__main__':
    unittest.main()