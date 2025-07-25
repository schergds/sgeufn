# Generated by Django 4.2.22 on 2025-06-27 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='tipo',
            field=models.CharField(choices=[('ADMINISTRADOR', 'Administrador'), ('COORDENADOR', 'Coordenador de Evento'), ('PARTICIPANTE', 'Participante'), ('MINISTRANTE', 'Ministrante')], default='PARTICIPANTE', help_text='* Campos obrigatórios', max_length=15, verbose_name='Tipo do usuário *'),
        ),
    ]
