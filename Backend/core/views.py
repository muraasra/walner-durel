
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from .permissions import *

# Boutique : uniquement superadmin peut y toucher
class BoutiqueViewSet(viewsets.ModelViewSet):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer
    # permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'ville']
    ordering_fields = ['nom']
    

# Produit : filtré par boutique + actif, tous les rôles sauf superadmin
class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['boutique', 'actif']
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'quantite']

# PrixProduit : visible uniquement par superadmin
class PrixProduitViewSet(viewsets.ModelViewSet):
    queryset = PrixProduit.objects.all()
    serializer_class = PrixProduitSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['produit']
    ordering_fields = ['date', 'prix_vente_yen']

# Partenaire : lié à la boutique, modifiable par admin ou superadmin
class PartenaireViewSet(viewsets.ModelViewSet):
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    # permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['boutique']
    search_fields = ['nom']

# Facture : filtrable par type, boutique, status
class FactureViewSet(viewsets.ModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'status', 'boutique']
    search_fields = ['created_by__username']
    ordering_fields = ['total', 'reste', 'created_at']

# Commande Client
class CommandeClientViewSet(viewsets.ModelViewSet):
    queryset = CommandeClient.objects.all()
    serializer_class = CommandeClientSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture', 'produit']

# Commande Partenaire
class CommandePartenaireViewSet(viewsets.ModelViewSet):
    queryset = CommandePartenaire.objects.all()
    serializer_class = CommandePartenaireSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture', 'partenaire', 'produit']

# Versement : tous les versements d'une facture
class VersementViewSet(viewsets.ModelViewSet):
    queryset = Versement.objects.all()
    serializer_class = VersementSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture']

# Historique des stocks : utile pour audit
class HistoriqueStockViewSet(viewsets.ModelViewSet):
    queryset = HistoriqueStock.objects.all()
    serializer_class = HistoriqueStockSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['produit', 'user']
    search_fields = ['motif']