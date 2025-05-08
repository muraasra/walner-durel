from django.db import models
from django.contrib.auth.models import AbstractUser

class Boutique(models.Model):
    ville = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)

    def _str_(self):
        return self.nom

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('superadmin', 'SuperAdmin'),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    boutique = models.ForeignKey(Boutique, on_delete=models.SET_NULL, null=True, blank=True)

class Produit(models.Model):
    choice = (
        ('telephone', 'Telephone'),
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
    category = models.CharField(max_length=20, choices=choice,default='ordinateur')
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantite = models.IntegerField()
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    
    actif = models.BooleanField(default=True)

class PrixProduit(models.Model):
    produit = models.OneToOneField(Produit, on_delete=models.CASCADE)
    prix_achat_yen = models.FloatField()
    prix_vente_yen = models.FloatField()
    taux_fcfa = models.FloatField(default=1)
    date = models.DateTimeField(auto_now_add=True)

    def prix_vente_fcfa(self):
        return self.prix_vente_yen * self.taux_fcfa

class Partenaire(models.Model):
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # revendeur, grossiste...
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)

class Facture(models.Model):
    TYPES = (
        ('client', 'Client'),
        ('partenaire', 'Partenaire'),
    )
    type = models.CharField(max_length=20, choices=TYPES)
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

    @property
    def total(self):
        return self.quantite * self.prix_unitaire_fcfa

class CommandePartenaire(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    partenaire = models.ForeignKey(Partenaire, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire_fcfa = models.FloatField()

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