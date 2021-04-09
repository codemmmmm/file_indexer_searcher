# Generated by Django 3.2 on 2021-04-07 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Files',
            fields=[
                ('md5_filepath', models.TextField(blank=True, db_column='MD5_FilePath')),
                ('currenttime', models.TextField(blank=True, db_column='CurrentTime')),
                ('filename', models.TextField(blank=True, db_column='FileName')),
                ('fileextension', models.TextField(blank=True, db_column='FileExtension')),
                ('filetype', models.TextField(blank=True, db_column='FileType')),
                ('filefullpath', models.TextField(blank=True, db_column='FileFullPath', unique=True)),
                ('filefullpathplaceholder', models.TextField(blank=True, db_column='FileFullPathPlaceholder')),
                ('directorypath', models.TextField(blank=True, db_column='DirectoryPath')),
                ('filesize', models.IntegerField(blank=True, db_column='FileSize')),
                ('filecreationdate', models.TextField(blank=True, db_column='FileCreationDate')),
                ('filelastmodificationdate', models.TextField(blank=True, db_column='FileLastModificationDate')),
                ('fileowner', models.TextField(blank=True, db_column='FileOwner')),
                ('key', models.TextField(blank=True, db_column='Key', primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'Files',
                'managed': False,
            },
        ),
    ]
