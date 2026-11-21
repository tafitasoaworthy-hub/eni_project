from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from accounts.models import log_action
from accounts.permissions import staff_required
from .models import ChatSession, ChatMessage
from . import services


@login_required
def chat_home(request):
    session = request.user.chat_sessions.first()
    if not session:
        session = ChatSession.objects.create(user=request.user)
    return render(request, "aiassistant/chat.html", {
        "session": session,
        "messages_list": session.messages.all(),
        "sessions": request.user.chat_sessions.all()[:15],
    })


@login_required
def chat_session(request, pk):
    session = get_object_or_404(ChatSession, pk=pk, user=request.user)
    return render(request, "aiassistant/chat.html", {
        "session": session,
        "messages_list": session.messages.all(),
        "sessions": request.user.chat_sessions.all()[:15],
    })


@login_required
@require_POST
def chat_send(request, pk):
    session = get_object_or_404(ChatSession, pk=pk, user=request.user)
    text = (request.POST.get("message") or "").strip()
    if not text:
        return JsonResponse({"error": "Message vide."}, status=400)

    ChatMessage.objects.create(session=session, role="user", content=text)
    if session.messages.count() == 1:
        session.titre = text[:60]
        session.save(update_fields=["titre"])

    history = [{"role": m.role, "content": m.content}
               for m in session.messages.all() if m.role in ("user", "assistant")]
    answer, via = services.ask_chatbot(request.user, history)
    msg = ChatMessage.objects.create(
        session=session, role="assistant", content=answer, via_openai=via)
    log_action(request, "AI", f"Chatbot utilisé (openai={via})")
    return JsonResponse({
        "answer": answer, "via_openai": via,
        "created": msg.created_at.strftime("%H:%M"),
    })


@login_required
@require_POST
def chat_new(request):
    session = ChatSession.objects.create(user=request.user)
    return redirect("aiassistant:chat_session", pk=session.pk)


# --- Assistant administratif (staff only) ---
@staff_required
def admin_assistant(request):
    result = None
    via = False
    task = request.POST.get("task", "courrier")
    instructions = request.POST.get("instructions", "")
    if request.method == "POST" and instructions.strip():
        result, via = services.admin_assist(request.user, task, instructions)
        log_action(request, "AI", f"Assistant administratif ({task}, openai={via})")
    return render(request, "aiassistant/admin_assistant.html", {
        "result": result, "via_openai": via, "task": task, "instructions": instructions,
        "tasks": [
            ("courrier", "Courrier administratif"),
            ("convocation", "Convocation"),
            ("annonce", "Annonce universitaire"),
            ("reformuler", "Reformuler un texte"),
            ("resumer", "Résumer un texte"),
            ("reponse", "Réponse à une demande"),
        ],
    })


# --- Analyse de données (staff only) ---
@staff_required
def data_analysis(request):
    result = None
    via = False
    focus = request.POST.get("focus", "")
    if request.method == "POST":
        result, via = services.analyze_data(request.user, focus)
        log_action(request, "AI", f"Analyse de données IA (openai={via})")
    return render(request, "aiassistant/analysis.html", {
        "result": result, "via_openai": via, "focus": focus,
    })


# --- Recherche intelligente ---
@login_required
def smart_search(request):
    result = None
    via = False
    query = request.GET.get("q", "").strip()
    if query:
        result, via = services.smart_search(request.user, query)
        log_action(request, "AI", f"Recherche intelligente : {query[:60]} (openai={via})")
    return render(request, "aiassistant/search.html", {
        "result": result, "via_openai": via, "query": query,
    })
