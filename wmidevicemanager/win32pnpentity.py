import sys
import types

from . import const


def _method_type(method, self, klass):
    if sys.version_info.major == 2:
        return types.MethodType(method, self, Win32PnpEntity)
    else:
        return types.MethodType(method, self)


def wrap_raw_wmi_object(obj):
    if isinstance(obj, tuple):
        return tuple(wrap_raw_wmi_object(x) for x in obj)
    elif isinstance(obj, list):
        return [wrap_raw_wmi_object(x) for x in obj]
    elif hasattr(obj, "Properties_") and hasattr(obj, "Methods_"):
        return Win32PnpEntity(obj)
    else:
        return obj


def create_const_dict():
    const_dict = {}
    for name, values in const.DEVPKEY_LIST:
        for value in values:
            long_name = "DEVPKEY_" + name + "_" + value
            for attr_name in (value, name + "_" + value,
                              "DEVPKEY_" + name + "_" + value):
                if attr_name not in const_dict:
                    const_dict[attr_name] = long_name
    return const_dict


class Win32PnpEntity(object):
    LONG_NAME_DICT = create_const_dict()

    def __init__(self, wmi_object):
        """Create a Win32PnpEntity.

        :param wmi_object: A raw WMI object, which represents Win32_PnPEntity.
        :type wmi_object: object
        """
        self._wmi_object = wmi_object
        self._device_id = None
        self._properties_list = set(x.Name for x in wmi_object.Properties_)
        self._methods_list = set(x.Name for x in wmi_object.Methods_)
        self._parent = False  # Special value for "not initialized"
        self._children = False  # Special value for "not initialized"

        if "DeviceID" in self._properties_list:
            self._device_id = wmi_object.Properties_["DeviceID"].Value

    def __getstate__(self):
        state = {
            "_wmi_object": None,
            "_device_id": self._device_id,
            "_properties_list": self._properties_list,
            "_methods_list": self._methods_list,
            "_parent": self._parent,
            "_children": self._children
        }
        if state["_device_id"] is None:
            state["_device_id"] = self._wmi_object.Properties_[
                "DeviceID"].Value
        return state

    @property
    def raw_object(self):
        """A WMI object.

        :return: WMI object
        :rtype: object
        """
        if self._wmi_object is None and self._device_id is not None:
            from .wmidevicemanager import _find_raw_device
            self._wmi_object = _find_raw_device(self._device_id)
        return self._wmi_object

    @property
    def parent(self):
        """Return a parent device.

        :return: Parent device.
        :rtype: Win32PnpEntity
        """
        if self._parent is False:
            parent = self.Device_Parent
            if parent is None or parent == "":
                self._parent = None
            else:
                from .wmidevicemanager import find_device
                self._parent = find_device(parent)
        return self._parent

    @property
    def children(self):
        """Return children devices.

        :return: Children devices.
        :rtype: Tuple[Win32PnpEntity]
        """
        if self._children is False:
            children = self.Device_Children
            if children is None or len(children) == 0:
                self._children = ()
            else:
                from .wmidevicemanager import find_device
                self._children = tuple(map(lambda x: find_device(x), children))
        return self._children

    def set_relationship(self, parent, children):
        self._parent = parent
        self._children = tuple(children)

    def reload(self):
        """Reload device status.
        """
        if self._device_id is None:
            raise RuntimeError('Cannot reload because device id is None.')
        self._wmi_object = None
        self.raw_object  # Reload _wmi_object based on _device_id.

    def __setattr__(self, key, value):
        if hasattr(self, "_properties_list") and key in self._properties_list:
            self.raw_object.Properties_[key].Value = value
        else:
            super(Win32PnpEntity, self).__setattr__(key, value)

    def __getattr__(self, key):
        if key in {
                "_properties_list", "_methods_list", "_wmi_object",
                "_device_id", "_parent", "_children"
        }:
            if key in self.__dict__:
                return self.__dict__[key]
            else:
                raise AttributeError

        if key in self._properties_list:
            return wrap_raw_wmi_object(self.raw_object.Properties_[key].Value)
        elif key in self._methods_list:
            return self._wrap_method(key)
        else:
            long_name = self.LONG_NAME_DICT.get(key)
            prop_value = None
            if long_name is not None:
                prop_value = self.GetDeviceProperties([long_name
                                                       ]).deviceProperties[0]
            if prop_value:
                if prop_value.Type == 0:
                    return None
                else:
                    return prop_value.Data

            if key in self.__dict__:
                return self.__dict__[key]
            else:
                raise AttributeError

    def _wrap_method(self, method_name):
        def wmi_method(self, *args, **kwargs):
            in_parameters = self.raw_object.Methods_[method_name].inParameters
            if in_parameters:
                params = in_parameters.SpawnInstance_()
                for param in params.Properties_:
                    param_id = param.Qualifiers_["ID"].Value
                    if param_id < len(args):
                        param.Value = args[param_id]
                    name = param.Name
                    if name in kwargs:
                        param.Value = kwargs[name]
            else:
                params = None
            return wrap_raw_wmi_object(
                self.raw_object.ExecMethod_(method_name, params))

        return _method_type(wmi_method, self, Win32PnpEntity)
