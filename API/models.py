from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

# ユーザーモデル。将来的にはメール認証を追加したい。
# その際はデフォルトでis_activeをfalseにする。
class UserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        """メール認証処理
        if not (extra_fields.get('is_staff') or extra_fields.get('is_superuser')):
            extra_fields.setdefault('is_active', False)
            user_id=str(extra_fields.get('id'))
            auth_url='~/api/v1/user/'+id+'/register/'

            #ダミー
            #text='本登録用URLはこちらです。'
            #send_email(url)

        """


        return user

    def create_user(self, email, password=None, **extra_fields):
        #is_activeをfalseにする。
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(_('username'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    org=models.ForeignKey('Organization',on_delete=models.CASCADE,null=True,blank=True)
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,editable=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    #ここにはいずれ、orgも入れる。
    REQUIRED_FIELDS = ['username']

class Organization(models.Model):
    org_id=models.UUIDField(default=uuid.uuid4,primary_key=True,editable=False)
    org_name=models.CharField(max_length=32)
    org_email=models.EmailField()
    watson_user_id=models.CharField(max_length=36)
    watson_user_pass=models.CharField(max_length=36)

    def __str__(self):
        return self.org_name

#会議情報
#http://d.hatena.ne.jp/metabo346/20090714/1247572086
class ConferenceList(models.Model):
    #会議IDはuuIDにしたいなぁ
    conf_id=models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    conf_name=models.CharField(max_length=32)
    speaker_list=models.ManyToManyField(User,related_name='conferences')
    org_id=models.ForeignKey('Organization',on_delete=models.CASCADE)

    #外部から参照された場合、会議IDを返す
    def __str__(self):
        return str(self.conf_id)

    class Meta:
        ordering=('conf_id',)

#会議ログ
class ConferenceLog(models.Model):
    #発話IDはuuid
    spoken_id=models.UUIDField(default=uuid.uuid4,editable=False,primary_key=True)
    conf_id=models.ForeignKey('ConferenceList',on_delete=models.CASCADE)
    timestamp=models.DateTimeField()
    speaker_name=models.CharField(max_length=32)
    text=models.TextField(blank=True)

    def __str__(self):
        return str(self.spoken_id)

    class Meta:
        ordering=('timestamp',)
