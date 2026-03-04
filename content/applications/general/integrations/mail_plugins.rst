:show-content:

============
Mail plugins
============

Mail plugins are connectors that bridge an Odoo database with email inboxes. With plugins, interact
with an Odoo database directly from an email inbox in the following ways:

- Log emails in the chatter of related Odoo records.
- Search for and create opportunities, tickets, and tasks.
- Open related Odoo records from an email inbox.
- Create Odoo contacts.

.. _integrations/mail_plugins/features:

Mail plugin features
====================

.. note::
   The options available in mail plugins will vary based on the applications installed in the
   database.

Create a contact
----------------

To create a contact record in Odoo from an email, click the :icon:`fa-plus-circle` :guilabel:`(New)`
icon.

.. note::
   A contact record **must** be created before a lead/opportunity can be created.

Create an opportunity
---------------------

To create an opportunity from an email, click the :icon:`fa-plus` :guilabel:`(New)` icon next to
:guilabel:`Opportunities`. Doing so opens a new opportunity record in Odoo in a new tab. The subject
of the email is used as the opportunity title, and the content of the email is added to the
:guilabel:`Notes` tab of the opportunity.

Create a task
-------------

To create a task from an email, click the :icon:`fa-plus` :guilabel:`(New)` icon next to
:guilabel:`Tasks`. Then, enter the title of the project where the task should be created in the
resulting field, and select the appropriate project from the resulting list. This opens a new task
record in Odoo in a new tab. The subject of the email is used as the task title, and the content of
the email is added to the :guilabel:`Description` tab.

Create a ticket
---------------

To create a ticket from an email, click the :icon:`fa-plus` :guilabel:`(New)` icon next to
:guilabel:`Tickets`. Doing so opens a new ticket record in Odoo in a new tab. The subject of the
email is used as the ticket title, and the content of the email is added to the
:guilabel:`Description` tab of the ticket.

Email providers
===============

Mail plugins are available for Outlook and Gmail:

.. cards::
   .. card:: Outlook plugin
      :target: mail_plugins/outlook
      :large:

      Learn how to set up the Outlook plugin and connect it to an Odoo database.

   .. card:: Gmail plugin
      :target: mail_plugins/gmail
      :large:

      Learn how to set up the Gmail plugin and connect it to an Odoo database.

.. toctree::
   :titlesonly:

   mail_plugins/outlook
   mail_plugins/gmail
