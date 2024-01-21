import re

from .vendor_map import vendor_map

def get_vendor_name(text):
    """
    Returns a vendor name given an ABN AMRO transaction text
    """

    vendor_name = text
    if text.startswith('SEPA '):
        vendor_name = sepa_name(text)
    elif text.startswith('/TRTP/SEPA ') or text.startswith('/TRTP/iDEAL/'):
        regexp = '/TRTP/.*?/NAME/(.*?)/(?:MARF|REMI|EREF)/'
        vendor_name = parse_name(regexp, text)
    elif text.startswith('BEA, '):
        regexp = r'BEA, (?:BETAALPAS|APPLE PAY)(.*?),PAS\d{3}'
        vendor_name = parse_name(regexp, text)
    elif text.startswith('eCom, '):
        regexp = r'eCom, (?:Betaalpas|Apple Pay)\s+(.*?)\s{3,}'
        vendor_name = parse_name(regexp, text)
    elif text.startswith('ACCOUNT BALANCED'):
        regexp = r'ACCOUNT BALANCED\s+(.*?)\d'
        vendor_name = parse_name(regexp, text)
    else:
        vendor_name = unparsable_name(text)

    return vendor_name


def get_description(text):
    """
    Returns a description given an ABN AMRO transaction text
    """

    # return the description as the vendor name if unable to parse
    description = text
    if text.startswith('SEPA '):
        description = sepa_description(text)
    elif text.startswith('/TRTP/SEPA ') or text.startswith('/TRTP/iDEAL/'):
        regexp = '/TRTP/.*?/NAME/.*?/REMI/(.*?)/(?:IBAN|EREF)'
        description = parse_description(regexp, text)
    elif text.startswith('BEA, '):
        regexp = r'BEA, (?:BETAALPAS|APPLE PAY).*?,PAS\d{3}(.*)'
        description = parse_description(regexp, text)
    elif text.startswith('eCom, '):
        regexp = r'eCom, (?:Betaalpas|Apple Pay)\s+(?:.*?)\s{3,}(.*)'
        description = parse_description(regexp, text)
    elif text.startswith('ACCOUNT BALANCED'):
        regexp = r'ACCOUNT BALANCED.*?(\d.*)'
        description = parse_description(regexp, text)
    else:
        description = unparsable_description(text)

    return description


def parse_name(regexp, text):
    name = text
    m = re.search(regexp, text, re.IGNORECASE)
    if m and m.group and m.group(1):
        name = m.group(1).strip()

    # Payment companies insert annoying prefixes like CCV*. Strp it
    if name.find('*') >= 0:
        bits = name.split('*')
        name = " / ".join(bits[1:])

    return name

def parse_description(regexp, text):
    description = text

    m = re.search(regexp, text, re.IGNORECASE)
    if m and m.group and m.group(1):
        description = m.group(1).strip()

    return re.sub(r'\s{2,}', ' / ', description) # replace multiple spaces by /

def trtp_name(text):
    name = text
    regexp = '/TRTP/.*?/NAME/(.*?)/(?:MARF|REMI|EREF)/'
    m = re.search(regexp, text)

def sepa_name(text):
    name = text
    regexp = r'NAAM: (.*?)(?:KENMERK|MACHTIGING|OMSCHRIJVING)'
    m = re.search(regexp, text, re.IGNORECASE)
    if m and m.group and m.group(1):
        name = m.group(1).strip()
    else:
        regexp = r'NAAM: (.*)'
        m = re.search(regexp, text, re.IGNORECASE)
        if m and m.group and m.group(1):
            name = m.group(1).strip()

    return name

def unparsable_name(text):
    # hard coded names for one-off transactions
    vendor_name = text

    # insert code here to handle text manually

    return vendor_name

def unparsable_description(text):
    # hard coded descriptions for one-off transactions
    description = text

    # insert code here to handle text manually

    return description


def sepa_description(text):
    description = text
    regexp = r'OMSCHRIJVING: (.*?)(KENMERK:|IBAN:|$)'
    m = re.search(regexp, text, re.IGNORECASE)
    if m and m.group and m.group(1):
        description = m.group(1).strip()

    return re.sub(r'\s{2,}', ' / ', description) # replace multiple spaces by /

def get_vendor_account(vendor_name, description):
    account = None
    if vendor_map.get(vendor_name):
        account = vendor_map[vendor_name]
    elif vendor_name.lower().startswith('albert heijn'):
        account = "Expenses:Groceries"
    elif vendor_name.startswith('NLOV'):
        account = "Expenses:Commuting:GVB"

    return account

