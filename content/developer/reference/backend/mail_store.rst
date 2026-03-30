
.. _reference/mail_store:

=============================
Store: Discuss Data Transfer
=============================

The ``Store`` class is a helper for building structured data dictionaries that are sent
to the web client's JavaScript store. It is the primary mechanism for transferring data
between the Python backend and the Odoo Discuss frontend.

The Store handles:

- Merging data from multiple sources
- Managing relations between records (One2many, Many2one, Many2many)
- Versioning for optimistic concurrency control
- Bus notifications for real-time updates

.. code-block:: python

    from odoo.addons.mail.tools.discuss import Store

    # Basic usage
    store = Store()
    store.add(partners, ["name", "email"])
    result = store.get_result()
    # Returns: {"res.partner": [{"id": 1, "name": "...", "email": "..."}]}

.. _reference/mail_store/quickstart:

Quick Start
===========

Adding Records to the Store
---------------------------

The ``add()`` method is the primary way to add records to the store:

.. code-block:: python

    # Add partners with specific fields
    store = Store()
    store.add(partners, ["name", "email", "phone"])
    return store.get_result()

If the model defines a ``_to_store()`` method, it will be called automatically:

.. code-block:: python

    class DiscussChannel(models.Model):
        _name = 'discuss.channel'

        def _to_store(self, store, field_list):
            # Custom logic to add channel data
            store.add_records_fields(field_list)

Specifying Fields
-----------------

Fields can be specified in multiple ways:

.. code-block:: python

    # As a list of field names
    store.add(records, ["field1", "field2"])

    # As a method name (must start with _store_ and end with _fields)
    store.add(channel, "_store_channel_fields")

    # As a callable
    store.add(records, lambda res: res.extend(["name", "email"]))

    # As a dict with static values
    store.add(records, {"name": "Static Name", "active": True})

.. _reference/mail_store/api:

API Reference
=============

Store Class
-----------

.. class:: Store(bus_channel=None, bus_subchannel=None)

    Helper to build a dict of data for sending to web client.

    :param bus_channel: Optional record to use as bus channel for notifications
    :param bus_subchannel: Optional subchannel identifier

    The keys of data are the names of models as defined in mail JS code, and the
    values are any format supported by the store.insert() method.

.. method:: Store.add(records, fields, *, as_thread=False, fields_params=None)

    Add records to the store.

    :param records: A recordset to add
    :type records: odoo.models.Model
    :param fields: Field specification. Can be:

        - A list of field names: ``["name", "email"]``
        - A method name (string): ``"_store_channel_fields"``
        - A callable: ``lambda res: res.extend(["name"])``
        - A dict with static values: ``{"computed": True}``

    :param as_thread: If True, add as mail.thread with model and id
    :param fields_params: Parameters passed to the field method
    :returns: self (for chaining)

    If the model defines ``_to_store()``, it will be called automatically.

    .. code-block:: python

        # Simple fields
        store.add(partners, ["name", "email"])

        # Using a field method
        store.add(channel, "_store_channel_fields")

        # With parameters
        store.add(messages, "_store_message_fields", fields_params={"format_reply": True})

.. method:: Store.add_global_values(field_fn=None, /, **values)

    Add global values to the Store singleton.

    :param values: Key-value pairs to add to the global store

    .. code-block:: python

        store.add_global_values(current_user_id=user.id, settings={...})

.. method:: Store.add_model_values(model_name, values)

    Add values to a model in the store. Use for JS records without a Python record.

    :param model_name: Name of the model
    :param values: Dictionary of values

    .. code-block:: python

        store.add_model_values("DataResponse", {"id": data_id, "result": data})

.. method:: Store.add_records_fields(field_list, as_thread=False)

    Add fields from inside ``_to_store()`` methods. Same as ``add()`` but without
    calling ``_to_store()``.

.. method:: Store.delete(records, as_thread=False)

    Mark records for deletion from the store.

    :param records: Records to delete
    :param as_thread: Delete as mail.thread

    .. code-block:: python

        store.delete(old_messages)

.. method:: Store.get_result()

    Get the resulting data dictionary.

    :returns: Dictionary with model names as keys and record data as values

    .. code-block:: python

        result = store.get_result()
        # {"res.partner": [{"id": 1, "name": "..."}], "discuss.channel": [...]}

