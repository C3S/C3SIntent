# -*- coding: utf-8  -*-
import tempfile
import subprocess
from fdfgen import forge_fdf
from c3sintent.gnupg_encrypt import encrypt_with_gnupg
from pyramid_mailer.message import Message
from pyramid_mailer.message import Attachment

DEBUG = False


def generate_pdf(appstruct):
    """
    this function receives an appstruct
    (a datastructure received via formsubmission)
    and prepares and returns a PDF using pdftk
    """
    DEBUG = False

    fdf_file = tempfile.NamedTemporaryFile()
    pdf_file = tempfile.NamedTemporaryFile()

    #import logging
    #log = logging.getLogger(__name__)
    #log.info("test ...! ")

    import os
    here = os.path.dirname(__file__)
    declaration_pdf_de = os.path.join(here, "../pdftk/DOIv2_de.pdf")
    declaration_pdf_en = os.path.join(here, "../pdftk/DOIv2_en.pdf")


# check for _LOCALE_, decide which language to use
    #print(appstruct['_LOCALE_'])
    if appstruct['_LOCALE_'] == "de":
        pdf_to_be_used = declaration_pdf_de
    elif appstruct['_LOCALE_'] == "en":
        pdf_to_be_used = declaration_pdf_en
    else:  # pragma: no cover
        # default fallback: english
        pdf_to_be_used = declaration_pdf_en

# here we gather all information from the supplied data to prepare pdf-filling

    fields = [
        ('FirstName', unicode(appstruct['firstname'])),
        ('LastName', unicode(appstruct['lastname'])),
        ('city', unicode(appstruct['city'])),
        ('email', unicode(appstruct['email'])),
        ('country', unicode(appstruct['country'])),
        ('composer',
         'Yes' if appstruct['activity'].issuperset(['composer']) else 'Off'),
        ('lyricist',
         'Yes' if appstruct['activity'].issuperset(['lyricist']) else 'Off'),
        ('producer',
         'Yes' if appstruct['activity'].issuperset(['music producer']) else 'Off'),
        ('remixer',
         'Yes' if appstruct['activity'].issuperset(['remixer']) else 'Off'),
        ('dj',
         'Yes' if appstruct['activity'].issuperset(['dj']) else 'Off'),
        #('YesDataProtection',
         #'Yes' if appstruct[
                #'noticed_dataProtection'] == u"(u'yes',)" else 'Off'),
        ('inColSoc', '1' if appstruct['member_of_colsoc'] == u'yes' else '2'),
        ('inColSocName', unicode(appstruct['name_of_colsoc']) if appstruct['member_of_colsoc'] == u'yes' else ''),
        ('URL', unicode(appstruct['opt_URL'])),
        ('bandPseudonym', unicode(appstruct['opt_band'])),
        ('investMmbr', '1' if appstruct['invest_member'] == u'yes' else '2'),
        ('dateOfBirth', appstruct['date_of_birth'].strftime("%d.%m.%Y")),
        ]

# generate fdf string

    fdf = forge_fdf("", fields, [], [], [])

# write it to a file

    if DEBUG:  # pragma: no cover
        print("== prepare: write fdf")

    fdf_file.write(fdf)
    fdf_file.seek(0)  # rewind to beginning

# process the PDF, fill in prepared data

    if DEBUG:  # pragma: no cover
        print("== PDFTK: fill_form & flatten")

        print("running pdftk...")
    pdftk_output = subprocess.call([
            'pdftk',
            pdf_to_be_used,  # input pdf with form fields
            'fill_form', fdf_file.name,  # fill in values
            'output', pdf_file.name,  # output file
            'flatten',  # make form read-only
#            'verbose'  # be verbose?
            ])

    if DEBUG:  # pragma: no cover
        print(pdf_file.name)
    pdf_file.seek(0)

    if DEBUG:  # pragma: no cover
        print("===== pdftk output ======")
        print(pdftk_output)

# return a pdf file
    from pyramid.response import Response
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")

    return response


def generate_csv(appstruct):
    """
    returns a csv with the relevant data
    to ease import of new data sets
    """
    from datetime import date
    # format:
    # date; signature; firstname; lastname; email;
    # city; country; composer; lyricist; producer; remixer;
    # dj; member_colsoc; dataProtection

    csv = tempfile.TemporaryFile()
    csv.write(
        (u"%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s") % (
            date.today().strftime("%Y-%m-%d"),  # e.g. 2012-09-02
            'pending...',  # #                           # has signature
            unicode(appstruct['firstname']),  # #    # lastname
            unicode(appstruct['lastname']),  # #    # surname
            unicode(appstruct['email']),  # #   # email
            unicode(appstruct['city']),
            unicode(appstruct['country']),  # # # country
            'j' if appstruct['invest_member'] == 'yes' else 'n',
            unicode(appstruct['opt_URL']),
            unicode(appstruct['opt_band']),
            unicode(appstruct['date_of_birth']),
            'j' if 'composer' in appstruct['activity'] else 'n',
            'j' if 'lyricist' in appstruct['activity'] else 'n',
            'j' if 'producer' in appstruct['activity'] else 'n',
            'j' if 'remixer' in appstruct['activity'] else 'n',
            'j' if 'dj' in appstruct['activity'] else 'n',
            'j' if appstruct['member_of_colsoc'] == 'yes' else 'n',
            unicode(appstruct['name_of_colsoc']),
            'j' if appstruct['noticed_dataProtection'] == 'yes' else 'n',
            ))
    # print for debugging? seek to beginning!
    #csv.seek(0)
    #print str(csv.read())
    csv.seek(0)
    return str(csv.read())


def make_mail_body(appstruct):
    """
    construct a multiline string to be used as the emails body
    """
    the_activities = ''
    for x in appstruct['activity']:
        the_activities += x + ', '
    unencrypted = u"""
Yay!
we got a declaration of intent through the form: \n
first name:                     %s
last name:                      %s
date of birth:                  %s
email:                          %s
city:                           %s
country:                        %s
investing member:               %s
homepage:                       %s
band/pseudonym:                 %s

activities:                     %s
member of coll. soc.:           %s
  name of coll. soc.:           %s
noticed data protection:        %s

that's it.. bye!""" % (
        unicode(appstruct['firstname']),
        unicode(appstruct['lastname']),
        unicode(appstruct['date_of_birth'].strftime("%d.%m.%Y")),
        unicode(appstruct['email']),
        unicode(appstruct['city']),
        unicode(appstruct['country']),
        unicode(appstruct['invest_member']),
        unicode(appstruct['opt_URL']),
        unicode(appstruct['opt_band']),
        the_activities,
        unicode(appstruct['member_of_colsoc']),
        unicode(appstruct['name_of_colsoc']),
        appstruct['noticed_dataProtection'],
        )

    return unencrypted


def accountant_mail(appstruct):

    unencrypted = make_mail_body(appstruct)

    message = Message(
        subject="[C3S] Yes! a new letter of intent",
        sender="noreply@c3s.cc",
        recipients=["yes@c3s.cc"],
        body=unicode(encrypt_with_gnupg((unencrypted)))
        )

    attachment = Attachment("DOI.csv.gpg", "application/gpg-encryption",
                            unicode(encrypt_with_gnupg(generate_csv(appstruct))))
    # TODO: make attachment contents a .csv with the data supplied.
    message.attach(attachment)

    return message
