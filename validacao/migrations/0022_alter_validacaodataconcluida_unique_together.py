from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("validacao", "0021_delete_movimentacaohistorico"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="validacaodataconcluida",
            unique_together={("empresa", "data_sped", "tipo_validacao")},
        ),
    ]
