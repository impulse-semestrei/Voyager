# Generated by Django 2.2.5 on 2019-10-09 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('procesamiento_reportes', '0010_cotizacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalisisCotizacion',
            fields=[
                ('id_analisis_cotizacion', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.IntegerField()),
                ('fecha', models.DateField()),
                ('analisis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='procesamiento_reportes.Analisis')),
                ('cotizacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='procesamiento_reportes.Cotizacion')),
            ],
        ),
    ]
