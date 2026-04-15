====================
Timesheets assistant
====================

Timesheets Assistant monitors the user’s activity on their computer and in their Internet browser to
simplify timesheet logging.

The calculation is based on predefined rules and learning from the user’s previous matches between
suggested timesheets and their assigned projects. These rules act as *key events*. Once a key event
is triggered, any subsequent activity of minimum one minute is associated with that event until a
new key event is triggered. The more rules that are configured, the more precise the results become
and the less they are affected by short or irrelevant entries.

By default, Timesheets Assistant includes ready-to-use rules to track the time spent working in
Odoo, on GitHub and Google Docs, browsing Gmail, and using Discord. These rules can be edited or
removed, and new ones can be added by the user.

.. example::
   A user opens a project task in their Odoo database (the key event), then spends one hour browsing
   websites and using various applications until they open another project task. Timesheets
   Assistant then suggests a one-hour timesheet entry linked to the most relevant project. This
   suggestion can be confirmed by matching it, or another project can be selected to associate the
   time with.

Timesheets Assistant also checks the user's calendar events and planning in Odoo to make
suggestions. For instance, if the user has a meeting with a customer from 10 to 11 AM, they will
receive a Timesheet entry suggestion for it.

Periods of keyboard and mouse inactivity are also tracked. Any inactive period of at least 3 minutes
is considered away-from-keyboard, and Timesheets Assistant identifies that time as a break.

.. important::
   The user’s activity data is processed locally on their device and is never shared with anyone,
   either within or outside their organization. Not even Odoo, as a company, can access a user’s
   activity.

Configuring Timesheets Assistant
================================

Activation
----------

Timesheets Assistant must be enabled before use.

.. important::
   Timesheets Assistant is only available when the encoding method is set to Hours / Minutes. Go to
   :menuselection:`Settings --> Timesheets` and make sure the Encoding Method is set to
   :guilabel:`Hours / Minutes`.

Then go to :menuselection:`Settings --> Timesheets` and enable :guilabel:`Timesheets Assistant`.
Click :guilabel:`Save`.

Installation
------------

A dedicated open source software called ActivityWatch must be installed on the user’s computer and
browser to track their activity.

Go to :menuselection:`Timesheets --> Assistant`.

.. note::
   If your browser requests access to apps and services on this device in a pop-up, click
   :guilabel:`Allow`.

   If you don’t see the prompt, in Google Chrome, click the Tune icon to the left of the address
   bar. Click :guilabel:`Site Settings`. Look for a permission related to “Apps on device” (or
   similar) and set it to :guilabel:`Allow`. Refresh the page.

Go to :menuselection:`Timesheets --> Assistant --> Start Now`.

Desktop activity
~~~~~~~~~~~~~~~~

:guilabel:`Desktop Activity` (required) tracks user activity on their computer by analyzing open
windows and applications. The minimum (oldest supported) versions required are Windows 10, macOS
10.15, and Ubuntu 24 on Linux.

Select the right operating system for your configuration below and follow the steps:

