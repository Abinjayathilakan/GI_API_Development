# tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
import io
import csv

class UserCSVUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('upload-csv')  # Make sure 'upload-csv' matches your URL name

    def create_test_csv(self, data):
        # Create a CSV file in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['name', 'email', 'age'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return SimpleUploadedFile(
            "test.csv",
            output.getvalue().encode('utf-8'),
            content_type='text/csv'
        )

    def test_valid_csv_upload(self):
        """Test uploading a valid CSV file"""
        test_data = [
            {'name': 'John Doe', 'email': 'john@example.com', 'age': '30'},
            {'name': 'Jane Doe', 'email': 'jane@example.com', 'age': '25'}
        ]
        csv_file = self.create_test_csv(test_data)
        response = self.client.post(self.url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['successful_records'], 2)
        self.assertEqual(response.data['rejected_records'], 0)
        self.assertEqual(len(response.data['validation_errors']), 0)

    def test_invalid_email(self):
        """Test uploading CSV with invalid email"""
        test_data = [
            {'name': 'John Doe', 'email': 'not-an-email', 'age': '30'}
        ]
        csv_file = self.create_test_csv(test_data)
        response = self.client.post(self.url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['successful_records'], 0)
        self.assertEqual(response.data['rejected_records'], 1)
        self.assertTrue('email' in response.data['validation_errors'][0]['errors'])

    def test_invalid_age(self):
        """Test uploading CSV with invalid age"""
        test_data = [
            {'name': 'John Doe', 'email': 'john@example.com', 'age': '150'}
        ]
        csv_file = self.create_test_csv(test_data)
        response = self.client.post(self.url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['successful_records'], 0)
        self.assertEqual(response.data['rejected_records'], 1)
        self.assertTrue('age' in response.data['validation_errors'][0]['errors'])

    def test_duplicate_email(self):
        """Test handling of duplicate emails"""
        test_data = [
            {'name': 'John Doe', 'email': 'john@example.com', 'age': '30'},
            {'name': 'Jane Doe', 'email': 'john@example.com', 'age': '25'}
        ]
        csv_file = self.create_test_csv(test_data)
        response = self.client.post(self.url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['successful_records'], 1)
        self.assertEqual(response.data['rejected_records'], 1)
        self.assertTrue('email' in response.data['validation_errors'][0]['errors'])

    def test_no_file_upload(self):
        """Test API response when no file is uploaded"""
        response = self.client.post(self.url, {}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('error' in response.data)

    def test_non_csv_file(self):
        """Test uploading a non-CSV file"""
        file = SimpleUploadedFile(
            "test.txt",
            b"this is not a CSV",
            content_type='text/plain'
        )
        response = self.client.post(self.url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('error' in response.data)