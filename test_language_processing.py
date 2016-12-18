from language_processing import LanguageProcessing
from events import Event
from datetime import datetime


class TestLanguageProcessing:
    def test_analyse_formal1(self):
        lp = LanguageProcessing()
        test_case1 = lp.analyse(0, '01.01.2001 10:00 Test case 1')[1]
        expected_test_case1 = Event(0, datetime(2001, 1, 1, 10, 0), datetime(2001, 1, 1, 10, 0), None, 'Test case 1', None)
        assert str(test_case1) == str(expected_test_case1)

    def test_analyse_formal2(self):
        lp = LanguageProcessing()
        test_case2 = lp.analyse(0, '01.01.01 10:00 Test case 2')[1]
        expected_test_case2 = Event(0, datetime(2001, 1, 1, 10, 0), datetime(2001, 1, 1, 10, 0), None, 'Test case 2', None)
        assert str(test_case2) == str(expected_test_case2)

    def test_analyse_formal3(self):
        lp = LanguageProcessing()
        test_case3 = lp.analyse(0, '01.01.01 10:00 02.02.02 20:00 Test case 3')[1]
        expected_test_case3 = Event(0, datetime(2001, 1, 1, 10, 0), datetime(2002, 2, 2, 20, 0), None, 'Test case 3', None)
        assert str(test_case3) == str(expected_test_case3)

    def test_analyse_formal4(self):
        lp = LanguageProcessing()
        test_case4 = lp.analyse(0, '01.01.01 10:00 10 мин Test case 4')[1]
        expected_test_case4 = Event(0, datetime(2001, 1, 1, 10, 0), datetime(2001, 1, 1, 10, 0), 10, 'Test case 4', None)
        assert str(test_case4) == str(expected_test_case4)

    def test_analyse_formal5(self):
        lp = LanguageProcessing()
        test_case5 = lp.analyse(0, '01.01.01 10:00 Test case 5')[1]
        expected_test_case5 = Event(0, datetime(2001, 1, 1, 10, 0), datetime(2001, 1, 1, 10, 0), None, 'Test case 5', None)
        assert str(test_case5) == str(expected_test_case5)

    def test_analyse_formal6(self):
        lp = LanguageProcessing()
        test_case6 = lp.analyse(0, '01.01.01 10:00 #basic Test case 6')[1]
        expected_test_case6 = Event(0, datetime(2001, 1, 1, 10, 0), datetime(2001, 1, 1, 10, 0), None, 'Test case 6', 'Basic')
        assert str(test_case6) == str(expected_test_case6)

    def analyse_formal_full1(self):
        lp = LanguageProcessing()
        test_case_formal_full1 = lp.analyse(0, '01.01.2001 10:00 02.02.02 20:00 10 мин #basic Test case FORMAL FULL 1')[1]
        expected_test_case_formal_full1 = Event(0, datetime(2001, 1, 1, 10, 0), datetime(2001, 1, 1, 10, 0), 10, 'Test case FORMAL FULL ',
                                    'Basic')
        assert str(test_case_formal_full1) == str(expected_test_case_formal_full1)