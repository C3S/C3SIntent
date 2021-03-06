# -*- coding: utf-8  -*-
import unittest
from pyramid import testing

from c3sintent.models import DBSession


def _initTestingDB():
    """
    set up a database to run tests against
    """
    from sqlalchemy import create_engine
    from c3sintent.models import initialize_sql
    try:
        session = initialize_sql(create_engine('sqlite:///:memory:'))
    except:
        session = DBSession
    return session


class TestUtilities(unittest.TestCase):
    """
    tests for c3sintent/utils.py
    """
    def setUp(self):
        """
        set up everything for a test case
        """
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        try:
            DBSession.remove()
        except:
            pass
        self.session = _initTestingDB()

    def tearDown(self):
        """
        clean up after a test case
        """
        DBSession.remove()
        testing.tearDown()

    def test_generate_pdf_en(self):
        """
        Test pdf generation
        and resulting pdf size
        """
        from c3sintent.views import generate_pdf

        mock_appstruct = {
            'firstname': u'Anne',
            'lastname': u'Gilles',
            'city': u'Müsterstädt',
            'email': u'foo@example.com',
            'date_of_birth': '1987-06-05',
            'country': u'some country',
            'opt_band': u'Moin Meldön',
            'opt_URL': 'http://moin.meldon.foo',
            'activity': set([u'composer', u'lyricist', u'dj']),
            'member_of_colsoc': 'member_of_colsoc',
            'name_of_colsoc': 'Foo Colsoc',
            'invest_member': 'yes',
            'noticed_dataProtection': 'noticed_dataProtection',
            '_LOCALE_': 'en',
        }

        # a skipTest iff pdftk is not installed
        import subprocess
        from subprocess import CalledProcessError
        try:
            res = subprocess.check_call(
                ["which", "pdftk"], stdout=None)
            if res == 0:
                # go ahead with the tests
                result = generate_pdf(mock_appstruct)

                self.assertEquals(result.content_type,
                                  'application/pdf')
                #print("size of pdf: " + str(len(result.body)))
                # check pdf size
                self.assertTrue(100000 > len(result.body) > 50000)

                # TODO: check pdf for contents

        except CalledProcessError, cpe:  # pragma: no cover
            print("pdftk not installed. skipping test!")
            print(cpe)

    def test_generate_pdf_de(self):
        """
        Test pdf generation
        and resulting pdf size
        """
        from c3sintent.views import generate_pdf

        mock_appstruct = {
            'firstname': u'Anne',
            'lastname': u'Gilles',
            'city': u'Müsterstädt',
            'email': u'foo@example.com',
            'date_of_birth': u'1987-06-05',
            'country': u'my country',
            'activity': set([u'composer', u'lyricist', u'dj']),
            'opt_band': u'Moin Meldön',
            'opt_URL': 'http://moin.meldon.foo',
            'member_of_colsoc': 'member_of_colsoc',
            'name_of_colsoc': 'Foo colsoc',
            'invest_member': 'yes',
            'noticed_dataProtection': 'noticed_dataProtection',
            '_LOCALE_': 'de',
            }

        # a skipTest iff pdftk is not installed
        import subprocess
        from subprocess import CalledProcessError
        try:
            res = subprocess.check_call(
                ["which", "pdftk"], stdout=None)
            if res == 0:
                # go ahead with the tests
                result = generate_pdf(mock_appstruct)

                self.assertEquals(result.content_type,
                                  'application/pdf')
                #print("size of pdf: " + str(len(result.body)))
                # check pdf size
                self.assertTrue(100000 > len(result.body) > 50000)

                # TODO: check pdf for contents

        except CalledProcessError, cpe:  # pragma: no cover
            print("pdftk not installed. skipping test!")
            print(cpe)

    def test_generate_csv(self):
        """
        test creation of csv snippet
        """
        from c3sintent.utils import generate_csv
        my_appstruct = {
            'activity': ['composer', 'dj'],
            'firstname': u'Jöhn',
            'lastname': u'Doe',
#            'address1': 'In the Middle',
#            'address2': 'Of Nowhere',
#            'postCode': '12345',
            'city': u'My Town',
            'email': u'john@example.com',
#            'region': 'Hessen',
            'country': u'de',
            'date_of_birth': u'1987-06-05',
            'member_of_colsoc': u'yes',
            'name_of_colsoc': u'GEMA FöTT',
            'opt_URL': u'http://foo.bar.baz',
            'opt_band': u'Moin Meldn',
            'consider_joining': u'yes',
            'noticed_dataProtection': u'yes',
            'invest_member': u'yes'
        }
        result = generate_csv(my_appstruct)
        #print("test_generate_csv: the result: %s") % result
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        expected_result = today + ',pending...,Jöhn,Doe,john@example.com,My Town,de,j,http://foo.bar.baz,Moin Meldn,1987-06-05,j,n,n,n,j,j,GEMA FöTT,j\r\n'
        # note the \r\n at the end: that is line-ending foo!

        #print("type of today: %s ") % type(today)
        #print("type of result: %s ") % type(result)
        #print("type of expected_result: %s ") % type(expected_result)
        #print("result: \n%s ") % (result)
        #print("expected_result: \n%s ") % (expected_result)
        self.assertEqual(result, expected_result)

