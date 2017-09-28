================
Tabular Data Set
================
Just s simple utility that's pure python to help work with xlwings range.expand() data.
Takes and excel spreadsheet and lets you convert it to and from dictionaries.

***************
Usage
***************

``pip install tabular_dataset``

``from tabular_dataset import TabularDataSet``

``td = TabularDataSet(raw_data=range.expand())``

``dict_list = list(td.as_dictionaries())``