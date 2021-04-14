import django_tables2 as tables
from .models import Files

class FilesTable(tables.Table):  
    filetype = tables.Column(orderable=False)
    filefullpath = tables.Column(attrs={"td": {"onClick": "navigator.clipboard.writeText(this.innerText); alert('Copied file path to clipboard!');"}})
    #bootstrap responsive columns
    #filepath = tables.Column(orderable=False, attrs={"td": {"onClick": "navigator.clipboard.writeText(this.innerText); alert('File path is in Clipboard!');",, "class":"filecolumn" }})  CSS: .filecolumn{ width: 75%}
    class Meta:
        model = Files        
        fields = ("filefullpath", "filetype", "filesize", "filelastmodificationdate")
        template_name = "django_tables2/bootstrap.html"