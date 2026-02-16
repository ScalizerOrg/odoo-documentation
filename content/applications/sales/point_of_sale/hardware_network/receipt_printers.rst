.. |LNA| replace:: :abbr:`LNA (Local Network Access)`

================
Receipt printers
================

ePOS printers are designed to integrate with Point of Sale systems and can receive print jobs
directly from the POS once they are properly configured and connected.

.. _pos/epos_printers/configuration:

Configuration
=============

To use an ePos printer in Point of Sale:

#. Go to :menuselection:`Point of Sale --> Configuration --> Settings`.
#. Scroll down to the :guilabel:`Connected Devices` section and enable :guilabel:`Receipt Printers`.
#. Click the :guilabel:`Printers` field, then select :guilabel:`Create`.
#. In the :guilabel:`Create Receipt Printers` popup, enter the printer's :guilabel:`Name`.
#. Specify the printer's purpose by selecting either :guilabel:`Preparation` or :guilabel:`Receipt`.
#. Set the :guilabel:`Printer Type` to :ref:`IP address <pos/epos_printers/supported-printers>` or
   :ref:`IoT <pos/epos_printers/iot-supported-printers>`.
#. Depending on the selected :guilabel:`Printer Type`, enter the :guilabel:`Epson Printer IP
   Address` or select the relevant :guilabel:`IoT Device`.
#. Enable :guilabel:`Use Local Network Access` to allow the printer to be detected through
   :doc:`Local Network Access (LNA) <pos_lna>`.
#. Click :guilabel:`Save`.

.. note::
   - When the printer connects to a network, it automatically prints a receipt with its IP address.
   - Once configured, printers can be managed from :menuselection:`Point of Sale -->
     Configuration --> Printers`.

.. _pos/epos_printers/supported-printers:

Directly supported ePOS printers
================================

The **Epson TM-m30 i/ii/iii (Wi-Fi or Ethernet only) models** are strongly recommended, as they have
been fully tested with Odoo Point of Sale.

Other Wi-Fi or Ethernet Epson printer models that support the **ePoS protocol** should also be
compatible.

.. important::
   - The ePoS printer must be capable of operating in HTTP mode.
   - When using :doc:`Local Network Access (LNA) <pos_lna>`, the ePOS printer must have a **static
     IP address**; otherwise, it may become unreachable. The static IP should be configured through
     the router.

.. _pos/epos_printers/iot-supported-printers:

ePOS printers with IoT system integration
=========================================

The following printers require an :doc:`IoT system </applications/general/iot/devices/printer>` to
be compatible with Odoo:

- Epson TM-T20 family (incompatible ePOS software)
- Epson TM-T88 family (incompatible ePOS software)
- Epson TM-U220 family (incompatible ePOS software)

.. important::
   - Epson printers using Wi-Fi/Ethernet connections and following the `EPOS SDK Javascript protocol
     <https://download4.epson.biz/sec_pubs/pos/reference_en/technology/epson_epos_sdk.html>`_ are
     compatible with Odoo **without** needing an :doc:`IoT system
     </applications/general/iot/devices/printer>`.
   - Thermal printers using ESC/POS are compatible **with** an :doc:`IoT system
     </applications/general/iot/devices/printer>`.
   - Epson printers using only USB connections are compatible **with** an :doc:`IoT system
     </applications/general/iot/devices/printer>`.
   - Epson printers that connect via Bluetooth are **not compatible**.

.. seealso::
   - :doc:`pos_lna`
   - :doc:`epos_ssc`
   - :doc:`/applications/general/iot/devices/printer`
