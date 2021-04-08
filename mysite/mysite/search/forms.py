from django import forms

class SearchForm(forms.Form):
    pattern = forms.CharField(help_text="Enter a pattern to match a file's path", label="Pattern")
    min_size = forms.IntegerField(help_text="Enter a minimum size in bytes", label="Minimum size", min_value=0, max_value=9223372036854775807, initial=0)
    max_size = forms.IntegerField(help_text="Enter a maximum size in bytes", label="Maximum size", min_value=0, max_value=9223372036854775807, initial=9223372036854775807)
    case_sensitive = forms.BooleanField(help_text="Check to enable case sensitive pattern matching", label="Case sensitivity", required=False)
