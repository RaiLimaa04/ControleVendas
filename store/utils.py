from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

class SuccessMessageMixin:
    """Mixin para adicionar mensagens de sucesso"""
    success_message = None

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response

class DeleteObjectMixin:
    """Mixin para lidar com exclusão de objetos"""
    success_message = None
    error_message = None
    success_url = None

    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, self.success_message)
        except Exception as e:
            messages.error(request, f'{self.error_message}: {str(e)}')
        return redirect(self.success_url)

class CreateObjectMixin:
    """Mixin para criar objetos com mensagens padrão"""
    success_message = None
    success_url = None

    def form_valid(self, form):
        self.object = form.save()
        if self.success_message:
            messages.success(self.request, self.success_message)
        return redirect(self.success_url)

class UpdateObjectMixin:
    """Mixin para atualizar objetos com mensagens padrão"""
    success_message = None
    redirect_url = None

    def update_object(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, self.success_message)
            return redirect(self.redirect_url)
        return self.form_invalid(form) 