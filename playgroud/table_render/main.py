from nicegui import ui

columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left'},
    {'name': 'age', 'label': 'Age', 'field': 'age', 'sortable': True},
]
rows = [
    {'name': 'Elsa', 'age': 18},
    {'name': 'Oaken', 'age': 46},
    {'name': 'Hans', 'age': 20},
    {'name': 'Sven'},
    {'name': 'Olaf', 'age': 4},
    {'name': 'Anna', 'age': 17},
]
ui.table(columns=columns, rows=rows, pagination=3)
ui.table(columns=columns, rows=rows, pagination={'rowsPerPage': 4, 'sortBy': 'age', 'page': 2})

ui.run()