from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """Une conversation avec l'assistant IA."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions",
    )
    titre = models.CharField(max_length=200, default="Nouvelle conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.titre} ({self.user})"


class ChatMessage(models.Model):
    ROLES = [("user", "Utilisateur"), ("assistant", "Assistant"), ("system", "Système")]
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages",
    )
    role = models.CharField(max_length=12, choices=ROLES, default="user")
    content = models.TextField()
    via_openai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
