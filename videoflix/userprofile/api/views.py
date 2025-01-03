from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from offer.models import Offer
from userprofile.api.permissions import IsCustomerCreateReview, IsOwnerOrAdmin, IsReviewerOrAdmin
from userprofile.api.serializers import BusinessUserProfileSerializer, CustomerUserProfileSerializer, RegistrationSerializer, ReviewSerializer, SingleReviewSerializer, UserGetProfileSerializer
from userprofile.models import Review, UserProfile
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_serializer, inline_serializer
from rest_framework import serializers



class BaseInfoView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(responses=inline_serializer(name='BaseInfoSerializer', fields={
        'review_count' : serializers.IntegerField(),
        'average_rating' : serializers.IntegerField(),
        'business_profile_count' : serializers.IntegerField(),
        'offer_count' : serializers.IntegerField(),
    }))
    def get(self, request):
        """
        Retrieves general basic information about the platform, including the number of reviews, the average review score,
        the number of business users (business profiles) and the number of listings.

        Returns:
            JSON: Returns the review count, average rating, business user count and offer count.
        """
        reviews = Review.objects.all()
        offers = Offer.objects.all()
        profiles= UserProfile.objects.filter(type='business')
        average_rating = 0
        for review in reviews:
            average_rating += review.rating
        
        if len(reviews) > 0:
            average_rating = average_rating/len(reviews)

        return Response({
            "review_count": len(reviews),
            "average_rating": average_rating,
            "business_profile_count": len(profiles),
            "offer_count": len(offers),
            }, status=status.HTTP_200_OK
        )


class ReviewModelFilter(filters.FilterSet):
    business_user_id = filters.NumberFilter(field_name='business_user')
    reviewer_id = filters.NumberFilter()
    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']

class ReviewView(generics.ListCreateAPIView):
    """
    Lists all available reviews or creates a new review for a business user if the user is authenticated and has a customer role.
    GET: Retrieves a list of all ratings, which can be sorted by updated_at or rating.
    POST: Creates a new rating. Only authenticated users who have a customer profile can create ratings. A user can only submit one rating per business profile.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerCreateReview]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['rating', 'updated_at']
    filterset_class = ReviewModelFilter
    
   
    def perform_create(self, serializer):
        # Reviewer aus der aktuellen Anfrage setzen
        reviewer = UserProfile.objects.get(user=self.request.user)
        serializer.save(reviewer=reviewer)

class SingleReviewView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = SingleReviewSerializer
    permission_classes = [IsReviewerOrAdmin]
    

class LoginView(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        """
        Authenticates a user and returns an authentication token that is used for further API requests.

        Args:
            request (auth.user): Only authenticated users

        Returns:
            JSON: Response with token, user id, email and username.
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        profile = UserProfile.objects.get(user=user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': profile.pk,
            'email': user.email,
            'username' : user.username
        }, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(responses=inline_serializer(name='RegisterResponseSerializer', fields={
        'token' : serializers.CharField(),
        'user_id' : serializers.IntegerField(),
        'email' : serializers.CharField(),
        'username' : serializers.CharField()
    }))
    def post(self, request):
        """
        A POST-request compares the given passwords and if the user or the email already exists.
        This API provides endpoints for user login and registration.
        Login provides the user with a token for authentication and registration creates a new user,
        automatically assigning a customer or business user profile.
        The function returns a JSON when is was successfull.

        Args:
            request (data): username: Username of the new user. Email: Email address of the new user.
	        Password: Password for the new user. Repeated_password: Repetition of the password for confirmation.
	        Type: Profile type (business or customer profile).

        Returns:
            JSON: Response with token, user id, email and username.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            
            profile = UserProfile.objects.create(user=saved_account, id=saved_account.id, type=request.data['type'] )
            token, created = Token.objects.get_or_create(user=saved_account)
            return Response({
            'token': token.key,
            'user_id': profile.pk,
            'email': saved_account.email,
            'username' : saved_account.username
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SingleProfileView(APIView):
    
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = UserGetProfileSerializer
    
    @extend_schema(responses=UserGetProfileSerializer)
    def get(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk)
        self.check_object_permissions(request, obj=profile)
        serializer = self.serializer_class(profile)
        return Response(serializer.data)
    
    @extend_schema(responses=UserGetProfileSerializer)
    def patch(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk)
        self.check_object_permissions(request, obj=profile)
      
        serializer = self.serializer_class(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class BusinessProfileView(APIView):
    @extend_schema(responses=BusinessUserProfileSerializer)
    def get(self, request):
        profiles = UserProfile.objects.filter(type='business')
        serializer = BusinessUserProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    
class CustomerProfileView(APIView):
    @extend_schema(responses=CustomerUserProfileSerializer)
    def get(self, request):
        profiles = UserProfile.objects.filter(type='customer')
        serializer = CustomerUserProfileSerializer(profiles, many=True)
        return Response(serializer.data)

