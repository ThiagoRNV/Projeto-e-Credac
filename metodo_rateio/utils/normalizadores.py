class Normalizadores:
    
    @staticmethod
    def normalizador_decimal(valor, max_digits=10, decimal_places=2):
        if valor is None or valor == '' or valor == 'null':
            return None
        try:
            if isinstance(valor, float):
                valor_float = valor
            elif isinstance(valor, int):
                valor_float = float(valor)
            else:
                valor_str = str(valor).strip().replace(',', '.').replace(' ', '')
                valor_float = float(valor_str)
        except (ValueError, AttributeError, TypeError):
            return None
        max_value = (10 ** (max_digits - decimal_places)) - (1 / (10 ** decimal_places))
        min_value = -max_value
        
        if valor_float > max_value:
            valor_float = max_value
        elif valor_float < min_value:
            valor_float = min_value
        
        from decimal import Decimal, ROUND_HALF_UP
        try:
            decimal_value = Decimal(str(valor_float))
            rounded = decimal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if float(rounded) > max_value:
                rounded = Decimal(str(max_value))
            elif float(rounded) < min_value:
                rounded = Decimal(str(min_value))
            return float(rounded)
        except:
            valor_arredondado = round(valor_float, decimal_places)
            if valor_arredondado > max_value:
                return max_value
            elif valor_arredondado < min_value:
                return min_value
            return valor_arredondado