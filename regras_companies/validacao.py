class ValidarRegra:

    def __init__(self, codigo_produto, regra) -> None:
        self.codigo_produto = codigo_produto
        self.regra = regra
        
    def validar_prefixo(self):
        if self.codigo_produto.startswith(self.regra):
                self.codigo_produto = self.codigo_produto[len(self.regra):]
                return self.codigo_produto

    def validar_caractere(self):

        if self.regra in self.codigo_produto:
            self.codigo_produto = self.codigo_produto.split('-', 1)[1]
            return self.codigo_produto

    def validar_sufixo(self):

        if self.codigo_produto.endswith(self.regra):
                self.codigo_produto = self.codigo_produto[:-len(self.regra)]
                return self.codigo_produto