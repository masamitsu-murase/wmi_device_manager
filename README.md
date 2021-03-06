
# WMI Device Manager
[![PyPI version](https://badge.fury.io/py/wmidevicemanager.svg)](https://badge.fury.io/py/wmidevicemanager)
[![Build Status](https://dev.azure.com/masamitsu-murase/wmi_device_manager/_apis/build/status/masamitsu-murase.wmi_device_manager?branchName=master)](https://dev.azure.com/masamitsu-murase/wmi_device_manager/_build/latest?definitionId=4&branchName=master)
[![Build status](https://ci.appveyor.com/api/projects/status/ktrn3q6nkx9dvdwd?svg=true)](https://ci.appveyor.com/project/masamitsu-murase/wmi-device-manager)

This is a library to get information in device manager on Windows10 based on WMI.

You can get almost all information of device manager via this library.  
For example, "BIOS Device Name", "Driver INF Path" and so on.

See [DEVPROPKEY](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/define-devpropkey) section for more details.

## How to use

Use files in `wmidevicemanager` directory.

You need to install `comtypes` library.

```python
import wmidevicemanager
wdm = wmidevicemanager.WmiDeviceManager()
for x in wdm:
    print(x.DeviceID)

pci_root = wdm.find_by("BiosDeviceName", r"\_SB.PCI0")
for child in pci_root.children:
    print(child.DeviceID)

for device in wdm:
    if device.BiosDeviceName in (r"\_SB.PCI0.RP01.PXSX", r"\_SB.PCI0.RP02.PXSX"):
        device.Disable()
```

## Library for Ruby

See [wmi_device_manager_ruby](https://github.com/masamitsu-murase/wmi_device_manager_ruby).

# License

Please use this library under MIT License

See LICENSE file.
