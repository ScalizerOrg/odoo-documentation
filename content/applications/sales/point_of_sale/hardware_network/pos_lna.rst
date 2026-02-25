.. |LNA| replace:: :abbr:`LNA (Local Network Access)`

====================
Local Network Access
====================

`Local Network Access <https://developer.chrome.com/release-notes/142#local_network_access_restrictions>`_
is a security feature that limits a website's ability to send requests to servers on a local
network. Access requires explicit user permission, which makes it possible to grant network access
to a specific web page. Using |LNA|, Odoo Point of Sale can communicate with devices with local
access directly from the browser and without requiring an :doc:`SSL certificate <epos_ssc>`.

.. note::
   Local Network Access is available in most browsers based on `Chromium version 142
   <https://developer.chrome.com/release-notes/142>`_ or higher, including Google Chrome, Brave,
   Microsoft Edge, Vivaldi, and Opera.

Activation
==========

|LNA| is enabled by default and automatically used for compatible devices, such as
:ref:`ePOS printers <pos/epos-printers/supported-printers>`, when the :guilabel:`Use Local
Network Access` checkbox is enabled on the :ref:`printer form <pos/epos-printers/configuration>`.

.. important::
   The ePOS printer must have a **static IP address**; otherwise, it may become unreachable. The
   static IP should be configured through the router.

Browser permission
==================

Once a device with local access, such as an :ref:`ePOS printer
<pos/epos-printers/supported-printers>`, is configured, the browser displays a popup requesting
permission to communicate with the devices on the local network.

.. image:: pos_lna/pos-lna.png
   :alt: Permission popup to access local network devices

.. note::
   - If the popup does not appear, permission can be granted manually through the browser's site
     settings.
   - Some browsers may require enabling a flag to activate the feature:

     - Brave: `brave://flags/#local-network-access-check`
     - Google Chrome: `chrome://flags/#local-network-access-check`

Point of sale LNA status
========================

To view the point of sale's |LNA| status, :ref:`open <pos/use/open-register>` or access the
register, click the :icon:`fa-bars` (:guilabel:`hamburger menu`) icon in the top-right corner, then
click the :guilabel:`Local Network Access` button at the bottom of the menu. The current |LNA|
status details are then displayed in the :guilabel:`LNA Permission status` popup.
