# Generated by Django 4.2.22 on 2025-07-09 11:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atestado_manual', '0002_alter_atestadomanual_responsavel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atestadomanual',
            name='atividade',
            field=models.TextField(blank=True, help_text='Coloque aqui uma descrição do atestado_manual para ajudar os autores a submeterem seus trabalhos', max_length=500, null=True, verbose_name='Descrição da atividade'),
        ),
        migrations.AlterField(
            model_name='atestadomanual',
            name='carga_horaria',
            field=models.DecimalField(decimal_places=0, default=1, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)], verbose_name='Carga horária da atividade '),
        ),
        migrations.AlterField(
            model_name='atestadomanual',
            name='data_fim',
            field=models.DateField(help_text='Use dd/mm/aaaa', max_length=10, null=True, verbose_name='Data do fim *'),
        ),
        migrations.AlterField(
            model_name='atestadomanual',
            name='data_inicio',
            field=models.DateField(help_text='Use dd/mm/aaaa', max_length=10, null=True, verbose_name='Data do início *'),
        ),
        migrations.AlterField(
            model_name='atestadomanual',
            name='instituicao',
            field=models.CharField(help_text='* Campo obrigatório', max_length=150, null=True, verbose_name='Departamento ou Setor ou Grupo responsável pela atividade *'),
        ),
        migrations.AlterField(
            model_name='atestadomanual',
            name='nome',
            field=models.CharField(db_index=True, help_text='* Campo obrigatório', max_length=150, verbose_name='Nome do participante *'),
        ),
    ]