.. method:: Store.get_client_action(next_action=None)

    Get a client action to insert this store in the client.

    :param next_action: Optional action to execute after insert
    :returns: A client action dict

    .. code-block:: python

        return store.get_client_action()

.. method:: Store.bus_send(notification_type="mail.record/insert")

    Send the store data via bus notification.

    :param notification_type: Type of notification

    Requires ``bus_channel`` to be set on the Store.

    .. code-block:: python

        Store(bus_channel=channel).add(channel, ["name"]).bus_send()

.. method:: Store.resolve_data_request(values=None, *, data_id=None)

    Resolve a specific data request from the client.

    :param values: Values to add
    :param data_id: ID of the data request

Store.Stores
------------

.. class:: Store.Stores

    Lazy mapping to manage a list of Store instances indexed by bus target.
    Store methods (``add``, ``bus_send``, ``delete``) are forwarded to all contained
    Store instances.

    .. code-block:: python

        from odoo.addons.mail.tools.discuss import Store

        stores = Store.Stores()
        # Accessing a target creates a Store for it lazily
        stores[channel].add(channel, ["name"])

        # Forwarding to all stores
        stores.add(records, ["name"])  # Adds to all stores

Store.Target
------------

.. class:: Store.Target(channel=None, subchannel=None)

    Target of the current store. Useful when information has to be added contextually
    depending on who is going to receive it.

    :param channel: A record to use as bus channel
    :param subchannel: Optional subchannel identifier

    .. attribute:: channel

        The bus channel record.

    .. attribute:: subchannel

        The subchannel identifier.

.. _reference/mail_store/relations:

Relations
=========

Store.One
---------

Use ``Store.One`` (or ``FieldList.one()``) for Many2one and One2one relations:

.. code-block:: python

    # In a field method
    def _store_message_fields(self, res):
        res.one("author_id", ["name", "email"])

    # Direct instantiation
    Store.One(store, "partner_id", ["name"], sudo=True)

.. class:: Store.One(store, record_or_field_name, fields, *, as_thread=False, dynamic_fields=None, fields_params=None, only_data=False, predicate=None, sudo=False, value=NO_VALUE)

    Flags a record or field name to be added to the store in a One relation.

    :param record_or_field_name: Field name or record
    :param fields: Fields to include on the related record
    :param as_thread: Add as mail.thread
    :param dynamic_fields: Method name or callable for dynamic fields
    :param fields_params: Parameters for field method
    :param only_data: If True, only add data without the ID reference
    :param predicate: Callable to filter records
    :param sudo: Use sudo() on the relation
    :param value: Custom value instead of field

    .. code-block:: python

        # Basic one relation
        res.one("author_id", ["name", "email"])

        # With sudo for access rights bypass
        res.one("partner_id", "_store_partner_fields", sudo=True)

        # With dynamic fields based on calling record
        res.one("author_id", "_store_author_fields", dynamic_fields="_store_dynamic_author")

Store.Many
----------

Use ``Store.Many`` (or ``FieldList.many()``) for One2many and Many2many relations:

.. code-block:: python

    # In a field method
    def _store_channel_fields(self, res):
        res.many("message_ids", ["body", "date"], mode="ADD")

    # Direct instantiation with mode
    Store.Many(store, "members", ["name"], mode="ADD")

.. class:: Store.Many(store, records_or_field_name, fields, *, mode="REPLACE", as_thread=False, dynamic_fields=None, fields_params=None, only_data=False, predicate=None, sort=None, sudo=False, value=NO_VALUE)

    Flags records or field name to be added to the store in a Many relation.

    :param mode: How to handle the relation:

        - ``"REPLACE"``: Replace all existing (default)
        - ``"ADD"``: Add to existing records
        - ``"DELETE"``: Remove from existing records

    :param sort: Field name or callable to sort records
    :param predicate: Callable to filter records

    .. code-block:: python

        # Add members without replacing existing
        res.many("members", ["name"], mode="ADD")

        # Sort messages by date
        res.many("message_ids", ["body"], sort="date")

        # Delete specific records
        res.many("old_messages", ["id"], mode="DELETE")

Store.Attr
----------

Use ``Store.Attr`` for custom attributes with computed or static values:

.. code-block:: python

    # In a field method
    def _store_partner_fields(self, res):
        res.attr("computed_field", lambda r: r._compute_something())

    # Direct instantiation
    Store.Attr(store, "is_admin", value=lambda r: r.user_id.has_group('base.group_admin'))

