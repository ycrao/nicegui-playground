from nicegui import app, ui
from tortoise import Tortoise
import models
from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


# Database initialization
async def init_db() -> None:
    await Tortoise.init(db_url='sqlite://cms.db', modules={'models': ['models']})
    await Tortoise.generate_schemas()
    # Create default admin user if not exists
    if not await models.User.filter(username='admin').exists():
        await models.User.create(username='admin', password='123456')


async def close_db() -> None:
    await Tortoise.close_connections()


app.on_startup(init_db)
app.on_shutdown(close_db)

# Load Quill globally
ui.add_body_html('''
    <link href="https://cdn.jsdelivr.net/npm/quill@2/dist/quill.snow.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/quill@2/dist/quill.js"></script>
''', shared=True)


# Authentication middleware
unrestricted_page_routes = {'/login'}


@app.add_middleware
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') and request.url.path not in unrestricted_page_routes:
                return RedirectResponse(f'/login?redirect_to={request.url.path}')
        return await call_next(request)


def sidebar():
    with ui.left_drawer().classes('bg-gray-100'):
        ui.label('CMS Admin').classes('text-xl font-bold p-4')
        ui.separator()
        ui.button('Dashboard', on_click=lambda: ui.navigate.to('/')).classes('w-full justify-start')
        ui.button('Categories', on_click=lambda: ui.navigate.to('/categories')).classes('w-full justify-start')
        ui.button('Articles', on_click=lambda: ui.navigate.to('/articles')).classes('w-full justify-start')
        ui.separator()
        ui.button('Logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login'))).classes('w-full justify-start text-red-600')


# Login page
@ui.page('/login')
def login(redirect_to: str = '/') -> Optional[RedirectResponse]:
    def try_login():
        async def check():
            user = await models.User.filter(username=username.value, password=password.value).first()
            if user:
                app.storage.user.update({'username': user.username, 'authenticated': True})
                ui.navigate.to(redirect_to)
            else:
                ui.notify('Wrong username or password', color='negative')
        ui.timer(0.1, check, once=True)

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center w-96'):
        ui.label('CMS Login').classes('text-2xl text-center mb-4')
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Login', on_click=try_login).classes('w-full')
    return None


# Dashboard
@ui.page('/')
async def dashboard():
    sidebar()
    async def load_stats():
        total_categories = await models.Category.all().count()
        total_articles = await models.Article.all().count()
        published_articles = await models.Article.filter(published=True).count()
        cat_count.set_text(str(total_categories))
        art_count.set_text(str(total_articles))
        pub_count.set_text(str(published_articles))

    ui.timer(0.1, load_stats, once=True)

    with ui.column().classes('w-full p-4'):
        ui.label('Dashboard').classes('text-3xl mb-8')
        with ui.grid(columns=3).classes('gap-4'):
            with ui.card():
                ui.icon('folder', size='3rem').classes('mb-2')
                ui.label('Total Categories')
                cat_count = ui.label('0').classes('text-2xl font-bold')
            with ui.card():
                ui.icon('article', size='3rem').classes('mb-2')
                ui.label('Total Articles')
                art_count = ui.label('0').classes('text-2xl font-bold')
            with ui.card():
                ui.icon('visibility', size='3rem').classes('mb-2')
                ui.label('Published Articles')
                pub_count = ui.label('0').classes('text-2xl font-bold')


# Categories CRUD
@ui.page('/categories')
async def categories():
    sidebar()
    async def load_categories():
        cats = await models.Category.all()
        table.rows = [{'id': c.id, 'name': c.name, 'articles_count': await c.articles.all().count()} for c in cats]
        table.update()

    async def add_category():
        if name_input.value:
            await models.Category.create(name=name_input.value)
            name_input.value = ''
            await load_categories()
            ui.notify('Category added', color='positive')

    async def delete_category(id):
        cat = await models.Category.get(id=id)
        if await cat.articles.all().count() > 0:
            ui.notify('Cannot delete category with articles', color='negative')
            return
        await cat.delete()
        await load_categories()
        ui.notify('Category deleted', color='positive')

    with ui.column().classes('w-full p-4'):
        ui.label('Categories').classes('text-3xl mb-4')

        with ui.row().classes('mb-4'):
            name_input = ui.input('Category Name')
            ui.button('Add Category', on_click=add_category)

        table = ui.table(
            columns=[
                {'name': 'name', 'label': 'Name', 'field': 'name'},
                {'name': 'articles_count', 'label': 'Articles Count', 'field': 'articles_count'},
                {'name': 'actions', 'label': 'Actions'}
            ],
            rows=[]
        )

        table.add_slot('body-cell-actions', '''
            <q-td :props="props">
                <q-btn flat round icon="delete" color="negative" @click="$parent.$emit('delete', props.row.id)" />
            </q-td>
        ''')

        table.on('delete', lambda e: delete_category(e.args))

        await load_categories()


