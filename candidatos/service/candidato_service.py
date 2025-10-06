from datetime import datetime
from typing import Tuple, Dict, Any
from candidatos.models import Candidato, ConcursoCandidato


def upsert_candidato_e_concurso(data: Dict[str, Any]) -> Tuple[Candidato, ConcursoCandidato]:
    uf = data.get('uf') or ''
    genero_map = {'1': 'M', '2': 'F'}
    genero = genero_map.get(data.get('sexo', ''), '')
    data_nasc = data.get('data_nascimento')
    if data_nasc:
        try:
            data_nasc = datetime.strptime(str(data_nasc).strip(), '%d/%m/%Y').date()
        except Exception:
            data_nasc = None

    lookup = {}
    if data.get('cpf'):
        lookup['cpf'] = data['cpf']
    elif data.get('email'):
        lookup['email'] = data['email']
    candidato, _created = Candidato.objects.get_or_create(**lookup, defaults={
        'nome': data.get('nome', ''),
        'cpf': data.get('cpf', ''),
        'email': data.get('email', ''),
        'telefone': data.get('telefone', ''),
        'celular': data.get('celular', ''),
        'rg': data.get('rg', ''),
        'registro_funcional': data.get('registro_funcional', ''),
        'vinculo': data.get('vinculo', ''),
        'data_nascimento': data_nasc or datetime(1900,1,1).date(),
        'genero': genero,
        'endereco': data.get('endereco', ''),
        'numero': data.get('numero', ''),
        'complemento': data.get('complemento', ''),
        'bairro': data.get('bairro', ''),
        'cidade': data.get('cidade', ''),
        'estado': uf,
        'cep': data.get('cep', ''),
    })
    if not _created:
        update_fields = {
            'nome': data.get('nome', candidato.nome),
            'telefone': data.get('telefone', candidato.telefone),
            'celular': data.get('celular', candidato.celular),
            'rg': data.get('rg', candidato.rg),
            'registro_funcional': data.get('registro_funcional', candidato.registro_funcional),
            'vinculo': data.get('vinculo', candidato.vinculo),
            'genero': genero or candidato.genero,
            'endereco': data.get('endereco', candidato.endereco),
            'numero': data.get('numero', candidato.numero),
            'complemento': data.get('complemento', candidato.complemento),
            'bairro': data.get('bairro', candidato.bairro),
            'cidade': data.get('cidade', candidato.cidade),
            'estado': uf or candidato.estado,
            'cep': data.get('cep', candidato.cep),
        }
        if data_nasc:
            update_fields['data_nascimento'] = data_nasc
        for k, v in update_fields.items():
            setattr(candidato, k, v)
        candidato.save()

    def _none_if_empty(value):
        if value is None:
            return None
        try:
            return None if str(value).strip() == '' else value
        except Exception:
            return value

    concurso = ConcursoCandidato.objects.create(
        candidato=candidato,
        codigo_inscricao=data.get('codigo_inscricao', ''),
        classificacao=_none_if_empty(data.get('classificacao')),
        pontos=data.get('pontos', ''),
        classificacao_pcd=_none_if_empty(data.get('classificacao_deficiente')),
        opcao_concurso=data.get('opcao_concurso', ''),
        codigo_cargo=data.get('codigo_cargo', ''),
        cota=data.get('cota', ''),
        descricao_cargo=data.get('descricao_cargo', ''),
        df=data.get('df', ''),
        classificacao_nna=_none_if_empty(data.get('classificacao_nna')),
        ano_concurso=data.get('ano_concurso', ''),
        observacao=data.get('observacao', ''),
    )

    return candidato, concurso 