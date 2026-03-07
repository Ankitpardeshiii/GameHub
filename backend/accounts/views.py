from django.contrib.auth.models import User
from django.contrib import auth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, GameScore, UserMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
import json


def get_user_profile(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return profile


# ============================================================
# AUTH ENDPOINTS
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username_or_email = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()

    if not username_or_email or not password:
        return Response({'error': 'Both fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Try standard username login first
    user = auth.authenticate(username=username_or_email, password=password)
    
    # If fails, check if input is an email (case-insensitive)
    if user is None and '@' in username_or_email:
        try:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                user = auth.authenticate(username=user_obj.username, password=password)
        except Exception:
            pass

    if user is None:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'error': 'Account is inactive.'}, status=status.HTTP_403_FORBIDDEN)

    get_user_profile(user)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    first_name = request.data.get('first_name', '').strip()
    last_name  = request.data.get('last_name', '').strip()
    username   = request.data.get('username', '').strip()
    email      = request.data.get('email', '').strip()
    password1  = request.data.get('password1', '')
    password2  = request.data.get('password2', '')

    if not all([first_name, last_name, username, email, password1, password2]):
        return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if password1 != password2:
        return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(
            username=username, password=password1,
            email=email, first_name=first_name, last_name=last_name
        )
        get_user_profile(user)
        
        # Return tokens immediately for auto-login
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Registration successful!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_logout(request):
    # With JWT, logout is handled client-side by deleting the token.
    # Optionally blacklist the refresh token if blacklist app is enabled.
    return Response({'message': 'Logged out successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_forgot_password(request):
    email = request.data.get('email', '').strip()
    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if user:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # In a real app, you'd point this to your frontend reset page
        reset_url = f"{settings.CORS_ALLOWED_ORIGINS[0]}/reset-password/{uid}/{token}/"
        
        subject = "Password Reset Request - GameHub"
        message = f"Hello {user.username},\n\nYou requested a password reset. Click the link below to set a new password:\n\n{reset_url}\n\nIf you didn't request this, please ignore this email."
        
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        except Exception as e:
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Return success message
    response_data = {'message': 'If an account exists with this email, a reset link has been sent.'}
    
    # For easier testing in development, include the link in the response
    if settings.DEBUG and user:
        response_data['dev_reset_url'] = reset_url
        
    return Response(response_data)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_reset_password(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('password')

    if not all([uidb64, token, new_password]):
        return Response({'error': 'UID, token and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password has been reset successfully.'})
    else:
        return Response({'error': 'Invalid or expired reset link.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_token_refresh(request):
    from rest_framework_simplejwt.serializers import TokenRefreshSerializer
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    
    serializer = TokenRefreshSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except TokenError as e:
        raise InvalidToken(e.args[0])
        
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


# ============================================================
# USER / PROFILE
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    user = request.user
    profile = get_user_profile(user)
    scores = GameScore.objects.filter(user=user).order_by('-updated_at')
    score = profile.visits + (profile.plays * 5)

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'profile': {
            'visits': profile.visits,
            'plays': profile.plays,
            'score': score,
        },
        'scores': [
            {
                'game_id': s.game_id,
                'score': s.score,
                'updated_at': s.updated_at.isoformat(),
            }
            for s in scores
        ]
    })


# ============================================================
# LEADERBOARD
# ============================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_leaderboard(request):
    users = Profile.objects.select_related('user').extra(
        select={'score': 'visits + (plays * 5)'}
    ).order_by('-score')

    data = [
        {
            'rank': idx + 1,
            'username': p.user.username,
            'visits': p.visits,
            'plays': p.plays,
            'score': p.visits + (p.plays * 5),
        }
        for idx, p in enumerate(users)
    ]
    return Response(data)


# ============================================================
# GAME TRACKING
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_visit(request):
    try:
        game = request.data.get('game')
        profile = get_user_profile(request.user)
        profile.visits += 1
        profile.save()
        score = profile.visits + (profile.plays * 5)
        return Response({'status': 'success', 'visits': profile.visits, 'plays': profile.plays, 'score': score})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_play(request):
    try:
        profile = get_user_profile(request.user)
        profile.plays += 1
        profile.save()
        score = profile.visits + (profile.plays * 5)
        return Response({'status': 'success', 'visits': profile.visits, 'plays': profile.plays, 'score': score})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_save_score(request):
    try:
        game_id = request.data.get('game_id')
        score = request.data.get('score')

        if not game_id or score is None:
            return Response({'error': 'Missing game_id or score'}, status=status.HTTP_400_BAD_REQUEST)

        game_score, created = GameScore.objects.get_or_create(user=request.user, game_id=game_id)
        if score > game_score.score:
            game_score.score = score
            game_score.save()
            return Response({'status': 'success', 'message': 'New high score!', 'high_score': game_score.score})
        return Response({'status': 'success', 'message': 'Score saved', 'high_score': game_score.score})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================
# FEEDBACK
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_send_feedback(request):
    content = request.data.get('content', '').strip()
    if not content:
        return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)

    msg = UserMessage.objects.create(
        user=request.user if request.user.is_authenticated else None,
        content=content
    )
    return Response({'status': 'success', 'message': 'Feedback sent! We appreciate your support.', 'id': msg.id})


# ============================================================
# KEEP OLD TEMPLATE VIEWS (for Django admin compatibility)
# ============================================================

def logout(request):
    auth.logout(request)
    return __import__('django.shortcuts', fromlist=['redirect']).redirect('/')
