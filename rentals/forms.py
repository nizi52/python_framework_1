"""Формы приложения rentals: фильтр списка аренд и создание/редактирование аренды."""

from django import forms
from django.utils import timezone

from domains.models import Domain
from rentals.models import Rental
from users.models import User


class RentalFilterForm(forms.Form):
    """Фильтры списка аренд. Имена полей совпадают с GET-параметрами страницы."""

    status = forms.ChoiceField(
        required=False,
        label="Статус",
        choices=[
            ("", "Активные"),
            (Rental.Status.COMPLETED, "Завершённые"),
            (Rental.Status.CANCELLED, "Отменённые"),
            ("all", "Все"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date = forms.DateField(
        required=False,
        label="Действует на дату",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control table-filter"}),
        error_messages={"invalid": "Укажите дату в формате ГГГГ-ММ-ДД."},
    )
    domain = forms.ModelChoiceField(
        queryset=Domain.objects.order_by("name"),
        required=False,
        label="Домен",
        empty_label="Все домены",
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"invalid_choice": "Такого домена нет."},
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by("name"),
        required=False,
        label="Арендатор",
        empty_label="Все арендаторы",
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"invalid_choice": "Такого арендатора нет."},
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировать по",
        choices=[
            ("start", "Началу"),
            ("end", "Окончанию"),
            ("domain", "Домену"),
            ("user", "Арендатору"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class RentalForm(forms.ModelForm):
    """Создание и редактирование аренды. Статус меняется отдельно: отменой или в админке."""

    class Meta:
        model = Rental
        fields = ["domain", "user", "start_date", "end_date"]
        labels = {
            "domain": "Домен",
            "user": "Арендатор",
            "start_date": "Начало аренды",
            "end_date": "Окончание аренды",
        }
        help_texts = {
            "domain": "Домен должен быть в реестре, а регистрация – действовать весь срок аренды.",
            "end_date": "Последний день аренды, не раньше даты начала.",
        }
        widgets = {
            "domain": forms.Select(attrs={"class": "form-select"}),
            "user": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "class": "form-control table-filter"}
            ),
            "end_date": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "class": "form-control table-filter"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["domain"].queryset = Domain.objects.in_registry().order_by("name")
        self.fields["user"].queryset = User.objects.order_by("name")

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]
        # У уже идущей аренды начало в прошлом: проверяем дату, только если её меняют.
        if "start_date" in self.changed_data and start_date < timezone.localdate():
            raise forms.ValidationError("Нельзя начать аренду с прошедшей даты.")
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        domain = cleaned_data.get("domain")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if not (domain and start_date and end_date):
            return cleaned_data

        if end_date < start_date:
            self.add_error("end_date", "Окончание аренды не может быть раньше начала.")
            return cleaned_data
        if domain.registration_end < end_date:
            self.add_error(
                "end_date",
                f"Регистрация домена действует только до {domain.registration_end:%d.%m.%Y}.",
            )
            return cleaned_data

        overlapping = (
            Rental.objects.active()
            .filter(domain=domain, start_date__lte=end_date, end_date__gte=start_date)
            .exclude(pk=self.instance.pk)
        )
        if overlapping.exists():
            raise forms.ValidationError("Домен уже сдан в аренду на часть выбранного периода.")
        return cleaned_data
