import arrow

from brick_server.minimal.models import User


def register_admin(user_id: str) -> User:
    users = User.objects(user_id=user_id)
    if not users:
        user = User(
            user_id=user_id,
            name=user_id,
            is_admin=True,
            is_approved=True,
            registration_time=arrow.get().datetime,
            email=user_id,
            activated_apps=[],
        )
        user.save()
    else:
        user = users[0]
        user.is_admin = True
        user.save()
    return user
