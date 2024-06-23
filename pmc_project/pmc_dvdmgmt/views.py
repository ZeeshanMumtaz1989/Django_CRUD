# Importing required items
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.conf import settings
from .models import DVDAddition, IssueReceiveRecord
from django.contrib import messages
from datetime import datetime
from django.db import transaction
from django.urls import reverse
from django.http import JsonResponse
import json
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    dvd_count = DVDAddition.objects.all()
    dvd_count = dvd_count.count()
    available_dvds = DVDAddition.objects.filter(booking_status='Available').count()
    reserve_dvds = DVDAddition.objects.filter(booking_status='Reserved').count()
    ooo_dvds = IssueReceiveRecord.objects.filter(status='OUT OF ORDER').count()

    context = {
        'BASE_URL': settings.BASE_URL, # As BASE_URL defined in settings.py
        'dvd_count': dvd_count,  
        'available_dvds': available_dvds,  
        'reserve_dvds': reserve_dvds,
        'ooo_dvds': ooo_dvds,
    }
    return render(request, 'index.html', context)




@login_required
def inventory(request):   
    dvds = DVDAddition.objects.all()
    issue_counts = {}

    for dvd in dvds:
        dvd_id = dvd.id
        issue_count = IssueReceiveRecord.objects.filter(dvd=dvd_id).count()
        issue_counts[dvd_id] = issue_count
    context = {'dvds': dvds, 'issue_counts': issue_counts,}
    return render(request, 'inventory.html', context)




@login_required
def dvdAddition(request):
    if request.method == 'POST':
        # Access form data
        cd_dvd_string = request.POST.get('cd_dvd_string')
        classification = request.POST.get('classification')
        specs = request.POST.get('specs')
        purchased_by = request.POST.get('purchased_by')
        purchased_date = request.POST.get('purchased_date')
        booking_status = request.POST.get('booking_status')

        if DVDAddition.objects.filter(name=cd_dvd_string).exists():
            messages.error(request, 'Already Exist in DB!')
            return redirect('/inventory/')
        else:
            # Save data to the database
            DVDAddition.objects.create(
                name=cd_dvd_string,
                classification=classification,
                specs=specs,
                purchased_by=purchased_by,
                purchase_date=purchased_date,
                booking_status=booking_status
            )
            messages.success(request, 'DVD entry added successfully!')
            return redirect('/inventory/')
    
    return render(request, 'dvd_addition.html')




@login_required
def dvdDeletionPage(request, dvd_id):
    dvd = DVDAddition.objects.get(pk=dvd_id)
    return render(request, 'inventory_delete.html', {'dvd': dvd})


@login_required
def dvdDeletion(request, dvd_id):
    # Retrieve the DVD object
    dvd = DVDAddition.objects.get(pk=dvd_id)
    if dvd.booking_status == 'Available':
            dvd.delete()  
    else:
        pass  
    return redirect('inventory')