.. class:: Store.Attr(store, field_name, value=NO_VALUE, *, predicate=None, sudo=False)

    Attribute to be added for each record.

    :param field_name: Name of the field
    :param value: Static value or callable(record) -> value
    :param predicate: Callable(record) -> bool to conditionally include
    :param sudo: Use sudo() when reading

    .. code-block:: python

        # Simple field (reads from record)
        res.attr("name")

        # With static value (same for all records)
        res.attr("computed", True)

        # With callable value (per-record computation)
        res.attr("display_name", lambda r: r._compute_display_name())

        # Conditional inclusion
        res.attr("secret", "value", predicate=lambda r: r.is_admin)

        # With sudo for access rights bypass
        res.attr("internal_field", sudo=True)

.. _reference/mail_store/fieldlist:

Store.FieldList
---------------

``FieldList`` is the main interface for specifying fields in ``_to_store()`` methods:

.. class:: Store.FieldList(store, records)

    Helper to provide short syntax for building a list of field definitions for a specific
    store.add call (with given records and target).

    :param store: The Store instance
    :param records: The recordset for which fields are being defined

    .. attribute:: records

        The records for which the field list will apply. Useful to pre-compute values in batch.

    .. attribute:: target

        Store.Target of the field list. Useful to adapt fields depending on the receivers.

.. method:: FieldList.attr(field_name, value=NO_VALUE, *, predicate=None, sudo=False, internal=False)

    Add an attribute to the field list.

    :param field_name: Name of the field
    :param value: Static value or callable(record) -> value
    :param predicate: Callable(record) -> bool to conditionally include
    :param sudo: Use sudo() when reading
    :param internal: Only for internal users

    .. code-block:: python

        # Simple field
        res.attr("name")

        # With static value
        res.attr("computed", True)

        # With callable value
        res.attr("display_name", lambda r: r._compute_display_name())

        # Conditional
        res.attr("secret", "value", predicate=lambda r: r.is_admin)

        # Internal users only
        res.attr("internal_data", internal=True)

.. method:: FieldList.one(record_or_field_name, fields, /, *args, internal=False, **kwargs)

    Add a x2one relation to the field list.

    :param record_or_field_name: Field name or record
    :param fields: Field specification
    :param internal: Only for internal users

    .. code-block:: python

        res.one("author_id", ["name", "email"])
        res.one("partner_id", "_store_partner_fields", sudo=True)
        res.one("create_uid", ["name"], internal=True)

.. method:: FieldList.many(records_or_field_name, fields, /, *args, internal=False, **kwargs)

    Add a x2many relation to the field list.

    .. code-block:: python

        res.many("message_ids", ["body", "date"], mode="ADD")
        res.many("members", "_store_member_fields", sort="name")
        res.many("internal_messages", ["body"], internal=True)

.. method:: FieldList.from_method(method_name, *, internal=False, **fields_params)

    Add fields coming from a method on the records to the field list.

    :param method_name: Method name (must start with ``_store_`` and end with ``_fields``)
    :param fields_params: Parameters to pass to the method

    .. code-block:: python

        res.from_method("_store_partner_fields")
        res.from_method("_store_message_fields", format_reply=True)

.. method:: FieldList.extend(fields, *, internal=False)

    Extend the field list with additional fields.

    :param fields: List of fields to add
    :param internal: Only for internal users

    .. code-block:: python

        res.extend(["name", "email", "phone"])

.. method:: FieldList.is_for_current_user()

    Return whether the current target is the current user or guest of the given env.
    If there is no target at all, this is always True.

    :returns: True if data will only be sent to current user

.. method:: FieldList.is_for_internal_users()

    Return whether the current target implies the information will only be sent to
    internal users.

    :returns: True if data will only be sent to internal users

.. method:: FieldList.target_user()

    Return target user (if any). Target user is either the current bus target if the
    bus is actually targeting a user, or the current user from env if there is no bus
    target at all but there is a user in the env.

    :returns: res.users recordset

.. method:: FieldList.target_guest()

    Return target guest (if any). Target guest is either the current bus target if the
    bus is actually targeting a guest, or the current guest from env if there is no bus
    target at all but there is a guest in the env.

    :returns: mail.guest recordset

