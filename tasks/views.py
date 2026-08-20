from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Task, TaskList


@login_required
def tasks_index(request, list_id=None):
    lists = TaskList.objects.filter(owner=request.user)
    current = None
    if list_id:
        current = get_object_or_404(TaskList, pk=list_id, owner=request.user)
    elif lists.exists():
        current = lists.first()
    tasks = current.tasks.all() if current else Task.objects.none()
    return render(request, 'tasks/index.html', {
        'lists': lists,
        'current': current,
        'tasks': tasks,
    })


@login_required
def task_list_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            tl = TaskList.objects.create(owner=request.user, name=name)
            messages.success(request, f'"{name}" siyahısı yaradıldı.')
            return redirect('tasks:list', list_id=tl.id)
        messages.error(request, 'Siyahı adı daxil edin.')
    return redirect('tasks:index')


@login_required
def task_list_delete(request, pk):
    tl = get_object_or_404(TaskList, pk=pk, owner=request.user)
    tl.delete()
    messages.success(request, 'Siyahı silindi.')
    return redirect('tasks:index')


@login_required
def task_create(request, list_id):
    tl = get_object_or_404(TaskList, pk=list_id, owner=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            Task.objects.create(
                task_list=tl,
                title=title,
                notes=request.POST.get('notes', '').strip(),
                priority=request.POST.get('priority', 'med'),
                due_date=request.POST.get('due_date') or None,
            )
            messages.success(request, 'Tapşırıq əlavə edildi.')
        else:
            messages.error(request, 'Tapşırıq mətni daxil edin.')
    return redirect('tasks:list', list_id=tl.id)


@login_required
def task_toggle(request, pk):
    t = get_object_or_404(Task, pk=pk, task_list__owner=request.user)
    t.done = not t.done
    t.save(update_fields=['done'])
    return redirect('tasks:list', list_id=t.task_list_id)


@login_required
def task_delete(request, pk):
    t = get_object_or_404(Task, pk=pk, task_list__owner=request.user)
    list_id = t.task_list_id
    t.delete()
    messages.success(request, 'Tapşırıq silindi.')
    return redirect('tasks:list', list_id=list_id)
