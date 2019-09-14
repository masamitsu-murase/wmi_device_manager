# coding: utf-8

import comtypes.client as cc
import comtypes.client._generate as g
import wmidevicemanager as wmi
import re
import pickle
import unittest
import os
import platform

# Do not create cache
cc.gen_dir = None
# Suppress debug messages
g.__verbose__ = False


class WmiTest(unittest.TestCase):
    def setUp(self):
        self._has_parent = False
        if platform.version().split(",", 1)[0] == "10":
            self._has_parent = True

    @unittest.skip("takes too long time")
    def test_list_all_devices(self):
        w = wmi.WmiDeviceManager(False)
        for i in w:
            try:
                print(i.DeviceID)
                print(i.BiosDeviceName)
            except Exception:
                pass

    def test_root_device(self):
        if self._has_parent:
            w = wmi.WmiDeviceManager()
            self.assertIsNotNone(w.root.DeviceID)

    def test_pci_device(self):
        if not self._has_parent:
            return

        w = wmi.WmiDeviceManager()
        pci_device = None
        for i in w:
            try:
                loc = i.Device_LocationInfo
                if re.search(u"PCI バス", loc) or re.search(r"PCI Bus", loc):
                    pci_device = i
                    break
            except Exception:
                pass
        self.assertIsNotNone(pci_device)
        self.assertIsNotNone(pci_device.BiosDeviceName)
        self.assertTrue(
            pci_device.BiosDeviceName == pci_device.Device_BiosDeviceName ==
            pci_device.DEVPKEY_Device_BiosDeviceName)

    def test_find(self):
        dev = wmi.find_device(r"HTREE\ROOT\0")
        self.assertIsNotNone(dev)
        if self._has_parent:
            self.assertIsNone(dev.parent)

    def test_pickle(self):
        dev = wmi.find_device(r"HTREE\ROOT\0")
        pci = pickle.loads(pickle.dumps(dev))
        self.assertIsNot(dev, pci)
        self.assertEqual(dev.DeviceID, pci.DeviceID)

    def test_pickle_wdm(self):
        if not self._has_parent:
            return

        w = wmi.WmiDeviceManager()
        w2 = pickle.loads(pickle.dumps(w))
        set_w = set(map(lambda x: x.DeviceID, w))
        set_w2 = set(map(lambda x: x.DeviceID, w2))
        self.assertEqual(set_w, set_w2)

    @unittest.skipIf(os.environ.get("APPVEYOR", False),
                     "AppVeyor may have yellow bang devices.")
    def test_error_devices(self):
        devices = wmi.error_devices()
        self.assertEqual(len(devices), 0)

    def test_wmi_find(self):
        wdm = wmi.WmiDeviceManager(False)
        if os.environ.get("APPVEYOR", False):
            device_name = r"\_SB.VMOD"
        else:
            device_name = r"\_SB.PCI0"
        dev1 = wdm.find(lambda item: item.BiosDeviceName == device_name)
        dev_list1 = wdm.select(lambda item: (item.BiosDeviceName or "").
                               startswith(r"\_SB."))
        self.assertIn(dev1, dev_list1)

        dev2 = wdm.find_by("BiosDeviceName", device_name)
        dev_list2 = wdm.select_by("BiosDeviceName", device_name)
        self.assertIn(dev2, dev_list2)

        self.assertIs(dev1, dev2)


if __name__ == "__main__":
    unittest.main()
