#!/bin/env/python
# -*- coding: utf-8 -*-
# http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
#                                            #creating-functional-tests
import unittest


class FunctionalTests(unittest.TestCase):
    """
    these tests are functional tests to check functionality of the whole app
    (i.e. integration tests)
    they also serve to get coverage for 'main'
    """
    def setUp(self):
        my_settings = {'sqlalchemy.url': 'sqlite://',
                       'available_languages': 'da de en es fr'}
                        # mock, not even used!?
        #from sqlalchemy import engine_from_config
        #engine = engine_from_config(my_settings)

        from c3sintent import main
        app = main({}, **my_settings)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        # maybe I need to check and remove globals here,
        # so the other tests are not compromised
        #del engine
        from c3sintent.models import DBSession
        DBSession.remove()

    def test_base_template(self):
        """load the front page, check string exists"""
        res = self.testapp.get('/', status=200)
        self.failUnless('Cultural Commons Collecting Society' in res.body)
        self.failUnless(
            'Copyright 2013, OpenMusicContest.org e.V.' in res.body)

    def test_faq_template(self):
        """load the FAQ page, check string exists"""
        res = self.testapp.get('/faq', status=200)
        self.failUnless('Why is it that C3S wants me to sign?' in res.body)
        self.failUnless(
            'Copyright 2013, OpenMusicContest.org e.V.' in res.body)

    def test_lang_en_LOCALE(self):
        """load the front page, forced to english (default pyramid way),
        check english string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/?_LOCALE_=en', status=200)
        self.failUnless('Start the fire!' in res.body)

    def test_lang_en(self):
        """load the front page, set to english (w/ pretty query string),
        check english string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/?en', status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        self.failUnless('Start the fire!' in res1.body)

# so let's test the app's obedience to the language requested by the browser
# i.e. will it respond to http header Accept-Language?

    # def test_accept_language_header_da(self):
    #     """check the http 'Accept-Language' header obedience: danish
    #     load the front page, check danish string exists"""
    #     res = self.testapp.reset()  # delete cookie
    #     res = self.testapp.get('/', status=200,
    #                            headers={
    #             'Accept-Language': 'da'})
    #     #print(res.body) #  if you want to see the pages source
    #     self.failUnless(
    #         '<input type="hidden" name="_LOCALE_" value="da"' in res.body)

    def test_accept_language_header_de_DE(self):
        """check the http 'Accept-Language' header obedience: german
        load the front page, check german string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/', status=200,
                               headers={
                'Accept-Language': 'de-DE'})
        #print(res.body) #  if you want to see the pages source
        self.failUnless(
            'zum geplanten Beitritt' in res.body)
        self.failUnless(
            '<input type="hidden" name="_LOCALE_" value="de"' in res.body)

    def test_accept_language_header_en(self):
        """check the http 'Accept-Language' header obedience: english
        load the front page, check english string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/', status=200,
                               headers={
                'Accept-Language': 'en'})
        #print(res.body) #  if you want to see the pages source
        self.failUnless(
            "I'm musically involved in creating at least three songs, and I'm considering"
            in res.body)

    # def test_accept_language_header_es(self):
    #     """check the http 'Accept-Language' header obedience: spanish
    #     load the front page, check spanish string exists"""
    #     res = self.testapp.reset()  # delete cookie
    #     res = self.testapp.get('/', status=200,
    #                            headers={
    #             'Accept-Language': 'es'})
    #     #print(res.body) #  if you want to see the pages source
    #     self.failUnless(
    #         'Luego de enviar el siguiente formulario,' in res.body)

    # def test_accept_language_header_fr(self):
    #     """check the http 'Accept-Language' header obedience: french
    #     load the front page, check french string exists"""
    #     res = self.testapp.reset()  # delete cookie
    #     res = self.testapp.get('/', status=200,
    #                            headers={
    #             'Accept-Language': 'fr'})
    #     #print(res.body) #  if you want to see the pages source
    #     self.failUnless(
    #         'En envoyant un courriel à data@c3s.cc vous pouvez' in res.body)

    def test_no_cookies(self):
        """load the front page, check default english string exists"""
        res = self.testapp.reset()  # delete cookie
        res = self.testapp.get('/', status=200,
                               headers={
                'Accept-Language': 'af, cn'})  # ask for missing languages
        #print res.body
        self.failUnless('Declaration' in res.body)

