
from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('job', '0022_alter_application_job'),  # Ensure this is the correct dependency
    ]

    operations = [
        migrations.AddField(
            model_name='applicantanswer',
            name='application',
            field=models.ForeignKey(
                to='job.Application',
                on_delete=models.CASCADE,
                related_name='answers',
                null=True,  # Allow null values
            ),
        ),
    ]