==========================================
SEPA Credit Transfer (SCT) vendor payments
==========================================

.. |SCT| replace:: :abbr:`SCT (SEPA Credit Transfer)`

SEPA (Single Euro Payments Area) is a European Union initiative that simplifies euro bank transfers
by enabling automated bank wire transfers through direct payment orders to banks.

.. important::
   - SEPA is supported by the banks in the 27 EU member states, as well as the following:

     - EFTA countries: Iceland, Liechtenstein, Norway, and Switzerland.
     - Non-EEA SEPA countries: Andorra, Monaco, San Marino, the United Kingdom, and the Vatican City
       State.
     - Non-EEA territories: Saint-Pierre-et-Miquelon, Guernsey, Jersey, and the Isle of Man.

   - The SEPA payment method is now exclusively valid for transactions in EUR currency.

Odoo supports vendor bill payments using SEPA Credit Transfer and ISO 20022. ISO 20022 is an open
global standard for financial information, offering consistent, rich, and structured data suitable
for all types of financial business transactions.

At the end of each day, a SEPA file containing all bank wire transfers is generated and exported as
an |SCT| XML file, following **pain.001.001.09 (ISO20022)** specifications by default. This widely
used standard enables corporate clients to send credit transfer instructions to financial
institutions for customer-to-bank electronic payment initiation. The file is then uploaded to the
online banking interface for processing.

.. note::
   Switzerland is currently in a transition phase, supporting both the older pain.001.001.03.ch.02
   and the newer pain.001.001.09 specifications, but the older format is being phased out.

After the bank processes payments, account statements can be imported into Odoo, where the
reconciliation process matches SEPA orders with corresponding bank statements.

.. seealso::
   `Single Euro Payments Area (SEPA) <https://www.ecb.europa.eu/paym/retail/sepa/html/index.en.html>`_

Configuration
=============

.. _accounting/pay_sepa/activate-sepa:

Activate SEPA Credit Transfer (SCT)
-----------------------------------

To pay suppliers with SEPA, activate the :guilabel:`SEPA Credit Transfer` option:

#. Go to :menuselection:`Accounting --> Configuration --> Settings` and scroll down to the
   :guilabel:`Vendor Payments` section.
#. Enable the :guilabel:`SEPA Credit Transfer / ISO20022` option.
#. Fill in the following fields:

   - :guilabel:`Name Identification`: Enter the unique ID number assigned to the payer by the
     issuer. This could be a corporate registration number, tax ID, or a custom internal code.
   - :guilabel:`Issuer`: Specify the authority that provides the identifier (e.g., KBO-BCE, KvK, or
     a specific bank).

.. note::
   Depending on the installed localization package, :guilabel:`SEPA Direct Debit` and
   :guilabel:`SEPA Credit Transfer / ISO20022` modules may be installed by default. If not,
   :ref:`install <general/install>` them manually.

.. _accounting/pay_sepa/activate-sepa-bank-journal:

Activate SEPA payment methods on banks
--------------------------------------

To activate the SEPA payment method on a :ref:`bank journal <accounting/journals/bank>`, follow
these steps:

#. In the accounting dashboard, click the :icon:`fa-ellipsis-v` :guilabel:`(vertical ellipsis)` icon
   on the relevant bank journal and select :guilabel:`Configuration`.
#. In the :guilabel:`Outgoing Payments` tab, click :guilabel:`Add a line` and select
   :guilabel:`ISO20022` as the :guilabel:`Payment Method` if it is not already set.
#. Optionally, set the :ref:`outstanding payments account
   <accounting/journals/outstanding-accounts>`.

.. note::
   Some countries, such as Switzerland or Sweden, require locally adapted ISO 20022 payment methods
   (e.g., :guilabel:`Swiss ISO20022`).

In the :guilabel:`Credit Transfer` section, update the following information that will be included
in the :ref:`SEPA Credit Transfer XML file <accounting/pay_sepa/xml-file-upload>`, if needed:

- :guilabel:`SEPA XML Format`: SEPA XML format (`pain` version) for generating |SCT| XML files.
- :guilabel:`ISO 20022 Charge Bearer`: Party responsible for ISO 20022 payment transaction
  processing charges.
- :guilabel:`Default Priority`: Payment priority level.

.. important::
   Make sure that a valid IBAN is entered in the :guilabel:`Account Number` field in the
   :guilabel:`Journal Entries` tab of the :ref:`bank journal <accounting/journals/bank>` used for
   |SCT| vendor payments.

.. _accounting/pay_sepa/registering-payments-sepa:

Payment registration
====================

Payments can be registered either :ref:`directly from a vendor bill
<finance/accounting/register-payment-invoice-bill>` or :ref:`independently
<accounting/payments/not-tied>`. Select the :ref:`configured SEPA payment method
<accounting/pay_sepa/activate-sepa-bank-journal>` in the :guilabel:`Payment Method` field.

.. seealso::
   :doc:`Payments <../payments>`

.. _accounting/pay_sepa/xml-file-upload:

XML file Export
===============

To generate a daily |SCT| XML payment file for upload to the online banking interface, :ref:`create
a batch payment <accounting/batch/creation>`. The XML file is then displayed in the chatter, where
it can be downloaded and submitted to the bank for processing.

.. seealso::
   :doc:`../bank/bank_synchronization`
