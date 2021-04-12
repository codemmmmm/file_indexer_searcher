import django_tables2 as tables
from .models import Files

class FilesTable(tables.Table):  
    filetype = tables.Column(orderable=False)
     
    class Meta:
        model = Files        
        fields = ("filefullpath", "filetype", "filesize", "filelastmodificationdate")