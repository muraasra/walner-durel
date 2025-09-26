from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'boutiques', BoutiqueViewSet)
router.register(r'produits', ProduitViewSet)
router.register(r'prix-produits', PrixProduitViewSet)
router.register(r'partenaires', PartenaireViewSet)
router.register(r'factures', FactureViewSet)
router.register(r'commandes-client', CommandeClientViewSet)
router.register(r'commandes-partenaire', CommandePartenaireViewSet)
router.register(r'versements', VersementViewSet)
router.register(r'historiques-stock', HistoriqueStockViewSet)
router.register(r'journaux', JournalViewSet)
router.register(r'users', UserViewSet)
router.register(r'debts', DebtViewSet, basename='debt')

urlpatterns = [
    path('metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('', include(router.urls)),
]