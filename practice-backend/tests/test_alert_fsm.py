from app.application.services.alert_workflow_service import ALLOWED_TRANSITIONS
from app.domain.enums import AlertStatus


def test_fsm_happy_path():
    assert AlertStatus.VIEWED in ALLOWED_TRANSITIONS[AlertStatus.CREATED]
    assert AlertStatus.ACKNOWLEDGED in ALLOWED_TRANSITIONS[AlertStatus.VIEWED]
    assert AlertStatus.RESOLVED in ALLOWED_TRANSITIONS[AlertStatus.ACKNOWLEDGED]
    assert AlertStatus.CLOSED in ALLOWED_TRANSITIONS[AlertStatus.RESOLVED]


def test_fsm_terminal_state():
    assert ALLOWED_TRANSITIONS[AlertStatus.CLOSED] == set()
