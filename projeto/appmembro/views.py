from __future__ import unicode_literals

import locale

from itertools import chain
from operator import attrgetter

from django.contrib.staticfiles import finders

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView

from django.http import HttpResponse
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.lib import colors

from mail_templated import EmailMessage

from utils.decorators import LoginRequiredMixin, MembroRequiredMixin

from atestado_manual.models import AtestadoManual
from aviso.models import Aviso
from evento.models import Evento
from frequencia.models import Frequencia
from inscricao.models import Inscricao
from usuario.models import Usuario

from .forms import MembroCreateForm, InscricaoForm, FrequenciaForm, AutenticaForm
from evento.forms import BuscaEventoForm


class HomeView(LoginRequiredMixin, MembroRequiredMixin, TemplateView):
    template_name = 'appmembro/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avisos'] = Aviso.ativos.filter(destinatario__in=[self.request.user.tipo, 'TODOS'])[0:2]
        return context

class AboutView(LoginRequiredMixin, MembroRequiredMixin, TemplateView):
    template_name = 'appmembro/about.html'
    

class DadosMembroUpdateView(LoginRequiredMixin, MembroRequiredMixin ,UpdateView):
    model = Usuario
    template_name = 'appmembro/dados_membro_form.html'
    form_class = MembroCreateForm  
    
    success_url = 'appmembro_home'

    def get_object(self, queryset=None):
        return self.request.user
     
    def get_success_url(self):
        messages.success(self.request, 'Seus dados foram alterados com sucesso!')
        return reverse(self.success_url)
    

class EventoListView(LoginRequiredMixin, MembroRequiredMixin, ListView):
    model = Evento
    template_name = 'appmembro/evento_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET:
            #quando ja tem dados filtrando
            context['form'] = BuscaEventoForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            context['form'] = BuscaEventoForm()
        return context

    def get_queryset(self):                
        qs = super().get_queryset().filter(is_active=True)
        
        if self.request.GET:
            #quando ja tem dados filtrando
            form = BuscaEventoForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            form = BuscaEventoForm()

        if form.is_valid():            
            pesquisa = form.cleaned_data.get('pesquisa')            
                        
            if pesquisa:
                qs = qs.filter(Q(nome__icontains=pesquisa) | Q(coordenador__nome__icontains=pesquisa) | Q(instituicao__nome__icontains=pesquisa) | Q(instituicao__sigla__icontains=pesquisa) | Q(descricao__icontains=pesquisa))   
            
        return qs


class InscricaoListView(LoginRequiredMixin, MembroRequiredMixin, ListView):
    model = Inscricao
    template_name = 'appmembro/inscricao_list.html'
   
    def get_queryset(self):
        queryset = super(InscricaoListView, self).get_queryset()
        return queryset.filter(participante = self.request.user)


class EventoMinistradoListView(LoginRequiredMixin, MembroRequiredMixin, ListView):
    model = Evento
    template_name = 'appmembro/eventoministrado_list.html'
   
    def get_queryset(self):
        queryset = super(EventoMinistradoListView, self).get_queryset()
        return queryset.filter(ministrantes = self.request.user).distinct()
        
    
