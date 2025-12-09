from nicegui import ui

editor = ui.editor(placeholder='Type something here')
ui.markdown() \
    .bind_content_from(editor, 'value', backward=lambda v: f'HTML code:\n```\n{v}\n```')

ui.run()