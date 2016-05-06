from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

import json

from guidedmodules.models import Task, ProjectMembership, Invitation
from questions import Module

def homepage(request):
	if not request.user.is_authenticated():
		# Public homepage.
		return render(request, "index.html")

	elif not Task.has_completed_task(request.user, "account_settings"):
		# First task: Fill out your account settings.
		return HttpResponseRedirect(Task.get_task_for_module(request.user, "account_settings").get_absolute_url())

	else:
		# Ok, show user what they can do.
		projects = [ ]
		for mbr in ProjectMembership.objects.filter(user=request.user).order_by('-project__created'):
			projects.append({
				"project": mbr.project,
				"tasks": Task.objects.filter(editor=request.user, project=mbr.project).order_by('-updated'),
				"others_tasks": Task.objects.filter(project=mbr.project).exclude(editor=request.user).order_by('-updated'),
				"open_invitations": Invitation.objects.filter(from_user=request.user, from_project=mbr.project, accepted_at=None, revoked_at=None).order_by('-created'),

	            "startable_modules": Module.get_anserable_modules(),
				"send_invitation": json.dumps(Invitation.form_context_dict(request.user, mbr.project)),
			})

		# Add a fake project for system modules for this user.
		system_tasks = Task.objects.filter(editor=request.user, project=None)
		if len(system_tasks):
			projects.append({
				"tasks": system_tasks
			})

		return render(request, "home.html", {
			"answerable_modules": Module.get_anserable_modules(),
			"projects": projects,
		})

from django.contrib.auth.backends import ModelBackend
class DirectLoginBackend(ModelBackend):
	# Register in settings.py!
	# Django can't log a user in without their password. Before they create
	# a password, we use this to log them in. Registered in settings.py.
	supports_object_permissions = False
	supports_anonymous_user = False
	def authenticate(self, user_object=None):
		return user_object
