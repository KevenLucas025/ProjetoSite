from django.db import models
from django.utils import timezone

class Projeto(models.Model):
    titulo = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    tecnologias = models.CharField(max_length=200, blank=True)  # ex: "Python, Django, SQLite"
    link_github = models.URLField(blank=True)
    link_demo = models.URLField(blank=True)
    imagem = models.CharField("Imagem",max_length=255,blank=True)
    destaque = models.BooleanField(default=False)
    criado_em = models.DateField(blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    tem_download = models.BooleanField(default=False)
    video_demo = models.CharField(max_length=255,blank=True,null=True)
    tempo_desenvolvimento = models.CharField(max_length=50,blank=True,null=True)

    class Meta:
        ordering = ["ordem", "-destaque", "-id"]

    def __str__(self):
        return self.titulo

    @property
    def tags(self):
        if not self.tecnologias:
            return []
        return [t.strip() for t in self.tecnologias.split(",") if t.strip()]
    
class Comentario(models.Model):
    class TipoComentario(models.TextChoices):
        ELOGIO = "elogio", "Elogio"
        SUGESTAO = "sugestao", "Sugestão"
        CRITICA = "critica", "Crítica ou reclamação"

    nome = models.CharField(max_length=80)
    texto = models.TextField(max_length=1000)

    avaliacao = models.PositiveSmallIntegerField(
        "Avaliação",
        choices=[
            (1, "1 estrela"),
            (2, "2 estrelas"),
            (3, "3 estrelas"),
            (4, "4 estrelas"),
            (5, "5 estrelas"),
        ],
        default=5,
    )

    tipo = models.CharField(
        "Tipo de comentário",
        max_length=20,
        choices=TipoComentario.choices,
        default=TipoComentario.ELOGIO,
    )

    publico = models.BooleanField(
        "Visível publicamente",
        default=True,
        editable=False,
    )

    editado = models.BooleanField(default=False)
    editado_em = models.DateTimeField(null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.filter(pk=self.pk).first()

            if original:
                campos = ("nome", "texto", "avaliacao", "tipo")

                if any(
                    getattr(original, campo) != getattr(self, campo)
                    for campo in campos
                ):
                    self.editado = True
                    self.editado_em = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"
