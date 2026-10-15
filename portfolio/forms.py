
from django import forms
from .models import Comentario


class ComentarioForm(forms.ModelForm):

    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "tabindex": "-1",
            "autocomplete": "off",
            "aria-hidden": "true",
        }),
    )

    class Meta:
        model = Comentario
        fields = ["nome", "avaliacao", "tipo", "texto"]

        widgets = {
            "nome": forms.TextInput(attrs={
                "placeholder": "Seu nome",
                "maxlength": 80,
                "autocomplete": "name",
            }),
            "avaliacao": forms.Select(attrs={
                "class": "campo-avaliacao",
            }),
            "tipo": forms.Select(attrs={
                "class": "campo-tipo-comentario",
            }),
            "texto": forms.Textarea(attrs={
                "placeholder": "Escreva seu comentário...",
                "maxlength": 1000,
                "rows": 5,
            }),
        }

        labels = {
            "nome": "Seu nome",
            "avaliacao": "Sua avaliação",
            "tipo": "Tipo de comentário",
            "texto": "Seu comentário",
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()

        if not nome:
            raise forms.ValidationError("Informe seu nome.")

        return nome

    def clean_texto(self):
        texto = self.cleaned_data["texto"].strip()

        if not texto:
            raise forms.ValidationError("Escreva um comentário.")

        return texto

    def clean_avaliacao(self):
        avaliacao = self.cleaned_data["avaliacao"]

        if avaliacao not in range(1, 6):
            raise forms.ValidationError(
                "Selecione uma avaliação de 1 a 5 estrelas."
            )

        return avaliacao
