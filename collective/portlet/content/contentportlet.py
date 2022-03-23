from AccessControl import getSecurityManager
from collective.portlet.content import ContentPortletMessageFactory as _
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.memoize import instance
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

__ = MessageFactory("plone")


class IContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(
        title=_(u'Portlet Title'),
        description=_('help_portlet_title',
                      default=u'Enter a title for this portlet. '
                               "This property is used as the portlet's title "
                               'in the "@@manage-portlets" screen. '
                               'Leave blank for "Content portlet".'),
        required=False,
    )

    custom_header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_('help_custom_header',
                      default=u"Set a custom header (title) for the rendered "
                              u"portlet. Leave empty to use the selected "
                              u"content's title."),
        required=False,
    )

    title_display = schema.Choice(
        title=_(u'Item Title in portlet content'),
        description=_('help_title_display',
                      default=u"Do you want to render the item's title inside "
                              u"the portlet content, and if yes, how?\n"
                              u"Note that by default, the item's title will "
                              u"be displayed in the portlet header."),
        vocabulary='collective.portlet.content.title_display_vocabulary',
        default=u'hidden',
        required=True,
    )

    content = schema.Choice(
        title=_(u"Content Item"),
        vocabulary="plone.app.vocabularies.Catalog",
        required=True,
    )
    directives.widget("content", RelatedItemsFieldWidget)

    item_display = schema.List(
        title=_(u'Item Display'),
        description=_('help_item_display',
                      default=u"Select which of the selected item's fields "
                              u"will be displayed in the portlet's content "
                              u"area. Note that selecting Body (text) will "
                              u"not work for an Image."),
        value_type=schema.Choice(
            vocabulary='collective.portlet.content.item_display_vocabulary',
        ),
        default=[u'date', u'description'],
        required=False,
    )

    more_text = schema.TextLine(
        title=_(u'Read More Link'),
        description=_('help_more_text',
                      default=u"Enter the text for the link in the portlet "
                              u"footer. Leave blank for no footer."),
        default=u'',
        required=False,
    )

    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_('help_omit_border',
                      default=u"Tick this box if you want to render the "
                              u"content item selected above without the "
                              u"standard header, border or footer."),
        required=False,
        default=False)

    omit_header = schema.Bool(
        title=_(u"Omit portlet header"),
        description=_('help_omit_header',
                      default=u"Tick this box if you don't want the portlet "
                               "header to be displayed."),
        required=False,
        default=False)


@implementer(IContentPortlet)
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    portlet_title = u''
    content = None
    title_display = u'hidden'
    item_display = [u'date', u'description']
    more_text = u''
    omit_border = False
    custom_header = u""
    omit_header = False

    def __init__(self, portlet_title=u'', content=None, title_display=u'link',
            item_display=[u'date', u'description'], more_text=u'',
            omit_border=None, custom_header=None, omit_header=None):
        self.portlet_title = portlet_title
        self.content = content
        self.omit_border = omit_border
        self.custom_header = custom_header
        self.omit_header = omit_header
        self.title_display = title_display
        self.item_display = item_display
        self.more_text = more_text

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        msg = __(u"Content portlet")
        return getattr(uuidToCatalogBrain(self.content), 'Title', None) or msg


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('contentportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @instance.memoizedproperty
    def content(self):
        """
        Returns the content object or None if it does not exist.
        """

        if not self.data.content:
            return None

        item = uuidToCatalogBrain(self.data.content)
        if item is None:
            return None

        if not getSecurityManager().checkPermission('View', item):
            return None

        return item

    def date(self):
        """
        Returns the item date or None if it should not be displayed.
        """
        if u'date' not in self.data.item_display:
            return
        return self.content.Date

    def image(self):
        """
        Returns the item image or None if it should not be displayed.
        """
        if u'image' not in self.data.item_display:
            return
        obj = self.content.getObject()
        image = getattr(obj.aq_base, 'image', None)
        if not image:
            return
        scaled_image = obj.restrictedTraverse("@@images").scale('image', scale='preview')
        return scaled_image

    def description(self):
        """
        Returns the item description or None if it should not be displayed.
        """
        if not u'description' in self.data.item_display:
            return None

        return self.content.Description

    def body(self):
        """
        Returns the body HTML or None if it should not be displayed.
        (or is not present on the object)
        """
        if u'body' not in self.data.item_display:
            return None

        # Currently nothing stops you from trying to get text from an Image
        obj = self.content.getObject()
        text = getattr(obj.aq_base, 'text', None)
        if not text:
            return
        if isinstance(text, RichTextValue):
            text = text.output
        return text

    def more_url(self):
        return self.content.getURL()

    def header(self):
        return self.data.custom_header or self.content.Title

    def has_footer(self):
        return bool(self.data.more_text)


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    schema = IContentPortlet
    label = _(u"Add Content Portlet")
    ddescription = _(u"A portlet that shows a content item.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    schema = IContentPortlet
    label = _(u"Edit Content Portlet")
    description = _(u"A portlet that shows a content item.")
