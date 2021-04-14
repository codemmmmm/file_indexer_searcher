from django import forms

class SearchForm(forms.Form):
    pattern = forms.CharField(help_text="Enter a pattern to match a file's path", label="Pattern", initial="/")
    min_size = forms.IntegerField(help_text="Enter a minimum size in bytes", label="Minimum size", min_value=0, max_value=9223372036854775807, initial=0)
    max_size = forms.IntegerField(help_text="Enter a maximum size in bytes", label="Maximum size", min_value=0, max_value=9223372036854775807, initial=9223372036854775807)
    case_sensitive = forms.BooleanField(help_text="Enable case sensitive pattern matching", label="Case sensitivity", required=False, disabled=True)
    min_age = forms.IntegerField(help_text="Enter minimum amount of days since last modification", label="Minimum age", required=False)
    max_age = forms.IntegerField(help_text="Enter maximum amount of days since last modification", label="Maximum age", required=False)

