from rest_framework import serializers
from .models import *

class BoutiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boutique
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'boutique')

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'

class PrixProduitSerializer(serializers.ModelSerializer):
    prix_vente_fcfa = serializers.FloatField(read_only=True)

    class Meta:
        model = PrixProduit
        fields = '__all__'

class PartenaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partenaire
        fields = '__all__'

class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = '__all__'

class CommandeClientSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()
    produit = ProduitSerializer(read_only=True)

    class Meta:
        model = CommandeClient
        fields = '__all__'

class CommandePartenaireSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()

    class Meta:
        model = CommandePartenaire
        fields = '__all__'

class VersementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Versement
        fields = '__all__'

class HistoriqueStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriqueStock
        fields = '__all__'