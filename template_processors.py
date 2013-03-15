from solutioner.users.views import graphs_user

def main_template_processor(request):
	try:
		if request.user.is_authenticated:
			graphs_currentuser_info = graphs_user(request, user_username=request.user.username, JSON=False)
			return {'graphs_currentuser_info': graphs_currentuser_info}
	except:
		return {}