.. tabs::

   .. tab:: Windows

      #. Odoo automatically detects that your operating system is Windows and offers you the option
         to download the appropriate ActivityWatcher installation package for your configuration by
         clicking :guilabel:`Download for Windows`. You can also download the `Windows installation
         package <https://nightly.odoo.com/aw/windows/activitywatch-odoo_patched-latest-setup.exe>`_.

      #. Follow the installation instructions. To complete the installation, you need to restart
         your computer or log out. Either option will close all running applications. After
         restarting or logging back in, return to Timesheets Assistant to continue setup :
         :menuselection:`Timesheets --> Assistant --> Start Now` .

      #. To help Timesheets Assistant automatically suggest your timesheet entries, your browser
         needs to be able to communicate with your local ActivityWatch server. Click
         :guilabel:`Open Settings` to access the ActivityWatch website. Under Server Settings,
         locate the CORS field. Copy and paste your Odoo database URL exactly as shown, in quotes
         and without a slash (/) at the end. Example: `"https://my-company.odoo.com"`

   .. tab:: Mac

      #. Install ActivityWatch

         #. Odoo automatically detects that your operating system is macOS and offers you the option
            to download the appropriate ActivityWatch installation package for your configuration by
            clicking :guilabel:`Download for macOS`. You can also download the `macOS
            installation package <https://github.com/ActivityWatch/activitywatch/releases/download/v0.13.2/activitywatch-v0.13.2-macos-x86_64.dmg>`_.

         #. Once downloaded, open the .dmg file and move the ActivityWatch application into your
            Mac's Applications folder.
         #. Go to the Applications folder and launch ActivityWatch.
         #. Click on the the ActivityWatch icon that is now in the menu bar and :

           - Click :guilabel:`Open Dashboard` to see a timeline of events captured by ActivityWatch.
           - Click :guilabel:`Modules Menu` to display a list of watchers and servers:

             - Python Server (aw-server) – Default server.
             - Rust Server (aw-server-rust) – More efficient, will eventually replace Python server.

      #. Configure Python Server (aw-server)

         Skip this section if :guilabel:`aw-server-rust` is enabled and go to Rust Server
         Configuration below.

         - Click the ActivityWatch icon in the menu bar and go to
           :guilabel:`Open Configuration Folder.`
         - The Finder opens the configuration folder, which contains:

           - :guilabel:`aw-client`: Web interface for user settings and timeline.
           - :guilabel:`aw-qt`: Main program launched by ActivityWatch.
           - :guilabel:`aw-server`: Python server configuration folder.
           - :guilabel:`aw-server-rust`: Rust server configuration folder.
           - :guilabel:`Watcher folders`: Programs capturing activity and sending it to the server.

         - Open :guilabel:`aw-server/aw-server.toml`.
         - To allow your Odoo database to communicate with ActivityWatch, update the CORS parameters
           to match this:

            [server]

           #host = "localhost"

           #port = "5600"

           #storage = "peewee"

           cors_origins = `"https://example.odoo.com"`

           [server.custom_static]

           [server-testing]

           #host = "localhost"

           #port = "5666"

           #storage = "peewee"
           #cors_origins = ""

           [server-testing.custom_static]

            .. important::
               In the parameters above, make sure to replace `https://example.odoo.com` with the URL
               of your odoo instance, in quotes and without a slash (/) at the end.

         - Save the file.

      #. Configure Rust Server (aw-server-rust)

         - Click the ActivityWatch menu in the menu bar and go to
           :guilabel:`Open Configuration Folder`.
         - Open :guilabel:`aw-server-rust/config.toml`.
         - To allow your Odoo database to communicate with ActivityWatch, update the CORS parameters
           to match this:

            ### DEFAULT SETTINGS ###

           #address = "127.0.0.1"

           #port = 5600

           cors = [`"https://example.odoo.com"`]

           #

           #[custom_static]

           .. important::
               In the parameters above, make sure to replace `https://example.odoo.com` with the URL
               of your odoo instance, in quotes and without a slash (/) at the end.

         - Save the file.

      #. Restart ActivityWatch

         - To apply configuration changes:

           - Click the :guilabel:`ActivityWatch` menu and :guilabel:`Quit ActivityWatch`.
           - Relaunch :guilabel:`ActivityWatch` from the Applications folder.

   .. tab:: Linux

      #. Odoo automatically detects that your operating system is Linux and offers you the option to
         download the appropriate ActivityWatcher installation package for your configuration by
         clicking :guilabel:`Download for Linux`. You can also download the `Linux installation
         package <https://nightly.odoo.com/aw/ubuntu/activitywatch-odoo.deb>`_. Then follow the
         instructions to install ActivityWatcher on your computer.

      #. To complete the installation, you need to restart your computer or log out. Either option
         will close all running applications. After restarting or logging back in, return to
         Timesheets Assistant to continue setup : :menuselection:`Timesheets --> Assistant --> Start
         Now`

      #. To help Timesheets Assistant automatically suggest your timesheet entries, your browser needs
         to be able to communicate with your local ActivityWatch server. Click
         :guilabel:`Open Settings` to access the ActivityWatch website. Under Server Settings,
         locate the CORS field. Copy and paste your Odoo database URL exactly as shown, in quotes
         and without a trailing slash (/) . Example: `"https://my-company.odoo.com"`

      #. Click the Odoo icon in your system tray (usually in the top bar or bottom right of your
         screen), then click :guilabel:`Restart Server`.

      #. Your browser may block connections to apps or services running on your computer. If
         prompted, allow access so the Assistant can detect and connect to ActivityWatch. Most
         browsers will prompt automatically when needed.

      #. Timesheets Assistant is now ready to track your activity. Click :guilabel:`Test Connection`
         to verify that everything is working. Start the server from the system tray at the
         beginning of your work day.

.. note::

   Optionally, ActivityWatch also provides
   `a wide range of watchers <https://docs.activitywatch.net/en/latest/watchers.html>`_ dedicated to
   specific activities that users can manually install if they want. Using more activity watchers
   allows Timesheets Assistant to provide more accurate results.

Browser activity
~~~~~~~~~~~~~~~~

:guilabel:`Browser Activity` (recommended) tracks user activity within the browser based on the open
tabs and websites. Although optional, enabling Browser Activity allows Timesheets Assistant to
generate more accurate results by processing additional data.

