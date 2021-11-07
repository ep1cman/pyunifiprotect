"""Tests for pyunifiprotect.unifi_protect_server."""

from datetime import timedelta
from unittest.mock import patch

import pytest

from pyunifiprotect import ProtectApiClient
from pyunifiprotect.data import EventType
from pyunifiprotect.utils import to_js_time
from tests.conftest import MockDatetime


@pytest.mark.asyncio
async def test_process_events_none(protect_client: ProtectApiClient, camera):
    def get_camera():
        return protect_client.bootstrap.cameras[camera["id"]]

    bootstrap_before = protect_client.bootstrap.unifi_dict()
    camera_before = get_camera().copy()

    async def get_events(*args, **kwargs):
        return []

    setattr(protect_client, "get_events_raw", get_events)

    await protect_client.update()

    assert protect_client.bootstrap.unifi_dict() == bootstrap_before
    assert get_camera() == camera_before


@pytest.mark.asyncio
@patch("pyunifiprotect.api.datetime", MockDatetime)
async def test_process_events_ring(protect_client: ProtectApiClient, now, camera):
    def get_camera():
        return protect_client.bootstrap.cameras[camera["id"]]

    bootstrap_before = protect_client.bootstrap.unifi_dict()
    camera_before = get_camera().copy()

    expected_event_id = "bf9a241afe74821ceffffd05"

    async def get_events(*args, **kwargs):
        return [
            {
                "id": expected_event_id,
                "type": "ring",
                "start": to_js_time(now - timedelta(seconds=1)),
                "end": to_js_time(now),
                "score": 0,
                "smartDetectTypes": [],
                "smartDetectEvents": [],
                "camera": camera["id"],
                "partition": None,
                "user": None,
                "metadata": {},
                "thumbnail": f"e-{expected_event_id}",
                "heatmap": f"e-{expected_event_id}",
                "modelKey": "event",
            },
        ]

    setattr(protect_client, "get_events_raw", get_events)

    await protect_client.update()

    camera_index = -1
    for index, camera_dict in enumerate(bootstrap_before["cameras"]):
        if camera_dict["id"] == camera["id"]:
            camera_index = index
            break

    camera_before.last_ring = now - timedelta(seconds=1)
    bootstrap_before["cameras"][camera_index]["lastRing"] = to_js_time(camera_before.last_ring)
    bootstrap = protect_client.bootstrap.unifi_dict()
    camera = get_camera()

    event = camera.last_ring_event
    camera_before.last_ring_event_id = None
    camera.last_ring_event_id = None

    assert bootstrap == bootstrap_before
    assert camera.dict() == camera_before.dict()
    assert event.id == expected_event_id
    assert event.type == EventType.RING
    assert event.thumbnail_id == f"e-{expected_event_id}"
    assert event.heatmap_id == f"e-{expected_event_id}"
    assert event.start == camera.last_ring


@pytest.mark.asyncio
@patch("pyunifiprotect.api.datetime", MockDatetime)
async def test_process_events_motion_in_progress(protect_client: ProtectApiClient, now, camera):
    def get_camera():
        return protect_client.bootstrap.cameras[camera["id"]]

    bootstrap_before = protect_client.bootstrap.unifi_dict()
    camera_before = get_camera().copy()

    expected_event_id = "bf9a241afe74821ceffffd05"

    async def get_events(*args, **kwargs):
        return [
            {
                "id": expected_event_id,
                "type": "motion",
                "start": to_js_time(now),
                "end": None,
                "score": 0,
                "smartDetectTypes": [],
                "smartDetectEvents": [],
                "camera": camera["id"],
                "partition": None,
                "user": None,
                "metadata": {},
                "thumbnail": f"e-{expected_event_id}",
                "heatmap": f"e-{expected_event_id}",
                "modelKey": "event",
            },
        ]

    setattr(protect_client, "get_events_raw", get_events)

    await protect_client.update()

    camera_index = -1
    for index, camera_dict in enumerate(bootstrap_before["cameras"]):
        if camera_dict["id"] == camera["id"]:
            camera_index = index
            break

    camera_before.is_motion_detected = True
    bootstrap_before["cameras"][camera_index]["isMotionDetected"] = True
    bootstrap = protect_client.bootstrap.unifi_dict()
    camera = get_camera()

    assert bootstrap == bootstrap_before
    assert camera == camera_before


