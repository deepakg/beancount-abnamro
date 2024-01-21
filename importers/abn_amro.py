from datetime import datetime, timedelta
from decimal import Decimal
import warnings

from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.number import Decimal
from beancount.ingest.importer import ImporterProtocol

from lib.bank_utils import get_vendor_name, get_description, get_vendor_account

class InvalidFormatError(Exception):
    """
    Raised in case the data file is not compatible with the importer
    """
    pass

class ABNAMROImporter(ImporterProtocol):
    def __init__(self, accounts, currency='EUR'):
        self.accounts = accounts
        self.currency = currency

        super().__init__()

    def identify(self, file):
        with open(file.name) as fd:
            line = fd.readline().strip()

        if not line:
            return False

        try:
            fields = line.split("\t")
        except ValueError:
            return False
        else:
            return len(fields) == 8 and fields[0] in self.accounts and fields[1] == self.currency

    def extract(self, file):
        if not self.identify(file):
            warnings.warn(
                f'{file.name} is not compatible with ABNAMROImporter'
            )

        with open(file.name) as fd:
            lines = fd.readlines()

        line_index = 1

        entries = []
        last_account = ""
        last_balance = ""
        last_date = ""
        for line in lines:
            fields = line.strip().split("\t")

            # if there are mulitple accounts in file
            # only import transactions that belong to the
            # account corresponding to this parser
            if fields[0] not in self.accounts:
                continue

            if last_account == "":
                last_account = fields[0]

            meta = data.new_metadata(file.name, line_index)
            amount = Amount(Decimal(fields[6].replace(',', '.')), self.currency)
            date = datetime.strptime(fields[2], '%Y%m%d').date()
            vendor_name = get_vendor_name(fields[7].strip())
            description = get_description(fields[7].strip())
            to_account = get_vendor_account(vendor_name, description)
            if to_account:
                #found which account spending for this vendor should be attributed to
                #add it ot the posting
                postings = [
                    data.Posting(self.accounts[fields[0]], amount, None, None, None, None),
                    data.Posting(to_account, None, None, None, None, None) #for later when you have vendor to account mapping
                ]
            else:
                # just add the from account and balance the books by hand
                postings = [
                    data.Posting(self.accounts[fields[0]], amount, None, None, None, None),
                ]

            entries.append(
                data.Transaction(
                    meta, date, self.FLAG, vendor_name, description,
                    data.EMPTY_SET, data.EMPTY_SET, postings
                )
            )
            line_index += 1

            if last_account != fields[0]:
                last_balance = Amount(Decimal(last_balance.replace(',', '.')), self.currency)

                entries.append(
                    data.Balance(data.new_metadata(file.name, line_index - 1),
                                 last_date + timedelta(days=1),
                                 self.accounts[last_account],
                                 last_balance, None, None)
                )

                last_account = fields[0]

            last_balance = fields[4]
            last_date = date

        last_balance = Amount(Decimal(last_balance.replace(',', '.')), self.currency)
        entries.append(
            data.Balance(data.new_metadata(file.name, line_index - 1),
                         last_date + timedelta(days=1),
                         self.accounts[last_account],
                         last_balance, None, None)
        )

        return entries
