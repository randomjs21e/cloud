from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .models import Contact


@login_required
def contacts_index(request):
    q = request.GET.get('q', '').strip()
    contacts = Contact.objects.filter(owner=request.user)
    if q:
        contacts = contacts.filter(name__icontains=q) | contacts.filter(phone__icontains=q) | contacts.filter(email__icontains=q)
    contacts = contacts.distinct()

    # Suggestions: registered users whose phone matches a contact, or users with a phone not yet added.
    my_phones = set(Contact.objects.filter(owner=request.user).exclude(phone='').values_list('phone', flat=True))
    suggestions = User.objects.exclude(pk=request.user.pk).exclude(phone='')
    suggestions = [u for u in suggestions if u.phone not in my_phones]

    return render(request, 'contacts/index.html', {
        'contacts': contacts,
        'q': q,
        'suggestions': suggestions,
    })


@login_required
def contacts_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Ad daxil edin.')
            return redirect('contacts:index')
        Contact.objects.create(
            owner=request.user,
            name=name,
            phone=request.POST.get('phone', '').strip(),
            email=request.POST.get('email', '').strip(),
            company=request.POST.get('company', '').strip(),
            address=request.POST.get('address', '').strip(),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, f'{name} kontaktı əlavə edildi.')
        return redirect('contacts:index')
    return redirect('contacts:index')


@login_required
def contacts_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk, owner=request.user)
    if request.method == 'POST':
        contact.name = request.POST.get('name', '').strip() or contact.name
        contact.phone = request.POST.get('phone', '').strip()
        contact.email = request.POST.get('email', '').strip()
        contact.company = request.POST.get('company', '').strip()
        contact.address = request.POST.get('address', '').strip()
        contact.notes = request.POST.get('notes', '')
        contact.save()
        messages.success(request, 'Kontakt yeniləndi.')
        return redirect('contacts:index')
    return render(request, 'contacts/edit.html', {'contact': contact})


@login_required
def contacts_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk, owner=request.user)
    contact.delete()
    messages.success(request, 'Kontakt silindi.')
    return redirect('contacts:index')


@login_required
def contacts_add_suggestion(request, user_id):
    """Add a suggested registered user as a contact."""
    u = get_object_or_404(User, pk=user_id)
    if u == request.user:
        return redirect('contacts:index')
    Contact.objects.get_or_create(
        owner=request.user,
        name=u.get_full_name() or u.username,
        defaults={'phone': u.phone, 'email': u.email},
    )
    messages.success(request, f'{u.get_full_name() or u.username} kontaktlara əlavə edildi.')
    return redirect('contacts:index')