#            result == str(today + ';unknown;pending...;John;Doe;' +
#                          'john@example.com;In the Middle;Of Nowhere;' +
#                          '12345;My Town;Hessen;de;j;n;n;n;n;j;j;j;j;j;j'))

    def test_mail_body(self):
        """
        test if mail body is constructed correctly
        and if umlauts work
        """
        #print("test_utils.py:TestUtilities.test_mail_body:\n")
        from c3sintent.utils import make_mail_body
        import datetime
        dob = datetime.date(1999, 1, 1)
        my_appstruct = {
            'activity': [u'composer', u'dj'],
            'firstname': u'Jöhn test_mail_body',
            'lastname': u'Döe',
            'date_of_birth': dob,
            'city': u'Town',
            'email': u'john@example.com',
            'country': u'af',
            'member_of_colsoc': u'yes',
            'name_of_colsoc': u'Hessen',
            'invest_member': u'yes',
            'opt_band': u'the yes',
            'opt_URL': u'http://the.yes',
            'noticed_dataProtection': u'yes'
        }
        result = make_mail_body(my_appstruct)
        #print("test_mail_body: result: \n %s") % result
        self.failUnless(u'composer, ' in result)
        self.failUnless(u'dj, ' in result)
        self.failUnless(u'Jöhn test_mail_body' in result)
        self.failUnless(u'Döe' in result)
        self.failUnless(u'Town' in result)
        self.failUnless(u'john@example.com' in result)
        self.failUnless(u'af' in result)
        self.failUnless(
            u'member of coll. soc.:           yes' in result)
        self.failUnless(
            u'noticed data protection:        yes' in result)
        self.failUnless(u"that's it.. bye!" in result)

    # def test_accountant_mail(self):
    #     """
    #     test creation of email Message object
    #     """
    #     from c3sintent.utils import accountant_mail
    #     import datetime
    #     my_appstruct = {
    #         'activity': [u'composer', u'dj'],
    #         'firstname': u'Jöhn test_accountant_mail',
    #         'lastname': u'Doe',
    #         'date_of_birth': datetime.date(1987, 6, 5),
    #         'city': u'Town',
    #         'email': u'john@example.com',
    #         'country': u'af',
    #         'member_of_colsoc': u'yes',
    #         'name_of_colsoc': u'Foo Colsoc',
    #         'invest_member': u'yes',
    #         'opt_URL': u'http://the.yes',
    #         'opt_band': u'the yes',
    #         'noticed_dataProtection': u'yes'
    #     }
    #     result = accountant_mail(my_appstruct)

    #     from pyramid_mailer.message import Message

    #     self.assertTrue(isinstance(result, Message))
    #     self.assertTrue('yes@c3s.cc' in result.recipients)
    #     self.failUnless('-----BEGIN PGP MESSAGE-----' in result.body,
    #                     'something missing in the mail body!')
    #     self.failUnless('-----END PGP MESSAGE-----' in result.body,
    #                     'something missing in the mail body!')
    #     self.failUnless(
    #         '[C3S] Yes! a new letter of intent' in result.subject,
    #         'something missing in the mail body!')
    #     self.failUnless('noreply@c3s.cc' == result.sender,
    #                     'something missing in the mail body!')
