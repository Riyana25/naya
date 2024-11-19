from multiprocessing import process
import os
from django.shortcuts import redirect, render
import pandas as pd
from rapidfuzz import fuzz
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomUserSerializer, LoginSerializer
from django.conf import settings  # To get the BASE_DIR path
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model

class SignupView(APIView):
    def get(self, request):
        return Response({'message': "API test successful!!"})

    def post(self, request):
        # Parse the incoming data
        serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid():
            # Save the user
            user = serializer.save()
           
            # Path to the CSV file (ensure the path is correct)
            csv_file_path = os.path.join(settings.BASE_DIR, 'app', 'csv_data', 'selected_columns_kathmanduonly_modified2.csv')

            # Error handling if the file does not exist
            if not os.path.exists(csv_file_path):
                return Response({'error': 'CSV file not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Load CSV data using pandas
            csv_data = pd.read_csv(csv_file_path)
            
            # Handle missing values by filling NaN with empty strings
            csv_data = csv_data.fillna('')

            # Check if required columns exist in the CSV
            if 'Registration No' not in csv_data.columns or 'Pharmacy Name' not in csv_data.columns:
                return Response({'error': 'CSV missing required columns: Registration No, Pharmacy Name'}, status=status.HTTP_400_BAD_REQUEST)

            # Get user data for comparison
            query_registrationNumber = str(user.registrationNumber)
            query_pharmacyName = user.pharmacyName

            # Flag to indicate if the user passes the matching criteria
            is_valid_user = False

  # Convert the user's registration number to a string without scientific notation
            query_registrationNumber = "{:.0f}".format(float(query_registrationNumber))
            # Iterate over the CSV rows and compare data
            for _, row in csv_data.iterrows():
                csv_registrationNumber = str(row['Registration No'])  # Convert to string

                csv_pharmacyName = row['Pharmacy Name']
                
                                # Convert the CSV registration number to string without scientific notation
                csv_registrationNumber = "{:.0f}".format(float(csv_registrationNumber))
                # Compare the user's registration number and pharmacy name with the CSV data using RapidFuzz
                name_similarity = fuzz.partial_ratio(query_registrationNumber, csv_registrationNumber)
                pharmacy_similarity = fuzz.token_sort_ratio(query_pharmacyName, csv_pharmacyName)

                # Define a threshold for match similarity (e.g., 70%)
                if name_similarity > 50 or pharmacy_similarity > 50:
                    is_valid_user = True
                    break  # If any match is found, break early (we don't need to continue)

            # Return success or failure based on the match result
            if is_valid_user:
                return Response({
                    'message': 'User created successfully',
                    'redirect_to_login': True  # Flag indicating to redirect
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'User created successfully',
                    'redirect_to_login': False  # Flag indicating to redirect
                }, status=status.HTTP_201_CREATED)

        # If serializer is invalid, return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


# Ensure you're using the custom user model
CustomUser = get_user_model()

class LoginView(APIView):
    def post(self, request):
        # Get email and password from the request data
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate email and password
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to authenticate using email and password
        user = authenticate(request, username=email, password=password)

        print(user)    
        if user is not None:
            # Authentication successful, log the user in and create the session
            login(request, user)

            # Return a success response with user data (don't include password)
            return Response({
                'message': 'Login successful',
                'user': {
                    'email': user.email,
                    'username': user.username,
                    'pharmacyName': user.pharmacyName,
                    'registrationNumber': user.registrationNumber,
                    'address': user.address,
                }
            }, status=status.HTTP_200_OK)
        else:
            # Authentication failed (invalid credentials)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
