from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# --- Types d'opérations du journal ---
OPERATION_TYPES = (
    ("CREATION", "Création"),
    ("MODIFICATION", "Modification"),
    ("SUPPRESSION", "Suppression"),
    ("CONNEXION", "Connexion"),
    ("DECONNEXION", "Déconnexion"),
)


class DebtQuerySet(models.QuerySet):
    def with_financials(self):
        """Annotations: total payé et restant dû (calculés côté DB)."""
        from django.db.models import DecimalField, ExpressionWrapper, F
        from django.db.models.functions import Coalesce

        annotated = self.annotate(
            calculated_total_paid=Coalesce(
                models.Sum("payments__amount"),
                Decimal("0.00"),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )

        return annotated.annotate(
            calculated_amount_due=ExpressionWrapper(
                F("amount") - F("calculated_total_paid"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )


class Boutique(models.Model):
    ville = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class User(AbstractUser):
    ROLES = (
        ("admin", "Admin"),
        ("user", "User"),
        ("superadmin", "SuperAdmin"),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    boutique = models.ForeignKey(Boutique, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Produit(models.Model):
    choice = (
        ('ordinateur', 'Ordinateur'),
        ('accessoire', 'Accessoire'),
        ('ecran', 'Ecran'),
        ('imprimante', 'Imprimante'),
        ('tablette', 'Tablette'),
        ('casque', 'Casque'),
        ('clavier', 'Clavier'),
        ('souris', 'Souris'),
        ('modem', 'Modem'),
        ('disquedur', 'Disque dur'),
        ('cleusb', 'Cle USB'),
        ('autre', 'Autre'),
    )
    reference = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, choices=choice, default='ordinateur')
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantite = models.IntegerField(default=0)
    prix_achat = models.FloatField()
    prix = models.FloatField()
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    # Champs spécifiques aux ordinateurs
    marque = models.CharField(max_length=100, blank=True, null=True, default=None)
    modele = models.CharField(max_length=100, blank=True, null=True, default=None)
    processeur = models.CharField(max_length=100, blank=True, null=True, default=None)
    ram = models.CharField(max_length=50, blank=True, null=True, default=None)
    stockage = models.CharField(max_length=100, blank=True, null=True, default=None)
    systeme_exploitation = models.CharField(max_length=100, blank=True, null=True, default=None)
    annee = models.IntegerField(blank=True, null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.reference})"

    class Meta:
        ordering = ['-created_at']


class PrixProduit(models.Model):
    produit = models.OneToOneField(Produit, on_delete=models.CASCADE)
    prix_achat_yen = models.FloatField()
    prix_vente_yen = models.FloatField()
    taux_fcfa = models.FloatField(default=1)
    date = models.DateTimeField(auto_now_add=True)

    def prix_vente_fcfa(self):
        return self.prix_vente_yen * self.taux_fcfa

class Partenaire(models.Model):
    choiceStatut = (
        ('encours','En Cours'),
        ('paye','Payé'),
    )
    
    nom = models.CharField(max_length=100)
    prenom =  models.CharField(max_length=100, default='')
    telephone = models.CharField(max_length=20,default=0)
    statut = models.CharField(max_length=20, choices=choiceStatut,default='encours')
    boutique = models.BooleanField(default=True)
    localisation = models.CharField(max_length=100, default='Bafoussam')
    dateadhesion = models.DateTimeField(default=now)

class Facture(models.Model):
    TYPES = (
        ('client', 'Client'),
        ('partenaire', 'Partenaire'),
    )
    type = models.CharField(max_length=20, choices=TYPES)
    nom = models.CharField(max_length=20, default='',blank=True)
    numero = models.CharField(max_length=20, default='',blank=True)
    total = models.FloatField()
    reste = models.FloatField()
    
    status = models.CharField(max_length=20, default='En attente')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CommandeClient(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire_fcfa = models.FloatField()
    prix_initial_fcfa = models.FloatField(null=True, blank=True)  # Prix initial avant modification
    justification_prix = models.TextField(blank=True)  # Justification si le prix a été modifié
    nom = models.CharField(max_length=100,default='')
    prenom = models.CharField(max_length=100,default='')
    telephone = models.CharField(max_length=100,default='')

    @property
    def total(self):
        return self.quantite * self.prix_unitaire_fcfa

class CommandePartenaire(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    partenaire = models.ForeignKey(Partenaire, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire_fcfa = models.FloatField()
    prix_initial_fcfa = models.FloatField(null=True, blank=True)  # Prix initial avant modification
    justification_prix = models.TextField(blank=True)  # Justification si le prix a été modifié

    @property
    def total(self):
        return self.quantite * self.prix_unitaire_fcfa

class Versement(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    montant = models.FloatField()
    date_versement = models.DateTimeField(auto_now_add=True)

class HistoriqueStock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    variation = models.IntegerField()
    motif = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)


class Journal(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE, null=True, blank=True)
    type_operation = models.CharField(max_length=20, choices=OPERATION_TYPES)
    description = models.TextField()
    details = models.JSONField(null=True, blank=True)
    date_operation = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-date_operation"]
        verbose_name = "Journal"
        verbose_name_plural = "Journaux"
        indexes = [
            models.Index(fields=["date_operation"]),
            models.Index(fields=["type_operation"]),
            models.Index(fields=["utilisateur"]),
            models.Index(fields=["boutique"]),
        ]

    def __str__(self):
        return f"{self.utilisateur.username} - {self.type_operation} - {self.date_operation}"

    def save(self, *args, **kwargs):
        # auto_now_add remplit déjà à la création ; garde ce fallback si un objet est créé manuellement avec date vide.
        if not self.date_operation:
            self.date_operation = timezone.now()
        super().save(*args, **kwargs)


class Debt(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PARTIALLY_PAID = "partially_paid"
    STATUS_PAID = "paid"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_PARTIALLY_PAID, "Partially Paid"),
        (STATUS_PAID, "Paid"),
    )

    reference = models.CharField(max_length=50, unique=True)
    machine_description = models.TextField()
    technician_name = models.CharField(max_length=255)
    reason = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    expected_return_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DebtQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["technician_name"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.reference} - {self.technician_name}"

    @property
    def total_paid(self) -> Decimal:
        if hasattr(self, "calculated_total_paid") and self.calculated_total_paid is not None:
            return Decimal(self.calculated_total_paid)
        return self.payments.aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

    @property
    def amount_due(self) -> Decimal:
        if hasattr(self, "calculated_amount_due") and self.calculated_amount_due is not None:
            remaining = Decimal(self.calculated_amount_due)
        else:
            remaining = self.amount - self.total_paid
        return remaining if remaining > Decimal("0.00") else Decimal("0.00")

    def apply_payment(self, amount: Decimal) -> "DebtPayment":
        payment = self.payments.create(amount=amount)
        self.refresh_status()
        return payment

    def refresh_status(self) -> None:
        if self.amount_due <= Decimal("0.00"):
            self.status = self.STATUS_PAID
        elif self.total_paid > Decimal("0.00"):
            self.status = self.STATUS_PARTIALLY_PAID
        else:
            self.status = self.STATUS_PENDING
        self.save(update_fields=["status", "updated_at"])

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_reference() -> str:
        today = timezone.now()
        prefix = today.strftime("DET-%Y-")
        last_reference = (
            Debt.objects.filter(reference__startswith=prefix)
            .order_by("-reference")
            .values_list("reference", flat=True)
            .first()
        )
        next_number = 1
        if last_reference:
            try:
                next_number = int(last_reference.split("-")[-1]) + 1
            except (ValueError, TypeError):
                next_number = 1
        return f"{prefix}{next_number:04d}"


class DebtPayment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Payment {self.amount} for {self.debt.reference}"
