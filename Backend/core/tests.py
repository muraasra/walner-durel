from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Boutique, Debt, Facture, User, Versement


class DebtApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester', password='password123', role='admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.boutique = Boutique.objects.create(ville='Douala', nom='Boutique Centrale')
        self.facture = Facture.objects.create(
            type='client',
            nom='Client Test',
            numero='FAC-001',
            total=1000,
            reste=0,
            status='payé',
            created_by=self.user,
            boutique=self.boutique,
        )

    def _create_debt(self, amount=Decimal('500000.00')):
        return Debt.objects.create(
            machine_description='Compresseur 20L',
            technician_name='Tech Alpha',
            reason='Réparation',
            amount=amount,
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )

    def test_partial_and_full_payment(self):
        debt = self._create_debt(Decimal('300000.00'))
        url = reverse('debt-pay', args=[debt.pk])

        response = self.client.patch(url, {'paid_amount': '100000'}, format='json')
        self.assertEqual(response.status_code, 200)
        debt.refresh_from_db()
        self.assertEqual(debt.status, Debt.STATUS_PARTIALLY_PAID)
        self.assertEqual(debt.total_paid, Decimal('100000'))

        response = self.client.patch(url, {'paid_amount': '500000'}, format='json')
        self.assertEqual(response.status_code, 200)
        debt.refresh_from_db()
        self.assertEqual(debt.status, Debt.STATUS_PAID)
        self.assertEqual(debt.amount_due, Decimal('0.00'))

    def test_metrics_endpoint_combines_sales_and_debts(self):
        Versement.objects.create(facture=self.facture, montant=Decimal('100000.00'))
        self._create_debt(Decimal('200000.00'))

        url = reverse('dashboard-metrics')
        response = self.client.get(url, {'period': 'month', 'includeDebts': 'true'})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['period'], 'month')
        self.assertEqual(payload['sales_encaissees'], 100000.0)
        self.assertEqual(payload['dettes_en_cours'], 200000.0)
        self.assertEqual(payload['ca_global'], 300000.0)