.. _reference/mail_store/decorators:

Decorators
==========

@store_version
--------------

.. decorator:: store_version(func)

    Decorator to manage versioned updates in the store.

    Store data is received from RPC and from the bus, and is applied directly to the
    store. Without versioning, the order of arrival can cause outdated data to
    overwrite newer data.

    This decorator injects version metadata into the return value of ``Store.get_result()``,
    both in the value returned by the decorated function and in any bus notifications
    emitted during its execution.

    The versioning is based on PostgreSQL snapshots and the REPEATABLE READ isolation level.

    .. code-block:: python

        from odoo.addons.mail.tools.discuss import store_version, Store

        class MyModel(models.Model):
            _name = 'my.model'

            @store_version
            def my_method(self):
                store = Store()
                store.add(self, ["name"])
                return store.get_result()

@mail_route
-----------

.. decorator:: mail_route(*route_args, **route_kwargs)

    Thin wrapper around ``route`` that adds guest context and enables versioning.
    HTTP route results that return a non-Response object will automatically be converted
    into a proper HTTP JSON response using ``request.make_json_response``.

    This decorator is equivalent to applying, in order::

        @route(*route_args, **route_kwargs)
        @store_version
        @add_guest_to_context

    The ``type`` keyword argument is required.

    .. code-block:: python

        from odoo.addons.mail.tools.discuss import mail_route, Store
        from odoo.http import Controller

        class MyController(Controller):
            @mail_route("/my/route", type="jsonrpc", auth="user")
            def my_route(self):
                store = Store()
                store.add(records, ["name"])
                return store.get_result()

@add_guest_to_context
---------------------

.. decorator:: add_guest_to_context(func)

    Decorate a function to extract the guest from the request.
    The guest is then available on the context of the current request.

    .. code-block:: python

        from odoo.addons.mail.tools.discuss import add_guest_to_context

        class MyController(Controller):
            @route("/my/route", type="jsonrpc", auth="public")
            @add_guest_to_context
            def my_route(self):
                guest = self.env.context.get('guest')
                # ...

.. _reference/mail_store/model_integration:

Model Integration
=================

Implementing _to_store
----------------------

Models can define ``_to_store()`` to customize how their data is added to the store.
This method is called automatically when using ``Store.add()`` on the model.

.. method:: Model._to_store(self, store, field_list)

    Add the model's data to the store.

    :param store: The Store instance
    :param field_list: Store.FieldList with field definitions

    .. code-block:: python

        class MyModel(models.Model):
            _name = 'my.model'

            name = fields.Char()
            partner_id = fields.Many2one('res.partner')

            def _to_store(self, store, field_list):
                # Add the basic fields from field_list
                store.add_records_fields(field_list)

        # Usage - _to_store is called automatically
        store.add(my_records, ["name"])

Field Method Convention
-----------------------

Field methods group related field definitions. They must:

- Start with ``_store_`` and end with ``_fields``
- Accept a ``Store.FieldList`` as first argument
- Optionally accept additional keyword arguments via ``fields_params``

.. code-block:: python

    class DiscussChannel(models.Model):
        _name = 'discuss.channel'

        def _store_channel_fields(self, res):
            """Main field method for channel data."""
            res.extend(["name", "description", "channel_type"])
            res.many("message_ids", "_store_message_fields", sort="date")
            res.one("discuss_category_id", ["name"])

        def _store_message_fields(self, res, format_reply=False):
            """Field method for messages with optional formatting."""
            res.extend(["body", "date", "author_id"])
            if format_reply:
                res.attr("formatted_body", lambda m: m._format_body())
            res.one("author_id", ["name", "email"])

    # Usage
    store.add(channels, "_store_channel_fields")
    store.add(messages, "_store_message_fields", fields_params={"format_reply": True})

Dynamic Fields
--------------

Use the ``dynamic_fields`` parameter to compute fields based on the calling record:

.. code-block:: python

    class MailMessage(models.Model):
        _inherit = 'mail.message'

        def _store_thread_fields(self, res):
            res.one(
                "author_id",
                "_store_author_fields",
                dynamic_fields="_store_dynamic_author_fields",
            )

        def _store_dynamic_author_fields(self, res, message):
            # message is the calling record
            if message.is_internal:
                res.attr("internal_email", message.author_id.email)

.. _reference/mail_store/examples:

