from datetime import timedelta
from decimal import Decimal
from random import choice, randint

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Debt


class Command(BaseCommand):
    help = "Crée quelques dettes d'exemple pour le développement."

    def handle(self, *args, **options):
        if Debt.objects.exists():
            self.stdout.write(self.style.NOTICE("Des dettes existent déjà, aucune donnée de démonstration ajoutée."))
            return

        technicians = [
            "Tech Alpha",
            "Tech Beta",
            "Tech Gamma",
            "Tech Delta",
        ]
        reasons = ["Réparation", "Diagnostic", "Pièces"]
        machines = [
            "Compresseur 20L, série A-12",
            "Groupe électrogène 5KVA",
            "Ordinateur portable - écran fissuré",
            "Perceuse industrielle - remplacement charbons",
        ]

        today = timezone.now().date()

        for index in range(1, 6):
            Debt.objects.create(
                reference=f"DET-{today.year}-{index:04d}",
                machine_description=choice(machines),
                technician_name=choice(technicians),
                reason=choice(reasons),
                amount=Decimal(randint(200_000, 800_000)),
                expected_return_date=today + timedelta(days=randint(3, 21)),
            )

        self.stdout.write(self.style.SUCCESS("Dettes de démonstration créées avec succès."))