@login_required
def issuereceiverecord(request):
    dvds = IssueReceiveRecord.objects.all()
    context = {'dvds': dvds}
    return render(request, 'issue_receive_record.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib import messages
from datetime import datetime

@login_required
def dvdIssuance(request):
    available_dvds = DVDAddition.objects.filter(booking_status='Available')

    if request.method == 'POST':
        cd_dvd_id = request.POST.get('cd_dvd_id') 
        issued_to = request.POST.get('issued_to')
        issue_date_str = request.POST.get('issue_date')
        issue_date = issue_date_str      
        remarks = request.POST.get('remarks', '')  # Default to empty string if not provided
        returned_by = request.POST.get('returnedBy', '')  # Default to empty string if not provided
        return_date_str = request.POST.get('return_date', None)  # Default to None if not provided

        # Check if return_date_str is not empty
        if return_date_str:
            # return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
            return_date = return_date_str

        else:
            return_date = None

        status = request.POST.get('status', '').upper()  # Convert to uppercase
        purpose = request.POST.get('purpose')
        return_status = request.POST.get('return_status')       
        dvd = get_object_or_404(DVDAddition, pk=cd_dvd_id)
        # Added on 30 May 2024
        file_upload = request.FILES.get('file_upload')  # Handle file upload
        if file_upload:
            print(f"Uploaded file name: {file_upload.name}")
        # print(file_upload)  

        try:
            with transaction.atomic():
                # Create IssueReceiveRecord entry
                dvd_entry = IssueReceiveRecord.objects.create(
                    dvd=dvd,
                    issued_to=issued_to,
                    issue_date=issue_date,
                    remarks=remarks,
                    returned_by=returned_by,
                    returned_date=return_date,
                    status=status,
                    purpose=purpose,
                    return_status=return_status,
                    uploaded_file=file_upload,  # Save file path to database
                    # Ensure default values for date_shredded and shredding_remarks are handled
                    shredding_remarks=None,
                    date_shredded=None,
                )

                # Update booking_status to 'Reserved' for the corresponding DVD_ID in DVDAddition
                if return_date_str and returned_by != '':
                    dvd_addition = DVDAddition.objects.get(pk=cd_dvd_id)
                    dvd_addition.booking_status = 'Available'
                    dvd_addition.save()
                else:                
                    dvd_addition = DVDAddition.objects.get(pk=cd_dvd_id)
                    dvd_addition.booking_status = 'Reserved'
                    dvd_addition.save()

                # messages.success(request, 'DVD entry added successfully!')
                messages.success(request, f'{dvd_addition} issued to {issued_to} successfully')

                return redirect(reverse('inventory'))  # Assuming 'inventory' is the name of your inventory URL
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            # print(str(e))
            return redirect(reverse('dvdIssuance'))

    return render(request, 'dvd_issuance.html', {'available_dvds': available_dvds})


@login_required
def inventoryView(request, dvd_id):
    dvd = DVDAddition.objects.get(pk=dvd_id)
    return render(request, 'inventory_view.html', {'dvd': dvd})


@login_required
def issuereceiverecordlist(request, dvd_id):
    # Get the DVD object
    dvd = get_object_or_404(DVDAddition, pk=dvd_id)
    
    # Query all IssueReceiveRecord instances related to this DVD
    issuerecords = IssueReceiveRecord.objects.filter(dvd=dvd)
    
    # Pass the queryset to the template
    context = {'dvd': dvd, 'issuerecords': issuerecords}
    return render(request, 'issuereceiverecordlist.html', context)

@login_required
def editinventoryitem(request, dvd_id):
    dvd = DVDAddition.objects.get(pk=dvd_id)

    if request.method == 'POST':
        cd_dvd_string = request.POST.get('cd_dvd_string')
        purchased_date = request.POST.get('purchased_date')
        classification = request.POST.get('classification')
        specs = request.POST.get('specs')
        purchased_by = request.POST.get('purchased_by')
        booking_status = request.POST.get('booking_status')
    

        # Update the DVDAddition object with the new data
        dvd.name = cd_dvd_string
        dvd.purchase_date = purchased_date
        dvd.classification = classification
        dvd.specs = specs
        dvd.purchased_by = purchased_by
        dvd.booking_status = booking_status

        # Save the changes to the database
        dvd.save()

        # Show success message
        messages.success(request, 'DVD entry updated successfully!')

        return redirect('/inventory/')


    context = {
        'dvd': dvd,
        'is_cd': dvd.classification == "CD",
        'is_dvd': dvd.classification == "DVD",
        'is_blue_ray': dvd.classification == "Blue Ray",
        'is_700mb': dvd.specs == "700 MB",
        'is_44gb': dvd.specs == "4.4 GB",
        'is_08gb': dvd.specs == "08 GB",
        'is_25gb': dvd.specs == "25 GB",
        'is_pqm': dvd.purchased_by == "P&QM",
        'is_si': dvd.purchased_by == "SI",
        'is_anyother': dvd.purchased_by == "AnyOther",
        'is_reserved': dvd.booking_status == "Reserved",
        'is_available': dvd.booking_status == "Available",
    }
    return render(request, 'editinventoryitem.html', context)


# New try as per requirement

@login_required
def editdvdissuance(request, dvd_id):
    dvd = get_object_or_404(IssueReceiveRecord, pk=dvd_id)

    if request.method == 'POST':
        cd_dvd_id = request.POST.get('cd_dvd_id')  
        issued_to = request.POST.get('issued_to')
        issue_date_str = request.POST.get('issue_date')
        # issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d %H:%M:%S')  # Parse the date
        issue_date = issue_date_str

        remarks = request.POST.get('remarks', '')
        returned_by = request.POST.get('returned_by', '')
        return_date_str = request.POST.get('return_date', None)

        if return_date_str:
            # return_date = datetime.strptime(return_date_str, '%Y-%m-%d %H:%M:%S')
            return_date = return_date_str

        else:
            return_date = None

        status = request.POST.get('status', '').upper()
        purpose = request.POST.get('purpose')
        return_status = request.POST.get('return_status')
                            # Added on 30 May 2024
        file_upload = request.FILES.get('file_upload')  # Handle file upload
        if file_upload:
            print(f"Uploaded file name: {file_upload.name}")
        print(file_upload) 

        try:
            with transaction.atomic():
                # Update the DVD issuance record
                dvd.issued_to = issued_to
                dvd.issue_date = issue_date
                dvd.remarks = remarks
                dvd.returned_by = returned_by
                dvd.returned_date = return_date
                dvd.status = status
                dvd.purpose = purpose
                dvd.return_status = return_status
                dvd.uploaded_file = file_upload
                dvd.save()

                # Update the booking status of the associated DVD in DVDAddition
                if status == 'OUT OF ORDER':
                    # print('inside IF Block')
                    dvd_addition = DVDAddition.objects.get(pk=dvd.dvd_id)
                    dvd_addition.booking_status = 'Reserved'
                    dvd_addition.save()

     
                elif return_date_str and returned_by and purpose != 'CIF':
                    print('inside ELIF Block')
                    dvd_addition = DVDAddition.objects.get(pk=dvd.dvd_id)
                    dvd_addition.booking_status = 'Available'
                    dvd_addition.save()
               

                else:
                    # print('inside ELSE Block')
                    dvd_addition = DVDAddition.objects.get(pk=dvd.dvd_id)
                    dvd_addition.booking_status = 'Reserved'
                    dvd_addition.save() 

                messages.success(request, 'DVD issuance record updated successfully!')
                return redirect(reverse('issuereceiverecord'))  # Redirect to inventory page after successful update
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return redirect(reverse('editdvdissuance', args=[dvd_id]))  # Redirect back to edit page on error

    context = {
        'dvd': dvd,
        'is_working': dvd.status == "WORKING",
        'is_ooo': dvd.status == "OUT OF ORDER",
        'is_anyotherstatus': dvd.status == "ANYOTHER",
        'is_cif': dvd.purpose == "CIF",
        'is_upload': dvd.purpose == "eOffice",
        'is_media': dvd.purpose == "Media",
        'is_anyother': dvd.purpose == "Any Other",
        'is_returnable': dvd.return_status == "RETURNABLE",
        'is_nonreturnable': dvd.return_status == "NON-RETURNABLE",
    }

    return render(request, 'editdvdissuance.html', context)


@login_required
def bulkdvdaddition(request):
    if request.method == 'POST':
        # Get form data
        cd_dvd_string_from = request.POST.get('cd_dvd_string_from')
        cd_dvd_string_to = request.POST.get('cd_dvd_string_to')
        
        # Parse CD/DVD string range
        prefix_parts = cd_dvd_string_from.split('/')[:-1]  # Extract all parts except the last one
        start_index = int(cd_dvd_string_from.split('/')[-1])
        end_index = int(cd_dvd_string_to.split('/')[-1])

        # Generate CD/DVD strings for the range with the same prefix
        cd_dvd_strings = [f"{'/'.join(prefix_parts)}/{str(i).zfill(3)}" for i in range(start_index, end_index + 1)]

        # Other form data
        purchased_date = request.POST.get('purchased_date')
        classification = request.POST.get('classification')
        specs = request.POST.get('specs')
        purchased_by = request.POST.get('purchased_by')
        booking_status = request.POST.get('booking_status')
        
        # Create DVD entries for each CD/DVD string
        for cd_dvd_string in cd_dvd_strings:
            dvd_entry = DVDAddition.objects.create(
                name=cd_dvd_string,
                classification=classification,
                specs=specs,
                purchased_by=purchased_by,
                purchase_date=purchased_date,
                booking_status=booking_status
            )
        
        # Show success message
        messages.success(request, f'{len(cd_dvd_strings)} DVD entries added successfully!')
        
        # Redirect to the inventory page
        return redirect(reverse('inventory'))

    return render(request, 'bulkdvdaddition.html')



@login_required
def issuereceiverecordquery(request):
    if request.method == 'POST':
        # print(request.body)
        try:
            # Parse JSON data received from frontend
            query_data = json.loads(request.body)
            rules = query_data.get('rules', [])

            # Ensure that rules is a list
            if not isinstance(rules, list):
                raise ValueError('Invalid rules format')

            # Define model and query objects for sqlalchemy-querybuilder
            models = {
                'IssueReceiveRecord': IssueReceiveRecord,
            }
            query = IssueReceiveRecord.objects.all()  # Initial queryset

            # Construct SQLAlchemy filters based on parsed rules
            myfilter = Filter(models, query)
            print("myfilter", myfilter)
            
            # Convert date string to datetime objects
            for rule in rules:
                if rule['type'] == 'date':
                    rule['value'] = [datetime.strptime(date_str, '%m/%d/%Y') for date_str in rule['value']]
            
            queryset = myfilter.querybuilder(rules)
            # print("queryset", queryset)

            # Convert queryset to JSON for response
            record_data = list(queryset.values())  # Convert queryset to list of dictionaries

            # Return JSON response
            return JsonResponse({'data': record_data})
        except Exception as e:
            # Handle any exceptions and return an error response
            return JsonResponse({'error': str(e)}, status=500)

    # Render the template if request method is not POST
    return render(request, 'issuereceiverecordquery.html')






#####################################################

@login_required
def issuereceiverecordadvsearch(request):
    # Get distinct DVD IDs from IssueReceiveRecord
    distinct_dvds = IssueReceiveRecord.objects.values('dvd').annotate(count=Count('dvd'))

    # Extract DVD IDs from distinct_dvds
    dvd_ids = [entry['dvd'] for entry in distinct_dvds]

    # Retrieve DVDAddition instances corresponding to the DVD IDs
    available_dvds = DVDAddition.objects.filter(pk__in=dvd_ids)

    if request.method == 'POST':
        try:
            print("Complete incoming request:", request.body)
            # Extract form data
            dvd_id = request.POST.get('cd_dvd_id')
            issued_to = request.POST.get('issued_to')
            issue_date_1 = request.POST.get('issue_date_1')
            issue_date_2 = request.POST.get('issue_date_2')
            returned_by = request.POST.get('returned_by')
            return_date_1 = request.POST.get('return_date_1')
            return_date_2 = request.POST.get('return_date_2')
            status = request.POST.get('status')
            purpose = request.POST.get('purpose')
            return_status = request.POST.get('return_status')
            shredd_status = request.POST.get('shredded')

            # Define initial queryset
            queryset = IssueReceiveRecord.objects.all()

            if dvd_id:
                queryset = queryset.filter(dvd=dvd_id)

            if issued_to:
                queryset = queryset.filter(issued_to__icontains=issued_to)
            if issue_date_1:
                queryset = queryset.filter(issue_date__gte=issue_date_1)
            if issue_date_2:
                queryset = queryset.filter(issue_date__lte=issue_date_2)
            if returned_by:
                queryset = queryset.filter(returned_by__icontains=returned_by)
            if return_date_1:
                queryset = queryset.filter(returned_date__gte=return_date_1)
            if return_date_2:
                queryset = queryset.filter(returned_date__lte=return_date_2)
            if status:
                queryset = queryset.filter(status=status)
            if purpose:
                queryset = queryset.filter(purpose=purpose)
            if return_status:
                queryset = queryset.filter(return_status=return_status)
            
            if shredd_status:
                queryset = queryset.filter(shredded=shredd_status)



            # Convert queryset to JSON for response
            record_data = list(queryset.values())  # Convert queryset to list of dictionaries
            # print('COMPLETE RECORD DATA:>>>>>>>>>>>>', record_data)

            # Replace dvd_id from just numeric with complete dvd_string
            for entry in record_data:
                dvd_id = entry['dvd_id']
                dvd_string = DVDAddition.objects.get(pk=dvd_id).name
                entry['dvd_id'] = dvd_string

            # Defining the format for the datetime string
            # datetime_format = "%d-%m-%Y %H:%M:%S"
            datetime_format = "%d-%m-%Y"


            # Loop through each dictionary in record_data
            for entry in record_data:
                # Check if 'issue_date' key exists in the dictionary
                if 'issue_date' in entry:
                    # Get the datetime object
                    issue_date = entry['issue_date']
                    # Format the datetime object
                    formatted_issue_date = issue_date.strftime(datetime_format)
                    # Update the dictionary with the formatted datetime string
                    entry['issue_date'] = formatted_issue_date


          # Loop through each dictionary in record_data
            for record in record_data:
                # Check if 'returned_date' key exists in the dictionary and if it's not None
                if 'returned_date' in record and record['returned_date'] is not None:
                    returned_date = record['returned_date']
                    # Format the datetime object
                    formatted_return_date = returned_date.strftime(datetime_format)
                    # Update the dictionary with the formatted datetime string
                    record['returned_date'] = formatted_return_date

            # print(record_data)

            # Return JSON response
            return JsonResponse({'data': record_data})
        except Exception as e:
            # Handle any exceptions and return an error response
            return JsonResponse({'error': str(e)}, status=500)

    # Render the template if request method is not POST
    return render(request, 'issuereceiverecordadvsearch.html', {'available_dvds': available_dvds})





def outofordershredding(request):
    # dvds = IssueReceiveRecord.objects.filter(status='OUT OF ORDER')

    dvds = IssueReceiveRecord.objects.filter(status='OUT OF ORDER', shredded='No')

    context = {'dvds': dvds}
    # print(context)
    return render(request, 'outofordershredding.html', context)


def shredd_dvds(request):
    if request.method == 'POST':
        selected_ids = request.POST.get('selected_ids')
        selected_ids_list = selected_ids.split(",")
        comments = request.POST.get('comments')
        shredd_date = request.POST.get('shredd_date')

        try:
            # Convert selected_ids_list to integers
            selected_ids_list = [int(id) for id in selected_ids_list]

            # Update records in the IssueReceiveRecord model
            IssueReceiveRecord.objects.filter(id__in=selected_ids_list).update(
                shredding_remarks=comments,
                shredded='Yes',
                date_shredded=shredd_date,
            )

            # Retrieve the dvd_ids related to the selected IssueReceiveRecord ids
            dvd_ids = IssueReceiveRecord.objects.filter(id__in=selected_ids_list).values_list('dvd_id', flat=True)

            # Update records in the DVDAddition model
            DVDAddition.objects.filter(id__in=dvd_ids).update(
                shredded='Yes',
            )

            return redirect('outofordershredding')  

        except Exception as e:
            return redirect('outofordershredding')  

    else:
        return render(request, 'outofordershredding.html')  



# Added on 05 Jun 2024
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password = password)

   
        if user is None:
            messages.error(request, 'Invalid Username & Password.')
            return redirect('login')  

        else:
            login(request, user)
            return redirect('index')       

    return render (request, 'registration/login.html')



@login_required
def logoutUser(request):
    logout(request)
    request.session.flush()
    return redirect('login')



@login_required
def inventoryAvailable(request):

    dvds = DVDAddition.objects.filter(booking_status='Available')
    issue_counts = {}

    for dvd in dvds:
        dvd_id = dvd.id
        issue_count = IssueReceiveRecord.objects.filter(dvd=dvd_id).count()
        issue_counts[dvd_id] = issue_count



    context = {'dvds': dvds, 'issue_counts': issue_counts,}

    return render(request, 'inventory_Available.html', context)




@login_required
def inventoryReserved(request):

    dvds = DVDAddition.objects.filter(booking_status='Reserved')
    issue_counts = {}

    for dvd in dvds:
        dvd_id = dvd.id
        issue_count = IssueReceiveRecord.objects.filter(dvd=dvd_id).count()
        issue_counts[dvd_id] = issue_count



    context = {'dvds': dvds, 'issue_counts': issue_counts,}

    return render(request, 'inventory_Reserved.html', context)



@login_required
def inventoryOutofOrder(request):
    dvds = IssueReceiveRecord.objects.filter(status='OUT OF ORDER')
    context = {'dvds': dvds}
    return render(request, 'inventory_OOO.html', context)