class InscricaoCreateView(LoginRequiredMixin, MembroRequiredMixin, CreateView):
    model = Inscricao
    template_name = 'appmembro/inscricao_form.html'
    form_class = InscricaoForm
    success_url = 'appmembro_evento_list'
    
    def get_initial(self):
        initials = super().get_initial()
        initials['usuario'] = Usuario.objects.get(slug=self.request.user.slug)
        initials['evento'] = Evento.objects.get(slug=self.request.GET.get('evento_slug'))
        return initials

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evento'] = Evento.objects.get(slug=self.request.GET.get('evento_slug'))
        return context

    def form_valid(self, form):
        try:
            formulario = form.save(commit=False)

            formulario.participante = self.request.user
            formulario.evento = Evento.objects.get(slug=self.request.GET.get('evento_slug'))
            
            if formulario.evento.quantidade_vagas <= 0:
                messages.error(self.request,"Não há mais vagas para este evento. Inscrição NÃO realizada. Aguarde liberar uma vaga!!!")  
                return super().form_invalid(form)
            
            formulario.save()
            
            try:
                """ enviar e-mail para participante """
                if not formulario.participante.email:
                    raise
                message = EmailMessage('usuario/email/inscricao_participante.html', {'inscricao': formulario, 'site': settings.DOMINIO_URL},
                        settings.EMAIL_HOST_USER, to=[formulario.participante.email])
                message.send()
            except Exception as e:
                # alterar para outro tipo de requisição http
                # messages.warning(self.request, f"SEM NOTIFICAÇÃO POR EMAIL AO PARTICIPANTE!! Erro: {e}")
                messages.warning(self.request, f"SEM NOTIFICAÇÃO POR EMAIL AO PARTICIPANTE!!")

            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, 'Erro ao inscrever-se no evento. Verifique se você já não está inscrito neste evento!')
            return super().form_invalid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Inscrição realizada com sucesso na plataforma!')
        return reverse(self.success_url)
    

class InscricaoDeleteView(LoginRequiredMixin, MembroRequiredMixin, DeleteView):
    model = Inscricao
    template_name = 'appmembro/inscricao_confirm_delete.html'
    success_url = 'appmembro_inscricao_list'
    
    def get_success_url(self):
        messages.success(self.request, 'Inscrição, para o evento, removida com sucesso na plataforma!')
        return reverse(self.success_url)

    def post(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        try:
            self.object = self.get_object()
            self.object.delete()
        except Exception as e:
            messages.error(request, f'Há dependências ligadas à essa Inscrição, permissão negada!')
        return redirect(self.success_url)
    
    
class FrequenciaCreateView(LoginRequiredMixin, MembroRequiredMixin, CreateView):
    model = Frequencia
    template_name = 'appmembro/frequencia_form.html'
    # fields = ['inscricao','codigo_frequencia']
    form_class = FrequenciaForm
    success_url = 'appmembro_inscricao_list'
    
    def get_initial(self):
        initials = super().get_initial()
        initials['inscricao'] = Inscricao.objects.get(slug=self.request.GET.get('inscricao_slug'))
        return initials

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inscricao'] = Inscricao.objects.get(slug=self.request.GET.get('inscricao_slug'))
        return context

    def form_valid(self, form):
        try:
            formulario = form.save(commit=False)
            formulario.inscricao = Inscricao.objects.get(slug=self.request.GET.get('inscricao_slug'))
            
            if formulario.inscricao.evento.codigo_frequencia != formulario.codigo_frequencia:
                messages.error(self.request, 'Código de frequência inválido. Verifique o código informado!')
                return super().form_invalid(form)

            if not formulario.inscricao.evento.pode_registrar_frequencia:
                messages.error(self.request, f"Não é possível registrar frequência para este evento. Passou da data limite {formulario.inscricao.evento.data_hora_limite_registro_frequencia.strftime('%d%m%Y %H:%M')}!")
                return super().form_invalid(form)
            
            formulario.save()

            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, 'Erro ao registrar frequência. Verifique se você já não realizaou a frequência neste evento!')
            return super().form_invalid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Frequência realizada com sucesso na plataforma!')
        return reverse(self.success_url)
    

class MinistrantePdfView(LoginRequiredMixin, MembroRequiredMixin, DetailView):
    pass

