from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, apellido, password=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico.")
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, apellido=apellido, **extra_fields)
        user.set_password(password)  # 🔒 Hashea la contraseña automáticamente
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('estado', 'activo')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, nombre, apellido, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ESTADOS = [
        ('activo', 'Activo'),
        ('sancionado', 'Sancionado'),
        ('inactivo', 'Inactivo'),
    ]

    usuario_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='inactivo')
    codigo_verificacion = models.CharField(max_length=6, blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'   # 🔑 Autenticación por correo
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def generar_codigo_verificacion(self):
        self.codigo_verificacion = str(random.randint(100000, 999999))
        self.save()

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"
