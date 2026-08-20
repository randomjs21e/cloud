from django.shortcuts import render


def landing(request):
    """Public landing page. If the user is logged in, redirect to files."""
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('files:index')
    return render(request, 'landing.html')
