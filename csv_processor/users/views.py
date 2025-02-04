
import csv
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

from .serializers import UserSerializer

class UserCSVUploadView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize counters and error list
        successful_records = 0
        rejected_records = 0
        validation_errors = []

        # Read and process CSV
        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            for row_number, row in enumerate(csv_data, start=1):
                serializer = UserSerializer(data=row)
                
                try:
                    if serializer.is_valid():
                        try:
                            serializer.save()
                            successful_records += 1
                        except IntegrityError:
                            rejected_records += 1
                            validation_errors.append({
                                'row': row_number,
                                'errors': {'email': ['Email address already exists']}
                            })
                    else:
                        rejected_records += 1
                        validation_errors.append({
                            'row': row_number,
                            'errors': serializer.errors
                        })
                except Exception as e:
                    rejected_records += 1
                    validation_errors.append({
                        'row': row_number,
                        'errors': {'general': str(e)}
                    })

        except Exception as e:
            return Response(
                {'error': f'Error processing CSV file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'successful_records': successful_records,
            'rejected_records': rejected_records,
            'validation_errors': validation_errors
        }, status=status.HTTP_200_OK)