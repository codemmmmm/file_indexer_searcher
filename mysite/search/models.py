# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Files(models.Model):
    md5_filepath = models.TextField(db_column='MD5_FilePath', blank=True, null=False)  # Field name made lowercase.
    currenttime = models.TextField(db_column='CurrentTime', blank=True, null=False)  # Field name made lowercase.
    filename = models.TextField(db_column='FileName', blank=True, null=False)  # Field name made lowercase.
    fileextension = models.TextField(db_column='FileExtension', blank=True, null=False)  # Field name made lowercase.
    filetype = models.TextField(db_column='FileType', blank=True, null=False, verbose_name="File type")  # Field name made lowercase.
    filefullpath = models.TextField(db_column='FileFullPath', unique=True, blank=True, null=False, verbose_name="File path")  # Field name made lowercase.
    filefullpathplaceholder = models.TextField(db_column='FileFullPathPlaceholder', blank=True, null=False)  # Field name made lowercase.
    directorypath = models.TextField(db_column='DirectoryPath', blank=True, null=False)  # Field name made lowercase.
    filesize = models.IntegerField(db_column='FileSize', blank=True, null=False, verbose_name="File size")  # Field name made lowercase.
    filecreationdate = models.TextField(db_column='FileCreationDate', blank=True, null=False)  # Field name made lowercase.
    #filelastmodificationdate = models.TextField(db_column='FileLastModificationDate', blank=True, null=False, verbose_name="Last modified")  
    filelastmodificationdate = models.DateTimeField(db_column='FileLastModificationDate', blank=True, null=False, verbose_name="Last modified") # Field name made lowercase.
    fileowner = models.TextField(db_column='FileOwner', blank=True, null=False)  # Field name made lowercase.
    key = models.TextField(db_column='Key', primary_key=True, blank=True, null=False)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Files'

    def __str__(self):
        return self.filefullpath
