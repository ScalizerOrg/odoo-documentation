==============================
Worldline & Axepta BNP Paribas
==============================

`Worldline <https://worldline.com/>`_ and `Axepta BNP Paribas <https://www.axeptabnpparibas.be/>`_
offer payment solutions through :doc:`payment terminals<../terminals>` to handle customer transactions.

.. important::
   - Connecting a Worldline or an Axepta BNP Paribas payment terminal to Odoo requires an
     :doc:`IoT system </applications/general/iot/connect>`.
   - Both Worldline and Axepta BNP Paribas are only available in **Belgium**, **the Netherlands**,
     and **Luxembourg** with Odoo.
   - Odoo is compatible with Worldline terminals that use the CTEP protocol (e.g., the **Yomani XR**
     and **Yoximo** terminals). Contact the payment provider to confirm the terminal's
     compatibility if necessary.
   - The configuration of Axepta BNP Paribas payment terminals is identical to that of Worldline terminals.

.. _pos/worldline/configuration:

Worldline/Axepta BNP Paribas configuration
==========================================

First, enable the Worldline or the Axepta BNP Paribas payment terminal in the :ref:`POS settings
<pos/use/settings>` under :guilabel:`Payment Terminals`. Then :doc:`connect the IoT system to Odoo
</applications/general/iot/connect>` and configure the terminal to use CTEP protocol, with hostname
setting set to the :ref:`IoT's IP address <iot/connect/IoT-form>` and port number 9001 (if using an :doc:`IoT box </applications/general/iot/iot_box>`)
or **9050** (if using a :doc:`Windows virtual IoT </applications/general/iot/windows_iot>`)

#. **Terminal configuration**:

   #. Choose CTEP protocol.
   #. Set the hostname to the :ref:`IoT's IP address <iot/connect/IoT-form>`.
   #. Port number must be 9001 (if using an :doc:`IoT box </applications/general/iot/iot_box>`) or **9050** (if using a :doc:`Windows virtual IoT </applications/general/iot/windows_iot>`)
   #. Reboot the terminal to apply settings

Odoo configuration
==================

To connect the Worldline terminal with Odoo Point of Sale, follow these steps:

#. Go to :menuselection:`Point of Sale --> Configuration --> Payment Methods` and :doc:`create a
   payment method <../../payment_methods>`.
#. Set the :guilabel:`Journal` field to :guilabel:`Bank`.
#. Set the :guilabel:`Integration` field to :guilabel:`Terminal`.
#. Set the :guilabel:`Integrate with` field to :guilabel:`Worldline`.
#. Select the configured device in the :guilabel:`Payment Terminal Device` field and save.
#. Go to :menuselection:`Point of Sale --> Configuration --> Settings` and add the created payment
   method to the :guilabel:`Payment Methods` list to make it available in the POS interface.
#. Click :guilabel:`Save`.

.. _worldline/yomani-info:

.. tip::
   - If a setup uses separate cashier and customer payment terminals, :ref:`configure
     <pos/worldline/configuration>` the cashier terminal first.
   - To prevent connection loss, set a fixed IP address on the IoT Box’s router or :ref:`restart
     the virtual IoT server <iot/windows_iot/restart>`.
   - Only one terminal can be connected per IoT Box
