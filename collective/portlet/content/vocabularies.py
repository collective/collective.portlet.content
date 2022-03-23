# -*- coding: utf-8 -*-
from collective.portlet.content import ContentPortletMessageFactory as _
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


@implementer(IVocabularyFactory)
class TitleDisplayVocabulary(object):
    """Vocabulary factory for title_display.
    """

    def __call__(self, context):
        return SimpleVocabulary(
            [SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                for pair in [
                    (u'hidden', _(u'Hidden')),
                    (u'text', _(u'Display as text')),
                    (u'link', _(u'Display as a link')),
            ]]
        )
TitleDisplayVocabularyFactory = TitleDisplayVocabulary()


@implementer(IVocabularyFactory)
class ItemDisplayVocabulary(object):
    """Vocabulary factory for item_display.
    """

    def __call__(self, context):
        return SimpleVocabulary(
            [SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                for pair in [
                    (u'date', _(u'Date')),
                    (u'description', _(u'Description')),
                    (u'image', _(u'Image')),
                    (u'body', _(u'Body')),
            ]]
        )
ItemDisplayVocabularyFactory = ItemDisplayVocabulary()
