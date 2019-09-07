import sys
import comtypes.client as cc

from .win32pnpentity import wrap_raw_wmi_object

__wmi_object = None


def _wmi_object():
    global __wmi_object
    if __wmi_object is None:
        __wmi_object = cc.CoGetObject(r"winmgmts:\\.\root\cimv2")
    return __wmi_object


def yellow_bang_devices():
    devices = _wmi_object().ExecQuery(
        "SELECT * from Win32_PnPEntity where ConfigManagerErrorCode <> 0")
    return tuple(wrap_raw_wmi_object(x) for x in devices)


def _find_raw_device(device_id):
    device_id = device_id.replace("\\", "\\\\")
    devices = _wmi_object().ExecQuery(
        "SELECT * from Win32_PnPEntity where DeviceID = '%s'" % device_id)
    return next(iter(devices), None)


def find_device(device_id):
    device = _find_raw_device(device_id)
    if device is None:
        return None
    return wrap_raw_wmi_object(device)


if sys.version_info[0] == 2:
    _dict_values = dict.itervalues
else:
    _dict_values = dict.values


class WmiDeviceManager(object):
    def __init__(self, construct_device_tree=True):
        self._root = None
        self.scan_device_tree()
        if construct_device_tree:
            self.construct_device_tree()

    def find(self, func):
        for item in self:
            if func(item):
                return item
        return None

    def find_by(self, key, value):
        for item in self:
            if getattr(item, key) == value:
                return item
        return None

    def select(self, func):
        return tuple(item for item in self if func(item))

    def select_by(self, key, value):
        return tuple(item for item in self if getattr(item, key) == value)

    @property
    def root(self):
        if self._root is None:
            raise Exception("Device tree not constructed.")
        return self._root

    def scan_device_tree(self):
        self._device_list = tuple(
            wrap_raw_wmi_object(i)
            for i in _wmi_object().ExecQuery("SELECT * from Win32_PnPEntity"))

    def construct_device_tree(self):
        device_hash = {}
        for device in self:
            device_hash[device.DeviceID.upper()] = {
                "device": device,
                "parent": None,
                "children": []
            }
        for value in _dict_values(device_hash):
            parent_id = value["device"].Parent
            if parent_id is None:
                self._root = value["device"]
            else:
                parent = device_hash.get(parent_id.upper())
                if parent:
                    parent["children"].append(value["device"])
                    value["parent"] = parent["device"]
        for value in _dict_values(device_hash):
            value["device"].set_relationship(value["parent"],
                                             value["children"])

    def __iter__(self):
        return iter(self._device_list)

    @property
    def device_list(self):
        return self._device_list
