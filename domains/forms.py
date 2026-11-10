"""Формы приложения domains."""

from django import forms

from domains.models import Domain

MAX_SCREENSHOT_SIZE = 2 * 1024 * 1024


class DomainScreenshotForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = ["screenshot"]
        labels = {"screenshot": "Изображение"}
        help_texts = {"screenshot": "PNG, JPG или WEBP, не больше 2 МБ."}
        widgets = {
            "screenshot": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/png,image/jpeg,image/webp"}
            ),
        }

    def clean_screenshot(self):
        screenshot = self.cleaned_data["screenshot"]
        # Размер проверяем только у нового файла: у сохранённого его нет в request.FILES.
        is_new_file = screenshot and "screenshot" in self.changed_data
        if is_new_file and screenshot.size > MAX_SCREENSHOT_SIZE:
            raise forms.ValidationError("Файл больше 2 МБ.")
        return screenshot
