"""Re-export do pacote candidatos.serializer para compatibilidade.

Mantido para imports legados do tipo `from candidatos.serializers import X`.
Novos códigos devem importar diretamente de `candidatos.serializer`.
"""

from candidatos.serializer import (
    BuscarPorCpfsSerializer,
    BuscarPorUuidsSerializer,
    CandidatoConcursoCreateSerializer,
    CandidatoSerializer,
    CandidatosLoteCreateSerializer,
    ConcursoCandidatoCpfUuidSerializer,
    ConcursoCandidatoEliminadoSerializer,
    ConcursoCandidatoReclassificadoSerializer,
    ConcursoCandidatoSerializer,
    EliminarSerializer,
    HabilitadosCalculadosParamsSerializer,
    LoteItemSerializer,
    ParametrizacaoSerializer,
    ReclassificarSerializer,
    SalvarLotesSerializer,
)

__all__ = [
    "BuscarPorCpfsSerializer",
    "BuscarPorUuidsSerializer",
    "CandidatoConcursoCreateSerializer",
    "CandidatoSerializer",
    "CandidatosLoteCreateSerializer",
    "ConcursoCandidatoCpfUuidSerializer",
    "ConcursoCandidatoEliminadoSerializer",
    "ConcursoCandidatoReclassificadoSerializer",
    "ConcursoCandidatoSerializer",
    "EliminarSerializer",
    "HabilitadosCalculadosParamsSerializer",
    "LoteItemSerializer",
    "ParametrizacaoSerializer",
    "ReclassificarSerializer",
    "SalvarLotesSerializer",
]
