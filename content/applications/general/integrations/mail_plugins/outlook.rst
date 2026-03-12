==============
Outlook plugin
==============

The Outlook plugin connects an Odoo database to an Outlook inbox, which enables users to create Odoo
records (such as opportunities, tasks, and tickets) directly in Outlook.

<<<<<<< afc24ce8ef1f6245a2041545c3a4b31a4efb6209
.. note::
   The Outlook plugin is available for both the desktop and web versions of Outlook. See
   `Microsoft's add-in article
   <https://support.microsoft.com/en-us/office/use-add-ins-in-outlook-1ee261f9-49bf-4ba6-b3e2-2ba7bcab64c8>`_.
||||||| 66c23246b12e619d39ed682fd3899cb742e701d4
.. important::
   Make sure to check the database version in the :guilabel:`Settings app --> General Settings`, at
   the bottom of the page.

   For database versions 19.2 and later, see the `latest documentation
   <https://www.odoo.com/documentation/master/applications/general/integrations/mail_plugins/outlook.html>`_
   for installation instructions.

Configuration
=============

The Outlook :doc:`Mail Plugin <../mail_plugins>` needs to be configured both on Odoo and Outlook.

.. _mail-plugin/outlook/enable-mail-plugin:

Enable Mail Plugin
------------------

First, enable the *Mail Plugin* module in the database. Go to :menuselection:`Settings --> General
Settings --> Integrations`, enable :guilabel:`Mail Plugin`, and :guilabel:`Save` the configuration.
=======
.. note::
   The Outlook plugin is available for both the desktop and web versions of Outlook. See
   `Microsoft's add-in article
   <https://support.microsoft.com/en-us/office/use-add-ins-in-outlook-1ee261f9-49bf-4ba6-b3e2-2ba7bcab64c8>`_.

Configuration
=============

The Outlook :doc:`Mail Plugin <../mail_plugins>` needs to be configured both on Odoo and Outlook.

.. important::
   Make sure to check the database version in the :guilabel:`Settings app --> General Settings`, at
   the bottom of the page.

   For database versions 19.2 and later, see the `latest documentation
   <https://www.odoo.com/documentation/master/applications/general/integrations/mail_plugins/outlook.html>`_
   for installation instructions.

.. _mail-plugin/outlook/enable-mail-plugin:

Enable Mail Plugin
------------------

First, enable the *Mail Plugin* module in the database. Go to :menuselection:`Settings --> General
Settings --> Integrations`, enable :guilabel:`Mail Plugin`, and :guilabel:`Save` the configuration.
>>>>>>> 909d363e86f4a0df797ef16ebc149201a44f2e00

.. _mail-plugin/outlook/install-plugin:

Install the Outlook plugin
==========================

.. important::
   Make sure to check the database version in the :menuselection:`Settings app --> General
   Settings`, at the bottom of the page.

   For database versions earlier than 19.2, see the `19.0 documentation
   <https://www.odoo.com/documentation/19.0/applications/general/integrations/mail_plugins/outlook.html>`_
   for installation instructions.

From the Microsoft Marketplace
------------------------------

To install the Odoo Outlook plugin, go to the `Odoo Inbox Addin
<https://marketplace.microsoft.com/en-us/product/WA200009923?tab=Overview>`_ page in the Microsoft
Marketplace and click :guilabel:`Get it now`. Sign in to the Outlook account to be connected to
Odoo. Fill out the :guilabel:`Name` and :guilabel:`Country / region` fields, then click
:guilabel:`Get it now` one more time to grant the necessary permissions, and the page redirects to
the Outlook inbox. Click :guilabel:`Add` to confirm the installation of the plugin.

From the Outlook inbox
----------------------

Alternatively, the plugin can be installed directly from the Outlook inbox. To do so, open an email
in the Outlook inbox, click on the :guilabel:`Apps` button in the top-right corner of the email,
then click :guilabel:`Get add-ins`. Click :guilabel:`Search add-ins`, then type `Odoo` and press
Enter. Click :guilabel:`Odoo Inbox Addin`, then click :guilabel:`Add` to confirm the installation of
the plugin.

.. image:: outlook/more-actions.png
   :alt: Apps button in the Outlook inbox.

Connect an Odoo database
========================

To open the plugin, click on the :guilabel:`Apps` button in the top-right corner of any email, and
select :guilabel:`Odoo`. The plugin panel opens to the right of the email.

Enter the Odoo database URL and click :guilabel:`Login`, or click :guilabel:`Sign Up` to create an
Odoo account. Click :guilabel:`Allow` and a pop-up window opens. Click :guilabel:`Allow` in the
pop-up window to let the Outlook plugin connect to the database.
