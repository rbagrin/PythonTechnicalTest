from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django.contrib.auth.models import User
from .models import Bond
from .serializers import BondSerializer, UserSerializer

import requests

class HelloWorld(APIView):

    def get(self, request):
        return Response("Hello World!")

class Bonds(APIView):

    permission_classes = [IsAuthenticated]

    # GET /bonds/ and GET /bonds?legal_name=*
    def get(self, request):

        bonds_queryset = Bond.objects.filter(user=request.user.id)

        legal_name = self.request.query_params.get('legal_name', None)
        if legal_name is not None:
            bonds_queryset = bonds_queryset.filter(legal_name=legal_name)

        bonds = BondSerializer(bonds_queryset, many=True)

        return Response(bonds.data)

    # POST /bonds/
    def post(self, request):

        data = JSONParser().parse(request)
        bond_serializer = BondSerializer(data=data)
        if bond_serializer.is_valid():

            try:
                res = requests.get('https://leilookup.gleif.org/api/v2/leirecords?lei=' + data['lei'])
                assert res.status_code == status.HTTP_200_OK
                res = res.json()
            
                legal_name = res[0]['Entity']['LegalName']['$'].replace(' ', '')
            except:
                return Response({"success": False, "message": "Something went wrong. Please check inserted details and try again!"}, status=status.HTTP_400_BAD_REQUEST)

            # Save bond
            bond_serializer.save(legal_name=legal_name, user=request.user)
            return Response(bond_serializer.data, status=status.HTTP_201_CREATED)

class UserList(APIView):

    # Only Admin users can add other users or query the list of users
    permission_classes = [IsAuthenticated & IsAdminUser]

    # GET /users/
    def get(self, request, format=None):

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # POST /users/
    def post(self, request, format=None):

        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
    
    # Only Admin or object owner can see or delete the objects
    permission_classes = [IsAuthenticated & IsAdminUser]

    def get_object(self, id):

        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise Http404

    # GET /users/id 
    def get(self, request, id, format=None):

        user = self.get_object(id)
        user = UserSerializer(user)
        return Response(user.data)

    # DELETE /users/id
    def delete(self, request, id, format=None):

        user = self.get_object(id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)