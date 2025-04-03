from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user signup.
    Validates that the password and confirm_password fields match.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password', 'first_name', 'last_name']

    def validate(self, data):
        """
        Ensure that password and confirm_password match.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """
        Create a new user instance.
        """
        validated_data.pop('confirm_password')  # Remove confirm_password before creating the user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates the email and password and returns tokens if valid.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate the email and password.
        """
        user = User.objects.filter(email=data['email']).first()
        if user and user.check_password(data['password']):
            refresh = RefreshToken.for_user(user)
            role = (
                "recruiter" if user.is_recruiter else
                "applicant" if user.is_applicant else
                "none"
            )
            return {
                'email': data['email'],  
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': role, 
            }
        raise serializers.ValidationError("Invalid email or password.")

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password.
    Validates that the email exists in the system.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Ensure the email exists in the system.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value
