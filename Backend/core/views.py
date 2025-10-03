from decimal import Decimal
from datetime import datetime

import django_filters
from django.db.models import DecimalField, FloatField, ExpressionWrapper, F, Q, Sum, Value, OuterRef, Subquery
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

        ca_global = self._sum_factures(start_date)
        sales_encaissees = self._sum_versements(start_date)
        dettes_en_cours = self._sum_outstanding_debts(start_date)

        timeseries = self._build_timeseries(start_date, include_debts)
        top_technicians = self._top_technicians()

        response = {
            'period': period,
            'sales_encaissees': float(sales_encaissees),
            'dettes_en_cours': float(dettes_en_cours),
            'ca_global': float(ca_global + (dettes_en_cours if include_debts else Decimal('0.00'))),
            'top_techniciens': top_technicians,
            'timeseries': timeseries,
        }
        return Response(response)

    def _sum_factures(self, start_date=None) -> Decimal:
        qs = Facture.objects.all()
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        agg = qs.aggregate(total=Coalesce(
            Sum('total', output_field=DecimalField(max_digits=12, decimal_places=2)),
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ))
        return agg.get('total') or Decimal('0.00')

    def _sum_versements(self, start_date=None) -> Decimal:
        qs = Versement.objects.all()
        if start_date:
            qs = qs.filter(date_versement__gte=start_date)
        agg = qs.aggregate(total=Coalesce(
            Sum('montant', output_field=DecimalField(max_digits=12, decimal_places=2)),
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ))
        return agg.get('total') or Decimal('0.00')

    def _get_period_start(self, period: str, now: datetime) -> datetime:
        if period == 'year':
            return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        if period == 'quarter':
            quarter = (now.month - 1) // 3
            first_month = quarter * 3 + 1
            return now.replace(month=first_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _sum_sales(self, start_date: datetime) -> Decimal:
        agg = (
            Versement.objects
            .filter(date_versement__gte=start_date)
            .aggregate(total=Coalesce(
                Sum('montant', output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            ))
        )
        total = agg.get('total') or 0.0
        return Decimal(str(total))



    def _sum_outstanding_debts(self, start_date=None) -> Decimal:
        payments_total_sq = (
            DebtPayment.objects
            .filter(debt_id=OuterRef('pk'))
            .values('debt_id')
            .annotate(total=Coalesce(
                Sum('amount', output_field=DecimalField(max_digits=12, decimal_places=2)),
                Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ))
            .values('total')[:1]
        )

        qs = Debt.objects.all()
        if start_date:
            qs = qs.filter(created_at__gte=start_date)

        qs = qs.annotate(
            paid_total=Coalesce(Subquery(payments_total_sq), Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=12, decimal_places=2)),
        ).annotate(
            amount_due=ExpressionWrapper(F('amount') - F('paid_total'),
            output_field=DecimalField(max_digits=12, decimal_places=2)),
        ).filter(amount_due__gt=0)

        agg = qs.aggregate(total_due=Coalesce(
            Sum('amount_due', output_field=DecimalField(max_digits=12, decimal_places=2)),
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ))
        return agg.get('total_due') or Decimal('0.00')



    def _build_timeseries(self, start_date: datetime, include_debts: bool):
        sales_by_day = (
            Versement.objects
            .filter(date_versement__gte=start_date)
            .annotate(day=TruncDate('date_versement'))
            .values('day')
            .annotate(total=Coalesce(
                Sum('montant', output_field=FloatField()),
                Value(0.0),
                output_field=FloatField(),
            ))
        )

        debts_by_day = (
            Debt.objects
            .filter(created_at__gte=start_date)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(total=Coalesce(
                Sum('amount', output_field=DecimalField(max_digits=12, decimal_places=2)),
                Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ))
        )

        series_map: dict = {}
        for entry in sales_by_day:
            day = entry['day']
            series_map.setdefault(day, {'sales': Decimal('0.00'), 'debts': Decimal('0.00')})
            series_map[day]['sales'] = Decimal(str(entry['total']))

        for entry in debts_by_day:
            day = entry['day']
            series_map.setdefault(day, {'sales': Decimal('0.00'), 'debts': Decimal('0.00')})
            series_map[day]['debts'] = Decimal(str(entry['total']))

        timeseries = []
        for day in sorted(series_map.keys()):
            sales_value = series_map[day]['sales']
            debts_value = series_map[day]['debts'] if include_debts else Decimal('0.00')
            timeseries.append({
                'date': day.isoformat(),
                'sales': float(sales_value),
                'debts': float(series_map[day]['debts']),
                'ca_global': float(sales_value + debts_value),
            })
        return timeseries



    def _top_technicians(self, start_date=None, limit=5):
        # Sous-requête: total payé pour chaque dette
        payments_total_sq = (
            DebtPayment.objects  # <-- ton modèle de paiement de dettes
            .filter(debt_id=OuterRef('pk'))
            .values('debt_id')
            .annotate(total=Coalesce(
                Sum('amount', output_field=DecimalField(max_digits=12, decimal_places=2)),
                Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ))
            .values('total')[:1]
        )

        # Base: dettes (tu peux filtrer ici selon ton besoin: non payées, non clôturées, etc.)
        base = Debt.objects.all()
        if start_date:
            base = base.filter(created_at__gte=start_date)

        # Montant payé par dette (via Subquery), puis reste à payer par dette
        base = base.annotate(
            paid_total=Coalesce(
                Subquery(payments_total_sq),
                Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        ).annotate(
            amount_due=ExpressionWrapper(
                F('amount') - F('paid_total'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        ).filter(amount_due__gt=0)

        # Agrégation finale par technicien
        qs = (
            base.values('technician_name')
            .annotate(montant=Coalesce(
                Sum('amount_due', output_field=DecimalField(max_digits=12, decimal_places=2)),
                Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ))
            .filter(montant__gt=0)
            .order_by('-montant')[:limit]
        )

        # Réponse au format attendu par le front
        return [
            {'technician_name': row['technician_name'], 'montant': float(row['montant'])}
            for row in qs
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