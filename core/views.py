from django.shortcuts import render
from django.views.generic import TemplateView
from accounts.models import FreelancerProfile
from listings.models import Order

class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Query for top freelancers based on average rating
        top_freelancers = FreelancerProfile.objects.order_by('-average_rating')[:10]  # top 10 freelancers
        context['top_freelancers'] = top_freelancers

        # Existing logic for matching orders
        if self.request.user.is_authenticated and self.request.user.user_type == 'freelancer':
            try:
                freelancer_profile = FreelancerProfile.objects.get(user=self.request.user)
                freelancer_skills = freelancer_profile.skills.all()
                matching_orders = Order.objects.filter(skills__in=freelancer_skills, status='open').distinct()[:3]
                context['matching_orders'] = matching_orders
            except FreelancerProfile.DoesNotExist:
                context['matching_orders'] = []

        return context


def custom_404_view(request, exception):
    return render(request, '404.html', {}, status=404)