Click on the Firefox or Google Chrome button to install the right extension for your browser, or
download it here for `Firefox <https://addons.mozilla.org/en-US/firefox/addon/aw-watcher-web/>`_ or
`Google Chrome <https://chromewebstore.google.com/detail/activitywatch-web-watcher/nglaklhklhcoonedhgnpgddginnjdadi>`_.

Assistant Rules
---------------

Assistant rules use regular expressions (regex) to provide Odoo with guidance on how to interpret
user activity tracked on their desktop and browser, and to convert it into timesheet entry
suggestions.

.. note::

   Regular expressions, often abbreviated as regex, can be used in Odoo in various ways to search,
   validate, and manipulate data. Regex can be powerful but also complex, so it’s essential to use
   it judiciously. `Learn more about Regex and how to use it <https://regexone.com/>`_.

To add a rule, go to :menuselection:`Timesheets --> Configuration --> Assistant Rules --> New`, then
fill in the following fields:

- :guilabel:`Name`: The title you want to give to your rule.

- :guilabel:`Regex`: The pattern used to classify an activity as a key event by capturing
  ActivityWatch events (window name, tab name or URL) and display them in the Timesheet Assistant
  when their duration exceeds 1 minute.

- :guilabel:`Type`: Choose the icon displayed in the assistant suggestions list.

- :guilabel:`Template`: Defines the name of the generated timesheet entry and is used by local rules
  for further processing. If left blank, the rule name is used instead.

- :guilabel:`Description`: A display-only label shown in the Timesheet Assistant. It is purely
  indicative and has no impact on local rules or timesheet generation.

- :guilabel:`Project` and :guilabel:`Task`: The values selected by default for activities matching
  this rule. If left blank, local rules apply.

- :guilabel:`Always active`: Enable it to track activities matched by this rule, even if
  ActivityWatch marks the user as inactive after three minutes of inactivity. For example, if a
  user has a meeting, inactivity on the keyboard and mouse might be interpreted as a break. If the
  rule covering meetings has Always Active enabled, ActivityWatch does not mark the user as
  inactive during that activity.

.. example::

   Here's an example for a Google Meet rule:

   - :guilabel:`Name`: Customer Meeting
   - :guilabel:`Regex`: Meet - (.*)\|https://meet.google.com
   - :guilabel:`Type`: Videocall
   - :guilabel:`Template`: Customer Meeting ($1) (refers to the value captured by the first group in
     the regex.)
   - :guilabel:`Description`: Customer Meeting (abc-123) (static example to illustrate — in practice
     , this is an indicative version of the template shown in the suggestions list, which can be
     used at the user’s convenience, e.g., "Customer Meeting (meet-id)")
   - :guilabel:`Project` and :guilabel:`Task`: Left empty, since each meeting may belong to a
     different customer/task
   - :guilabel:`Always active`: Enabled

Local Assistant Rules
---------------------

.. important::

   Local Assistant Rules are only available in
   :doc:`Developer mode </applications/general/developer_mode>` (also called *Debug Mode*).

   Turn on :guilabel:`Developer Mode`, then go to
   :menuselection:`Timesheets --> Configuration --> Local Assistant Rules`.


:guilabel:`Local Assistant Rules` show the project and task assigned to each ActivityWatch key
event. It is available for informational purposes, to help understand why Odoo selects a project or
task for a key event, or why Odoo does not detect the correct project or task.

When suggested timesheet entries are matched with projects, Odoo learns from those selections to
improve future suggestions. The data shown here indicate how timesheet entry patterns are analyzed
to help recommend relevant projects and tasks based on past behavior.

Using Timesheets Assistant
==========================

Once Timesheet Assistant is properly setup, go to :menuselection:`Timesheets --> Assistant`.  In the
:guilabel:`Suggestions` section, click on one or multiple :guilabel:`Unmatched` timesheet
suggestions.

Then select a project in the left panel to assign the suggestion(s). You can also add a
:guilabel:`Description`, select a :guilabel:`Task`, or adjust the recorded time if needed, mark it
as :guilabel:`Billable` if required, and click :guilabel:`Create`.

.. note::
   The time rounding configured in :menuselection:`Configuration --> Settings --> Time Rounding` is
   applied to the timesheets suggestions.

Hover over a suggestion and click :guilabel:`Remove` to delete it if needed.

To edit a timesheet entry you’ve already created, click the entry, make the necessary changes, and
click :guilabel:`Save`.

While timesheet suggestions remain private to the user, once a timesheet is created, the data
becomes public and visible to other users in your organization.
