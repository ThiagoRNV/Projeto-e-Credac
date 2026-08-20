class NormalizadoresUtils:

    def __init__(self, valor_str) -> None:

        self.valor_str = valor_str
    
    def normalizador_decimal(self):
        '''
        Converte o valor de str (2000,00) pra decimal (2000.00)
        '''

        if not self.valor_str:
            return 0.0
        
        self.valor_str = self.valor_str.replace('.', '').replace(',', '.')

        try:
            return float(self.valor_str)
        except ValueError:
            raise ValueError(f"Valor inválido para conversão: {self.valor_str}")
