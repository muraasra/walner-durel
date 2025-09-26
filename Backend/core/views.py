from decimal import Decimal
from datetime import datetime

import django_filters
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .permissions import *
from .serializers import *

class FactureFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(method='filter_by_date')

    class Meta:
        model = Facture
        fields = ['type', 'status', 'boutique', 'created_at']

    def filter_by_date(self, queryset, name, value):
        return queryset.annotate(date_only=TruncDate('created_at')).filter(date_only=value)


class DebtFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(method='filter_from_date')
    to_date = django_filters.DateFilter(method='filter_to_date')
    q = django_filters.CharFilter(method='filter_query')

    class Meta:
        model = Debt
        fields = ['status', 'technician_name']

    def filter_from_date(self, queryset, name, value):
        return queryset.filter(created_at__date__gte=value)

    def filter_to_date(self, queryset, name, value):
        return queryset.filter(created_at__date__lte=value)

    def filter_query(self, queryset, name, value):
        return queryset.filter(
            Q(reference__icontains=value)
            | Q(technician_name__icontains=value)
            | Q(machine_description__icontains=value)
            | Q(reason__icontains=value)
        )

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


class DebtViewSet(viewsets.ModelViewSet):
    serializer_class = DebtSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DebtFilter
    search_fields = ['reference', 'technician_name', 'machine_description', 'reason']
    ordering_fields = ['created_at', 'expected_return_date', 'amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return Debt.objects.with_financials().prefetch_related('payments')

    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsAdminOrSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.refresh_status()

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.refresh_status()

    @action(detail=True, methods=['patch'], url_path='pay')
    def pay(self, request, pk=None):
        debt = self.get_object()
        payment_serializer = DebtPaymentCreateSerializer(data=request.data)
        payment_serializer.is_valid(raise_exception=True)
        paid_amount = payment_serializer.validated_data['paid_amount']

        debt.refresh_from_db()
        outstanding = debt.amount_due
        if outstanding <= Decimal('0.00'):
            return Response(
                {'detail': "Cette dette est déjà soldée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if paid_amount > outstanding:
            paid_amount = outstanding

        payment = debt.apply_payment(paid_amount)
        debt = Debt.objects.with_financials().get(pk=debt.pk)
        response_data = self.get_serializer(debt).data
        response_data['last_payment'] = DebtPaymentSerializer(payment).data
        return Response(response_data, status=status.HTTP_200_OK)


class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    PERIOD_CHOICES = {'month', 'quarter', 'year'}

    def get(self, request):
        period = request.query_params.get('period', 'month').lower()
        include_debts = request.query_params.get('includeDebts', 'true').lower() not in {'false', '0', 'no'}

        if period not in self.PERIOD_CHOICES:
            return Response(
                {'detail': "Période invalide. Utilisez 'month', 'quarter' ou 'year'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        start_date = self._get_period_start(period, now)

        sales_total = self._sum_sales(start_date)
        outstanding_debts = self._sum_outstanding_debts(include_debts)

        ca_global = sales_total + (outstanding_debts if include_debts else Decimal('0.00'))
        timeseries = self._build_timeseries(start_date, include_debts)
        top_technicians = self._top_technicians()

        response = {
            'period': period,
            'sales_encaissees': float(sales_total),
            'dettes_en_cours': float(outstanding_debts),
            'ca_global': float(ca_global),
            'top_techniciens': top_techniciens,
            'timeseries': timeseries,
        }
        return Response(response)

    def _get_period_start(self, period: str, now: datetime) -> datetime:
        if period == 'year':
            return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        if period == 'quarter':
            quarter = (now.month - 1) // 3
            first_month = quarter * 3 + 1
            return now.replace(month=first_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _sum_sales(self, start_date: datetime) -> Decimal:
        total = (
            Versement.objects.filter(date_versement__gte=start_date)
            .aggregate(total=Coalesce(Sum('montant'), Decimal('0.00')))
            .get('total', Decimal('0.00'))
        )
        return Decimal(total or Decimal('0.00'))

    def _sum_outstanding_debts(self, include_debts: bool) -> Decimal:
        if not include_debts:
            return Decimal('0.00')

        total = (
            Debt.objects.with_financials()
            .filter(status__in=[Debt.STATUS_PENDING, Debt.STATUS_PARTIALLY_PAID])
            .aggregate(total=Coalesce(Sum('calculated_amount_due'), Decimal('0.00')))
            .get('total', Decimal('0.00'))
        )
        return Decimal(total or Decimal('0.00'))

    def _build_timeseries(self, start_date: datetime, include_debts: bool):
        sales_by_day = (
            Versement.objects.filter(date_versement__gte=start_date)
            .annotate(day=TruncDate('date_versement'))
            .values('day')
            .annotate(total=Coalesce(Sum('montant'), Decimal('0.00')))
        )

        debts_by_day = (
            Debt.objects.filter(created_at__gte=start_date)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(total=Coalesce(Sum('amount'), Decimal('0.00')))
        )

        series_map = {}
        for entry in sales_by_day:
            day = entry['day']
            series_map.setdefault(day, {'sales': Decimal('0.00'), 'debts': Decimal('0.00')})
            series_map[day]['sales'] = Decimal(entry['total'])

        for entry in debts_by_day:
            day = entry['day']
            series_map.setdefault(day, {'sales': Decimal('0.00'), 'debts': Decimal('0.00')})
            series_map[day]['debts'] = Decimal(entry['total'])

        timeseries = []
        for day in sorted(series_map.keys()):
            sales_value = series_map[day]['sales']
            debts_value = series_map[day]['debts'] if include_debts else Decimal('0.00')
            timeseries.append(
                {
                    'date': day.isoformat(),
                    'sales': float(sales_value),
                    'debts': float(series_map[day]['debts']),
                    'ca_global': float(sales_value + debts_value),
                }
            )
        return timeseries

    def _top_technicians(self):
        technicians = (
            Debt.objects.with_financials()
            .filter(status__in=[Debt.STATUS_PENDING, Debt.STATUS_PARTIALLY_PAID])
            .values('technician_name')
            .annotate(montant=Coalesce(Sum('calculated_amount_due'), Decimal('0.00')))
            .order_by('-montant')[:5]
        )
        return [
            {
                'technician_name': tech['technician_name'],
                'montant': float(tech['montant']),
            }
            for tech in technicians
        ]



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