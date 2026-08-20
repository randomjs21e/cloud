import json
import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from accounts.models import User
from .models import PaymentRecord

# Plan durations (days) for a paid subscription.
PLAN_DURATION_DAYS = {
    'pro': 30,
    'business': 30,
}

# Map Ko-fi tier names / shop item codes to our plan keys.
TIER_TO_PLAN = {
    'pro': 'pro',
    'business': 'business',
    'pro plan': 'pro',
    'business plan': 'business',
}


@login_required
def plan_view(request):
    """Show the current plan and upgrade options via Ko-fi."""
    return render(request, 'payments/plan.html', {
        'ko_fi_username': settings.KO_FI_USERNAME,
    })


def _parse_message(message):
    """Extract (username, plan) from a Ko-fi message like 'username=altexel#pro'."""
    if not message:
        return None, None
    m = re.search(r'username\s*=\s*([A-Za-z0-9_.@+-]+)\s*#\s*([A-Za-z]+)', message)
    if not m:
        return None, None
    return m.group(1), m.group(2).lower()


def _upgrade_user(user, plan):
    """Set the user's plan and expiry. Returns True if changed."""
    if plan not in ('pro', 'business'):
        return False
    now = timezone.now()
    # Extend from now (or from current expiry if still active).
    base = user.plan_expires_at if (user.plan == plan and user.plan_expires_at and user.plan_expires_at > now) else now
    user.plan = plan
    user.plan_expires_at = base + timedelta(days=PLAN_DURATION_DAYS.get(plan, 30))
    if plan == 'pro':
        user.storage_limit_mb = 102400  # 100 GB
    elif plan == 'business':
        user.storage_limit_mb = 1048576  # 1 TB
    user.save(update_fields=['plan', 'plan_expires_at', 'storage_limit_mb'])
    return True


@csrf_exempt
def ko_fi_webhook(request):
    """Ko-fi webhook endpoint. Receives payment notifications and upgrades plans."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    token = request.POST.get('verification_token', '')
    expected = settings.KO_FI_VERIFICATION_TOKEN
    if expected and token != expected:
        return HttpResponse('Invalid token', status=403)

    data_raw = request.POST.get('data', '')
    event_type = request.POST.get('type', '')
    message_id = request.POST.get('message_id', '')

    try:
        data = json.loads(data_raw) if data_raw else {}
    except (ValueError, TypeError):
        data = {}

    message = data.get('message', '') or ''
    username, plan = _parse_message(message)

    # If no plan in the message, try to infer from tier/shop item.
    if not plan:
        tier = (data.get('tier_name') or '').lower()
        plan = TIER_TO_PLAN.get(tier)
        if not plan:
            for item in data.get('shop_items', []) or []:
                code = (item.get('direct_link_code') or '').lower()
                plan = TIER_TO_PLAN.get(code) or TIER_TO_PLAN.get(item.get('name', '').lower())
                if plan:
                    break

    user = None
    if username:
        user = User.objects.filter(username=username).first() or User.objects.filter(email=username).first()

    record = PaymentRecord.objects.create(
        user=user,
        message_id=message_id,
        type=event_type,
        amount=data.get('amount'),
        tier_name=data.get('tier_name', ''),
        plan=plan or '',
        raw_data=data_raw,
    )

    if user and plan:
        _upgrade_user(user, plan)
        record.processed = True
        record.save(update_fields=['processed'])

    return HttpResponse(status=200)
