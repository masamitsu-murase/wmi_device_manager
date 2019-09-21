import sys
import warnings
import comtypes.client as cc

from .win32pnpentity import wrap_raw_wmi_object

__wmi_object = None


def _wmi_object():
    global __wmi_object
    if __wmi_object is None:
        __wmi_object = cc.CoGetObject(r"winmgmts:\\.\root\cimv2")
    return __wmi_object


def yellow_bang_devices():
    warnings.warn("yellow_bang_devices is deprecated.", DeprecationWarning)
    return error_devices()


def error_devices():
    """Find all error devices, whose error code is not 0.

    :return: List of Win32PnpEntity
    :rtype: List[Win32PnpEntity]
    """
    devices = _wmi_object().ExecQuery(
        "SELECT * from Win32_PnPEntity where ConfigManagerErrorCode <> 0")
    return [wrap_raw_wmi_object(x) for x in devices]


def _find_raw_device(device_id):
    device_id = device_id.replace("\\", "\\\\")
    devices = _wmi_object().ExecQuery(
        "SELECT * from Win32_PnPEntity where DeviceID = '%s'" % device_id)
    return next(iter(devices), None)


def find_device(device_id):
    """Find a device of a specific device id.

    :param device_id: Device ID of the target device.
    :type device_id: str
    :return: A found device.
    :rtype: Optional[Win32PnpEntity]
    """
    device = _find_raw_device(device_id)
    if device is None:
        return None
    return wrap_raw_wmi_object(device)


if sys.version_info.major == 2:
    _dict_values = dict.itervalues
else:
    _dict_values = dict.values


class WmiDeviceManager(object):
    def __init__(self, construct_device_tree=True):
        """Create a device manager object.

        :param construct_device_tree: If True, create tree structure.
                   Otherwise, parent and children are not set.
                   defaults to True
        :type construct_device_tree: Optional[bool]
        """
        self._root = None
        self._scan_device_tree()
        if construct_device_tree:
            self._construct_device_tree()

    def find(self, pred):
        """Find a device, where pred(device) returns True.

        :param pred: A callable object, which returns True for a target.
        :type pred: Callable[[Win32PnpEntity], bool]
        :return: A found device.
        :rtype: Optional[Win32PnpEntity]
        """
        for item in self:
            if pred(item):
                return item
        return None

    def find_by(self, key, value):
        """Find a device, whose key is value.

        :param key: Key to be checked.
        :type key: str
        :param value: Value to be compared.
        :type value: Any
        :return: A found device.
        :rtype: Optional[Win32PnpEntity]
        """
        for item in self:
            if getattr(item, key) == value:
                return item
        return None

    def select(self, pred):
        """Find all devices, where pred(device) returns True.

        :param pred: A callable object, which returns True for a target.
        :type pred: Callable[[Win32PnpEntity], bool]
        :return: Found devices
        :rtype: List[Win32PnpEntity]
        """
        return [item for item in self if pred(item)]

    def select_by(self, key, value):
        """Find all devices, whose key is value.

        :param key: Key to be checked.
        :type key: str
        :param value: Value to be compared.
        :type value: Any
        :return: Found devices
        :rtype: List[Win32PnpEntity]
        """
        return [item for item in self if getattr(item, key) == value]

    @property
    def root(self):
        """Root device of the device tree

        :return: A root device
        :rtype: Win32PnpEntity
        """
        if self._root is None:
            raise RuntimeError("Device tree not constructed.")
        return self._root

    def _scan_device_tree(self):
        self._device_list = tuple(
            wrap_raw_wmi_object(i)
            for i in _wmi_object().ExecQuery("SELECT * from Win32_PnPEntity"))

    def _construct_device_tree(self):
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
        """Return all devices.

        :return: All devices.
        :rtype: Tuple[Win32PnpEntity]
        """
        return self._device_list
