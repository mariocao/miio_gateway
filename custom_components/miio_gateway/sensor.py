import logging

from homeassistant.const import UnitOfTemperature
from homeassistant.components.sensor.const import SensorDeviceClass

from homeassistant.components.sensor import (
    DEVICE_CLASSES)

from . import DOMAIN, CONF_DATA_DOMAIN, CONF_SENSOR_SID, CONF_SENSOR_CLASS, CONF_SENSOR_NAME, CONF_SENSOR_RESTORE, XiaomiGwDevice

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    SensorDeviceClass.ILLUMINANCE: {"unit_of_measurement": "lm", "icon": "mdi:white-balance-sunny"},
    SensorDeviceClass.TEMPERATURE: {"unit_of_measurement": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    SensorDeviceClass.HUMIDITY: {"unit_of_measurement": "%", "icon": "mdi:water-percent"},
    SensorDeviceClass.PRESSURE: {"unit_of_measurement": "hPa", "icon": "mdi:weather-windy"},
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.info("Setting up sensors")

    # Make a list of default + custom device classes
    all_device_classes = DEVICE_CLASSES

    gateway = hass.data[DOMAIN]
    entities = []

    # Gateways's illuminace sensor
    entities.append(XiaomiGwSensor(gateway, SensorDeviceClass.ILLUMINANCE, "miio.gateway", "Gateway Illuminance Sensor", False))

    for cfg in hass.data[CONF_DATA_DOMAIN]:
        if not cfg:
            cfg = {}

        sid = cfg.get(CONF_SENSOR_SID)
        device_class = cfg.get(CONF_SENSOR_CLASS)
        name = cfg.get(CONF_SENSOR_NAME)
        restore = cfg.get(CONF_SENSOR_RESTORE)

        if sid is None or device_class is None:
            continue

        gateway.append_known_sid(sid)

        if device_class in all_device_classes:
            _LOGGER.info("Registering " + str(device_class) + " sid " + str(sid) + " as sensor")
            entities.append(XiaomiGwSensor(gateway, device_class, sid, name, restore))

    if not entities:
        _LOGGER.info("No sensors configured")
        return False

    add_entities(entities)
    return True

class XiaomiGwSensor(XiaomiGwDevice):

    def __init__(self, gw, device_class, sid, name, restore):
        XiaomiGwDevice.__init__(self, gw, "sensor", device_class, sid, name, restore)

        self._device_class = device_class

    @property
    def state(self):
        return self._state

    @property
    def device_class(self):
        return self._device_class

    @property
    def icon(self):
        try:
            return SENSOR_TYPES.get(self._device_class).get("icon")
        except TypeError:
            return None

    @property
    def unit_of_measurement(self):
        try:
            return SENSOR_TYPES.get(self._device_class).get("unit_of_measurement")
        except TypeError:
            return None

    def parse_incoming_data(self, model, sid, event, params):
        
        if self._device_class == SensorDeviceClass.ILLUMINANCE:
            illumination = params.get("illumination")
            if illumination is not None:
                self._state = illumination
                return True

        elif self._device_class == SensorDeviceClass.TEMPERATURE:
            temperature = params.get("temperature")
            if temperature is not None:
                self._state = round(temperature/100, 1)
                return True

        elif self._device_class == SensorDeviceClass.HUMIDITY:
            humidity = params.get("humidity")
            if humidity is not None:
                self._state = round(humidity/100, 1)
                return True

        elif self._device_class == SensorDeviceClass.PRESSURE:
            pressure = params.get("pressure")
            if pressure is not None:
                self._state = round(pressure/100, 1)
                return True

        return False
