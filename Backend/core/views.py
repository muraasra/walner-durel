from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from django.db.models.functions import TruncDate
from .serializers import *
from .permissions import *

class FactureFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(method='filter_by_date')

    class Meta:
        model = Facture
        fields = ['type', 'status', 'boutique', 'created_at']

    def filter_by_date(self, queryset, name, value):
        return queryset.annotate(date_only=TruncDate('created_at')).filter(date_only=value)

# Boutique : uniquement superadmin peut y toucher
class BoutiqueViewSet(viewsets.ModelViewSet):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'ville']
    ordering_fields = ['nom']
    

# Produit : filtré par boutique + actif, tous les rôles sauf superadmin
class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['boutique', 'actif', 'category']
    search_fields = ['nom', 'description', 'marque', 'modele', 'processeur']
    ordering_fields = ['nom', 'quantite', 'prix', 'created_at']

    def perform_create(self, serializer):
        try:
            instance = serializer.save()
            create_journal_entry(
                user=self.request.user,
                type_operation='creation',
                description=f"Création du produit {instance.nom}",
                boutique=instance.boutique,
                details={
                    'produit_id': instance.id,
                    'nom': instance.nom,
                    'reference': instance.reference,
                    'category': instance.category,
                    'quantite': instance.quantite,
                    'prix': instance.prix
                }
            )
        except Exception as e:
            print(f"Erreur lors de la création du produit: {str(e)}")
            raise

    def perform_update(self, serializer):
        try:
            instance = serializer.save()
            create_journal_entry(
                user=self.request.user,
                type_operation='modification',
                description=f"Modification du produit {instance.nom}",
                boutique=instance.boutique,
                details={
                    'produit_id': instance.id,
                    'nom': instance.nom,
                    'reference': instance.reference,
                    'category': instance.category,
                    'quantite': instance.quantite,
                    'prix': instance.prix
                }
            )
        except Exception as e:
            print(f"Erreur lors de la mise à jour du produit: {str(e)}")
            raise

# PrixProduit : visible uniquement par superadmin
class PrixProduitViewSet(viewsets.ModelViewSet):
    queryset = PrixProduit.objects.all()
    serializer_class = PrixProduitSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['produit']
    ordering_fields = ['date', 'prix_vente_yen']

# Partenaire : lié à la boutique, modifiable par admin ou superadmin
class PartenaireViewSet(viewsets.ModelViewSet):
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['boutique']
    search_fields = ['nom']

# Facture : filtrable par type, boutique, status
class FactureViewSet(viewsets.ModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FactureFilter
    search_fields = ['created_by__username']
    ordering_fields = ['total', 'reste', 'created_at']

    def perform_create(self, serializer):
        instance = serializer.save()
        create_journal_entry(
            user=self.request.user,
            type_operation='creation',
            description=f"Création de la facture {instance.numero}",
            boutique=instance.boutique,
            details={
                'facture_id': instance.id,
                'numero': instance.numero,
                'type': instance.type,
                'total': instance.total,
                'reste': instance.reste
            }
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        create_journal_entry(
            user=self.request.user,
            type_operation='modification',
            description=f"Modification de la facture {instance.numero}",
            boutique=instance.boutique,
            details={
                'facture_id': instance.id,
                'numero': instance.numero,
                'type': instance.type,
                'total': instance.total,
                'reste': instance.reste,
                'status': instance.status
            }
        )

# Commande Client
class CommandeClientViewSet(viewsets.ModelViewSet):
    queryset = CommandeClient.objects.all()
    serializer_class = CommandeClientSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture', 'produit']

    def perform_create(self, serializer):
        instance = serializer.save()
        create_journal_entry(
            user=self.request.user,
            type_operation='vente',
            description=f"Vente de {instance.quantite} {instance.produit.nom}",
            boutique=instance.facture.boutique,
            details={
                'commande_id': instance.id,
                'produit': instance.produit.nom,
                'quantite': instance.quantite,
                'prix_unitaire': instance.prix_unitaire_fcfa,
                'total': instance.total
            }
        )

# Commande Partenaire
class CommandePartenaireViewSet(viewsets.ModelViewSet):
    queryset = CommandePartenaire.objects.all()
    serializer_class = CommandePartenaireSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture', 'partenaire', 'produit']

    def perform_create(self, serializer):
        instance = serializer.save()
        create_journal_entry(
            user=self.request.user,
            type_operation='achat',
            description=f"Achat de {instance.quantite} {instance.produit.nom}",
            boutique=instance.facture.boutique,
            details={
                'commande_id': instance.id,
                'produit': instance.produit.nom,
                'quantite': instance.quantite,
                'prix_unitaire': instance.prix_unitaire_fcfa,
                'total': instance.total
            }
        )

# Versement : tous les versements d'une facture
class VersementViewSet(viewsets.ModelViewSet):
    queryset = Versement.objects.all()
    serializer_class = VersementSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture']

    def perform_create(self, serializer):
        instance = serializer.save()
        create_journal_entry(
            user=self.request.user,
            type_operation='modification',
            description=f"Versement de {instance.montant} XAF pour la facture {instance.facture.numero}",
            boutique=instance.facture.boutique,
            details={
                'versement_id': instance.id,
                'facture': instance.facture.numero,
                'montant': instance.montant,
                'date': instance.date_versement
            }
        )

# Historique des stocks : utile pour audit
class HistoriqueStockViewSet(viewsets.ModelViewSet):
    queryset = HistoriqueStock.objects.all()
    serializer_class = HistoriqueStockSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['produit', 'user']
    search_fields = ['motif']

class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['date_operation', 'type_operation', 'utilisateur']
    ordering = ['-date_operation']

    def get_queryset(self):
        queryset = Journal.objects.all()
        
        # Filtres
        boutique = self.request.query_params.get('boutique', None)
        type_operation = self.request.query_params.get('type_operation', None)
        utilisateur = self.request.query_params.get('utilisateur', None)
        date_debut = self.request.query_params.get('date_debut', None)
        date_fin = self.request.query_params.get('date_fin', None)

        if boutique:
            queryset = queryset.filter(boutique_id=boutique)
        if type_operation:
            queryset = queryset.filter(type_operation=type_operation)
        if utilisateur:
            queryset = queryset.filter(utilisateur_id=utilisateur)
        if date_debut:
            queryset = queryset.filter(date_operation__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_operation__lte=date_fin)

        return queryset.select_related('utilisateur', 'boutique')

    def perform_create(self, serializer):
        try:
            serializer.save(utilisateur=self.request.user)
        except Exception as e:
            print(f"Erreur lors de la création du journal: {str(e)}")
            raise

# Fonction utilitaire pour créer des entrées de journal
def create_journal_entry(user, type_operation, description, boutique=None, details=None):
    try:
        # Créer l'entrée de journal sans essayer d'accéder à la requête
        Journal.objects.create(
            utilisateur=user,
            boutique=boutique,
            type_operation=type_operation,
            description=description,
            details=details,
            ip_address=None  # On ne stocke plus l'IP pour éviter les problèmes
        )
    except Exception as e:
        print(f"Erreur lors de la création du journal: {str(e)}")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'boutique']
    search_fields = ['username', 'email']