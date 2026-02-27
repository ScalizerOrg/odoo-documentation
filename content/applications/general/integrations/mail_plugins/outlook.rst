==============
Outlook plugin
==============

Outlook allows for third-party applications to connect in order to execute database actions from
emails. Odoo has a plugin for Outlook that allows for the creation of an opportunity from the email
panel.

.. _mail-plugin/outlook/install-plugin:

Install the Outlook plugin
==========================

To install the Odoo Outlook plugin, go to the `Odoo Inbox Addin
<https://marketplace.microsoft.com/en-us/product/WA200009923?tab=Overview>`_ page in the Microsoft
Marketplace and click :guilabel:`Get it now` to install the plugin. Sign in to the Outlook account
to be connected to Odoo. Fill out the :guilabel:`Name` and :guilabel:`Country / region` fields, then
click :guilabel:`Get it now` one more time to grant the necessary permissions, and the page
redirects to the Outlook inbox. Click :guilabel:`Add`

Alternatively, the plugin can be installed directly from the Outlook inbox. To do so, open an email
in the Outlook inbox, click on the :guilabel:`Apps` button in the top-right corner of the email,
then click :guilabel:`Get add-ins`. Click :guilabel:`Search add-ins`, then type `Odoo` and press
Enter. Click :guilabel:`Odoo Inbox Addin`, then click :guilabel:`Add` to install the plugin.

.. image:: outlook/more-actions.png
   :alt: Apps button in Outlook

To open the plugin, click on the :guilabel:`Apps` button in the top-right corner of any email, and
select :guilabel:`Odoo`. The plugin panel opens to the right of the email.

Enter the Odoo database URL and click :guilabel:`Login`, or click :guilabel:`Sign Up` to create an
Odoo account. Click :guilabel:`Allow` and a pop-up window opens. Click :guilabel:`Allow` in the
pop-up window to let the Outlook plugin connect to the database.
