## Synopsis
ABN AMRO Bank in the Netherlands lets you export your bank statements to plain text (.TAB) files. This importer (beancount-abnamro) helps you convert them to beancount transactions that you can append to your ledger.

## Installation
This module isn't available on PyPy yet so you'll have to install in manually. A sample statement and configuration file is included in the repository.

## Usage
Assuming you already have beancount installed and have configured it to use this importer, you should be able to run bean-extract.

```
bean-extract config.py TXT231209180908.TAB
```

(Don't forget to change `TXT231209180908.TAB` to the filename of the statement you are trying to import)

## Miscellany
Under the lib/ folder of this repository, you'll find a file called `vendor_map.py`. This file contains a dictionary that maps the name of the vendor to the account. You'll very likely want to edit this file to use your own expense accounts and modify vendor names.

`vendor_map.py`

```
vendor_map = {
    "KLM": "Expenses:Travel:Transport",
    "Spotify AB by Adyen": "Expenses:Subscriptions:Spotify",
    "Tokyo Ramen Iki": "Expenses:Eatout",
}
```

You could also leave the dictionary bank if you prefer to balance your books by hand. I personally prefer to map the most common transactions automatically and then use [fava](https://beancount.github.io/fava/) to look deeper.

You'll also see a file called bank_utils.py. It tries to parse transaction descriptions that ABN AMRO uses to a sensible, beancount friendly payee and narration. Each year I come across certain transaction descriptions (let's say around 1 in 1000) that defy all existing parsing logic. You can customize the `unparsable_name` and `unparsable_description` methods to handle those. By default these methods simply return whatever you pass to them.
