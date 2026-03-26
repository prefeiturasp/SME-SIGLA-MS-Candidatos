class SalvarLotesException(Exception):
    def __init__(self, mensagem: str, detalhes: str | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or ''

    def __str__(self) -> str:
        return self.mensagem
