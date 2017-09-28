from tabular_dataset.tabular_dataset import *

base_dictionaries = [
    {'a': 1, 'b': 2},
    {'a': 1, 'b': 2},
]


def test_frame_creation():
    expected = [
        ['a', 'b'],
        [1, 2],
        [1, 2],
    ]
    assert convert_dictionaries_to_frame(base_dictionaries) == expected


def test_get_header():
    assert sorted(get_header(base_dictionaries)) == sorted(['a', 'b'])


def test_get_header_no_data():
    assert get_header([]) == []


def test_get_header_ragged_dicts():
    ragged_dictionaries = [
        {'a': 1, 'b': 2},
        {'a': 1, 'b': 2, 'c': 3},
    ]
    assert sorted(get_header(ragged_dictionaries)) == sorted(['a', 'b', 'c'])


def test_all_keys():
    assert list(all_keys(base_dictionaries)) == ['a', 'b', 'a', 'b']


def test_as_dictionaries():
    td = TabularDataSet(raw_data=[
        ['a', 'b'],
        [1, 2],
        [1, 2]
    ])
    assert list(td.as_dictionaries()) == base_dictionaries


def test_from_dictionaries():
    td = TabularDataSet.from_dicts(base_dictionaries)
    assert list(td.as_dictionaries()) == base_dictionaries


def test_append_row():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.append_row(base_dictionaries[0])
    expected = base_dictionaries + [base_dictionaries[0]]
    assert list(td.as_dictionaries()) == expected


def test_append_row_ragged():
    td = TabularDataSet.from_dicts(base_dictionaries)
    new_row = {'c': 0}
    td.append_row(new_row)
    assert td.data_rows == [[1, 2, None], [1, 2, None], [None, None, 0]]


def test_header():
    td = TabularDataSet.from_dicts(base_dictionaries)
    assert td.header == list(base_dictionaries[0].keys())


def test_header_blank_data():
    td = TabularDataSet(raw_data=[])
    assert td.header == []


def test_as_dictionaries_with_index():
    td = TabularDataSet.from_dicts(base_dictionaries)
    expected = [dict(d) for d in base_dictionaries]
    for index, d in enumerate(expected):
        d["__index"] = index + 1
    assert list(td.as_dictionaries("__index")) == expected


def test_data_row_length():
    td = TabularDataSet.from_dicts(base_dictionaries)
    assert len(td.data_rows) == len(base_dictionaries)


def test_clear_data():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.clear_data()
    assert len(td.data_rows) == 0


def test_rename_column():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.rename_column(old_column_name='a', new_column_name='replaced')
    assert td.header == ['replaced', 'b']


def test_replace_column():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.replace_column(old_column_name='a',
                      new_column_name='replaced',
                      method=lambda x: x['a'] + 10)
    assert td.header == ['replaced', 'b']
    assert td.data_rows == [[11, 2]] * 2


def test_update():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.update(0, {'a': 5})
    assert td.data_rows[0] == [5, 2]


def test_remove_column():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.remove_column('b')
    assert td.data_rows == [[1], [1]]


def test_add_derived_column():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.add_derived_column("c", method=lambda x: 1)
    assert td.raw_data == [['a', 'b', 'c'], [1, 2, 1], [1, 2, 1]]


def test_add_derived_with_existing_column():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.add_derived_column("b", method=lambda x: 1)
    assert td.raw_data == [['a', 'b'], [1, 1], [1, 1]]


def test_filter():
    td = TabularDataSet.from_dicts(base_dictionaries)
    td.filter(lambda x: x['b'] == 2)
    assert td.raw_data == [['a', 'b']]


def test_addition():
    td1 = TabularDataSet.from_dicts(base_dictionaries)
    td2 = TabularDataSet.from_dicts(base_dictionaries)
    result = td1 + td2
    expected = td1
    for row in td2.data_rows:
        td1.raw_data.append(row)
    assert result.raw_data == expected.raw_data


def test_merge():
    header1 = ["name", "value", "value2"]
    bob1 = ["bob", 3, None]
    brett1 = ["brett", 2, 5]
    biff1 = ["biff", 2, None]

    header2 = ["name", "value2", "v3"]
    bill2 = ["bill", 4, 5]
    brett2 = ["brett", 6, 5]
    biff2 = ["biff", 7, 5]

    d1 = TabularDataSet(raw_data=[header1, bob1, brett1, biff1])
    d2 = TabularDataSet(raw_data=[header2, bill2, brett2, biff2])
    d3 = merge(d1, d2, lambda x: x['name'])

    expected = [['name', 'value', 'value2', 'v3'],
                ['bob', 3, None, None],
                ['brett', 2, 5, 5],
                ['biff', 2, 7, 5],
                ['bill', None, 4, 5]]

    assert d3.raw_data == expected


def test_merge2():
    header1 = ["name", "value", "value2"]
    bob1 = ["bob", 3, None]
    brett1 = ["brett", 2, 5]
    biff1 = ["biff", 2, None]

    header2 = ["name", "value2", "v3"]
    brett2 = ["brett", 6, 5]

    d1 = TabularDataSet(raw_data=[header1, bob1, brett1, biff1])
    d2 = TabularDataSet(raw_data=[header2, brett2])
    d3 = merge(d1, d2, lambda x: x['name'])

    expected = [['name', 'value', 'value2', 'v3'],
                ['bob', 3, None, None],
                ['brett', 2, 5, 5],
                ['biff', 2, None, None]]

    assert d3.raw_data == expected
