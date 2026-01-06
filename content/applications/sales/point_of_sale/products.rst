========
Products
========

Products can be created from the backend or the POS interface. To manage products from the backend,
go to :menuselection:`Point of Sale --> Products --> Products`. Click :guilabel:`New` to create a
product, or open an existing one to edit it. Update the fields as needed and ensure the
:guilabel:`Point of Sale` checkbox is enabled at the top of the form.

To create products from the POS interface, access the POS register, click the :icon:`fa-bars`
(:guilabel:`hamburger menu`) icon, then :guilabel:`Create Product`. Enter the product details in the
pop-up window and click :guilabel:`Save`. The product is immediately available in the register.

To update an existing product from the POS register, long-click a product to open the information
pop-up, and click :guilabel:`Edit`. Change the necessary product details and click :guilabel:`Save`
to return to the POS register.

.. tip::
   To temporarily make the product unavailable for sale in the POS register or :doc:`self-ordering
   menu <../point_of_sale/self_order>`, click :guilabel:`Snooze`, select the desired duration, and
   click :guilabel:`Apply`. To reactivate the product before the set period ends, long-click the
   product in the register, click the countdown timer, then click :guilabel:`Yes` to confirm.

.. seealso::
   `Product creation (video tutorial) <https://youtu.be/b5eVusXHEvg?si=Xn3EBMmRfJ35mqyu>`_

POS product categories
======================

POS product categories are used to organize products in the POS register.

To manage POS categories, follow these steps:

#. Navigate to :menuselection:`Point of Sale --> Configuration --> PoS Product Categories`.
#. Click :guilabel:`New` to create a category or click an existing one to update it.
#. Classify and build a hierarchy between categories: Associate a category with a parent
   category by filling in the :guilabel:`Parent Category` field. A parent category groups one or
   more child categories (e.g., use `Drinks` to group `Hot beverages` and `Soft drinks`).

Once POS product categories are created, assign them to specific products:

#. Go to :menuselection:`Point of Sale --> Products --> Products` and open a product form.
#. Navigate to the :guilabel:`Point of Sale` tab and fill in the :guilabel:`Category` field with one
   or multiple POS categories.

To limit the categories displayed on the POS register, navigate to the :ref:`POS settings
<pos/use/settings>` and select the relevant categories in the :guilabel:`Restrict Categories` field
under the :guilabel:`Product & PoS categories` section.

.. _pos/products/combos:

Product combos
==============

A product combo is a bundle of multiple products sold together as a unit. Each product combo
consists of multiple categories, known as :ref:`combo choices <pos/products/combo-choices>`, and
each combo choice contains several items. When purchasing a product combo, customers can select one
or more items from each combo choice.

.. example::
    A burger menu is offered as a product combo including three combo choices: one burger, one
    drink, and one portion of fries. For each combo choice, customers select one item from the
    available options (e.g., cheeseburger or chicken burger; soda or water; regular or large fries).

.. seealso::
   `Product combos (video tutorial) <https://youtu.be/H8e2CakLhaQ?si=yjPbvYkj00K7OP3q>`_

.. _pos/products/combo-choices:

Combo choice creation
---------------------

To create the combo choices that will be added to the :ref:`product combo
<pos/products/combo-creation>`, follow the next steps:

#. Go to :menuselection:`Point of Sale --> Products --> Combo Choices` and click :guilabel:`New`.
#. Enter a name for the :guilabel:`Combo Choice`.
#. Set the maximum selectable items for the combo choice using the :guilabel:`Maximum items` field.
#. Set the number of items included in the combo choice using the :guilabel:`Includes items` field.
#. Optionally, enable the :guilabel:`Is Upsell` option if the combo choice is an upsell in the
   :ref:`POS register <pos/use/open-register>`.
#. Click :guilabel:`Add a line` under the :guilabel:`Options` section to add the products that
   constitute the :guilabel:`Combo Choices`.
#. If needed, click a product to add an :guilabel:`Extra Price`.

.. admonition:: Combo Price vs. Extra Price

  - The :guilabel:`Combo Price` field shows the price applied to any additional product a customer
    might select (i.e., when the :guilabel:`Maximum items` field is set to `2` or higher). This
    price is automatically calculated based on the price of the least expensive product defined in
    the :guilabel:`Combo Choice`.
  - The :guilabel:`Extra Price` field is used to set an additional charge for a specific product in
    the combo choice, e.g., to cover higher costs or encourage upselling. This extra price is
    applied each time a customer selects that product within the combo choice.

.. note::
   Enabling the :guilabel:`Is Upsell` option removes the :guilabel:`Includes items` field, which
   prevents from including items for free.

.. _pos/products/combo-creation:

Product combo creation
----------------------

To create a specific product that contains :ref:`combo choices <pos/products/combo-choices>`,
follow the next steps:

#. Go to :menuselection:`Point of Sale --> Products --> Products` and click :guilabel:`New`.
#. Enter a product name.
#. Set the :guilabel:`Product Type` to :guilabel:`Combo` and select the relevant :ref:`Combo
   Choices <pos/products/combo-choices>`.
#. Add a :guilabel:`Sales Price`.
#. Optionally, click the :guilabel:`Point of Sale` tab to select the preferred :guilabel:`Category`.

.. seealso::
   :doc:`/applications/sales/sales/products_prices/products/variants`

.. _pos/products/combo-application:

Combo application
-----------------

To apply combos, follow these steps:

#. Open the :ref:`POS register <pos/use/open-register>`.
#. Click the desired product combo, and select the preferred items for each combo choice.
#. Click :guilabel:`Add to order`.
#. Continue with the order process.

.. note::
   The total price of the product combo, as displayed in the :ref:`POS register
   <pos/use/open-register>`, is based on the :guilabel:`Sales Price` defined on the :ref:`product
   combo's form <pos/products/combo-creation>`. Selecting several products in the combo choices and
   selecting a product with an :guilabel:`Extra Price` influences the total price.

   .. example::
      The :guilabel:`Office Combo` has a :guilabel:`Sales Price` of **300** € and offers a
      selection of chairs and desks. The combo choice for chairs includes a conference chair, an
      office chair, and an armchair with a maximum selectable amount set to 2. The :guilabel:`Combo
      Price` for the chair combo choice is **35** € per added item because the conference chair is
      the least expensive product. The armchair has an :guilabel:`Extra Price` of **100** € because
      it is made of leather. Selecting the conference chair with the armchair increases the price
      of the :guilabel:`Office Combo` to **435** €. Thus, selecting the armchair adds **35** €
      (:guilabel:`Combo Price`) + **100** € (:guilabel:`Extra Price`).

      .. image:: products/office-combo.png
         :scale: 60%
