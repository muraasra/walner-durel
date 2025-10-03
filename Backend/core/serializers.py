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
        extra_kwargs = {
            'marque': {'required': False, 'allow_null': True},
            'modele': {'required': False, 'allow_null': True},
            'processeur': {'required': False, 'allow_null': True},
            'ram': {'required': False, 'allow_null': True},
            'stockage': {'required': False, 'allow_null': True},
            'systeme_exploitation': {'required': False, 'allow_null': True},
            'annee': {'required': False, 'allow_null': True},
            'reference': {'required': False},
            'description': {'required': False},
            'prix_achat': {'required': True},
            'prix': {'required': True},
            'quantite': {'required': True},
            'boutique': {'required': True},
            'category': {'required': True},
            'nom': {'required': True}
        }

    def validate(self, data):
        # S'assurer que tous les champs spécifiques aux ordinateurs sont présents
        if data.get('category') == 'ordinateur':
            computer_fields = ['ram', 'stockage', 'processeur', 'annee', 'marque', 'modele', 'systeme_exploitation']
            for field in computer_fields:
                if field not in data:
                    data[field] = None
        return data

    # Validation simplifiée pour le champ annee
    def validate_annee(self, value):
        # Accepter None ou valeur vide
        if value is None or value == '' or value == '':
            return None
        
        # Essayer de convertir en entier si c'est une chaîne
        if isinstance(value, str):
            try:
                value = int(value.strip())
            except (ValueError, TypeError):
                # Si la conversion échoue, retourner None au lieu de lever une erreur
                return None
        
        return value

    def create(self, validated_data):
        # S'assurer que les champs spécifiques aux ordinateurs sont correctement gérés
        if validated_data.get('category') == 'ordinateur':
            for field in ['ram', 'stockage', 'processeur', 'annee', 'marque', 'modele', 'systeme_exploitation']:
                if field not in validated_data or validated_data[field] == '':
                    validated_data[field] = None

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # S'assurer que les champs spécifiques aux ordinateurs sont correctement mis à jour
        if validated_data.get('category', instance.category) == 'ordinateur':
            for field in ['ram', 'stockage', 'processeur', 'annee', 'marque', 'modele', 'systeme_exploitation']:
                if field not in validated_data or validated_data[field] == '':
                    validated_data[field] = None
                    
        return super().update(instance, validated_data)

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
        extra_kwargs = {
            'garantie': {'required': False},
            'contrat_confidentialite': {'required': False}
        }

class CommandeClientSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()
    produit = ProduitSerializer(read_only=True)
    produit_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CommandeClient
        fields = ['id', 'facture', 'nom', 'quantite', 'prenom', 'telephone', 'produit', 'produit_id', 
                 'prix_unitaire_fcfa', 'prix_initial_fcfa', 'justification_prix', 'total']
        extra_kwargs = {
            'produit': {'read_only': True},
            'prix_initial_fcfa': {'required': False},
            'justification_prix': {'required': False}
        }
    
    def validate(self, data):
        # Récupérer le produit pour vérifier le prix d'achat
        produit_id = data.get('produit_id')
        if produit_id:
            try:
                produit = Produit.objects.get(id=produit_id)
                prix_achat = produit.prix_achat or 0
                prix_vente = data.get('prix_unitaire_fcfa', 0)
                marge_minimale = 5000  # 5000 FCFA
                
                if prix_vente < prix_achat + marge_minimale:
                    raise serializers.ValidationError(
                        f"Le prix de vente ({prix_vente} FCFA) doit être au moins {prix_achat + marge_minimale} FCFA "
                        f"(prix d'achat: {prix_achat} FCFA + marge minimale: {marge_minimale} FCFA)"
                    )
            except Produit.DoesNotExist:
                raise serializers.ValidationError("Produit introuvable")
        
        return data
    
    def create(self, validated_data):
        produit_id = validated_data.pop('produit_id')
        produit = Produit.objects.get(id=produit_id)
        # Sauvegarder le prix initial
        validated_data['prix_initial_fcfa'] = validated_data.get('prix_unitaire_fcfa')
        commande = CommandeClient.objects.create(produit=produit, **validated_data)
        return commande

class CommandePartenaireSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()
    produit = ProduitSerializer(read_only=True)
    produit_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CommandePartenaire
        fields = ['id', 'facture', 'partenaire', 'quantite', 'produit', 'produit_id', 
                 'prix_unitaire_fcfa', 'prix_initial_fcfa', 'justification_prix', 'total']
        extra_kwargs = {
            'produit': {'read_only': True},
            'prix_initial_fcfa': {'required': False},
            'justification_prix': {'required': False}
        }

    def validate(self, data):
        # Même validation que pour CommandeClientSerializer
        produit_id = data.get('produit_id')
        if produit_id:
            try:
                produit = Produit.objects.get(id=produit_id)
                prix_achat = produit.prix_achat or 0
                prix_vente = data.get('prix_unitaire_fcfa', 0)
                marge_minimale = 5000  # 5000 FCFA
                
                if prix_vente < prix_achat + marge_minimale:
                    # Ne pas révéler le prix d'achat dans le message d'erreur
                    raise serializers.ValidationError(
                        f"Le prix de vente ({prix_vente} FCFA) est trop bas. "
                        f"Le prix minimum requis est {prix_achat + marge_minimale} FCFA."
                    )
            except Produit.DoesNotExist:
                raise serializers.ValidationError("Produit introuvable")
        
        return data

    def create(self, validated_data):
        produit_id = validated_data.pop('produit_id')
        produit = Produit.objects.get(id=produit_id)
        # Sauvegarder le prix initial
        validated_data['prix_initial_fcfa'] = validated_data.get('prix_unitaire_fcfa')
        commande = CommandePartenaire.objects.create(produit=produit, **validated_data)
        return commande

class VersementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Versement
        fields = '__all__'

class HistoriqueStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriqueStock
        fields = '__all__'

class DebtPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtPayment
        fields = ['id', 'amount', 'created_at']
        read_only_fields = ['id', 'created_at']


class DebtSerializer(serializers.ModelSerializer):
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    amount_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    payments = DebtPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Debt
        fields = [
            'id',
            'reference',
            'machine_description',
            'technician_name',
            'reason',
            'amount',
            'status',
            'expected_return_date',
            'created_at',
            'updated_at',
            'total_paid',
            'amount_due',
            'payments',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'total_paid', 'amount_due', 'payments']

    def validate_expected_return_date(self, value):
        from django.utils import timezone

        if value < timezone.now().date():
            raise serializers.ValidationError("La date de retour prévue doit être aujourd'hui ou ultérieure.")
        return value


class DebtPaymentCreateSerializer(serializers.Serializer):
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_paid_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Le montant payé doit être supérieur à 0.')
        return value


class JournalSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.SerializerMethodField()
    boutique_nom = serializers.SerializerMethodField()

    class Meta:
        model = Journal
        fields = '__all__'
        read_only_fields = ('date_operation',)

    def get_utilisateur_nom(self, obj):
        return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}" if obj.utilisateur else obj.utilisateur.username

    def get_boutique_nom(self, obj):
        return obj.boutique.nom if obj.boutique else None