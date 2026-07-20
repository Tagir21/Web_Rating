from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.timezone import make_aware, get_current_timezone
from datetime import datetime, timezone

class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

#Тоже придется переделывать

class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=255)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    study_group_id = models.IntegerField()
    is_login = models.IntegerField()

    is_admin = models.IntegerField(default=0, db_column='is_admin')
    last_event = models.IntegerField(blank=True, null=True, db_column='last_event')

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def last_login(self):
        if self.last_event is None:
            return None

        return datetime.fromtimestamp(self.last_event, tz=timezone.utc)

    @last_login.setter
    def last_login(self, value):
        if value is None:
            self.last_event = None
        else:
            if value.tzinfo is None:
                value = make_aware(value)
            self.last_event = int(value.timestamp())


    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return self.login
