======
Mollie
======

Connecting a **Mollie** :doc:`payment terminal <../terminals>` allows you to offer a fluid payment
flow to your customers and ease the work of your cashiers.

.. note::
   - Mollie payment terminals do not require an :doc:`IoT Box </applications/general/iot>` to
     operate.
   - The Mollie Tap app allows a smartphone with an NFC chip to be used as a payment terminal.

.. seealso::
   - `List of supported countries <https://help.mollie.com/hc/en-us/articles/33911501243154-In-person-payments-supported-countries>`_

Mollie configuration
====================

To configure a Mollie terminal, go to your `Mollie account <https://my.mollie.com>`_,
and then follow these steps:

#. Go to :guilabel:`Point-of-sale` in the left sidebar.
#. You should see your list of payment terminals. If you haven't setup a terminal with Mollie yet,
   you can find all the available options on the `Mollie website <https://www.mollie.com/products/pos-payments>`_.
#. Select the desired payment terminal from the list.
#. Go to :guilabel:`Terminal information` from the tabs at the top.
#. Copy the :guilabel:`Terminal ID` for later.
#. Go to the :guilabel:`Developers` link in the bottom left corner.
#. Copy the :guilabel:`Live API key` for later.

.. warning::
   Treat your Live API key like a password, do not share it with anyone or write it down anywhere insecure,
   as it can grant access to your Mollie account.

Odoo POS configuration
======================

To connect the Mollie terminal with Odoo Point of Sale, follow these steps:

#. Go to :menuselection:`Point of Sale --> Configuration --> Payment Methods` and :doc:`create a
   payment method <../../payment_methods>`.
#. Set the :guilabel:`Journal` field to :guilabel:`Bank`.
#. Select the desired point of sale in the :guilabel:`Point of Sale` field.
#. Set the :guilabel:`Integration` field to :guilabel:`Terminal`.
#. :guilabel:`Activate` the Mollie integration from the list of providers if you haven't already.
#. Set the :guilabel:`Integrate with` field to :guilabel:`Mollie`.
#. Set the :guilabel:`Mollie Payment Provider` field to :guilabel:`Mollie`.
#. Paste the Terminal ID into the :guilabel:`Mollie Terminal ID` field.
#. Save the form.
#. Follow the internal link on :guilabel:`Mollie Payment Provider`.
#. Paste the API key into the :guilabel:`API Key` field. You can leave the payment provider as
   :guilabel:`Disabled` if you don't intend to also use it for online payments.
#. Save the payment provider form.
