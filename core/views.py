from django.shortcuts import render
from django.views.generic import TemplateView
from accounts.models import FreelancerProfile
from listings.models import Order
class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_freelancers'] = FreelancerProfile.objects.order_by('-average_rating')[:3]

        if self.request.user.is_authenticated and hasattr(self.request.user, 'freelancer_profile'):
            freelancer_skills = self.request.user.freelancer_profile.skills.all()
            matching_orders = Order.objects.filter(skills__in=freelancer_skills).distinct()
            context['matching_orders'] = matching_orders

        return context


def custom_404_view(request, exception):
    return render(request, '404.html', {}, status=404)
