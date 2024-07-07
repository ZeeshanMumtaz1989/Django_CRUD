from django.db import models
from django.utils import timezone

# Create your models here.

class DVDAddition(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    specs = models.CharField(max_length=10, choices=[('700 MB', '700 MB'), ('4.4 GB', '4.4 GB'), ('08 GB', '08 GB'), ('25 GB', '25 GB')])
    classification = models.CharField(max_length=10, choices=[('CD', 'CD'), ('DVD', 'DVD'), ('BLUE RAY', 'BLUE RAY')])
    purchase_date = models.DateField()
    purchased_by = models.CharField(max_length=10, choices=[('P&QM', 'P&QM'), ('SI', 'SI'), ('ANYOTHER', 'ANYOTHER')])
    booking_status = models.CharField(max_length=10, choices=[('Reserved', 'Reserved'), ('Available', 'Available')], default='Available')
    shredded = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"  # Customize this according to how you want the DVDAddition object to be displayed

    class Meta:
        """The managed = False attribute tells Django not to manage the table.
        The db_table = 'dvd_addition' attribute specifies the name of the existing table in your XAMPP 
        SQL database that Django should use.
        After making these changes, Django will not create a new table for the DVDAddition model.
        Instead, it will use the existing dvd_addition table in your XAMPP SQL database. """

        managed = False
        db_table = 'dvd_addition'


class IssueReceiveRecord(models.Model):
    id = models.AutoField(primary_key=True)
    dvd = models.ForeignKey('DVDAddition', on_delete=models.CASCADE, related_name='issue_records')
    issued_to = models.CharField(max_length=100)
    issue_date = models.DateField()
    returned_by = models.CharField(max_length=100, blank=True, null=True)
    returned_date = models.DateField(blank=True, null=True)

    STATUS_CHOICES = (
        ('WORKING', 'WORKING'),
        ('OUT OF ORDER', 'OUT OF ORDER'),
        ('ANYOTHER', 'ANYOTHER'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    PURPOSE_CHOICES = (
        ('CIF', 'CIF'),
        ('eOffice', 'eOffice'),
        ('Media', 'Media'),
        ('ANYOTHER', 'ANYOTHER'),
    )
    purpose = models.CharField(max_length=100, choices=PURPOSE_CHOICES)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    RETURN_STATUS_CHOICES = (
        ('RETURNABLE', 'RETURNABLE'),
        ('NON-RETURNABLE', 'NON-RETURNABLE'),
    )
    return_status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES)
    # Added on 30 May 2024
    uploaded_file = models.FileField(blank=True, null=True) 
    # Added on 30 May 2024
    shredded = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    shredding_remarks = models.CharField(max_length=100, blank=True, null=True)
    date_shredded = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'issue_receive_record'



