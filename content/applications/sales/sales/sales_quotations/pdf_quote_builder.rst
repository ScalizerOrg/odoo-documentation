:show-content:
:hide-page-toc:

=================
PDF quote builder
=================

The *PDF Quote Builder* in Odoo *Sales* provides the opportunity to send customers a fully
customized PDF file for quotes, showcasing the company and products, with various information and
design elements, instead of just showing the price and total.

The PDF Quote Builder groups header pages, product descriptions, the price(s), and footer pages to
create a detailed quote. It can also inject dynamic texts or custom notes in the PDF to personalize
the offer for the customer.

Having a customized PDF in quotes provides a heightened conclusion to the shopping experience for
customers, and adds an elegant level of professionalism to a company.

.. seealso::
   `Odoo Quick Tips - Create a PDF quote [video] <https://www.youtube.com/watch?v=tQNydBZt-VI>`_

.. note::
   It is recommended to edit PDF forms with Adobe software. The form fields on the header and footer
   PDF templates are necessary to get dynamic values with Odoo.

.. cards::

   .. card:: Add dynamic text to PDFs
      :target: pdf_quote_builder/dynamic_text

      Add dynamic text fields to PDFs.

   .. card:: Add PDFs to quotes
      :target: pdf_quote_builder/add_pdf_quotes

      Add a PDF header or footer to a quote.

   .. card:: Add PDFs to products
      :target: pdf_quote_builder/add_pdf_products

      Set up the headers and footers for products. These will appear on sales quotes and online
      store pages.


Configuration
=============

In order to add custom PDF files for quotes, the :guilabel:`PDF Quote builder` feature *must* be
configured.

To do that, navigate to :menuselection:`Sales app --> Configuration --> Settings`. Then, on the
:guilabel:`Settings` page, scroll to the :guilabel:`Quotations & Orders` section, and locate the
:guilabel:`PDF Quote builder` feature.

Add PDF as Header/Footer
========================

In Odoo *Sales*, it's possible to add a custom PDF that can be used either as a header or a footer.
When the PDF quote builder is activated in a quotation, you can then select as many headers and
footers as you wish to use, these PDF will then also be inserted in the final PDF.

To add a custom PDF as header or footer, start by navigating to :menuselection:`Sales app -->
Configuration --> Headers/Footers`. From this page, either click :guilabel:`New` or
:guilabel:`Upload`.

Clicking :guilabel:`Upload` instantly provides the opportunity to upload the desired document. Then,
the document can be further configured on the document card, or by clicking the
:icon:`fa-ellipsis-v` :guilabel:`(vertical ellipsis)` icon in the top right corner of the document
card, and then clicking :guilabel:`Edit`.

Clicking :guilabel:`New` reveals a blank documents form, in which the desired PDF can be uploaded
via the :guilabel:`Upload your file` button on the form, located in the :guilabel:`File Content`
field.

Various information and configurations related to the uploaded document can be modified here.

The first field on the documents form is for the :guilabel:`Name` of the document, and it is
grayed-out (not clickable) until a document is uploaded. Once a PDF has been uploaded, the
:guilabel:`Name` field is auto-populated with the name of the PDF, and it can then be edited.

Then, in the :guilabel:`Document Type` field, click the drop-down menu, and select either:
:guilabel:`Header`, or :guilabel:`Footer` to define whether these files would be selectable to be at
the beginning or at the end of your quote.

Under this, in the :guilabel:`Quotation Templates` section, this PDF can be restricted quotation
templates only.

.. note::
   Alternatively, you can also navigate to :menuselection:`Sales app --> Configuration --> Quotation
   Templates`, select a template and directly :guilabel:`Add` or :guilabel:`Upload` a PDF to it in
   the :guilabel:`Quote Builder` tab.

Lastly, beside the :guilabel:`File Content` field, you have the possibility to :guilabel:`Configure
dynamic fields`.

.. toctree::
   :titlesonly:

   pdf_quote_builder/dynamic_text
   pdf_quote_builder/add_pdf_quotes
   pdf_quote_builder/add_pdf_products
