# coding: utf-8

import comtypes
import comtypes.client as cc
import comtypes.client._generate as g
import wmidevicemanager as wmi
import re
import pickle
import unittest

# Do not create cache
cc.gen_dir = None
# Suppress debug messages
g.__verbose__ = False

class WmiTest(unittest.TestCase):
    def test_list_all_devices(self):
        w = wmi.WmiDeviceManager(False)
        for i in w:
            print(i.DeviceID)

    def test_root_device(self):
        w = wmi.WmiDeviceManager()
        self.assertIsNotNone(w.root.DeviceID)

    def test_pci_device(self):
        w = wmi.WmiDeviceManager()
        first_pci_device = None
        for i in w:
            try:
                i.BiosDeviceName
                i.Device_BiosDeviceName
                i.DEVPKEY_Device_BiosDeviceName
                loc = i.Device_LocationInfo
                if re.search(ur"PCI バス", loc) or re.search(r"PCI Bus", loc):
                    print(loc)
                    print(i.DeviceID)
                    if first_pci_device is None:
                        first_pci_device = i
            except:
                pass
        self.assertIsNotNone(first_pci_device)

    def test_find(self):
        dev = wmi.find_device(r"HTREE\ROOT\0")
        self.assertIsNotNone(dev)
        self.assertIsNone(dev.parent)

    def test_pickle(self):
        dev = wmi.find_device(r"HTREE\ROOT\0")
        pci = pickle.loads(pickle.dumps(dev))
        self.assertIsNot(dev, pci)
        self.assertEqual(dev.DeviceID, pci.DeviceID)

    def test_pickle_wdm(self):
        w = wmi.WmiDeviceManager()
        w2 = pickle.loads(pickle.dumps(w))
        set_w = set(map(lambda x: x.DeviceID, w))
        set_w2 = set(map(lambda x: x.DeviceID, w2))
        self.assertEqual(set_w, set_w2)

    def test_yellow_bang_devices(self):
        ybd = wmi.yellow_bang_devices()
        self.assertEqual(len(ybd), 0)


if __name__ == "__main__":
    unittest.main()
