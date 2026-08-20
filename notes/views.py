from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Note


@login_required
def notes_index(request):
    notes = Note.objects.filter(owner=request.user)
    selected = notes.first()
    return render(request, 'notes/index.html', {'notes': notes, 'selected': selected})


@login_required
def notes_create(request):
    note = Note.objects.create(owner=request.user)
    return redirect('notes:edit', pk=note.id)


@login_required
def notes_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    if request.method == 'POST':
        note.title = request.POST.get('title', '').strip()
        note.body = request.POST.get('body', '')
        note.save()
        messages.success(request, 'Qeyd yadda saxlandı.')
        return redirect('notes:edit', pk=note.id)
    notes = Note.objects.filter(owner=request.user)
    return render(request, 'notes/index.html', {'notes': notes, 'selected': note})


@login_required
def notes_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    note.delete()
    messages.success(request, 'Qeyd silindi.')
    return redirect('notes:index')
