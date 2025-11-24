from rest_framework import serializers
from candidatos.models import ConcursoCandidato


class ConcursoCandidatoSerializer(serializers.ModelSerializer):
    candidato = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ConcursoCandidato
        fields = '__all__'
        read_only_fields = ['criado_em', 'atualizado_em', 'esta_ativo']

    def get_candidato(self, obj):
        c = obj.candidato
        if not c:
            return None
        return {
            'id': c.id,
            'nome': c.nome,
            'cpf': c.cpf,
            'email': c.email,
            'telefone': c.telefone,
            'celular': getattr(c, 'celular', ''),
            'rg': getattr(c, 'rg', ''),
            'registro_funcional': getattr(c, 'registro_funcional', ''),
            'vinculo': getattr(c, 'vinculo', ''),
            'data_nascimento': c.data_nascimento,
            'genero': c.genero,
            'endereco': c.endereco,
            'numero': getattr(c, 'numero', ''),
            'complemento': getattr(c, 'complemento', ''),
            'bairro': getattr(c, 'bairro', ''),
            'cidade': c.cidade,
            'estado': c.estado,
            'cep': c.cep,
        }


class BuscarPorUuidsSerializer(serializers.Serializer):
    """
    Serializer para validação do payload da action buscar_por_uuids.
    Valida que uuids é uma lista não vazia de UUIDs válidos.
    """
    uuids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        error_messages={
            'required': 'O campo "uuids" é obrigatório',
            'empty': 'A lista de UUIDs não pode estar vazia',
            'min_length': 'A lista de UUIDs deve conter pelo menos 1 item',
            'invalid': 'O campo "uuids" deve ser uma lista de UUIDs válidos'
        }
    )


