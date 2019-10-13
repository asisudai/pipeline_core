from sqlalchemy.exc import IntegrityError
from pipsy.entities import User


def test_cls_name():
    assert User.cls_name() == 'User'


def test_fullname(user):
    assert user.fullname == '{0.first_name} {0.last_name}'.format(user)


def test_find(user):
    assert user in User.find()


def test_find_fullname(user):
    assert user in User.find(fullname=user.fullname)


def test_findby_ids(user):
    assert user in User.findby_ids([user.id])


def test_find_one(user):
    assert user == user.find_one(id=user.id)


def test_findby_name(user):
    assert user == User.find_one(first_name=user.first_name,
                                 last_name=user.last_name)


def test_create_uq_login(user):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        return User.create(first_name='random', last_name='random',
                           email='random@unittest.com', login=user.login)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_uq_email(user):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        return User.create(first_name='random', last_name='random',
                           email=user.email, login='random')
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
