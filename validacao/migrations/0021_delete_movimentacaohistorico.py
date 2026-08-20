from django.db import migrations


class Migration(migrations.Migration):
    """Remove MovimentacaoHistorico do estado do app validacao."""

    dependencies = [
        ("validacao", "0020_movimentacaohistorico_ano_sped"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="MovimentacaoHistorico"),
            ],
            database_operations=[
                migrations.DeleteModel(name="MovimentacaoHistorico"),
            ],
        ),
    ]