class InscricaoPdfView(LoginRequiredMixin, MembroRequiredMixin, DetailView):
    model = Inscricao
  
    caminho_imagem = finders.find('core/img/logoUFN_hor.jpg')
    caminho_imagem_lap = finders.find('core/img/logo_lapinf_hor.png')

    imagem = Image(caminho_imagem, width=200,height=80)
    imagem_lap = Image(caminho_imagem_lap, width=220,height=75)
    story = []

    styles = getSampleStyleSheet()

    # Estilo do título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=40,
        spaceBefore=40,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto justificado
    justify_style = ParagraphStyle(
        'JustifyStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=18
    )
    
    # Estilo para texto centralizado
    center_style = ParagraphStyle(
        'CenterStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    right_style = ParagraphStyle(
        'RightStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_RIGHT,
        fontName='Helvetica'
    )

    @staticmethod
    def parte_participante(inscricao):
        # colocar logo da UFN ao lado do logo do LAP
        # InscricaoPdfView.append(imagem)
        InscricaoPdfView.story.append(InscricaoPdfView.imagem)
        
        # Título do documento
        InscricaoPdfView.story.append(Paragraph("ATESTADO DE PARTICIPAÇÃO", InscricaoPdfView.title_style))
        InscricaoPdfView.story.append(Spacer(1, 20))
        
        # Texto principal do atestado
        evento_titulo = getattr(inscricao.evento, 'titulo', inscricao.evento.nome)  # Usar titulo se existir, senão nome
        
        # Formatação das datas e horários
        data_inicio = inscricao.evento.data_inicio.strftime('%d/%m/%Y') if inscricao.evento.data_inicio else 'N/A'
        hora_inicio = getattr(inscricao.evento, 'hora_inicio', None)
        hora_inicio_str = hora_inicio.strftime('%H:%M') if hora_inicio else 'N/A'

        #Ministrantes for
        ministrantes = inscricao.evento.ministrantes.all()
        if ministrantes.exists():
            if ministrantes.count() > 1:
                ministrantes_lista = [ministrante.nome for ministrante in ministrantes]
                ministrantes_texto = ", ".join(ministrantes_lista[:-1]) + f" e {ministrantes_lista[-1]}"
            else:
                ministrantes_texto = ministrantes.first().nome
        else:
            ministrantes_texto = "N/A"

        texto_atestado = f"""
        Atestamos que <b>{inscricao.participante.nome}</b> participou do evento <b>{evento_titulo}</b>, 
        realizado no dia <b>{data_inicio}</b>, às <b>{hora_inicio_str}</b> horas, 
        no local <b>{inscricao.evento.local}</b>, situado em <b>{inscricao.evento.instituicao}</b>. 
        O referido evento teve carga horária total de <b>{ inscricao.evento.carga_horaria }</b> 
        hora(s) e foi promovido e coordenado pelo(a) <b>{ inscricao.evento.grupo }</b>"""

        if ministrantes.exists():
            texto_atestado +=  f", ministrado por <b>{ministrantes_texto}</b>."
        else:
            texto_atestado += "."

        texto_atestado += f"""<br/>
                             O código de inscrição para validação do atestado é <b>{ inscricao.codigo_matricula }</b>.            
                           """
        
        InscricaoPdfView.story.append(Paragraph(texto_atestado, InscricaoPdfView.justify_style))
        InscricaoPdfView.story.append(Spacer(1, 40))

        data_texto = f"Santa Maria, { inscricao.evento.data_inicio.strftime('%d de %B de %Y')}."
        InscricaoPdfView.story.append(Paragraph(data_texto, InscricaoPdfView.right_style))
        InscricaoPdfView.story.append(Spacer(1, 50))
        
        # Texto final explicativo
        texto_final = """
        <i>O atestado de participação é gerado automaticamente pelo Sistema de Gestão de Eventos (SGEUFN), 
        no momento em que o participante confirma sua presença no evento. Para validar a autenticidade
        deste atestado, utilize o código de inscrição fornecido acima no formulário de validação do SGEUFN.</i>
        """
        
        InscricaoPdfView.story.append(Paragraph(texto_final, InscricaoPdfView.justify_style))
        InscricaoPdfView.story.append(Spacer(1, 40))
        
        # Rodapé com informações do sistema
        InscricaoPdfView.story.append(Spacer(1, 20))
            

    def get(self, request, *args, **kwargs):
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        inscricao = self.get_object()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="atestado_participacao_{inscricao.participante.nome}_{inscricao.evento.nome}.pdf"'
  
        doc = SimpleDocTemplate(response, pagesize=A4, 
                    topMargin=1*inch, bottomMargin=1*inch,
                    leftMargin=1*inch, rightMargin=1*inch)
        
        InscricaoPdfView.parte_participante(inscricao)

        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=InscricaoPdfView.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Helvetica-Oblique',
            textColor=colors.grey
        )
        
        rodape_texto = f"""
        ___________________________________________________<br/>
        Laboratório de Práticas Computação UFN<br/>
        Rua dos Andradas, 1614 – Santa Maria – RS<br/>
        CEP 97010-032 - https://sge.lapinf.ufn.edu.br
        """
        
        InscricaoPdfView.story.append(Paragraph(rodape_texto, footer_style))
        
        # Constrói o PDF
        doc.build(InscricaoPdfView.story)
        
        return response
    
