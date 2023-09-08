from django_filters import rest_framework as filters
from authentication.models import Facilitator


class FacilitatorFilter(filters.FilterSet):
    class Meta:
        model = Facilitator
        fields = ["role"]