Examples
========

Basic Record Addition
---------------------

.. code-block:: python

    from odoo.addons.mail.tools.discuss import Store

    def get_partners(self):
        store = Store()
        partners = self.env['res.partner'].search([('active', '=', True)])
        store.add(partners, ["name", "email", "phone"])
        return store.get_result()

Relations with Predicates
-------------------------

.. code-block:: python

    class DiscussChannel(models.Model):
        _name = 'discuss.channel'

        def _store_channel_fields(self, res):
            res.extend(["name", "description"])

            # Add members only for non-archived channels
            res.many(
                "channel_member_ids",
                ["partner_id"],
                predicate=lambda c: c.active,
            )

            # Add author with sudo for portal access
            res.one("create_uid", ["name"], sudo=True)

Bus Notifications
-----------------

.. code-block:: python

    from odoo.addons.mail.tools.discuss import Store

    def notify_channel_update(self):
        channel = self.env['discuss.channel'].browse(self.id)
        store = Store(bus_channel=channel)
        store.add(channel, ["name", "description"])
        store.bus_send()  # Sends to all channel members via bus

Controller with Versioning
--------------------------

.. code-block:: python

    from odoo.http import Controller
    from odoo.addons.mail.tools.discuss import mail_route, Store

    class DiscussController(Controller):
        @mail_route("/discuss/channel/info", type="jsonrpc", auth="user")
        def channel_info(self, channel_id):
            channel = self.env['discuss.channel'].browse(channel_id)
            store = Store()
            store.add(channel, "_store_channel_fields")
            return store.get_result()

Internal vs External Data
-------------------------

.. code-block:: python

    class ResUsers(models.Model):
        _inherit = 'res.users'

        def _store_user_fields(self, res):
            # Basic fields for all users
            res.extend(["name", "email"])

            # Internal-only fields
            res.attr("internal_settings", internal=True)
            res.from_method("_store_admin_fields", internal=True)

Full Model Integration
----------------------

.. code-block:: python

    class DiscussChannel(models.Model):
        _name = 'discuss.channel'

        name = fields.Char()
        description = fields.Text()
        channel_type = fields.Selection([('chat', 'Chat'), ('channel', 'Channel')])
        message_ids = fields.One2many('mail.message', 'res_id')
        channel_member_ids = fields.One2many('discuss.channel.member', 'channel_id')

        def _to_store(self, store, field_list):
            store.add_records_fields(field_list)

        def _store_channel_fields(self, res):
            """Main field method for channel data."""
            res.extend(["name", "description", "channel_type", "uuid"])
            res.many("channel_member_ids", "_store_member_fields", sort="id")

            # Only add messages for non-chat channels
            res.many(
                "message_ids",
                "_store_message_fields",
                predicate=lambda c: c.channel_type != 'chat',
                sort="date",
            )

        def _store_member_fields(self, res):
            res.extend(["create_date"])
            res.one("partner_id", ["name", "email"])

.. _reference/mail_store/best_practices:

Best Practices
==============

Performance
-----------

- Use ``sudo=True`` sparingly - it bypasses access rights
- Use ``predicate`` to conditionally include data instead of adding then deleting
- Batch operations by using ``extend()`` with a list rather than multiple ``attr()`` calls

Security
--------

- Use ``internal=True`` for fields that should only be visible to internal users
- Use ``predicate`` to conditionally show sensitive data
- Be careful with ``sudo=True`` - it bypasses access control

Avoiding Circular Dependencies
------------------------------

- Don't call ``store.add()`` from within ``_to_store()`` - use ``store.add_records_fields()`` instead
- Use ``only_data=True`` when you only need the data without the ID reference

.. code-block:: python

    def _to_store(self, store, field_list):
        # WRONG - will cause infinite loop
        # store.add(self, ["name"])

        # CORRECT
        store.add_records_fields(field_list)

Target-Aware Fields
-------------------

Use ``is_for_current_user()``, ``is_for_internal_users()``, and ``target`` to adapt
the data based on who will receive it:

.. code-block:: python

    def _store_user_fields(self, res):
        res.extend(["name"])

        # Only add sensitive data when sending to the user themselves
        if res.is_for_current_user():
            res.attr("preferences", lambda u: u._get_preferences())

        # Only add admin data for internal users
        if res.is_for_internal_users():
            res.attr("admin_notes")
