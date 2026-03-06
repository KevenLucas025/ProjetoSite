from django.db import models

class Projeto(models.Model):
    titulo = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    tecnologias = models.CharField(max_length=200, blank=True)  # ex: "Python, Django, SQLite"
    link_github = models.URLField(blank=True)
    link_demo = models.URLField(blank=True)
    imagem = models.ImageField(upload_to="projetos/", blank=True, null=True)
    destaque = models.BooleanField(default=False)
    criado_em = models.DateField(blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    tem_download = models.BooleanField(default=False)

    class Meta:
        ordering = ["ordem", "-destaque", "-id"]

    def __str__(self):
        return self.titulo

    @property
    def tags(self):
        if not self.tecnologias:
            return []
        return [t.strip() for t in self.tecnologias.split(",") if t.strip()]