@pytest.mark.asyncio
@patch("pyunifiprotect.api.datetime", MockDatetime)
async def test_process_events_motion(protect_client: ProtectApiClient, now, camera):
    def get_camera():
        return protect_client.bootstrap.cameras[camera["id"]]

    bootstrap_before = protect_client.bootstrap.unifi_dict()
    camera_before = get_camera().copy()

    expected_event_id = "bf9a241afe74821ceffffd05"

    async def get_events(*args, **kwargs):
        return [
            {
                "id": expected_event_id,
                "type": "motion",
                "start": to_js_time(now - timedelta(seconds=30)),
                "end": to_js_time(now),
                "score": 0,
                "smartDetectTypes": [],
                "smartDetectEvents": [],
                "camera": camera["id"],
                "partition": None,
                "user": None,
                "metadata": {},
                "thumbnail": f"e-{expected_event_id}",
                "heatmap": f"e-{expected_event_id}",
                "modelKey": "event",
            },
        ]

    setattr(protect_client, "get_events_raw", get_events)

    await protect_client.update()

    camera_index = -1
    for index, camera_dict in enumerate(bootstrap_before["cameras"]):
        if camera_dict["id"] == camera["id"]:
            camera_index = index
            break

    camera_before.last_motion = now
    camera_before.is_motion_detected = False
    bootstrap_before["cameras"][camera_index]["lastMotion"] = to_js_time(camera_before.last_motion)
    bootstrap_before["cameras"][camera_index]["isMotionDetected"] = False
    bootstrap = protect_client.bootstrap.unifi_dict()
    camera = get_camera()

    event = camera.last_motion_event
    camera.last_motion_event_id = None
    camera_before.last_motion_event_id = None

    assert bootstrap == bootstrap_before
    assert camera.dict() == camera_before.dict()
    assert event.id == expected_event_id
    assert event.type == EventType.MOTION
    assert event.thumbnail_id == f"e-{expected_event_id}"
    assert event.heatmap_id == f"e-{expected_event_id}"
    assert event.start == (now - timedelta(seconds=30))
    assert event.end == camera.last_motion


@pytest.mark.asyncio
@patch("pyunifiprotect.api.datetime", MockDatetime)
async def test_process_events_smart(protect_client: ProtectApiClient, now, camera):
    def get_camera():
        return protect_client.bootstrap.cameras[camera["id"]]

    bootstrap_before = protect_client.bootstrap.unifi_dict()
    camera_before = get_camera().copy()

    expected_event_id = "bf9a241afe74821ceffffd05"

    async def get_events(*args, **kwargs):
        return [
            {
                "id": expected_event_id,
                "type": "smartDetectZone",
                "start": to_js_time(now - timedelta(seconds=30)),
                "end": to_js_time(now),
                "score": 0,
                "smartDetectTypes": ["person"],
                "smartDetectEvents": [],
                "camera": camera["id"],
                "partition": None,
                "user": None,
                "metadata": {},
                "thumbnail": f"e-{expected_event_id}",
                "heatmap": f"e-{expected_event_id}",
                "modelKey": "event",
            },
        ]

    setattr(protect_client, "get_events_raw", get_events)

    await protect_client.update()

    camera_index = -1
    for index, camera_dict in enumerate(bootstrap_before["cameras"]):
        if camera_dict["id"] == camera["id"]:
            camera_index = index
            break

    camera_before.last_smart_detect = now
    bootstrap_before["cameras"][camera_index]["lastMotion"] = to_js_time(camera_before.last_motion)
    bootstrap = protect_client.bootstrap.unifi_dict()
    camera = get_camera()

    smart_event = camera.last_smart_detect_event
    camera.last_smart_detect_event_id = None
    camera_before.last_smart_detect_event_id = None

    assert bootstrap == bootstrap_before
    assert camera.dict() == camera_before.dict()
    assert smart_event.id == expected_event_id
    assert smart_event.type == EventType.SMART_DETECT
    assert smart_event.thumbnail_id == f"e-{expected_event_id}"
    assert smart_event.heatmap_id == f"e-{expected_event_id}"
    assert smart_event.start == (now - timedelta(seconds=30))
    assert smart_event.end == now