class MinistrantePdfView(LoginRequiredMixin, MembroRequiredMixin, DetailView):
    model = Evento
  
    caminho_imagem = finders.find('core/img/logoUFN_hor.jpg')
    caminho_imagem_lap = finders.find('core/img/logo_lapinf_hor.png')

    imagem = Image(caminho_imagem, width=220,height=100)
    imagem_lap = Image(caminho_imagem_lap, width=220,height=75)
    story = []

    styles = getSampleStyleSheet()

    # Estilo do título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=40,
        spaceBefore=40,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto justificado
    justify_style = ParagraphStyle(
        'JustifyStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=18
    )
    
    # Estilo para texto centralizado
    center_style = ParagraphStyle(
        'CenterStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    right_style = ParagraphStyle(
        'RightStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_RIGHT,
        fontName='Helvetica'
    )

    @staticmethod
    def parte_ministrante(evento):
        # colocar logo da UFN ao lado do logo do LAP
        # story.append(imagem)
        MinistrantePdfView.story.append(MinistrantePdfView.imagem)
        
        # Título do documento
        MinistrantePdfView.story.append(Paragraph("ATESTADO DE PARTICIPAÇÃO", MinistrantePdfView.title_style))
        MinistrantePdfView.story.append(Spacer(1, 20))
        
        # Texto principal do atestado
        evento_titulo = getattr(evento, 'titulo', evento.nome)  # Usar titulo se existir, senão nome
        
        # Formatação das datas e horários
        data_inicio = evento.data_inicio.strftime('%d/%m/%Y') if evento.data_inicio else 'N/A'
        hora_inicio = getattr(evento, 'hora_inicio', None)
        hora_inicio_str = hora_inicio.strftime('%H:%M') if hora_inicio else 'N/A'

        #Ministrantes for
        ministrantes = evento.ministrantes.all()
        if ministrantes.exists():
            if ministrantes.count() > 1:
                ministrantes_lista = [ministrante.nome for ministrante in ministrantes]
                ministrantes_texto = ", ".join(ministrantes_lista[:-1]) + f" e {ministrantes_lista[-1]}"
            else:
                ministrantes_texto = ministrantes.first().nome
        else:
            ministrantes_texto = "N/A"

        texto_atestado = f"""
        Atestamos que <b> {ministrantes_texto}</b> ministrou(ram) no evento <b>{evento_titulo}</b>, 
        realizado no dia <b>{data_inicio}</b>, às <b>{hora_inicio_str}</b> horas, 
        no local <b>{evento.local}</b>, situado em <b>{evento.instituicao}</b>. 
        O referido evento teve carga horária total de <b>{evento.carga_horaria }</b> 
        hora(s) e foi promovido e coordenado pelo(a) <b>{evento.grupo }</b>.
        <br/>
        O código hash para validação do atestado é <b>{evento.slug}</b>.
        """
        
        MinistrantePdfView.story.append(Paragraph(texto_atestado, MinistrantePdfView.justify_style))
        MinistrantePdfView.story.append(Spacer(1, 40))

        data_texto = f"Santa Maria, {evento.data_inicio.strftime('%d de %B de %Y')}."
        MinistrantePdfView.story.append(Paragraph(data_texto, MinistrantePdfView.right_style))
        MinistrantePdfView.story.append(Spacer(1, 50))
        
        # Texto final explicativo
        texto_final = """
        <i>O atestado de participação é gerado automaticamente pelo Sistema de Gestão de Eventos (SGEUFN). 
        Para validar a autenticidade
        deste atestado, utilize o código hash fornecido acima no formulário de validação do SGEUFN.</i>
        """
        
        MinistrantePdfView.story.append(Paragraph(texto_final, MinistrantePdfView.justify_style))
        MinistrantePdfView.story.append(Spacer(1, 40))
        
        # Rodapé com informações do sistema
        MinistrantePdfView.story.append(Spacer(1, 20))
            

    def get(self, request, *args, **kwargs):
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        evento = self.get_object()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="atestado_ministrante_{evento.nome}.pdf"'
  
        doc = SimpleDocTemplate(response, pagesize=A4, 
                    topMargin=1*inch, bottomMargin=1*inch,
                    leftMargin=1*inch, rightMargin=1*inch)
        
        MinistrantePdfView.parte_ministrante(evento)

        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=MinistrantePdfView.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Helvetica-Oblique',
            textColor=colors.grey
        )
        
        rodape_texto = f"""
        ___________________________________________________<br/>
        Laboratório de Práticas Computação UFN<br/>
        Rua dos Andradas, 1614 – Santa Maria – RS<br/>
        CEP 97010-032 - https://sge.lapinf.ufn.edu.br
        """
        
        MinistrantePdfView.story.append(Paragraph(rodape_texto, footer_style))
        
        # Constrói o PDF
        doc.build(MinistrantePdfView.story)
        
        return response


