from typing import Optional
from decimal import Decimal, InvalidOperation
from datetime import datetime

# Função para retornar decimal, arredondar e limitar valor para salvar no banco/exibir
def normalizador_decimal(valor, max_digits=20, decimal_places=2):
    """
    Normaliza um valor numérico e garante que possui duas casas decimais, retornando decimal.
    """
    from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

    if valor is None or valor == '' or valor == 'null':
        return None

    try:
        # Tentativa de conversão segura para Decimal
        if isinstance(valor, Decimal):
            valor_decimal = valor
        elif isinstance(valor, (float, int)):
            valor_decimal = Decimal(str(valor))
        else:
            valor_str = str(valor).strip().replace(' ', '').replace(',', '.')
            valor_decimal = Decimal(valor_str)
    except (InvalidOperation, ValueError, AttributeError, TypeError):
        return None

    max_value = Decimal(str((20 ** (max_digits - decimal_places)) - (1 / (20 ** decimal_places))))
    min_value = -max_value

    # Limita aos valores máximo e mínimo permitidos
    if valor_decimal > max_value:
        valor_decimal = max_value
    elif valor_decimal < min_value:
        valor_decimal = min_value

    try:
        # Garante número fixo de casas decimais
        quant = Decimal('1').scaleb(-decimal_places)
        valor_decimal = valor_decimal.quantize(quant, rounding=ROUND_HALF_UP)

        # Reforça os limites depois do arredondamento
        if valor_decimal > max_value:
            valor_decimal = max_value.quantize(quant, rounding=ROUND_HALF_UP)
        elif valor_decimal < min_value:
            valor_decimal = min_value.quantize(quant, rounding=ROUND_HALF_UP)

        return valor_decimal
    except Exception:
        # Fallback: retorna None em falhas inesperadas
        return None

def _norm(value: Optional[str]) -> Optional[str]:
            if value is None:
                return None
            v = str(value).strip()
            return v if v else None



def _to_decimal(value):
            if value in (None, "", "None", "NaN", "nan"):
                return Decimal("0")
            if isinstance(value, Decimal):
                return value
            # Tratar NaN explicitamente
            if isinstance(value, float) and (value != value or str(value).lower() == 'nan'):
                return Decimal("0")
            try:
                value_str = str(value).strip()
                if not value_str or value_str.lower() in ('nan', 'none', 'null'):
                    return Decimal("0")
                if "," in value_str and "." in value_str and value_str.find(",") > value_str.find("."):
                    value_str = value_str.replace(".", "").replace(",", ".")
                else:
                    value_str = value_str.replace(",", ".")
                decimal_value = Decimal(value_str)
                # Verificar se é NaN
                if decimal_value != decimal_value:
                    return Decimal("0")
                return decimal_value
            except (InvalidOperation, ValueError, TypeError):
                return Decimal("0")

def format_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip(), "%d%m%Y").date()
    except (ValueError, TypeError):
        return None