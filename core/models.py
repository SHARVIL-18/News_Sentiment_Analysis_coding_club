from django.db import models

class NewsCard(models.Model):
    title = models.TextField(null=True)
    text = models.TextField(null=True)
    link = models.URLField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)

    def __str__nc(self):
        return self.title if self.title else ''