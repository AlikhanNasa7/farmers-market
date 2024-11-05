from django.db import models


class User(models.Model):
    userid = models.CharField(db_column='userID', primary_key=True, max_length=15)  # Field name made lowercase.
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100)
    image = models.CharField(max_length=25)
    password = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=6)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'User'
