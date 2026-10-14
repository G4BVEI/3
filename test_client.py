from datetime import date
from uuid import UUID, uuid4

import pytest
from client import Client, ClientDraft, Err, Ok

D = ClientDraft()


def test_id_is_uuid():
    match D.build():
        case Ok(c):
            assert isinstance(c.id, UUID)
        case Err(e):
            pytest.fail(f"esperava Ok, veio Err({e!r})")


def test_default_values():
    match D.build():
        case Ok(c):
            assert c.phone is None
            assert c.is_active is True
        case Err(e):
            pytest.fail(f"esperava Ok, veio Err({e!r})")


def test_provided_values():
    cid = uuid4()
    result = D.with_(id=cid, phone="11999999999", is_active=False).build()
    match result:
        case Ok(c):
            assert c.id == cid
            assert c.phone == "11999999999"
            assert c.is_active is False
        case Err(e):
            pytest.fail(f"esperava Ok, veio Err({e!r})")


def test_email_saved_lowercase():
    match D.with_(email="JOAO@EXAMPLE.COM").build():
        case Ok(c):
            assert c.email == "joao@example.com"
        case Err(e):
            pytest.fail(f"esperava Ok, veio Err({e!r})")


def test_age_in_complete_years():
    today = date.today()
    birth = date(today.year - 30, today.month, today.day)
    match D.with_(birth_date=birth).build():
        case Ok(c):
            assert c.age() == 30
        case Err(e):
            pytest.fail(f"esperava Ok, veio Err({e!r})")


def test_age_before_birthday_this_year():
    match D.with_(birth_date=date(1990, 5, 15)).build():
        case Ok(c):
            today = date.today()
            expected = today.year - 1990 - ((today.month, today.day) < (5, 15))
            assert c.age() == expected
        case Err(e):
            pytest.fail(f"esperava Ok, veio Err({e!r})")


def test_deactivate():
    match D.build():
        case Ok(c):
            c.deactivate()
            assert c.is_active is False
        case Err(e):
            pytest.fail(f"esperava Ok, veio Err({e!r})")


def test_activate():
    match D.with_(is_active=False).build():
        case Ok(c):
            c.activate()
            assert c.is_active is True
        case Err(e):
            pytest.fail(f"esperava Ok, veio Err({e!r})")


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"name": ""}, "name_required"),
        ({"name": "a" * 251}, "name_too_long"),
        ({"cpf": ""}, "cpf_required"),
        ({"email": ""}, "email_required"),
        ({"email": "sem-arroba"}, "invalid_email"),
        ({"email": "a@b"}, "invalid_email"),
        ({"email": "@b.com"}, "invalid_email"),
        ({"email": "a@.com"}, "invalid_email"),
        ({"email": "a@b."}, "invalid_email"),
        ({"birth_date": "1990-01-01"}, "invalid_birth_date"),
    ],
    ids=[
        "name_required",
        "name_too_long",
        "cpf_required",
        "email_required",
        "invalid_email_no_at",
        "invalid_email_no_dot",
        "invalid_email_empty_user",
        "invalid_email_empty_part",
        "invalid_email_trailing_dot",
        "invalid_birth_date",
    ],
)
def test_create_errors(overrides, expected):
    result = D.with_(**overrides).build()

    match result:
        case Err(error):
            assert error == expected
        case Ok(_):
            pytest.fail(f"esperava Err({expected!r}), veio Ok")


def test_match_on_specific_error():
    match D.with_(name="").build():
        case Err("name_required"):
            pass
        case Err(other):
            pytest.fail(f"esperava name_required, veio {other!r}")
        case Ok(_):
            pytest.fail("esperava Err")


def test_create_success():
    match D.build():
        case Ok(client):
            assert isinstance(client, Client)
            assert client.name == "João"
        case Err(e):
            pytest.fail(f"esperava Ok, veio {e!r}")
