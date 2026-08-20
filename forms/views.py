from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Answer, Question, Response, Survey


@login_required
def forms_index(request):
    surveys = Survey.objects.filter(owner=request.user)
    return render(request, 'forms/index.html', {'surveys': surveys})


@login_required
def forms_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip() or 'Adsız anket'
        description = request.POST.get('description', '')
        requires_account = request.POST.get('requires_account') == 'on'
        survey = Survey.objects.create(
            owner=request.user,
            title=title,
            description=description,
            requires_account=requires_account,
        )
        messages.success(request, 'Anket yaradıldı. İndi suallar əlavə edin.')
        return redirect('forms:edit', pk=survey.id)
    return redirect('forms:index')


@login_required
def forms_edit(request, pk):
    survey = get_object_or_404(Survey, pk=pk, owner=request.user)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'add_question':
            qtype = request.POST.get('qtype', Question.TYPE_TEXT)
            text = request.POST.get('qtext', '').strip()
            options = request.POST.get('qoptions', '')
            required = request.POST.get('qrequired') == 'on'
            if text:
                Question.objects.create(
                    survey=survey,
                    text=text,
                    type=qtype,
                    options=options,
                    required=required,
                    order=survey.questions.count(),
                )
                messages.success(request, 'Sual əlavə edildi.')
        elif action == 'delete_question':
            Question.objects.filter(pk=request.POST.get('qid'), survey=survey).delete()
            messages.success(request, 'Sual silindi.')
        elif action == 'update_settings':
            survey.title = request.POST.get('title', survey.title).strip()
            survey.description = request.POST.get('description', '')
            survey.requires_account = request.POST.get('requires_account') == 'on'
            survey.save()
            messages.success(request, 'Anket yeniləndi.')
        return redirect('forms:edit', pk=survey.id)
    return render(request, 'forms/edit.html', {'survey': survey})


@login_required
def forms_delete(request, pk):
    survey = get_object_or_404(Survey, pk=pk, owner=request.user)
    survey.delete()
    messages.success(request, 'Anket silindi.')
    return redirect('forms:index')


@login_required
def forms_responses(request, pk):
    survey = get_object_or_404(Survey, pk=pk, owner=request.user)
    responses = survey.responses.all()
    return render(request, 'forms/responses.html', {'survey': survey, 'responses': responses})


def forms_fill(request, token):
    survey = get_object_or_404(Survey, token=token)
    if survey.requires_account and not request.user.is_authenticated:
        messages.warning(request, 'Bu anketi doldurmaq üçün hesabınıza daxil olmalısınız.')
        return redirect('accounts:login')
    if request.method == 'POST':
        respondent = request.user if request.user.is_authenticated else None
        response = Response.objects.create(survey=survey, respondent=respondent)
        for q in survey.questions.all():
            key = f'q_{q.id}'
            if q.type == Question.TYPE_MULTI:
                value = ','.join(request.POST.getlist(key))
            else:
                value = request.POST.get(key, '')
            Answer.objects.create(response=response, question=q, value=value)
        messages.success(request, 'Cavabınız qeyd edildi. Təşəkkürlər!')
        return redirect('forms:thanks', token=survey.token)
    return render(request, 'forms/fill.html', {'survey': survey})


def forms_thanks(request, token):
    survey = get_object_or_404(Survey, token=token)
    return render(request, 'forms/thanks.html', {'survey': survey})
