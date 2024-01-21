import sys

sys.path.append('.')

from importers.abn_amro import ABNAMROImporter

accounts = {
    '122013192': 'Assets:ABNAMRO:Checking:PersonA',
    '871952010': 'Assets:ABNAMRO:Checking:PersonB',
}

CONFIG = [ABNAMROImporter(accounts)]
