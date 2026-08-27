from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restricts a view to logged-in staff users (church staff), so the
    upload dashboard isn't reachable by ordinary site visitors or the
    Flutter app's regular users."""

    login_url = reverse_lazy("core:login")

    def test_func(self):
        return self.request.user.is_staff
