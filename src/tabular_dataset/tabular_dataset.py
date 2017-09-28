from collections import namedtuple
from copy import deepcopy


def all_keys(dictionaries):
    for row in dictionaries:
        for key in row.keys():
            yield key


def get_header(dictionaries):
    if len(dictionaries) == 0:
        return []
    return list({key: 1 for key in all_keys(dictionaries)}.keys())


def ordered_list(data, order, default=None):
    return [data.get(key, default) for key in order]


def order_all(data, order, default=None):
    return [ordered_list(row, order, default) for row in data]


def convert_dictionaries_to_frame(dictionaries):
    dictionaries = list(dictionaries)
    header = get_header(dictionaries)
    return [header] + order_all(dictionaries, header)


def as_dict(row, header):
    return dict(zip(header, row))


DataPair = namedtuple("DataPair", "raw, indexed")


class TabularDataSet:
    def __init__(self, *, raw_data):
        self.raw_data = raw_data

    @classmethod
    def from_dicts(cls, dict_list):
        return cls(raw_data=convert_dictionaries_to_frame(dict_list))

    def add_derived_column(self, column_name, *, method=lambda x: None):
        original_header = list(self.header)
        self._add_header_column(column_name)
        for pair in self._data_pairs:
            pair.raw.append(method(pair.indexed))
        if column_name in original_header:
            self.remove_column(column_name)

    def remove_column(self, column_name):
        index = self._first_index_of(column_name)
        for row in self.raw_data:
            del row[index]

    def filter(self, filter_func):
        to_remove = []
        for row in list(self.as_dictionaries(row_index_field_name="__index")):
            if filter_func(row):
                to_remove.append(self.raw_data[row["__index"]])
        for row in to_remove:
            self.raw_data.remove(row)

    def update(self, row_index, data):
        for k, v in data.items():
            self.data_rows[row_index][self._first_index_of(k)] = v

    def replace_column(self, *, old_column_name, new_column_name, method=None):
        if method is not None:
            for pair in self._data_pairs:
                index = self._first_index_of(old_column_name)
                pair.raw[index] = method(pair.indexed)
        self.rename_column(old_column_name=old_column_name,
                           new_column_name=new_column_name)

    def rename_column(self, *, old_column_name, new_column_name):
        self.header[self._first_index_of(old_column_name)] = new_column_name

    @property
    def header(self):
        if len(self.raw_data) > 0:
            return self.raw_data[0]
        return []

    @property
    def data_rows(self):
        if len(self.raw_data) > 1:
            return self.raw_data[1:]
        return []

    def clear_data(self):
        self.raw_data = [self.raw_data[0]]

    def as_dictionaries(self, row_index_field_name=None):
        if len(self.raw_data) > 1:
            header = list(self.header)
            if row_index_field_name is not None:
                header = list(header)
                header.append(row_index_field_name)
            for i, row in enumerate(self.data_rows, start=1):
                if row_index_field_name is not None:
                    row = list(row)
                    row.append(i)
                yield dict(zip(header, row))

    def append_row(self, item):
        new_row = [None] * len(self.header)
        for k, v in item.items():
            if k not in self.header:
                self.add_derived_column(column_name=k)
                new_row.append(None)
            index = self.header.index(k)
            new_row[index] = v
        self.raw_data.append(new_row)

    def __add__(self, other):
        ret = TabularDataSet(raw_data=[])
        ret.raw_data = deepcopy(self.raw_data)
        for item in other.as_dictionaries():
            ret.append_row(item)
        return ret

    def deep_copy(self):
        return TabularDataSet(raw_data=deepcopy(self.raw_data))

    @property
    def _data_pairs(self):
        for row in self.data_rows:
            yield DataPair(row, as_dict(row, self.header))

    def _add_header_column(self, column_name):
        self.header.append(column_name)

    def _first_index_of(self, column_name):
        return self.header.index(column_name)


def merge(dataset1, dataset2, key_func=None):
    new_ds = dataset1.deep_copy()

    existing = {key_func(d): d for d in new_ds.as_dictionaries(row_index_field_name="index")}
    for ds2_row in dataset2.as_dictionaries():
        key = key_func(ds2_row)
        if key not in existing.keys():
            new_ds.append_row(ds2_row)
        else:
            val = existing[key]
            for column_name, cell_value in ds2_row.items():
                if column_name not in new_ds.header:
                    new_ds.add_derived_column(column_name=column_name)
                existing_value = new_ds.raw_data[val["index"]][new_ds.header.index(column_name)]
                if existing_value is None:
                    new_ds.raw_data[val["index"]][new_ds.header.index(column_name)] = cell_value
    return new_ds