# Articles CRUD
@ui.page('/articles')
async def articles():
    sidebar()
    async def load_articles():
        arts = await models.Article.all().prefetch_related('category')
        table.rows = [{
            'id': a.id,
            'title': a.title,
            'category': a.category.name if a.category else 'No Category',
            'published': 'Yes' if a.published else 'No',
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')
        } for a in arts]
        table.update()

    async def add_or_edit_article(article_id=None):
        art = await models.Article.get_or_none(id=article_id) if article_id else None
        cats = await models.Category.all()
        cat_options = {c.id: c.name for c in cats}

        with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl p-6'):
            ui.label('Edit Article' if art else 'Add Article').classes('text-2xl font-bold mb-6')
            title_input = ui.input('Title', value=art.title if art else '').classes('w-full mb-4')
            cat_select = ui.select(cat_options, label='Category', value=art.category_id if art else None).classes('w-full mb-4')
            ui.html('<div id="quill-editor" style="height:400px; margin:20px 0;"></div>', sanitize=False)
            published_switch = ui.switch('Published', value=art.published if art else False).classes('mb-4')

            async def save():
                if not cat_select.value:
                    ui.notify('Please select a category', color='negative')
                    return
                content = await ui.run_javascript('window.quill.root.innerHTML')
                if art:
                    art.title = title_input.value
                    art.content = content
                    art.category_id = cat_select.value
                    art.published = published_switch.value
                    await art.save()
                else:
                    await models.Article.create(
                        title=title_input.value,
                        content=content,
                        category_id=cat_select.value,
                        published=published_switch.value
                    )
                dialog.close()
                await load_articles()
                ui.notify('Article saved', color='positive')

            with ui.row().classes('justify-end gap-4 mt-6'):
                ui.button('Save', on_click=lambda: ui.timer(0.1, save, once=True)).classes('px-6')
                ui.button('Cancel', on_click=dialog.close).props('outline')

        await ui.run_javascript(f'''
            setTimeout(() => {{
                window.quill = new Quill('#quill-editor', {{theme:'snow', modules:{{toolbar:true}}}});
                window.quill.root.innerHTML = {repr(art.content if art else '')};
            }}, 100);
        ''')
        dialog.open()

    async def delete_article(id):
        art = await models.Article.get(id=id)
        await art.delete()
        await load_articles()
        ui.notify('Article deleted', color='positive')

    with ui.column().classes('w-full p-4'):
        ui.label('Articles').classes('text-3xl mb-4')

        ui.button('Add Article', on_click=lambda: add_or_edit_article()).classes('mb-4')

        table = ui.table(
            columns=[
                {'name': 'title', 'label': 'Title', 'field': 'title'},
                {'name': 'category', 'label': 'Category', 'field': 'category'},
                {'name': 'published', 'label': 'Published', 'field': 'published'},
                {'name': 'created_at', 'label': 'Created At', 'field': 'created_at'},
                {'name': 'actions', 'label': 'Actions'}
            ],
            rows=[]
        )

        table.add_slot('body-cell-actions', '''
            <q-td :props="props">
                <q-btn flat round icon="edit" color="primary" @click="$parent.$emit('edit', props.row.id)" />
                <q-btn flat round icon="delete" color="negative" @click="$parent.$emit('delete', props.row.id)" />
            </q-td>
        ''')

        table.on('edit', lambda e: add_or_edit_article(e.args))
        table.on('delete', lambda e: delete_article(e.args))

        await load_articles()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080, storage_secret='cms_secret')
