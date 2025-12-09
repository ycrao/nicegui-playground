from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=255)


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)


class Article(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    category = fields.ForeignKeyField('models.Category', related_name='articles', null=True)
    published = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
