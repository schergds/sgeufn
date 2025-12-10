# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AtestadoManualAtestadomanual(models.Model):
    atividade = models.TextField(blank=True, null=True)
    instituicao = models.CharField(max_length=150, blank=True, null=True)
    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)
    carga_horaria = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    codigo_matricula = models.CharField(max_length=20)
    is_active = models.BooleanField()
    slug = models.CharField(max_length=200, blank=True, null=True)
    responsavel = models.CharField(max_length=150)
    pessoa = models.ForeignKey('UsuarioUsuario', models.DO_NOTHING, blank=True, null=True)
    papel = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'atestado_manual_atestadomanual'
        unique_together = (('pessoa', 'codigo_matricula'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AvisoAviso(models.Model):
    titulo = models.CharField(unique=True, max_length=100)
    texto = models.TextField()
    data = models.DateField()
    destinatario = models.CharField(max_length=20)
    enviado = models.BooleanField()
    is_active = models.BooleanField()
    slug = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'aviso_aviso'


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UsuarioUsuario', models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EventoEvento(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    site = models.CharField(max_length=100, blank=True, null=True)
    grupo = models.CharField(max_length=150, blank=True, null=True)
    data_inicio = models.DateField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    data_inscricao = models.DateField(blank=True, null=True)
    carga_horaria = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    local = models.CharField(max_length=300, blank=True, null=True)
    lotacao = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    codigo_frequencia = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField()
    slug = models.CharField(max_length=200, blank=True, null=True)
    coordenador = models.ForeignKey('UsuarioUsuario', models.DO_NOTHING)
    instituicao = models.ForeignKey('InstituicaoInstituicao', models.DO_NOTHING)
    tipo = models.ForeignKey('TipoEventoTipoevento', models.DO_NOTHING)
    frequencia_liberada = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'evento_evento'
        unique_together = (('nome', 'data_inicio'),)


class EventoEventoMinistrantes(models.Model):
    evento = models.ForeignKey(EventoEvento, models.DO_NOTHING)
    usuario = models.ForeignKey('UsuarioUsuario', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'evento_evento_ministrantes'
        unique_together = (('evento', 'usuario'),)


class FrequenciaFrequencia(models.Model):
    data_hora_frequencia = models.DateTimeField()
    slug = models.CharField(max_length=200, blank=True, null=True)
    inscricao = models.OneToOneField('InscricaoInscricao', models.DO_NOTHING)
    codigo_frequencia = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'frequencia_frequencia'
        unique_together = (('inscricao', 'codigo_frequencia'),)


class InscricaoInscricao(models.Model):
    data_hora_inscricao = models.DateTimeField()
    codigo_matricula = models.CharField(max_length=20)
    is_active = models.BooleanField()
    slug = models.CharField(max_length=200, blank=True, null=True)
    evento = models.ForeignKey(EventoEvento, models.DO_NOTHING)
    participante = models.ForeignKey('UsuarioUsuario', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inscricao_inscricao'
        unique_together = (('evento', 'participante'),)


class InstituicaoInstituicao(models.Model):
    nome = models.CharField(unique=True, max_length=100)
    sigla = models.CharField(max_length=10, blank=True, null=True)
    pais = models.CharField(max_length=30)
    estado = models.CharField(max_length=30)
    cidade = models.CharField(max_length=100)
    is_active = models.BooleanField()
    slug = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'instituicao_instituicao'


class RelatorioRelatorio(models.Model):
    titulo = models.CharField(unique=True, max_length=200)
    descricao = models.TextField()
    script_sql = models.TextField(blank=True, null=True)
    resposta = models.TextField(blank=True, null=True)
    data = models.DateField()
    slug = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'relatorio_relatorio'


class TipoEventoTipoevento(models.Model):
    descricao = models.CharField(unique=True, max_length=100)
    is_active = models.BooleanField()
    slug = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_evento_tipoevento'


class UsuarioUsuario(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    nome = models.CharField(max_length=100)
    instituicao = models.CharField(max_length=50)
    email = models.CharField(unique=True, max_length=100)
    celular = models.CharField(max_length=14)
    cpf = models.CharField(max_length=14)
    aceita_termo = models.BooleanField()
    eh_avaliador = models.BooleanField()
    is_active = models.BooleanField()
    slug = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'usuario_usuario'