class InscricaoDetailView(LoginRequiredMixin, MembroRequiredMixin, DetailView):
    model = Inscricao
    template_name = 'appmembro/inscricao_detail.html'
    
    
class AutenticaListView(LoginRequiredMixin, MembroRequiredMixin, ListView):
    model = Inscricao
    template_name = 'appmembro/autentica.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET:
            #quando ja tem dados filtrando
            context['form'] = AutenticaForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            context['form'] = AutenticaForm()
        return context

    def get_queryset(self):                
        
        qs = None
        
        if self.request.GET:
            #quando ja tem dados filtrando
            form = AutenticaForm(data=self.request.GET)
        else:
            #quando acessa sem dados filtrando
            form = AutenticaForm()

        if form.is_valid():            
            pesquisa = form.cleaned_data.get('pesquisa')            
                        
            if pesquisa:
                '''
                Aqui, vamos buscar tanto as inscrições quanto os atestados manuais e eventos
                que correspondem ao código de matrícula informado.'''
                inscricoes = Inscricao.objects.filter(codigo_matricula=pesquisa)
                atestados_manuais = AtestadoManual.objects.filter(codigo_matricula=pesquisa)
                eventos = Evento.objects.filter(slug=pesquisa)
                qs = list(chain(inscricoes, atestados_manuais, eventos))
                                   
            
        return qs
    
    
class AtestadoManualListView(LoginRequiredMixin, MembroRequiredMixin, ListView):
    model = AtestadoManual
    template_name = 'appmembro/atestadomanual_list.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     if self.request.GET:
    #         # quando ja tem dados filtrando
    #         context['form'] = BuscaAtestadoManualForm(data=self.request.GET)
    #     else:
    #         # quando acessa sem dados filtrando
    #         context['form'] = BuscaAtestadoManualForm()
    #     return context

    def get_queryset(self):
        qs = super().get_queryset().filter(pessoa=self.request.user)

        # if self.request.GET:
        #     # quando ja tem dados filtrando
        #     form = BuscaAtestadoManualForm(data=self.request.GET)
        # else:
        #     # quando acessa sem dados filtrando
        #     form = BuscaAtestadoManualForm()

        # if form.is_valid():
        #     pesquisa = form.cleaned_data.get('pesquisa')

        #     if pesquisa:
        #         qs = qs.filter(
        #             Q(pessoa__nome__icontains=pesquisa) | Q(atividade__icontains=pesquisa) | Q(responsavel__icontains=pesquisa))

        return qs