#############################################################################
# check for validation stuff

    def test_form_lang_en_non_validating(self):
        """load the join form, check english string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/?_LOCALE_=en', status=200)
        form = res.form
        #print(form.fields)
        #print(form.fields.values())
        form['firstname'] = 'John'
        #form['address2'] = 'some address part'
        res2 = form.submit('submit')
        self.failUnless(
            'There was a problem with your submission' in res2.body)

    def test_form_lang_de(self):
        """load the join form, check german string exists"""
        res = self.testapp.get('/?de', status=302)
        #print(res)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res2 = res.follow()
        #print(res2)
        # test for german translation of template text (lingua_xml)
        self.failUnless('Mit dem Formular erklärst Du Deine Absicht' in res2.body)
        # test for german translation of form field label (lingua_python)
        self.failUnless('Texter' in res2.body)

    def test_form_lang_LOCALE_de(self):
        """load the join form in german, check german string exists
        this time forcing german locale the pyramid way
        """
        res = self.testapp.get('/?_LOCALE_=de', status=200)
        # test for german translation of template text (lingua_xml)
        self.failUnless('Mit dem Formular erklärst Du Deine Absicht' in res.body)
        # test for german translation of form field label (lingua_python)
        self.failUnless('Texter' in res.body)

###########################################################################
# checking the disclaimer

    def test_disclaimer_en(self):
        """load the disclaimer in english (via query_string),
        check english string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/disclaimer?en', status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        self.failUnless(
            'you may order your data to be deleted at any time' in str(
                res1.body),
            'expected string was not found in web UI')

    def test_disclaimer_de(self):
        """load the disclaimer in german (via query_string),
        check german string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/disclaimer?de', status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        self.failUnless(
            'Die Cultural Commons Collecting Society ist ein Projekt von' in str(
                res1.body),
            'expected string was not found in web UI')

    def test_disclaimer_LOCALE_en(self):
        """load the disclaimer in english, check english string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/disclaimer?_LOCALE_=en', status=200)
        self.failUnless(
            'you may order your data to be deleted at any time' in str(
                res.body),
            'expected string was not found in web UI')

    def test_disclaimer_LOCALE_de(self):
        """load the disclaimer in german, check german string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/disclaimer?_LOCALE_=de', status=200)
        self.failUnless(
            'Die Cultural Commons Collecting Society ist ein Projekt von' in str(
                res.body),
            'expected string was not found in web UI')

    def test_success_wo_data_en(self):
        """load the success page in german (via query_string),
        check for redirection and german string exists"""
        res = self.testapp.reset()
        res = self.testapp.get('/success?en', status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        #print(res1)
        self.failUnless(  # check text on page redirected to
            'After submitting the form below' in str(
                res1.body),
            'expected string was not found in web UI')

    def test_success_pdf_wo_data_en(self):
        """
        try to load a pdf (which must fail because the form was not used)
        check for redirection and string exists
        """
        res = self.testapp.reset()
        res = self.testapp.get(
            '/C3S_DeclarationOfIntent_ThefirstnameThelastname.pdf',
            status=302)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res1 = res.follow()
        #print(res1)
        self.failUnless(  # check text on page redirected to
            'After submitting the form below' in str(
                res1.body),
            'expected string was not found in web UI')

    def test_success_w_data(self):
        """
        load the form, fill the form, (in one go via POST request)
        check for redirection, download PDF
        """
        res = self.testapp.reset()
        #res = self.testapp.get('/', status=200)
        res = self.testapp.post(
            '/',  # where the form is served
            {
                'submit': True,
                'firstname': 'TheFirstName',
                'lastname': 'TheLastName',
                'date_of_birth': '1987-06-05',
                'city': 'Devilstown',
                'email': 'email@example.com',
                '_LOCALE_': 'en',
                'activity': set(
                    [
                        u'composer',
                        #u'dj'
                    ]
                ),
                'country': 'AF',
                'invest_member': 'yes',
                'member_of_colsoc': 'yes',
                'name_of_colsoc': 'schmoo',
                'opt_band': 'yes band',
                'opt_URL': 'http://yes.url',
                'noticed_dataProtection': 'yes'

            },
            status=302,  # expect redirection to success page
        )

        #print(res.body)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res2 = res.follow()
        self.failUnless('Success' in res2.body)
        #print res2.body
        self.failUnless('TheFirstName' in res2.body)
        self.failUnless('TheLastName' in res2.body)
        self.failUnless('1987-06-05' in res2.body)
        self.failUnless('Devilstown' in res2.body)
        self.failUnless('email@example.com' in res2.body)
        self.failUnless('composer' in res2.body)
#        self.failUnless('dj' in res2.body)
        self.failUnless('schmoo' in res2.body)
        self.failUnless('yes band' in res2.body)
        self.failUnless('yes.url' in res2.body)

#        # try to download the PDF
#        res3 = self.testapp.get(
#            '/C3S_DeclarationOfIntent_ThefirstnameThelastname.pdf',
#            status=200
#        )
#        self.failUnless(40000 < len(res3.body) < 60000)  # check pdf size

        # now check for the "mail was sent" confirmation
        res3 = self.testapp.post(
            '/check_email',
            {
                'submit': True,
                'value': "send mail"
            }
        )

    def test_success_and_reedit(self):
        """
        submit form, check success, re-edit: are the values pre-filled?
        """
        res = self.testapp.reset()
        #res = self.testapp.get('/', status=200)
        res = self.testapp.post(
            '/',  # where the form is served
            {
                'submit': True,
                'firstname': 'TheFirstNäme',
                'lastname': 'TheLastNäme',
                'date_of_birth': '1987-06-05',
                'city': 'Devilstöwn',
                'email': 'email@example.com',
                '_LOCALE_': 'en',
                'activity': set(
                    [
                        'composer',
                        #u'dj'
                    ]
                ),
                'country': 'AF',
                'invest_member': 'yes',
                'member_of_colsoc': 'yes',
                'name_of_colsoc': 'schmoö',
                'opt_band': 'yes bänd',
                'opt_URL': 'http://yes.url',
                'noticed_dataProtection': 'yes'

            },
            status=302,  # expect redirection to success page
        )

        #print(res.body)
        self.failUnless('The resource was found at' in res.body)
        # we are being redirected...
        res2 = res.follow()
        self.failUnless('Success' in res2.body)
        #print("success page: \n%s") % res2.body
        #self.failUnless(u'TheFirstNäme' in (res2.body))

        # go back to the form and check the pre-filled values
        res3 = self.testapp.get('/')
        #print(res3.body)
        #print("edit form: \n%s") % res3.body
        self.failUnless('TheFirstNäme' in res3.body)
        form = res3.form
        self.failUnless(form['firstname'].value == u'TheFirstNäme')

    def test_email_confirmation(self):
        """
        test email confirmation
        """
        res = self.testapp.reset()
        res = self.testapp.get('/verify/foo@shri.de/ABCDEFGHIJ', status=200)
        #print(res.body)
        self.failUnless("Success. load your PDF!" in res.body)
        res2 = self.testapp.get(
            '/C3S_DeclarationOfIntent_ThefirstnameThelastname.pdf',
            status=200
        )
        self.failUnless(40000 < len(res2.body) < 60000)  # check pdf size

    def test_email_confirmation_wrong_mail(self):
        """
        test email confirmation with a wrong email
        """
        res = self.testapp.reset()
        res = self.testapp.get(
            '/verify/NOTEXISTS@shri.de/ABCDEFGHIJ', status=200)
        #print(res.body)
        self.failUnless("something went wrong." in res.body)

    def test_email_confirmation_wrong_code(self):
        """
        test email confirmation with a wrong code
        """
        res = self.testapp.reset()
        res = self.testapp.get('/verify/foo@shri.de/WRONGCODE', status=200)
        #print(res.body)
        self.failUnless("Not found. check URL." in res.body)

    def test_success_check_email(self):
        """
        test "check email" success page with wrong data
        """
        res = self.testapp.reset()
        res = self.testapp.get('/check_email', status=302)

        res2 = res.follow()
        self.failUnless("After submitting the form below" in res2.body)
